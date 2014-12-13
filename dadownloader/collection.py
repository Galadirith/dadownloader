import  math
import  time
from    dadownloader.progressbar            import progressBar
from    dadownloader.deviation.deviation    import Deviation
from    dadownloader.deviation.img          import Img
from    dadownloader.deviation.film         import Film
from    StringIO                            import StringIO
from    lxml                                import etree
from    collections                         import OrderedDict

class Collection:
    """
    A single favourite collection of deviations

    This Object acts as a container for a single collection of favourite
    deviations, and provides methods to gather the data and meta data given
    a collections URL.

    :var str name: Name of the collection.
    :var str url: URL of the collection.
    :var dadownloader.deviation.deviation.Deviation[] collection: List of the
        deviations in the collection.
    :var requests.Session session: An instance through which all remote requests
        should be made.
    """

    def __init__(self, name, url, session):
        """
        :param str name: Name of the collection
        :param str url: URL to the collection
        :param requests.Session session: An instance through which all remote
            requests should be made.
        """
        self.name       = name
        self.url        = url
        self.collection = []
        self.session    = session

        self.grabCol()

    def grabCol(self):
        """Adds all favourite devations in the collection to this container"""

        # Report the collection that is being processed
        print(' '+self.name)

        # Generate ElementTree list of every page in the collection
        pages, deviationsCount = self.grabPages()

        # Start a progress bar to report deviations with meta data harvested
        progressBar('  Deviations\t', 0, deviationsCount)

        for i in range(len(pages)):
            # Generate div list for all non-stored deviations
            deviations = pages[i].xpath(
                '//div[span/span['\
                '@class="tt-fh-tc" and span/a/@class!="instorage"]]')

            # Push the deviation into the collection
            for j in range(len(deviations)):
                self.pushFav(deviations[j])
                progressBar('  Deviations\t', j+1+i*24, deviationsCount)

    def grabPages(self):
        """
        Generates a list of ElementTree's of every page in the collection

        :rtype: (lxml.etree.ElementTree[], int)
        :return: (List of every page in the collection, number of deviations in
            the collection)
        """
        # Request the collections root page
        rootResponse    = self.session.get(self.url)

        # Find number of pages in collection
        parser          = etree.HTMLParser()
        rootXML         = etree.parse(StringIO(rootResponse.text), parser)
        deviationsCount = rootXML.xpath('//div[@id="gallery_pager"]/@gmi-limit')[0]
        pagesCount      = int(math.ceil(float(deviationsCount)/24))

        # Start a progress bar to report pages downloaded
        progressBar('  Pages\t', 1, pagesCount)

        # Now request any further pages that exist in the collection
        pagesResponses = []
        for i in range(pagesCount-1):
            pagesResponses.append(
                self.session.get(self.url+'?offset=%i' % ((i+1)*24))
            )
            # Be kind to the server
            time.sleep(1)
            progressBar('  Pages\t', i+2, pagesCount)

        # Prepare ElementTree's from each response
        pagesXML = []
        for response in pagesResponses:
            pagesXML.append(etree.parse(StringIO(response.text), parser))

        # Add the root page to the begining of teh list
        pagesXML.insert(0, rootXML)

        return (pagesXML, int(deviationsCount))

    def pushFav(self, deviation):
        """
        Adds a favourite deviation to the collection

        Adds a favourite deviation to the collection and populates the new
	    favourite with data from the deviation parameter.

        :param lxml.etree.Element deviation: A div element from a collections
            page that contains basic meta data about the deviation.
        """
        imgURL  = deviation.xpath('.//span[@class="tt-fh-tc"]//a/@data-super-img')
        filmURL = deviation.xpath('.//span[@class="tt-fh-tc"]//b[@class="film"]')

        if len(imgURL) != 0:
            self.collection.append(Img(deviation, self.session))
        elif len(filmURL) != 0:
            self.collection.append(Film(deviation, self.session))
        else:
            self.collection.append(Deviation('data', deviation, self.session))

    def toDict(self):
        """Return the instance fields as a dictionary"""
        # Compile just the fields of the deviations
        collection = []
        for deviation in self.collection:
            collection.append(deviation.toDict())

        return OrderedDict((
            ('name',         self.name),
            ('url',          self.url),
            ('collection',   collection)
        ))
