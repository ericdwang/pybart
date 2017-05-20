import argparse
import sys

import pybart
from pybart import settings
from pybart.api import BART
from pybart.draw import EstimateDrawer
from pybart.utils import Window


api_key = settings.BART_API_KEY or settings.DEFAULT_API_KEY


def main():
    """Parse arguments and run the appropriate function.

    Serves as the entry point for the program.
    """
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        description='Display real time BART estimates.',
        epilog=(
            'examples:\n'
            '  bart                get estimates for $BART_STATIONS\n'
            '  bart list           list all stations\n'
            '  bart est mcar       get estimates for MacArthur station\n'
            '  bart est embr cols  get estimates for Embarcadero and Coliseum '
            'stations'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-v', '--version', action='version', version=pybart.__version__)

    # Add parsers for sub-commands
    subparsers = parser.add_subparsers(title='commands')

    list_parser = subparsers.add_parser(
        'list', help='show list of stations and their abbreviations')
    list_parser.set_defaults(func=list_stations)

    estimate_parser = subparsers.add_parser(
        'est', help='display estimates for specified stations')
    estimate_parser.add_argument('stations', nargs='*', metavar='STN')
    estimate_parser.set_defaults(func=display_estimates)

    # If arguments were supplied parse them and run the appropriate function,
    # otherwise default to displaying estimates
    if len(sys.argv) > 1:
        args = parser.parse_args()
        args.func(args, parser)
    else:
        # Note: the argv check and this explicit call are only necessary for
        # Python 2 because a default function can't be set. In Python 3 all
        # that's needed is: parser.set_defaults(func=display_estimates)
        display_estimates(None, parser)


def list_stations(args, parser):
    bart = BART(api_key)

    try:
        stations = bart.get_stations()
    except RuntimeError as error:
        print(error)
        exit(1)

    for station in stations:
        print('{abbr} - {name}'.format(abbr=station[0], name=station[1]))


def display_estimates(args, parser):
    # Use the default stations if no arguments were passed in
    try:
        stations = args.stations
    except AttributeError:
        stations = settings.BART_STATIONS

    # Show help text if no stations were specified
    if not stations:
        parser.print_help()
        exit(1)

    # Initialize variables
    bart = BART(api_key)
    window = Window(settings.REFRESH_INTERVAL, settings.TOTAL_COLUMNS)
    drawer = EstimateDrawer(bart, stations, window)
    char = ''

    # Keep running until 'q' is pressed to exit or an error occurs
    while char != 'q':
        try:
            drawer.draw()
        except RuntimeWarning:
            pass
        except RuntimeError as error:
            window.endwin()
            print(error)
            exit(1)

        try:
            char = window.getch()

        # Catch interrupt keys like Control-C so that the program doesn't exit
        # without properly de-initializing curses
        except KeyboardInterrupt:
            break

    window.endwin()
