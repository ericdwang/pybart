import curses


def exit_on_error(
        function, end_curses=True, error_message='', args=(), kwargs={}):
    """Call a function, ending the program and displaying an error if one
    occurs.
    """
    try:
        return function(*args, **kwargs)
    except Exception as error:
        if end_curses:
            curses.endwin()

        if error_message:
            print(error_message)
        else:
            print(str(error))

        exit(1)


class Window(object):
    """Wrapper for the curses module."""
    COLOR_ORANGE = 0
    SPACING = 0
    WIDTH = 0

    window = None

    def __init__(self, refresh_interval, total_columns):
        """Initialize the window with various settings."""
        self.window = curses.initscr()

        # Initialize colors with red, green, yellow, and blue
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 5):
            curses.init_pair(i, i, -1)

        # Use the orange color if the terminal supports it, and magenta
        # otherwise
        if curses.COLORS == 256:
            self.COLOR_ORANGE = 208
        else:
            self.COLOR_ORANGE = curses.COLOR_MAGENTA
        curses.init_pair(self.COLOR_ORANGE, self.COLOR_ORANGE, -1)

        # Disable typing echo and hide the cursor
        curses.noecho()
        curses.curs_set(0)

        # Set the refresh interval
        curses.halfdelay(refresh_interval)

        # Get the width of the window and the spacing needed for columns
        _, self.WIDTH = self.window.getmaxyx()
        self.SPACING = self.WIDTH // total_columns

    def _get_color(self, color_name):
        """Get the color to use based on the name given."""
        if not color_name:
            return 0

        if color_name == 'ORANGE':
            color = self.COLOR_ORANGE
        else:
            color = getattr(curses, 'COLOR_' + color_name)
        return curses.color_pair(color)

    def addstr(self, y, x, string, color_name='', bold=False):
        """Add a string with optional color and boldness."""
        color = self._get_color(color_name)
        if bold:
            color |= curses.A_BOLD

        exit_on_error(
            self.window.addstr, error_message='Terminal too small.',
            args=(y, x, string, color))

    def center(self, y, text):
        """Center the text in bold at a specified location."""
        self.addstr(y, (self.WIDTH - len(text)) // 2, text, bold=True)

    def clear_lines(self, y, lines=1):
        """Clear the specified lines."""
        for i in range(lines):
            self.window.addstr(y + i, 0, ' ' * self.WIDTH)

    def getch(self):
        """Get the character input."""
        return self.window.getch()

    def endwin(self):
        """End the window."""
        curses.endwin()
