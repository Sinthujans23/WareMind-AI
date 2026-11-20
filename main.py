
"""WareMind AI - Multi-Agent Warehouse Simulation.

Controls:
O     - Add a random order
B     - Add a random dynamic obstacle
R     - Remove a random dynamic obstacle
SPACE - Pause or resume
ESC   - Exit

Run: python main.py
"""

import random
import pygame

from waremind.core import (
    WIDTH,
    HEIGHT,
    SHELVES,
    DEPOT,
    CHARGER,
)
from waremind.mesa_model import WarehouseMesaModel


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

CELL = 46
SIDE = 400

SCREEN_WIDTH = WIDTH * CELL + SIDE
SCREEN_HEIGHT = HEIGHT * CELL

FPS = 30
SIMULATION_INTERVAL = 12

BACKGROUND = (19, 27, 41)
FLOOR_COLOR = (45, 59, 77)
SHELF_COLOR = (151, 116, 71)
TEXT_COLOR = (224, 234, 244)
MUTED_COLOR = (150, 165, 185)
ACCENT_COLOR = (75, 195, 220)

ROBOT_COLORS = [
    (50, 115, 235),
    (35, 170, 105),
    (235, 155, 50),
]


# --------------------------------------------------
# PERFORMANCE METRICS
# --------------------------------------------------

def get_performance_metrics(model):
    world = model.warehouse
    robots = world.robots

    total_orders = len(world.orders)
    completed_orders = world.completed_count
    pending_orders = total_orders - completed_orders

    total_robots = len(robots)

    average_battery = (
        sum(robot.battery for robot in robots)
        / total_robots
        if total_robots else 0.0
    )

    return {
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "pending_orders": pending_orders,

        "working_robots": sum(
            robot.order_id is not None
            for robot in robots
        ),

        "idle_robots": sum(
            robot.order_id is None and not robot.charging
            for robot in robots
        ),

        "charging_robots": sum(
            robot.charging
            for robot in robots
        ),

        "stuck_robots": sum(
            robot.stuck
            for robot in robots
        ),

        "average_battery": average_battery,

        "total_waiting_ticks": sum(
            robot.waiting_ticks
            for robot in robots
        ),

        "recovery_count": world.recovery_count,

        "messages_sent": len(model.bus.history),
    }


# --------------------------------------------------
# BATTERY BAR
# --------------------------------------------------

def draw_battery_bar(screen, x, y, width, battery):
    battery = max(0.0, min(100.0, battery))

    height = 10

    pygame.draw.rect(
        screen,
        (65, 75, 90),
        (x, y, width, height),
        border_radius=5,
    )

    if battery < 25:
        color = (235, 85, 85)
    elif battery < 60:
        color = (240, 180, 65)
    else:
        color = (65, 195, 130)

    filled_width = int(width * battery / 100)

    if filled_width > 0:
        pygame.draw.rect(
            screen,
            color,
            (x, y, filled_width, height),
            border_radius=5,
        )


# --------------------------------------------------
# DRAW WAREHOUSE
# --------------------------------------------------

def draw_warehouse(screen, world, font):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            rect = pygame.Rect(
                x * CELL,
                y * CELL,
                CELL - 1,
                CELL - 1,
            )

            color = (
                SHELF_COLOR
                if (x, y) in SHELVES
                else FLOOR_COLOR
            )

            pygame.draw.rect(
                screen,
                color,
                rect,
                border_radius=3,
            )

    # Dynamic obstacles
    for x, y in world.dynamic_obstacles:
        pygame.draw.rect(
            screen,
            (210, 70, 75),
            (
                x * CELL + 5,
                y * CELL + 5,
                CELL - 10,
                CELL - 10,
            ),
            border_radius=5,
        )

    # Depot and charger
    special_cells = [
        (DEPOT, (137, 95, 220), "D"),
        (CHARGER, (40, 190, 205), "C"),
    ]

    for pos, color, name in special_cells:
        x, y = pos

        pygame.draw.rect(
            screen,
            color,
            (
                x * CELL + 5,
                y * CELL + 5,
                CELL - 10,
                CELL - 10,
            ),
            border_radius=6,
        )

        label = font.render(
            name,
            True,
            (255, 255, 255),
        )

        screen.blit(
            label,
            label.get_rect(
                center=(
                    x * CELL + CELL // 2,
                    y * CELL + CELL // 2,
                )
            ),
        )

    # Orders
    for order in world.orders:
        if order.completed:
            continue

        # Hide pickup marker after collection.
        assigned_robot = next(
            (
                robot
                for robot in world.robots
                if robot.order_id == order.id
                and robot.carrying
            ),
            None,
        )

        if assigned_robot is not None:
            continue

        x, y = order.pickup

        pygame.draw.circle(
            screen,
            (255, 225, 100),
            (
                x * CELL + CELL // 2,
                y * CELL + CELL // 2,
            ),
            9,
        )

    # Robots
    for robot in world.robots:
        x, y = robot.pos

        color = ROBOT_COLORS[
            (robot.id - 1) % len(ROBOT_COLORS)
        ]

        pygame.draw.circle(
            screen,
            color,
            (
                x * CELL + CELL // 2,
                y * CELL + CELL // 2,
            ),
            17,
        )

        label = font.render(
            str(robot.id),
            True,
            (255, 255, 255),
        )

        screen.blit(
            label,
            label.get_rect(
                center=(
                    x * CELL + CELL // 2,
                    y * CELL + CELL // 2,
                )
            ),
        )


