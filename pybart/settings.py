import os


USAGE_TEXT = (
    'Usage: bart [OPTION]... [STN]...\n'
    'Display real time estimates about the STNs\n'
    '(using the BART_STATIONS environment variable if not specified).\n\n'
    'Options\n'
    '  -l, --list     print list of station abbreviations and exit\n'
    '  -h, --help     display this help and exit\n'
    '  -v, --version  output version information and exit\n\n'
    'Examples\n'
    '  bart mcar       get estimates for the MacArthur station\n'
    '  bart embr cols  get estimates for the Embarcadero and Coliseum stations'
)

DEFAULT_API_KEY = 'MW9S-E7SL-26DU-VV8V'

REFRESH_INTERVAL = 100  # Milliseconds
TOTAL_COLUMNS = 4

BART_API_KEY = os.environ.get('BART_API_KEY')
BART_STATIONS = os.environ.get('BART_STATIONS')
