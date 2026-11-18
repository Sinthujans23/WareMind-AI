
from waremind.navigation import astar
from waremind.core import SHELVES, pathfind


def test_astar_finds_path():
    path = astar((2, 2), (13, 8))

    assert path
    assert path[0] == (2, 2)
    assert path[-1] == (13, 8)


def test_astar_avoids_shelves():
    path = astar((2, 2), (13, 8))

    assert all(pos not in SHELVES for pos in path)


def test_astar_shortest_path_matches_bfs():
    start = (2, 2)
    goal = (13, 8)

    assert len(astar(start, goal)) == len(pathfind(start, goal))


def test_astar_avoids_dynamic_obstacle():
    blocked = {(3, 2), (3, 3)}

    path = astar((2, 2), (7, 2), blocked)

    assert path
    assert all(pos not in blocked for pos in path)


def test_astar_unreachable_goal():
    blocked = {(1, 0), (0, 1)}

    assert astar((0, 0), (2, 2), blocked) == []


def test_astar_start_equals_goal():
    assert astar((2, 2), (2, 2)) == [(2, 2)]
