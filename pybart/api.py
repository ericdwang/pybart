try:
    from urllib2 import URLError
    from urllib2 import urlopen
except ImportError:
    from urllib.error import URLError
    from urllib.request import urlopen

import errno
from collections import namedtuple
from xml.etree import cElementTree


Advisory = namedtuple('Advisory', ('posted', 'sms_text', 'type'))
Estimate = namedtuple('Estimate', ('color', 'length', 'minutes'))


class BART(object):
    """Wrapper for the BART API."""
    BART_URL = 'http://api.bart.gov/api/{api}.aspx?cmd={cmd}&key={key}'

    ADVISORY_URL = ''
    DEPATURE_URL = ''
    STATION_URL = ''

    def __init__(self, key):
        """Set the URLs to use based on the API key given."""
        self.ADVISORY_URL = self.BART_URL.format(
            api='bsa', cmd='bsa', key=key) + '&date=today'
        self.DEPARTURE_URL = self.BART_URL.format(
            api='etd', cmd='etd', key=key) + '&orig={orig}'
        self.STATION_URL = self.BART_URL.format(
            api='stn', cmd='stns', key=key)

    def _get_xml_root(self, url):
        """Get the XML root of the response from the specified URL.

        Raise a RuntimeError if there's no Internet connection or there was an
        error in the response.
        """
        try:
            response = urlopen(url)
            root = cElementTree.fromstring(response.read())
            response.close()
        except URLError as error:
            # Treat interrupted signal calls as warnings
            if error.reason.errno == errno.EINTR:
                raise RuntimeWarning
            raise RuntimeError('No Internet connection.')

        try:
            raise RuntimeError(root.find('.//error').find('details').text)
        except AttributeError:
            pass

        return root

    def get_advisories(self):
        """Get the current service advisories."""
        root = self._get_xml_root(self.ADVISORY_URL)
        advisories = []

        for advisory in root.iterfind('bsa'):
            # Ignore advisories that state there aren't any delays
            try:
                advisories.append(Advisory(
                    posted=advisory.find('posted').text,
                    sms_text=advisory.find('sms_text').text,
                    type=advisory.find('type').text,
                ))
            except AttributeError:
                break

        return advisories

    def get_departures(self, station_abbr):
        """Get the current departure estimates for a station."""
        root = self._get_xml_root(self.DEPARTURE_URL.format(orig=station_abbr))
        station = root.find('station')
        station_name = station.find('name').text
        departures = []

        for departure in station.iterfind('etd'):
            destination = departure.find('destination').text
            estimates = []

            for estimate in departure.iterfind('estimate'):
                minutes = estimate.find('minutes').text

                # Estimates with less than 1 minute say 'Leaving' instead
                try:
                    minutes = str(int(minutes)) + ' min'
                except ValueError:
                    pass

                estimates.append(Estimate(
                    color=estimate.find('color').text,
                    length=estimate.find('length').text,
                    minutes=minutes,
                ))

            departures.append((destination, estimates))

        return (station_name, departures)

    def get_stations(self):
        """Get the abbreviations and names for all stations."""
        root = self._get_xml_root(self.STATION_URL)
        stations = []

        for station in root.find('stations').iterfind('station'):
            stations.append((
                station.find('abbr').text, station.find('name').text))

        return stations
