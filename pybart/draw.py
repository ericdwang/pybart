from datetime import datetime
from textwrap import TextWrapper


class EstimateDrawer(object):
    """Class for drawing BART estimates on the terminal."""
    bart = None
    stations = None
    window = None
    wrapper = None

    prev_lines = 0

    def __init__(self, bart, stations, window):
        self.bart = bart
        self.stations = stations
        self.window = window
        self.wrapper = TextWrapper()

    def _get_minutes_color(self, minutes):
        """Get the color to use for the minutes estimate."""
        try:
            minutes = int(minutes.split()[0])
            if minutes <= 5:
                return 'RED'
            elif minutes <= 10:
                return 'YELLOW'
        except ValueError:
            return 'RED'

    def _get_length_color(self, length):
        """Get the color to use for the train length."""
        length = int(length)
        if length < 6:
            return 'YELLOW'
        elif length >= 8:
            return 'GREEN'

    def draw(self):
        """Draw the information on the terminal."""
        y = 0

        # Display the current time
        self.window.center(y, 'BART departures as of {time}'.format(
            time=datetime.now().strftime('%I:%M:%S %p')))

        # Display advisories (if any)
        advisories = self.bart.get_advisories()
        for advisory in advisories:
            self.window.clear_lines(y + 1)
            y += 1

            text = '{type} ({posted}) - {sms_text}'.format(
                posted=advisory.posted, type=advisory.type,
                sms_text=advisory.sms_text)

            self.wrapper.width = self.window.width
            for line in self.wrapper.wrap(text):
                y += 1
                self.window.fill_line(y, line, color_name='RED', bold=True)

        # Display stations
        for station_abbr in self.stations:
            self.window.clear_lines(y + 1)
            y += 2
            station, departures = self.bart.get_departures(station_abbr)
            self.window.fill_line(y, station, bold=True)

            # Display all destinations for a station
            for destination, estimates in departures:
                y += 1
                self.window.addstr(y, 0, destination + ' ' * (
                    self.window.spacing - len(destination)))
                x = self.window.spacing

                # Display all estimates for a destination on the same line
                for i, estimate in enumerate(estimates, start=1):
                    self.window.addstr(y, x, '# ', color_name=estimate.color)
                    x += 2

                    minutes = estimate.minutes + ' '
                    color = self._get_minutes_color(estimate.minutes)
                    self.window.addstr(
                        y, x, minutes, color_name=color, bold=True)
                    x += len(minutes)

                    length = '({length} car)'.format(length=estimate.length)
                    color = self._get_length_color(estimate.length)
                    self.window.addstr(y, x, length, color_name=color)
                    x += len(length)

                    # Clear the space between estimates
                    space = (i + 1) * self.window.spacing - x
                    if space > 0:
                        self.window.addstr(y, x, ' ' * space)
                        x += space

                # Clear the rest of the line
                remaining = self.window.width - x
                if remaining > 0:
                    self.window.addstr(y, x, ' ' * remaining)

        # Display help text at the bottom
        self.window.clear_lines(y + 1)
        self.window.fill_line(y + 2, 'Press \'q\' to quit.')

        # Clear the bottom lines that contained text from the previous draw
        y = y + 3
        self.window.clear_lines(y, lines=self.prev_lines - y)

        # Save the number of lines drawn, excluding cleared lines at the bottom
        self.prev_lines = y
