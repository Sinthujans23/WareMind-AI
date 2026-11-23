
from waremind.safety_rules import evaluate_robot_safety


def test_low_battery_idle_robot_should_charge():
    actions = evaluate_robot_safety(
        idle=True,
        battery=20,
        charging=False,
    )
    assert "START_CHARGING" in actions


def test_busy_robot_rejects_new_task():
    actions = evaluate_robot_safety(
        idle=False,
        battery=100,
        charging=False,
    )
    assert "REJECT_NEW_TASK" in actions


def test_charging_robot_rejects_new_task():
    actions = evaluate_robot_safety(
        idle=True,
        battery=50,
        charging=True,
    )
    assert "REJECT_NEW_TASK" in actions


def test_insufficient_battery_rejects_task():
    actions = evaluate_robot_safety(
        idle=True,
        battery=30,
        charging=False,
        required_battery=40,
    )
    assert "REJECT_NEW_TASK" in actions


def test_healthy_robot_has_no_safety_restrictions():
    actions = evaluate_robot_safety(
        idle=True,
        battery=100,
        charging=False,
        required_battery=30,
    )
    assert actions == set()
