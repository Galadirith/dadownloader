from dadownloader.deviation.deviation   import Deviation
from urlparse                           import urlparse
from os.path                            import basename
from StringIO                           import StringIO
from lxml                               import etree
from collections                        import OrderedDict
import json
import os

class Film(Deviation):
    """
    A single film deviation

    :var str thumb: DeviantArt generates a comic book strip style thumbnail of
        film uploads. This string holds its name including extension.
    :var str thumburl: URL to the films thumbnail.
    :var str film: Name of the film file including extension.
    :var str filmurl: URL to the film file.
    """

    def __init__(self, deviation, session, page=None):
        """
        :param lxml.etree.Element deviation: A div element from a collections
            page that contains basic meta data about the deviation.
        :param requests.Session session: An instance through which all remote
            requests should be made.
        :param lxml.etree.Element page: The deviations page.
        """
        Deviation.__init__(self, 'film', deviation, session)

        # Determine thumbnail details
        self.thumburl = deviation.xpath(
            './/span[@class="tt-fh-tc"]//b[@class="film"]/img/@src')[0]
        parsedURL   = urlparse(self.thumburl)
        self.thumb  = basename(parsedURL[2])

        # To determine film file details we have to load the deviations page
        page = self.session.get(self.url)

        # The details of the film file can be found in json string embedded in
        # the page that takes the form:
        # {
        #   "360p": {
        #     "label": "360p",
        #     "src": <filmurl>,
        #     "width": 480,
        #     "height": 360
        #   }
        # }
        parser  = etree.HTMLParser()
        pageXML = etree.parse(StringIO(page.text), parser)
        jsonStr = pageXML.xpath('//*[@id="gmi-FilmPlayer"]/@gmon-sources')[0]

        # json.loads returns unicode strs but the url is safe to encode as ascii
        jsonObj         = json.loads(jsonStr)
        self.filmurl    = jsonObj['360p']['src'].encode('ascii')
        parsedURL       = urlparse(self.filmurl)
        self.film       = basename(parsedURL[2])

    def toDict(self):
        """
        Return the instance fields as a dictionary

        :rtype: OrderedDict
        :return: An ordered dictionary of the instance fields of this deviation.
        """
        fields = Deviation.toDict(self)
        fields.update((
            ('thumb',       self.thumb),
            ('thumburl',    self.thumburl),
            ('film',        self.film),
            ('filmurl',     self.filmurl)
        ))
        return fields

    def download(self, path=''):
        """
        Download film file associated with deviation

        :param str path: Directory path to where the resources should be
            downloaded. Default to current working directory.
        """
        # os.open *should* give a thread-safe way to exlusivly open files
        filepath = os.path.join(path,self.film)
        filepath = os.path.normpath(filepath)
        try:
            # os.O_BINARY is only avilable and needed on windows
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_BINARY
        except:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(filepath, flags)
        except:
            return

        try:
            response = self.session.get(self.filmurl, stream=True)
            if response.status_code == 200:
                for chunk in response.iter_content(1024):
                    os.write(fd, chunk)
        except:
            # Remove partial img file if request or stream fails
            os.close(fd)
            os.remove(filepath)