# --------------------------------------------------
# DRAW DASHBOARD
# --------------------------------------------------

def draw_dashboard(screen, model, small, paused):
    world = model.warehouse
    metrics = get_performance_metrics(model)

    ox = WIDTH * CELL + 16
    y = 12

    def draw_text(text, color=TEXT_COLOR, gap=19):
        nonlocal y

        label = small.render(
            str(text),
            True,
            color,
        )

        screen.blit(label, (ox, y))
        y += gap

    def section(title):
        nonlocal y
        y += 5
        draw_text(title, ACCENT_COLOR, 22)

    # Header
    draw_text(
        "WAREMIND AI",
        (255, 255, 255),
        21,
    )

    draw_text(
        "MULTI-AGENT DASHBOARD",
        MUTED_COLOR,
        25,
    )

    status = "PAUSED" if paused else "RUNNING"

    draw_text(
        f"Tick: {world.tick}   Status: {status}",
        gap=19,
    )

    # Order statistics
    section("ORDER STATISTICS")

    draw_text(
        f"Total: {metrics['total_orders']}    "
        f"Completed: {metrics['completed_orders']}"
    )

    draw_text(
        f"Pending: {metrics['pending_orders']}"
    )

    # Robot status
    section("ROBOT STATUS")

    draw_text(
        f"Working: {metrics['working_robots']}    "
        f"Idle: {metrics['idle_robots']}"
    )

    draw_text(
        f"Charging: {metrics['charging_robots']}    "
        f"Stuck: {metrics['stuck_robots']}"
    )

    # Performance
    section("PERFORMANCE")

    draw_text(
        f"Avg Battery: "
        f"{metrics['average_battery']:.1f}%"
    )

    draw_text(
        f"Waiting: {metrics['total_waiting_ticks']}    "
        f"Recoveries: {metrics['recovery_count']}"
    )

    # Robot battery
    section("ROBOT BATTERY")

    for robot in world.robots:
        if robot.stuck:
            robot_status = "STUCK"
        elif robot.charging:
            robot_status = "CHARGE"
        elif robot.order_id is not None:
            robot_status = "WORK"
        else:
            robot_status = "IDLE"

        label = (
            f"R{robot.id} {robot_status} "
            f"{robot.battery:.0f}%"
        )

        screen.blit(
            small.render(
                label,
                True,
                TEXT_COLOR,
            ),
            (ox, y),
        )

        draw_battery_bar(
            screen,
            ox + 180,
            y + 4,
            170,
            robot.battery,
        )

        y += 23

    # Agent communication
    section("AGENT COMMUNICATION")

    draw_text(
        f"Messages Sent: {metrics['messages_sent']}"
    )

    # Controls
    section("CONTROLS")

    draw_text(
        "[O] Order    [B] Block",
        gap=18,
    )

    draw_text(
        "[R] Remove   [SPACE] Pause",
        gap=18,
    )

    draw_text(
        "[ESC] Exit",
        gap=18,
    )


# --------------------------------------------------
# OBSTACLE CONTROLS
# --------------------------------------------------

def add_random_obstacle(world):
    occupied = {
        robot.pos
        for robot in world.robots
    }

    protected_pickups = {
        order.pickup
        for order in world.orders
        if not order.completed
    }

    candidates = [
        (x, y)
        for x in range(WIDTH)
        for y in range(HEIGHT)
        if (x, y) not in SHELVES
        and (x, y) not in occupied
        and (x, y) not in protected_pickups
        and (x, y) not in world.dynamic_obstacles
        and (x, y) not in (DEPOT, CHARGER)
    ]

    random.shuffle(candidates)

    for pos in candidates:
        if world.add_obstacle(pos):
            return


def remove_random_obstacle(world):
    if not world.dynamic_obstacles:
        return

    pos = random.choice(
        tuple(world.dynamic_obstacles)
    )

    world.remove_obstacle(pos)


def add_random_order(world):
    occupied = {
        robot.pos
        for robot in world.robots
    }

    existing_pickups = {
        order.pickup
        for order in world.orders
        if not order.completed
    }

    candidates = [
        (x, y)
        for x in range(WIDTH)
        for y in range(HEIGHT)
        if (x, y) not in SHELVES
        and (x, y) not in world.dynamic_obstacles
        and (x, y) not in occupied
        and (x, y) not in existing_pickups
        and (x, y) not in (DEPOT, CHARGER)
    ]

    if candidates:
        world.add_order(
            random.choice(candidates)
        )


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    pygame.display.set_caption(
        "WareMind AI | Multi-Agent Warehouse"
    )

    font = pygame.font.SysFont(
        "consolas",
        18,
    )

    small = pygame.font.SysFont(
        "consolas",
        15,
    )

    clock = pygame.time.Clock()

    model = WarehouseMesaModel()
    world = model.warehouse

    # Initial demo orders
    for pickup in [
        (7, 2),
        (13, 8),
        (2, 9),
    ]:
        world.add_order(pickup)

    running = True
    paused = False
    frames = 0

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    paused = not paused

                elif event.key == pygame.K_o:
                    add_random_order(world)

                elif event.key == pygame.K_b:
                    add_random_obstacle(world)

                elif event.key == pygame.K_r:
                    remove_random_obstacle(world)

        if not running:
            break

        frames += 1

        if (
            not paused
            and frames % SIMULATION_INTERVAL == 0
        ):
            model.step()

        screen.fill(BACKGROUND)

        draw_warehouse(
            screen,
            world,
            font,
        )

        draw_dashboard(
            screen,
            model,
            small,
            paused,
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
