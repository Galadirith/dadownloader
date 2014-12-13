from dadownloader.deviation.deviation   import Deviation
from urlparse                           import urlparse
from os.path                            import basename
from StringIO                           import StringIO
from lxml                               import etree
from collections                        import OrderedDict
import re

class Data(Deviation):
    """
    A single data deviation

    Holds the data for a single data deviation. This may be a swf file or
    actually just a collection of files/data.

    :var str thumb: The thumbnail preview is probaby more important for data
        deviations because their is no well defined way to map data (exg a zip
        file) to so pictorial representation ... obviously :D This holds the
        name of the thumbnail including extension.
    :var str thumburl: URL to the datas thumbnail.
    :var str data: Name of the data file including extension.
    :var str dataurl: URL to the data file.
    """

    def __init__(self, deviation, session, page=None):
        """
        :param lxml.etree.Element deviation: A div element from a collections
            page that contains basic meta data about the deviation.
        :param requests.Session session: An instance through which all remote
            requests should be made.
        :param lxml.etree.Element page: The deviations page.
        """
        Deviation.__init__(self, 'data', deviation, session)

        # Determine thumbnail details.
        # I discovered I could mod the url to get a bigger thumbnail image.
        thumburl = deviation.xpath(
            './/span[@class="tt-fh-tc"]//a[@class="thumb"]/img/@src')[0]
        self.thumburl = re.sub(r'\/200H', r'', thumburl)
        parsedURL   = urlparse(self.thumburl)
        self.thumb  = basename(parsedURL[2])

        # To determine data file details we have to load the deviations page
        if page == None:
            page    = self.session.get(self.url)
            parser  = etree.HTMLParser()
            pageXML = etree.parse(StringIO(page.text), parser)
        else:
            pageXML = page

        # The details of the data file can be found in json string embedded in
        self.dataurl = pageXML.xpath(
            '//a[contains(@class,"dev-page-download")]/@href')[0]
        parsedURL    = urlparse(self.dataurl)
        self.data    = basename(parsedURL[2])

    def toDict(self):
        """Override parent and return the instance fields as a dictionary"""
        return OrderedDict((
            ('type',        self.type),
            ('title',       self.title),
            ('url',         self.url),
            ('creator',     self.creator),
            ('creatorurl',  self.creatorurl),
            ('thumb',       self.thumb),
            ('thumburl',    self.thumburl),
            ('data',        self.data),
            ('dataurl',     self.dataurl),
            ('avatar',      self.avatar),
            ('avatarurl',   self.avatarurl)
        ))
