import curses
import random
import time
import threading
from collections import deque
import shutil


class SnakeGame:
    """
    A terminal-based Snake game implemented using the curses library.

    Attributes:
        width (int): Width of the game area.
        height (int): Height of the game area.
        snake (deque): Deque representing the snake's body coordinates.
        direction (str): Current moving direction of the snake.
        next_direction (str): Next direction input from the user.
        food (tuple or None): Coordinates of the current food item.
        score (int): Player's current score.
        game_over (bool): Flag indicating if the game has ended.
        running (bool): Flag indicating if the game loop is running.
        delay (int): Delay between snake moves in milliseconds.
        stdscr (curses.window): The main curses screen.
        game_win (curses.window): Window displaying the game area.
        test_mode (bool): Whether running in test mode (no curses initialization).
    """

    def __init__(self, test_mode=False):
        """
        Initialize the Snake game with default settings.

        Args:
            test_mode (bool): If True, skip curses initialization for testing.

        Sets up game dimensions, initial snake state, score, and
        initializes the curses display (unless in test mode). Also validates terminal size.
        """
        # Game dimensions
        self.width = 40
        self.height = 20

        # Game state
        self.snake = deque()
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.food = None
        self.score = 0
        self.game_over = False
        self.running = True
        self.test_mode = test_mode

        # Game speed (delay between moves in milliseconds)
        self.delay = 150

        # Initialize curses and UI elements only if not in test mode
        self.stdscr = None
        self.game_win = None

        if not test_mode:
            self.window_terminal_validity()
            self.init_curses()

    def window_terminal_validity(self):
        """
        Check if the current terminal size is sufficient for the game.

        Validates that the terminal dimensions are large enough to display
        the game area plus borders and UI elements. The minimum required
        size accounts for the game area plus 4 additional characters for
        borders and spacing.

        Raises:
            Exception: If the terminal is smaller than required dimensions
                      (height+4 x width+4). Includes current and required
                      dimensions in the error message.
        """
        size = shutil.get_terminal_size(fallback=(80, 24))
        terminal_width = size.columns
        terminal_height = size.lines

        if terminal_height < self.height + 4 or terminal_width < self.width + 4:
            raise Exception(
                f"Terminal too small! Minimum required: "
                f"{self.height+4}x{self.width+4}, "
                f"Current: {terminal_height}x{terminal_width}\n"
                "Please expand terminal size"
            )

    def init_curses(self):
        """
        Initialize the curses display and configure game window.

        Sets up:
            - Main screen with proper input/output settings
            - Input and display options (no echo, non-blocking input)
            - Color pairs for snake, food, border, and text elements
            - Game window with borders and keypad support
            - Non-blocking input for real-time gameplay

        Color pairs defined:
            1: Green snake on default background
            2: Red food on default background
            3: Green border on default background
            4: White text on default background
            5: Yellow game over text on default background
        """
        if self.test_mode:
            return

        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        # Enable colors
        curses.start_color()
        curses.use_default_colors()

        # Define color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)  # Snake (green)
        curses.init_pair(2, curses.COLOR_RED, -1)  # Food (red)
        curses.init_pair(3, curses.COLOR_GREEN, -1)  # Border (dark green)
        curses.init_pair(4, curses.COLOR_WHITE, -1)  # Score text (white)
        curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Game over text (yellow)

        # Create game window with border
        self.game_win = curses.newwin(self.height + 2, self.width + 2, 2, 2)
        self.game_win.keypad(True)
        self.game_win.nodelay(True)

        # Get screen dimensions for score placement
        screen_height, screen_width = self.stdscr.getmaxyx()

    def draw_border(self):
        """
        Draw the dark green border around the game area.

        Creates a visual boundary for the playing field using curses
        border characters. The border is drawn in green with bold
        formatting to make it clearly visible and distinguish the
        game area from the surrounding terminal space.
        """
        if self.test_mode or not self.game_win:
            return

        self.game_win.attron(curses.color_pair(3) | curses.A_BOLD)
        self.game_win.border()
        self.game_win.attroff(curses.color_pair(3) | curses.A_BOLD)

    def init_snake(self):
        """
        Initialize the snake at the center of the screen.

        Creates a new snake with 3 segments positioned horizontally
        in the center of the game area. The snake starts facing right
        with the head at the center and two body segments trailing
        to the left. This provides a consistent starting state for
        each new game.
        """
        center_x = self.width // 2
        center_y = self.height // 2

        # Snake starts with 3 segments
        self.snake = deque([(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)])

    def spawn_food(self):
        """
        Spawn food at a random empty location within the game area.

        Continuously generates random coordinates within the playable
        area (excluding border positions) until finding a location
        that doesn't overlap with any part of the snake's body.
        This ensures food is always accessible and visible to the player.

        The food coordinates are stored in self.food as a tuple (x, y).
        """
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def draw_snake(self):
        """
        Draw the green snake on the game area.

        Renders each segment of the snake using the block character "█"
        in green color with bold formatting. Iterates through all
        segments in the snake deque and draws them at their respective
        coordinates within the game window.
        """
        if self.test_mode or not self.game_win:
            return

        for segment in self.snake:
            x, y = segment
            self.game_win.addch(y, x, "█", curses.color_pair(1) | curses.A_BOLD)

    def draw_food(self):
        """
        Draw the red food item on the game area.

        Renders the food as a circular bullet character "●" in red
        color with bold formatting. Only draws the food if it exists
        (self.food is not None), positioning it at the stored
        coordinates within the game window.
        """
        if self.test_mode or not self.game_win:
            return

        if self.food:
            x, y = self.food
            self.game_win.addch(y, x, "●", curses.color_pair(2) | curses.A_BOLD)

    def draw_score(self):
        """
        Draw the current score at the bottom right outside the game border.

        Displays the score in the format "Score: X" positioned below
        and to the right of the game area. The text is right-aligned
        and rendered in white with bold formatting for visibility.

        Position calculation accounts for:
        - Game window position and dimensions
        - Text length for proper alignment
        - Border spacing for clean layout
        """
        if self.test_mode or not self.stdscr:
            return

        score_text = f"Score: {self.score}"
        # Position: bottom right corner outside the game border
        score_y = 2 + self.height + 2  # Below the game window
        score_x = 2 + self.width + 2 - len(score_text)  # Right aligned

        self.stdscr.addstr(score_y, score_x, score_text, curses.color_pair(4) | curses.A_BOLD)

    def draw_instructions(self):
        """
        Draw game control instructions to the right of the game area.

        Displays a list of available controls and commands:
        - Movement controls (WASD or Arrow Keys)
        - Quit command ('q')
        - Restart command ('r')

        Instructions are positioned to the right of the game border
        in white text, providing players with easily accessible
        reference for game controls.
        """
        if self.test_mode or not self.stdscr:
            return

        instructions = ["Use WASD or Arrow Keys to move", "Press 'q' to quit", "Press 'r' to restart"]

        start_y = 2
        for i, instruction in enumerate(instructions):
            self.stdscr.addstr(start_y + i, 2 + self.width + 5, instruction, curses.color_pair(4))

    def move_snake(self):
        """
        Move the snake in the current direction and handle game logic.

        Performs the core game movement logic:
        1. Calculates new head position based on current direction
        2. Checks for collisions with walls or snake body
        3. Adds new head to snake
        4. Handles food consumption (grows snake, increases score, spawns new food)
        5. Removes tail segment if no food was eaten
        6. Increases game speed slightly when food is consumed

        Sets game_over flag to True if collision is detected.
        Updates score and respawns food when food is consumed.
        Implements speed increase mechanism for progressive difficulty.
        """
        head_x, head_y = self.snake[0]

        # Calculate new head position
        if self.direction == "UP":
            new_head = (head_x, head_y - 1)
        elif self.direction == "DOWN":
            new_head = (head_x, head_y + 1)
        elif self.direction == "LEFT":
            new_head = (head_x - 1, head_y)
        elif self.direction == "RIGHT":
            new_head = (head_x + 1, head_y)

        # Check for collisions
        if self.check_collision(new_head):
            self.game_over = True
            return

        # Add new head
        self.snake.appendleft(new_head)

        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
            # Increase speed slightly
            if self.delay > 50:
                self.delay = max(50, self.delay - 2)
        else:
            # Remove tail if no food eaten
            self.snake.pop()

    def check_collision(self, position):
        """
        Check if a given position results in a collision.

        Args:
            position (tuple): The (x, y) coordinates to check for collision.

        Returns:
            bool: True if collision detected, False otherwise.

        Collision detection includes:
        - Wall collision: position is at or beyond game area boundaries
        - Self collision: position overlaps with any part of snake body

        The method checks boundaries against the playable area (excluding
        the border positions) and iterates through the snake deque to
        detect self-intersection.
        """
        x, y = position

        # Check wall collision
        if x <= 0 or x >= self.width - 1 or y <= 0 or y >= self.height - 1:
            return True

        # Check self collision
        if position in self.snake:
            return True

        return False

    def handle_input(self):
        """
        Handle keyboard input in a separate thread for real-time control.

        Runs continuously while the game is active, processing keyboard
        input without blocking the main game loop. Supports both WASD
        and arrow key controls with collision prevention (can't reverse
        directly into snake body).

        Supported controls:
        - W/Up Arrow: Move up (if not currently moving down)
        - S/Down Arrow: Move down (if not currently moving up)
        - A/Left Arrow: Move left (if not currently moving right)
        - D/Right Arrow: Move right (if not currently moving left)
        - Q: Quit game
        - R: Restart game (only when game over)

        Input is case-insensitive. Includes small delay to prevent
        excessive CPU usage while maintaining responsiveness.
        """
        if self.test_mode or not self.game_win:
            return

        while self.running:
            key = self.game_win.getch()

            if key != -1:  # Key was pressed
                # Convert to uppercase for consistency
                if key in [ord("w"), ord("W"), curses.KEY_UP]:
                    if self.direction != "DOWN":
                        self.next_direction = "UP"
                elif key in [ord("s"), ord("S"), curses.KEY_DOWN]:
                    if self.direction != "UP":
                        self.next_direction = "DOWN"
                elif key in [ord("a"), ord("A"), curses.KEY_LEFT]:
                    if self.direction != "RIGHT":
                        self.next_direction = "LEFT"
                elif key in [ord("d"), ord("D"), curses.KEY_RIGHT]:
                    if self.direction != "LEFT":
                        self.next_direction = "RIGHT"
                elif key in [ord("q"), ord("Q")]:
                    self.running = False
                    self.game_over = True
                elif key in [ord("r"), ord("R")] and self.game_over:
                    self.restart_game()

            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    def restart_game(self):
        """
        Reset the game to its initial state for a fresh start.

        Clears all game state and reinitializes core components:
        - Clears snake body
        - Resets score to 0
        - Sets direction back to RIGHT
        - Clears game over flag
        - Resets game speed to initial value
        - Reinitializes snake position
        - Spawns new food

        This method is called when the player presses 'R' during
        the game over screen, allowing for immediate replay without
        restarting the entire program.
        """
        self.snake.clear()
        self.score = 0
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.game_over = False
        self.delay = 150
        self.init_snake()
        self.spawn_food()

    def draw_game_over(self):
        """
        Draw the game over screen with final score and restart options.

        Displays centered text on the game area including:
        - "GAME OVER!" message in yellow with bold formatting
        - Final score display in white
        - Restart/quit instructions in white

        All text is centered both horizontally and vertically within
        the game window to create a clear, prominent game over screen
        that provides the player with their final score and next steps.
        """
        if self.test_mode or not self.game_win:
            return

        # Calculate center position
        center_y = self.height // 2
        center_x = self.width // 2

        game_over_text = "GAME OVER!"
        restart_text = "Press 'r' to restart or 'q' to quit"
        final_score_text = f"Final Score: {self.score}"

        # Draw game over messages
        self.game_win.addstr(
            center_y - 1, center_x - len(game_over_text) // 2, game_over_text, curses.color_pair(5) | curses.A_BOLD
        )
        self.game_win.addstr(center_y, center_x - len(final_score_text) // 2, final_score_text, curses.color_pair(4))
        self.game_win.addstr(center_y + 1, center_x - len(restart_text) // 2, restart_text, curses.color_pair(4))

    def draw_welcome(self):
        """
        Draw the welcome screen and wait for player input to start.

        Displays the initial game screen with:
        - "SNAKE GAME" title in green with bold formatting
        - "Press any key to start!" instruction in white
        - Game border for visual context

        The method temporarily disables non-blocking input to wait
        for a key press before starting the game, then re-enables
        non-blocking mode for gameplay. All text is centered within
        the game window for an attractive welcome presentation.
        """
        if self.test_mode or not self.game_win:
            return

        welcome_text = "SNAKE GAME"
        start_text = "Press any key to start!"

        center_y = self.height // 2
        center_x = self.width // 2

        self.draw_border()
        self.game_win.addstr(
            center_y - 1, center_x - len(welcome_text) // 2, welcome_text, curses.color_pair(1) | curses.A_BOLD
        )
        self.game_win.addstr(center_y + 1, center_x - len(start_text) // 2, start_text, curses.color_pair(4))
        self.game_win.refresh()

        # Wait for key press
        self.game_win.nodelay(False)
        self.game_win.getch()
        self.game_win.nodelay(True)

    def update_display(self):
        """
        Update the entire game display with current game state.

        Performs a complete refresh of all visual elements:
        1. Clears the game area (preserving border)
        2. Draws game border
        3. Draws snake at current position
        4. Draws food at current position
        5. Shows game over screen if applicable
        6. Updates score display
        7. Updates instruction display
        8. Refreshes both main screen and game window

        This method is called every game loop iteration to ensure
        the display accurately reflects the current game state.
        The clearing and redrawing approach prevents visual artifacts
        and ensures clean animation.
        """
        if self.test_mode or not self.game_win:
            return

        # Clear the game area (not the border)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.game_win.addch(y, x, " ")

        # Draw game elements
        self.draw_border()
        self.draw_snake()
        self.draw_food()

        if self.game_over:
            self.draw_game_over()

        # Update score and instructions
        self.stdscr.clear()
        self.draw_score()
        self.draw_instructions()

        # Refresh windows
        self.stdscr.refresh()
        self.game_win.refresh()

    def run(self):
        """
        Main game execution method that runs the complete game loop.

        Orchestrates the entire game flow:

        1. Shows welcome screen and waits for start
        2. Initializes snake and food
        3. Starts input handling thread for real-time controls
        4. Runs main game loop until quit/exit:
            - Updates snake direction from input
            - Moves snake (if game not over)
            - Updates display
            - Controls game speed with delay
        5. Handles cleanup on exit

        Exception Handling:
            - Catches KeyboardInterrupt (Ctrl+C) for graceful exit.
            - Ensures proper curses cleanup in finally block.

        The method uses threading for input handling to maintain
        responsive controls while managing game timing and display
        updates in the main thread.
        """

        try:
            # Show welcome screen
            self.draw_welcome()

            # Initialize game
            self.init_snake()
            self.spawn_food()

            # Start input handling thread
            input_thread = threading.Thread(target=self.handle_input, daemon=True)
            input_thread.start()

            # Main game loop
            while self.running:
                if not self.game_over:
                    # Update direction
                    self.direction = self.next_direction

                    # Move snake
                    self.move_snake()

                # Update display
                self.update_display()

                # Game speed control
                time.sleep(self.delay / 1000.0)

        except KeyboardInterrupt:
            self.running = False
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Clean up curses environment and restore terminal state.

        Properly shuts down the curses interface by:
        - Disabling cbreak mode (restoring line buffering)
        - Re-enabling echo for normal terminal input
        - Restoring cursor visibility
        - Ending the curses session

        This method is essential for leaving the terminal in a
        usable state after the game exits. Called automatically
        in the finally block of the run() method to ensure
        cleanup occurs even if the game exits unexpectedly.
        """
        if self.test_mode or not self.stdscr:
            return

        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
