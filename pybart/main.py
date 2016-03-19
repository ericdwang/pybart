import sys
from datetime import datetime
from textwrap import TextWrapper

import pybart
from pybart import settings
from pybart.api import BART
from pybart.utils import Window


# Initialize BART API
bart = BART(settings.BART_API_KEY or settings.DEFAULT_API_KEY)

# Parse command line arguments
arguments = sys.argv[1:]
for argument in arguments:
    if argument.startswith('-'):
        if argument == '-h' or argument == '--help':
            print(settings.USAGE_TEXT)
        elif argument == '-v' or argument == '--version':
            print(pybart.__version__)
        elif argument == '-l' or argument == '--list':
            try:
                stations = bart.get_stations()
            except RuntimeError as error:
                print(error)
                exit(1)

            for station in stations:
                print('{abbr} - {name}'.format(
                    abbr=station[0], name=station[1]))

        # Unrecognized option
        else:
            print(
                'bart: unrecognized option \'{option}\'\n'
                'Try \'bart --help\' for more information.'.format(
                    option=argument))
            exit(1)

        exit()

# Use the default stations unless ones were specified
try:
    arguments = arguments or settings.BART_STATIONS.split(',')
except AttributeError:
    pass

# Show the usage text if no stations were specified
if not arguments:
    print(settings.USAGE_TEXT)
    exit(1)

# Initialize window
window = Window(settings.REFRESH_INTERVAL, settings.TOTAL_COLUMNS)
wrapper = TextWrapper()


def draw(prev_lines):
    """Draw the information on the terminal."""
    def get_minutes_color(minutes):
        """Get the color to use for the minutes estimate."""
        try:
            minutes = int(minutes.split()[0])
            if minutes <= 5:
                return 'RED'
            elif minutes <= 10:
                return 'YELLOW'
        except ValueError:
            return 'RED'

    def get_length_color(length):
        """Get the color to use for the train length."""
        length = int(length)
        if length < 6:
            return 'YELLOW'
        elif length >= 8:
            return 'GREEN'

    y = 0

    # Display the current time
    window.center(y, 'BART departures as of {time}'.format(
        time=datetime.now().strftime('%I:%M:%S %p')))

    # Display advisories (if any)
    advisories = bart.get_advisories()
    for advisory in advisories:
        window.clear_lines(y + 1)
        y += 1

        text = '{type} ({posted}) - {sms_text}'.format(
            posted=advisory.posted, type=advisory.type,
            sms_text=advisory.sms_text)

        wrapper.width = window.width
        for line in wrapper.wrap(text):
            y += 1
            window.fill_line(y, line, color_name='RED', bold=True)

    # Display stations
    for station_abbr in arguments:
        window.clear_lines(y + 1)
        y += 2
        station, departures = bart.get_departures(station_abbr)
        window.fill_line(y, station, bold=True)

        # Display all destinations for a station
        for destination, estimates in departures:
            y += 1
            window.addstr(y, 0, destination + ' ' * (
                window.spacing - len(destination)))
            x = window.spacing

            # Display all estimates for a destination on the same line
            for i, estimate in enumerate(estimates, start=1):
                window.addstr(y, x, '# ', color_name=estimate.color)
                x += 2

                minutes = estimate.minutes + ' '
                color = get_minutes_color(estimate.minutes)
                window.addstr(y, x, minutes, color_name=color, bold=True)
                x += len(minutes)

                length = '({length} car)'.format(length=estimate.length)
                color = get_length_color(estimate.length)
                window.addstr(y, x, length, color_name=color)
                x += len(length)

                # Clear the space between estimates
                space = (i + 1) * window.spacing - x
                if space > 0:
                    window.addstr(y, x, ' ' * space)
                    x += space

            # Clear the rest of the line
            remaining = window.width - x
            if remaining > 0:
                window.addstr(y, x, ' ' * remaining)

    # Display help text at the bottom
    window.clear_lines(y + 1)
    window.fill_line(y + 2, 'Press \'q\' to quit.')

    # Clear the bottom lines that contained text from the previous draw
    y = y + 3
    window.clear_lines(y, lines=prev_lines - y)

    # Return the number of lines drawn, excluding cleared lines at the bottom
    return y


def main():
    """Keep running until 'q' is pressed to exit or an error occurs."""
    char = ''
    prev_lines = 0

    while char != 'q':
        try:
            prev_lines = draw(prev_lines)
        except RuntimeWarning:
            pass
        except RuntimeError as error:
            window.endwin()
            print(error)
            exit(1)

        char = window.getch()

    window.endwin()
