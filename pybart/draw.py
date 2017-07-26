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

    def _format_minutes(self, minutes):
        """Return the minutes estimate formatted with its color."""
        color = None

        try:
            minutes = int(minutes)
            if minutes <= 5:
                color = 'RED'
            elif minutes <= 10:
                color = 'YELLOW'
            minutes = str(minutes) + ' min'
        except ValueError:
            color = 'RED'

        return (minutes + ' ', color)

    def _format_length(self, length):
        """Return the train length formatted with its color."""
        color = None
        length = int(length)

        if length < 6:
            color = 'YELLOW'
        elif length >= 8:
            color = 'GREEN'

        return ('({length} car)'.format(length=length), color)

    def draw(self):
        """Draw the information on the terminal."""
        y = 0

        # Display the current time
        self.window.center(y, 'BART departures as of {time}'.format(
            time=datetime.now().strftime('%I:%M:%S %p')))

        # Display advisories (if any)
        for advisory in self.bart.bsa.bsa().iterfind('bsa'):
            # Ignore advisories that state there aren't any delays
            try:
                text = '{type} ({posted}) - {sms_text}'.format(
                    posted=advisory.find('posted').text,
                    type=advisory.find('type').text,
                    sms_text=advisory.find('sms_text').text,
                )
            except AttributeError:
                break

            self.window.clear_lines(y + 1)
            y += 1

            self.wrapper.width = self.window.width
            for line in self.wrapper.wrap(text):
                y += 1
                self.window.fill_line(y, line, color_name='RED', bold=True)

        # Display stations
        for station_abbr in self.stations:
            self.window.clear_lines(y + 1)
            y += 2
            station = self.bart.etd.etd(station_abbr).find('station')
            self.window.fill_line(y, station.find('name').text, bold=True)

            # Display all destinations for a station
            for departure in station.iterfind('etd'):
                y += 1
                destination = departure.find('destination').text
                self.window.addstr(y, 0, destination + ' ' * (
                    self.window.spacing - len(destination)))
                x = self.window.spacing

                # Display all estimates for a destination on the same line
                for i, estimate in enumerate(
                        departure.iterfind('estimate'), start=1):
                    self.window.addstr(
                        y, x, '# ', color_name=estimate.find('color').text)
                    x += 2

                    minutes, color = self._format_minutes(
                        estimate.find('minutes').text)
                    self.window.addstr(
                        y, x, minutes, color_name=color, bold=True)
                    x += len(minutes)

                    length, color = self._format_length(
                        estimate.find('length').text)
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
