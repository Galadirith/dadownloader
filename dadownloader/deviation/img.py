from dadownloader.deviation.deviation   import Deviation
from urlparse                           import urlparse
from os.path                            import basename
from collections                        import OrderedDict
import os

class Img(Deviation):
    """
    A single image deviation

    :var str img: File name of the img including its extension.
    :var str imgurl: URL to the img.
    """

    def __init__(self, deviation, session, page=None):
        """
        :param lxml.etree.Element deviation: A div element from a collections
            page that contains basic meta data about the deviation.
        :param requests.Session session: An instance through which all remote
            requests should be made.
        :param lxml.etree.Element page: The deviations page.
        """
        Deviation.__init__(self, 'img', deviation, session)

        if page == None:
            # If imgurl not under data-super-full-img it is under data-super-img
            try:
                self.imgurl = deviation.xpath(
                    './/span[@class="tt-fh-tc"]//a/@data-super-full-img')[0]
            except IndexError:
                self.imgurl = deviation.xpath(
                    './/span[@class="tt-fh-tc"]//a/@data-super-img')[0]
        else:
            self.imgurl = page.xpath('//img[@class="dev-content-full"]/@src')[0]

        # Extract the filename of the img
        parsedURL   = urlparse(self.imgurl)
        self.img    = basename(parsedURL[2])

    def toDict(self):
        """
        Return the instance fields as a dictionary

        :rtype: OrderedDict
        :return: An ordered dictionary of the instance fields of this deviation.
        """
        fields = Deviation.toDict(self)
        fields.update((
            ('img',     self.img),
            ('imgurl',  self.imgurl)
        ))
        return fields

    def download(self):
        """Download image file associated with deviation to working directory"""
        
        # os.open *should* give a thread-safe way to exlusivly open files
        filepath = self.img
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
            response = self.session.get(self.imgurl, stream=True)
            if response.status_code == 200:
                for chunk in response.iter_content(1024):
                    os.write(fd, chunk)
        except:
            # Remove partial img file if request or stream fails
            os.close(fd)
            os.remove(filepath)
