"""Run: python main.py. Press O to create an order, SPACE to pause, ESC to quit."""
import random
import pygame
from waremind.core import Warehouse, WIDTH, HEIGHT, SHELVES, DEPOT, CHARGER

CELL = 46
SIDE = 330
COLORS = [(50, 115, 235), (35, 170, 105), (235, 155, 50)]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH * CELL + SIDE, HEIGHT * CELL))
    pygame.display.set_caption('WareMind AI | Multi-Agent Warehouse')
    font = pygame.font.SysFont('consolas', 18)
    small = pygame.font.SysFont('consolas', 15)
    clock = pygame.time.Clock()
    world = Warehouse()
    for p in [(7, 2), (13, 8), (2, 9)]:
        world.add_order(p)
    running = True; paused = False; frames = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused
            if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                free = [(x, y) for x in range(WIDTH) for y in range(HEIGHT) if (x, y) not in SHELVES and (x, y) != DEPOT]
                world.add_order(random.choice(free))
        frames += 1
        if not paused and frames % 12 == 0:
            world.step()
        screen.fill((19, 27, 41))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                rect = pygame.Rect(x * CELL, y * CELL, CELL - 1, CELL - 1)
                color = (45, 59, 77) if (x, y) not in SHELVES else (151, 116, 71)
                pygame.draw.rect(screen, color, rect, border_radius=3)
        for pos, color, name in [(DEPOT, (137, 95, 220), 'D'), (CHARGER, (40, 190, 205), 'C')]:
            pygame.draw.rect(screen, color, (pos[0] * CELL + 5, pos[1] * CELL + 5, CELL - 10, CELL - 10), border_radius=6)
            screen.blit(font.render(name, True, (255, 255, 255)), (pos[0] * CELL + 16, pos[1] * CELL + 12))
        for order in world.orders:
            if not order.completed:
                x, y = order.pickup
                pygame.draw.circle(screen, (255, 225, 100), (x * CELL + CELL // 2, y * CELL + CELL // 2), 9)
        for robot in world.robots:
            x, y = robot.pos
            pygame.draw.circle(screen, COLORS[robot.id - 1], (x * CELL + CELL // 2, y * CELL + CELL // 2), 17)
            screen.blit(small.render(str(robot.id), True, 'white'), (x * CELL + 18, y * CELL + 14))
        ox = WIDTH * CELL + 16
        lines = ['WAREMIND AI', '', f'Tick: {world.tick}', f'Orders delivered: {world.completed_count}/{len(world.orders)}', '', 'ROBOTS']
        for robot in world.robots:
            lines += [f'R{robot.id} | battery {robot.battery:.0f}%', f'   task: {robot.order_id or "idle"}']
        lines += ['', 'EVENTS'] + [line[:37] for line in world.events[-6:]] + ['', '[O] Add order', '[SPACE] Pause/resume', '[ESC] Exit']
        for i, line in enumerate(lines):
            screen.blit(small.render(line, True, (224, 234, 244)), (ox, 12 + i * 21))
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()


if __name__ == '__main__':
    main()
