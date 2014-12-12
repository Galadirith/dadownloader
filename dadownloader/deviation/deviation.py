from urlparse       import urlparse
from os.path        import basename
from collections    import OrderedDict

class Deviation:
    """
    A single deviation

    This Object encapsulates the data for a single deviation including img name,
    description, creator etc.

    :var str type: Type of deviation. This can take the values
        IMG     =='An Image ;D'
        FILM    =='A Film'
        DATA    =='All other binary formats'
    :var str title: Title of the deviation.
    :var str url: URL to the deviations page.
    :var str creator: Deviant who created the deviation.
    :var str creatorurl: URL to the deviant who created the deviation.
    :var str avatar: File name + extension of the avatar of the creator.
    :var str avatarurl: URL of the avatar of the creator.
    :var requests.Session session: An instance through which all remote requests
        should be made.
    """

    def __init__(self, type, deviation, session ):
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
        self.session = session

        # Some of the avatar URLs have a query string which we want to strip
        parsedURL   = urlparse(self.avatarurl)
        self.avatar = basename(parsedURL[2])

    def toDict(self):
        """Return the instance fields as a dictionary"""
        return OrderedDict((
            ('type',        self.type),
            ('title',        self.title),
            ('url',          self.url),
            ('creator',      self.creator),
            ('creatorurl',   self.creatorurl),
            ('avatar',       self.avatar),
            ('avatarurl',    self.avatarurl)
        ))
