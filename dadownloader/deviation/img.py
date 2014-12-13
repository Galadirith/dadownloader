from dadownloader.deviation.deviation   import Deviation
from urlparse                           import urlparse
from os.path                            import basename
from collections                        import OrderedDict

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
                    '//span[@class="tt-fh-tc"]//a/@data-super-img')[0]
        else:
            self.imgurl = page.xpath('//img[@class="dev-content-full"]/@src')[0]

        # Extract the filename of the img
        parsedURL   = urlparse(self.imgurl)
        self.img    = basename(parsedURL[2])

    def toDict(self):
        """Override parent and return the instance fields as a dictionary"""
        return OrderedDict((
            ('type',        self.type),
            ('title',       self.title),
            ('url',         self.url),
            ('creator',     self.creator),
            ('creatorurl',  self.creatorurl),
            ('img',         self.img),
            ('imgurl',      self.imgurl),
            ('avatar',      self.avatar),
            ('avatarurl',   self.avatarurl)
        ))
