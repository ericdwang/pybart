try:
    # Python 3 imports
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError:
    # Python 2 imports
    from urllib import urlencode
    from urllib2 import URLError
    from urllib2 import urlopen

import errno
import json
from contextlib import closing
from xml.etree import cElementTree

from pybart import settings


api_key = settings.BART_API_KEY or settings.DEFAULT_API_KEY


class BaseAPI(object):
    """Base wrapper for the individual BART APIs."""
    BART_URL = 'https://api.bart.gov/api/{api}.aspx'

    api = ''
    base_url = ''
    json_format = False
    key = ''

    def __init__(self, key, json_format):
        self.base_url = self.BART_URL.format(api=self.api)
        self.key = key
        self.json_format = json_format

    def _get_response_root(self, url):
        """Get the root of the response from the specified URL.

        Raise a RuntimeError if there's no Internet connection or there was an
        error in the response.
        """
        try:
            # Note: closing isn't necessary in Python 3 because urlopen returns
            # a context manager already
            with closing(urlopen(url)) as response:
                body = response.read()

        except URLError as error:
            # Treat interrupted signal calls as warnings
            if error.reason.errno == errno.EINTR:
                raise RuntimeWarning
            raise RuntimeError('No Internet connection.')

        # Note: the BART API returns XML for errors (even when requesting JSON)
        # so all responses need to be checked for XML
        try:
            root = cElementTree.fromstring(body)
            try:
                raise RuntimeError(root.find('.//error').find('details').text)
            except AttributeError:  # XML with no errors
                return root
        except cElementTree.ParseError:  # JSON
            return json.loads(body)['root']


def api_method(method):
    """Decorator for using method signatures to validate and make API calls."""
    def wrapper(self, *args, **kwargs):
        # Validate arguments
        method(self, *args, **kwargs)

        # Convert positional arguments to keyword arguments
        kwargs.update(zip(method.__code__.co_varnames[1:], args))

        # Use the method name for the command and add other parameters
        kwargs.update({'cmd': method.__name__, 'key': self.key})
        if self.json_format:
            kwargs['json'] = 'y'

        # Make the request and parse the response
        return self._get_response_root(self.base_url + '?' + urlencode(kwargs))

    return wrapper


class AdvisoryAPI(BaseAPI):
    """API for advisories: https://api.bart.gov/docs/bsa/"""
    api = 'bsa'

    @api_method
    def bsa(self, orig=None):
        pass

    @api_method
    def count(self):
        pass

    @api_method
    def elev(self):
        pass


class EstimateAPI(BaseAPI):
    """API for real time estimates: https://api.bart.gov/docs/etd/"""
    api = 'etd'

    @api_method
    def etd(self, orig, plat=None, dir=None):
        pass


class RouteAPI(BaseAPI):
    """API for route information: https://api.bart.gov/docs/route/"""
    api = 'route'

    @api_method
    def routeinfo(self, route, sched=None, date=None):
        pass

    @api_method
    def routes(self, sched=None, date=None):
        pass


class ScheduleAPI(BaseAPI):
    """API for schedule information: https://api.bart.gov/docs/sched/"""
    api = 'sched'

    @api_method
    def arrive(self, orig, dest, time=None, date=None, b=None, a=None, l=None):
        pass

    @api_method
    def depart(self, orig, dest, time=None, date=None, b=None, a=None, l=None):
        pass

    @api_method
    def fare(self, orig, dest):
        pass

    @api_method
    def holiday(self):
        pass

    @api_method
    def routesched(self, route, date=None, time=None, l=None, sched=None):
        pass

    @api_method
    def scheds(self):
        pass

    @api_method
    def special(self, l=None):
        pass

    @api_method
    def stnsched(self, orig, date=None):
        pass


class StationAPI(BaseAPI):
    """API for station information: https://api.bart.gov/docs/stn/"""
    api = 'stn'

    @api_method
    def stnaccess(self, orig, l=None):
        pass

    @api_method
    def stninfo(self, orig):
        pass

    @api_method
    def stns(self):
        pass


class VersionAPI(BaseAPI):
    """API for version information: https://api.bart.gov/docs/version/"""
    api = 'version'

    def __call__(self):
        """Allow calling the class directly since the version API has no
        parameters: https://api.bart.gov/docs/version/version.aspx
        """
        return self._get_response_root(self.base_url)


class BART(object):
    """Wrapper for the BART API."""
    bsa = None
    etd = None
    route = None
    sched = None
    stn = None
    version = None

    def __init__(self, key=api_key, json_format=False):
        """Initialize the individual APIs with the API key."""
        args = (key, json_format)
        self.bsa = AdvisoryAPI(*args)
        self.etd = EstimateAPI(*args)
        self.route = RouteAPI(*args)
        self.sched = ScheduleAPI(*args)
        self.stn = StationAPI(*args)
        self.version = VersionAPI(*args)
