from    dadownloader.collection import Collection
from    StringIO                import StringIO
from    lxml                    import etree
from    collections             import OrderedDict
import  os

class Favourites:
    """
    Object to hold a complete set of favourite collections

    This Object encapsulates a complete set of collections from a DeviantArt
    users favourites. This class also contains the crucial methods that actually
    gather all of the data from deviantART :D

    :var str url: URL to the deviants user page to whom the favourites belong.
    :var str favurl: URL to the favourites page.
    :var dadownloader.collection.Collection[] collections: List of collections
        including the root collection of the users favourites.
    :var requests.Session session: An instance through which all remote requests
        should be made.
    """

    def __init__(self, username, session):
        """
        :param str username: Username of the deviant from whom we wish to
            download the favourites from.
        :param requests.Session session: An instance through which all remote
            requests should be made.
        """
        self.url            = 'http://%s.deviantart.com' % username
        self.favurl         = self.url+'/favourites/'
        self.session        = session
        self.collections    = []

        # Identify current working directory
        cwd = os.getcwd()

        # Create encapsulating folder and make working directory
        try:
            os.mkdir(username)
        except OSError:
            pass
        os.chdir(username)

        # Identify and process all collections
        if self.grabCols() == False:
            print(' Failed to identify any remaining collections')

        # Return to original working directory
        os.chdir(cwd)


    def pushCol(self, name, url):
        """
        Adds a single favourite collection to the container

        :param str name: Name of the collection
        :param str url: URL to the collection
        """
        collection = Collection(name, url, self.session)
        self.collections.append(collection)

    def grabCols(self):
        """Adds every favourite collection to the container"""

        # Add the root collection
        self.pushCol('Favourites', self.favurl)

        # Load the root collection page to identify any further collections
        try:
            root = self.session.get(self.favurl)
        except:
            return False

        # Harvest the name and url of each sub-collection
        parser      = etree.HTMLParser()
        rootXML     = etree.parse(StringIO(root.text), parser)
        colNames    = rootXML.xpath('//div[@class="tv150"]/div[@class="tv150-tag"]/text()')
        colURLs     = rootXML.xpath('//div[@class="tv150"]/a[@class="tv150-cover"]/@href')

        # Push each sub-collection to collections
        for i in range(len(colNames)):
            self.pushCol(colNames[i], colURLs[i])

        return True

    def toDict(self):
        """Return the instance fields as a dictionary"""
        # Compile just the fields of the collections
        collections = []
        for collection in self.collections:
            collections.append(collection.toDict())

        return OrderedDict((
            ('url',          self.url),
            ('collections',  collections)
        ))
