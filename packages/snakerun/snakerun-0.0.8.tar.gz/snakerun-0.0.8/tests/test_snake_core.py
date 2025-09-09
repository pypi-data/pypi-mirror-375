import pytest
from collections import deque

from snakerun import SnakeGame


class TestSnakeGame:
    def setup_method(self):
        # use test_mode to skip curses init
        self.game = SnakeGame(test_mode=True)

    def teardown_method(self, method):
        del self.game

    def test_init_snake(self):
        self.game.init_snake()
        assert len(self.game.snake) == 3
        head_x, head_y = self.game.snake[0]
        assert (head_x, head_y) == (self.game.width // 2, self.game.height // 2)

    def test_spawn_food_not_on_snake(self):
        self.game.init_snake()
        self.game.spawn_food()
        assert self.game.food is not None
        assert self.game.food not in self.game.snake

    def test_move_snake_forward(self):
        self.game.init_snake()
        head_before = self.game.snake[0]
        self.game.move_snake()
        head_after = self.game.snake[0]
        assert head_after[0] == head_before[0] + 1
        assert head_after[1] == head_before[1]

    def test_snake_eats_food_and_grows(self):
        self.game.init_snake()
        head_x, head_y = self.game.snake[0]
        self.game.food = (head_x + 1, head_y)
        initial_length = len(self.game.snake)

        self.game.move_snake()

        assert len(self.game.snake) == initial_length + 1
        assert self.game.score == 1
        assert self.game.food is not None

    def test_snake_collision_with_wall(self):
        self.game.snake = deque([(self.game.width - 2, 5)])
        self.game.direction = "RIGHT"
        self.game.move_snake()
        assert self.game.game_over is True

    def test_snake_collision_with_itself(self):
        self.game.snake = deque([(5, 5), (4, 5), (3, 5), (3, 6), (4, 6), (5, 6)])
        self.game.direction = "UP"
        self.game.snake.appendleft((5, 6))
        assert self.game.check_collision((5, 6)) is True

    def test_restart_game_resets_state(self):
        self.game.init_snake()
        self.game.score = 10
        self.game.game_over = True
        self.game.restart_game()
        assert self.game.score == 0
        assert self.game.game_over is False
        assert len(self.game.snake) == 3
        assert self.game.food is not None


class TestSmallTerminalSnakegame:
    """
    Cross-platform test for small terminal rejection.
    On Linux/macOS -> use pexpect (real pseudo-terminal).
    On Windows -> fall back to capsys.
    """

    @pytest.mark.skip(reason="Skipping terminal size test for now")
    def test_window_terminal_validity_capsys(self, capsys):
        """Windows fallback: capture stdout/stderr directly."""
        with pytest.raises(Exception):
            SnakeGame()
        captured = capsys.readouterr()
        assert "Terminal too small" in captured.out
        assert "Minimum required: 24x44" in captured.out
