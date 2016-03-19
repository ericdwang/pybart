import curses


class Window(object):
    """Wrapper for the curses module."""
    COLOR_ORANGE = 0

    spacing = 0
    total_columns = 0
    width = 0
    window = None

    def __init__(self, refresh_interval, total_columns):
        """Initialize the window with various settings."""
        self.total_columns = total_columns
        self.window = curses.initscr()

        # Initialize colors with red, green, yellow, blue, and white
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 5):
            curses.init_pair(i, i, -1)
        curses.init_pair(7, 7, -1)

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

        self._update_dimensions()

    def _get_color(self, color_name):
        """Get the color to use based on the name given."""
        if not color_name:
            return 0

        if color_name == 'ORANGE':
            color = self.COLOR_ORANGE
        else:
            color = getattr(curses, 'COLOR_' + color_name)
        return curses.color_pair(color)

    def _update_dimensions(self):
        """Update the width of the window and spacing needed for columns."""
        _, self.width = self.window.getmaxyx()
        self.spacing = self.width // self.total_columns

    def addstr(self, y, x, string, color_name='', bold=False):
        """Add a string with optional color and boldness."""
        color = self._get_color(color_name)
        if bold:
            color |= curses.A_BOLD

        try:
            self.window.addstr(y, x, string, color)
        except curses.error:
            raise RuntimeError('Terminal too small.')

    def center(self, y, text):
        """Center the text in bold at a specified location."""
        text_length = len(text)
        center = (self.width - text_length) // 2
        text_end = center + text_length

        centered_text = ' ' * center + text + ' ' * (self.width - text_end)
        self.addstr(y, 0, centered_text, bold=True)

    def fill_line(self, y, text, *args, **kwargs):
        """Add the text and fill the rest of the line with whitespace."""
        self.addstr(
            y, 0, text + ' ' * (self.width - len(text)), *args, **kwargs)

    def clear_lines(self, y, lines=1):
        """Clear the specified lines."""
        for i in range(lines):
            self.addstr(y + i, 0, ' ' * self.width)

    def getch(self):
        """Get the character input as an ASCII string.

        Also update the dimensions of the window if the terminal was resized.
        """
        char = self.window.getch()
        if char == curses.KEY_RESIZE:
            self._update_dimensions()

        try:
            return chr(char)
        except ValueError:
            return ''

    def endwin(self):
        """End the window."""
        curses.endwin()
