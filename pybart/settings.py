import os


DEFAULT_API_KEY = 'MW9S-E7SL-26DU-VV8V'

REFRESH_INTERVAL = 100  # Milliseconds
TOTAL_COLUMNS = 4

BART_API_KEY = os.environ.get('BART_API_KEY')

try:
    BART_STATIONS = os.environ['BART_STATIONS'].split(',')
except KeyError:
    BART_STATIONS = []
