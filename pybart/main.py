import sys
from datetime import datetime

import pybart
from pybart import settings
from pybart.api import BART
from pybart.utils import Window
from pybart.utils import exit_on_error


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
            stations = exit_on_error(bart.get_stations, end_curses=False)
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


def draw():
    """Draw the information on the terminal."""
    y = 0

    # Display the current time
    window.center(y, 'BART departures as of {time}'.format(
        time=datetime.now().strftime('%I:%M:%S %p')))

    # Display advisories (if any)
    advisories = exit_on_error(bart.get_advisories)
    for advisory in advisories:
        window.clear_lines(y + 1)
        y += 2
        window.addstr(y, 0, '{type} ({posted}) - {sms_text}'.format(
            posted=advisory.posted,
            type=advisory.type,
            sms_text=advisory.sms_text,
        ), color_name='RED', bold=True)

    # Display stations
    for station_abbr in arguments:
        window.clear_lines(y + 1)
        y += 2
        station, departures = exit_on_error(
            bart.get_departures, args=(station_abbr,))
        window.addstr(y, 0, station, bold=True)

        # Display all destinations for a station
        for destination, estimates in departures:
            y += 1
            window.addstr(y, 0, destination)
            x = window.SPACING

            # Display all estimates for a destination on the same line
            for i, estimate in enumerate(estimates, start=1):
                window.addstr(y, x, '# ', color_name=estimate.color)
                x += 2

                minutes = estimate.minutes + ' '
                window.addstr(y, x, minutes, bold=True)
                x += len(minutes)

                length = '({length} car)'.format(length=estimate.length)
                window.addstr(y, x, length)
                x += len(length)

                # Clear the space between estimates
                space = (i + 1) * window.SPACING - x
                window.addstr(y, x, ' ' * space)
                x += space

            # Clear the rest of the line
            window.addstr(y, x, ' ' * (window.WIDTH - x))

    # Display help text at the bottom
    window.clear_lines(y + 1)
    window.addstr(y + 2, 0, 'Press \'q\' to quit.')

    # Clear the bottom 2 lines in case rows were moved up
    window.clear_lines(y + 3, lines=2)


def main():
    """Keep running until 'q' is pressed to exit or an error occurs."""
    char = -1

    while char != ord('q'):
        draw()
        char = window.getch()

    window.endwin()
