import argparse
import sys
import webbrowser

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
            '  bart                 get estimates for $BART_STATIONS\n'
            '  bart map             open station map\n'
            '  bart list            list all stations\n'
            '  bart est mcar        get estimates for MacArthur station\n'
            '  bart est embr cols   get estimates for Embarcadero and '
            'Coliseum stations\n'
            '  bart fare conc sfia  get fare for a trip between Concord and '
            'SFO stations'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-v', '--version', action='version', version=pybart.__version__)

    # Add parsers for sub-commands
    subparsers = parser.add_subparsers(title='commands')

    map_parser = subparsers.add_parser(
        'map', help='open station map in web browser')
    map_parser.set_defaults(func=open_map)

    list_parser = subparsers.add_parser(
        'list', help='show list of stations and their abbreviations')
    list_parser.set_defaults(func=list_stations)

    estimate_parser = subparsers.add_parser(
        'est', help='display estimates for specified stations')
    estimate_parser.add_argument('stations', nargs='*', metavar='STN')
    estimate_parser.set_defaults(func=display_estimates)

    fare_parser = subparsers.add_parser(
        'fare', help='show fare for a trip between two stations')
    fare_parser.add_argument('stations', nargs=2, metavar='STN')
    fare_parser.set_defaults(func=show_fare)

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


def catch_errors_and_exit(function):
    """Run the function and return its output, catching errors and exiting if
    one occurs.
    """
    try:
        return function()
    except RuntimeError as error:
        print(error)
        exit(1)


def open_map(args, parser):
    webbrowser.open_new_tab(settings.BART_MAP_URL)


def show_fare(args, parser):
    fare = catch_errors_and_exit(
        lambda: BART(api_key).get_fare(*args.stations))
    print('$' + fare)


def list_stations(args, parser):
    stations = catch_errors_and_exit(lambda: BART(api_key).get_stations())
    for abbrevation, name in stations:
        print('{abbr} - {name}'.format(abbr=abbrevation, name=name))


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
