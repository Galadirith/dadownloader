from urlparse           import urlparse
from os.path            import basename
from collections        import OrderedDict
from datetime           import datetime
from calendar           import timegm
from StringIO           import StringIO
from lxml               import etree
import re
import os

class Deviation:
    """
    A single deviation

    This Object encapsulates the data for a single deviation including name,
    description, creator etc.

    :var str type: Type of deviation. This can take the values
        img         == An Image ;D
        film        == A Film
        text        == A text file
        data        == All other binary formats
        restricted  == A restricted deviation. This type will only occur if
            session is not logged in to DeviantArt. All the xpath queries in
            this class are valid for restricted content.
        unknown     == 'Unknown deviation type'
    :var str title: Title of the deviation.
    :var str url: URL to the deviations page.
    :var str creator: Deviant who created the deviation.
    :var str creatorurl: URL to the deviant who created the deviation.
    :var str avatar: File name + extension of the avatar of the creator.
    :var str avatarurl: URL of the avatar of the creator.
    :var int submitted: Unix timestamp for the date the deviation was submitted.
    :var str downloadurl: URL to the original file if the creator enabled this
        option when submitting the deviation. None otherwise.
    :var requests.Session session: An instance through which all remote requests
        should be made.
    """

    def __init__(self, type, deviation, session):
        """
        :param str type: Type of deviation.
        :param lxml.etree.Element deviation: A div element from a collections
            page that contains basic meta data about the deviation.
        :param requests.Session session: An instance through which all remote
            requests should be made.
        """
        self.type       = type
        self.title      = deviation.xpath(
            './/span[@class="tt-fh-tc"]'\
            '/following-sibling::span[@class="details"]'\
            '//*[not(*) and (@class="tt-fh-oe" or @class="t")]'\
            '/text()')[0]
        self.url        = deviation.xpath(
            './/span[@class="tt-fh-tc"]'\
            '//a/@href')[0]
        self.creator    = deviation.xpath(
            './/span[@class="tt-fh-tc"]'\
            '/../../@username')[0]
        try:
            self.creatorurl = deviation.xpath(
                './/span[@class="tt-fh-tc"]'\
                '/following-sibling::span[@class="details"]'\
                '/small//a[starts-with(@class, "u")]/@href')[0]
        except IndexError:
            # Split creatorurl from url if 'Banned or Deactivated' username
            parsedURL       = urlparse(self.url)
            self.creatorurl = parsedURL[0] + '://' + parsedURL[1]
        self.avatarurl  = deviation.xpath(
            './/span[@class="tt-fh-tc"]'\
            '/../../@usericon')[0]
        self.downloadurl = None
        self.session = session

        # Some of the avatar URLs have a query string which we want to strip
        parsedURL   = urlparse(self.avatarurl)
        self.avatar = basename(parsedURL[2])

        # Determine Submission date
        datestr = deviation.xpath(
            './/span[@class="tt-fh-tc"]/'\
            'following-sibling::span[@class="details"]/a/@title')[0]
        datestr         = re.sub(r'^.*?, (?=(?:.{3} .{1,2}?, .{4}))', r'', datestr)
        date            = datetime.strptime(datestr, '%b %d, %Y')
        self.submitted  = timegm(date.timetuple())

    def toDict(self):
        """
        Return the instance fields as a dictionary

        :rtype: OrderedDict
        :return: An ordered dictionary of the instance fields of this deviation.
        """
        return OrderedDict((
            ('type',        self.type),
            ('title',       self.title),
            ('submitted',   self.submitted),
            ('url',         self.url),
            ('creator',     self.creator),
            ('creatorurl',  self.creatorurl),
            ('avatar',      self.avatar),
            ('avatarurl',   self.avatarurl)
        ))

    def download(self):
        """
        Download resources associated with deviation to working directory

        This method should be overriden by any sub-class that has remote
        resources that need to be downloaded, such as img files, data files,
        films files etc.
        """
        pass

    def downloadDescription(self):
        """Download description associated with deviation"""

        # STAGE 1: Download description html

        # Create description directory if it doesn't exist
        path = 'descriptions'
        try:
            os.mkdir(path)
        except OSError:
            pass

        # Construct a filename for the description
        parsedURL   = urlparse(self.url)
        filename    = os.path.basename(parsedURL[2])+'.original'

        # os.open *should* give a thread-safe way to exlusivly open files
        flags       = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        filepath    = os.path.join(path,filename)
        filepath    = os.path.normpath(filepath)
        try:
            fd = os.open(filepath, flags)
        except:
            return
        f = os.fdopen(fd, 'w')

        # Load the page
        try:
            page = self.session.get(self.url)
        except:
            # Remove the empty file if the remote request failed
            f.close()
            os.remove(filepath)
            return
        parser  = etree.HTMLParser(remove_blank_text=True)
        pageXML = etree.parse(StringIO(page.text), parser)

        # Find the description
        description = pageXML.xpath(
            '//div[contains(@class,"dev-description")]'\
            '//div[@class="text block"]')[0]
        f.write(etree.tostring(description, pretty_print=True))

        # Find the downloadurl if it exists
        try:
            self.downloadurl = pageXML.xpath(
                '//a[contains(@class,"dev-page-download")]/@href')[0]
        except:
            pass

        # STAGE 2: Download description images and point descriptions as them

        # Create imgs directory if it doesn't exist
        imgPath = os.path.join(path,'imgs')
        imgPath = os.path.normpath(imgPath)
        try:
            os.mkdir(imgPath)
        except OSError:
            pass

        # Find all img elements, download associated images and fix html
        imgs = description.xpath('.//img')
        for img in imgs:
            # Fix img src to point at local file
            url                 = img.attrib['src']
            parsedURL           = urlparse(url)
            imgFilename         = basename(parsedURL[2])
            relImgFilepath      = os.path.join('imgs',imgFilename)
            relImgFilepath      = os.path.normpath(relImgFilepath)
            img.attrib['src']   = relImgFilepath

            # Download img
            try:
                # os.O_BINARY is only avilable and needed on windows
                try:
                    flags   = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_BINARY
                except:
                    flags   = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                imgFilepath = os.path.join(imgPath,imgFilename)
                fd          = os.open(os.path.normpath(imgFilepath), flags)
            except:
                continue

            response = self.session.get(url, stream=True)
            if response.status_code == 200:
                for chunk in response.iter_content(1024):
                    os.write(fd, chunk)

        # Construct a filename for the fixed description
        parsedURL   = urlparse(self.url)
        filename    = os.path.basename(parsedURL[2])+'.html'

        # Write fixed description html to file
        description.attrib['class'] = "description"
        try:
            flags       = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            filepath    = os.path.join(path,filename)
            fd          = os.open(os.path.normpath(filepath), flags)
            f           = os.fdopen(fd, 'w')
        except:
            return

        f.write(etree.tostring(description, pretty_print=True))

    def downloadAvatar(self):
        """Download the Avatar of the creator of the deviation"""

        # Create avatars directory in the working directory if it doesn't exist
        path = 'avatars'
        try:
            os.mkdir(path)
        except OSError:
            pass

        # os.open *should* give a thread-safe way to exlusivly open files
        filepath = os.path.join(path,self.avatar)
        filepath = os.path.normpath(filepath)
        try:
            # os.O_BINARY is only defined and needed on windows
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_BINARY
        except:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(filepath, flags)
        except:
            return

        try:
            response = self.session.get(self.avatarurl, stream=True)
            if response.status_code == 200:
                for chunk in response.iter_content(1024):
                    os.write(fd, chunk)
        except:
            # Remove partial avatar file if request or stream fails
            os.close(fd)
            os.remove(filepath)
