import  math
import  time
import  os
from    dadownloader.progressbar            import progressBar
from    dadownloader.deviation.deviation    import Deviation
from    dadownloader.deviation.img          import Img
from    dadownloader.deviation.film         import Film
from    dadownloader.deviation.data         import Data
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
    var bool avatars: If True the avatar of the creator of each deviation will
        be downloaded.
    :var bool descriptions: If True the description of each deviations will be
        downloaded.
    :var bool files: If True the file asociated with each deviation (such as and
        image or film file) will be downloaded.
    """

    def __init__(self, name, url, session, avatars=False, descriptions=False, files=False):
        """
        :param str name: Name of the collection
        :param str url: URL to the collection
        :param requests.Session session: An instance through which all remote
            requests should be made.
        :param bool avatars: If True the avatar of the creator of each deviation
            will be downloaded.
        :param bool descriptions: If True the description of each deviations will
            be downloaded.
        :param bool files: If True the file asociated with each deviation (such
            as and image or film file) will be downloaded.
        """
        self.name       = name
        self.url        = url
        self.collection = []
        self.session    = session

        self.avatars        = avatars
        self.descriptions   = descriptions
        self.files          = files

        # Identify current working directory
        cwd = os.getcwd()

        # Create encapsulating folder for collection and make working directory
        try:
            os.mkdir(self.name)
        except OSError:
            # Passed if folder exists so its probably OK :D
            pass
        os.chdir(self.name)

        # Identify and process all deviations in the collection
        self.grabCol()

        # Return to original working directory
        os.chdir(cwd)

    def grabCol(self):
        """
        Adds all favourite devations in the collection to this container
        """

        # Report the collection that is being processed
        print(' '+self.name)

        # Generate ElementTree list of every page in the collection
        pages = self.grabPages()
        if pages == None:
            print('  Failed to load collection')
            return
        else:
            pages, deviationsCount = pages

        # Start a progress bar to report deviations with meta data harvested
        progressBar('  Deviations', 0, deviationsCount)

        for i in range(len(pages)):
            # Generate div list for all non-stored deviations
            deviations = pages[i].xpath(
                '//div[span/span['\
                '@class="tt-fh-tc" and span/a/@class!="instorage"]]')

            # Push the deviation into the collection
            for j in range(len(deviations)):
                self.pushFav(deviations[j])
                if self.avatars:
                    self.collection[-1].downloadAvatar()
                if self.descriptions:
                    self.collection[-1].downloadDescription()
                if self.files:
                    self.collection[-1].download()
                progressBar('  Deviations', j+1+i*24, deviationsCount)

    def grabPages(self):
        """
        Generates a list of ElementTree's of every page in the collection

        :rtype: (lxml.etree.ElementTree[], int)
        :return: (List of every page in the collection, number of deviations in
            the collection). If any of the remote requests fail with a
            connection error `None` is returned.
        """
        # Request the collections root page
        try:
            rootResponse = self.session.get(self.url)
        except:
            return None

        # Find number of pages in collection
        parser          = etree.HTMLParser()
        rootXML         = etree.parse(StringIO(rootResponse.text), parser)
        deviationsCount = rootXML.xpath('//div[@id="gallery_pager"]/@gmi-limit')[0]
        pagesCount      = int(math.ceil(float(deviationsCount)/24))

        # Start a progress bar to report pages downloaded
        progressBar('  Pages', 1, pagesCount)

        # Now request any further pages that exist in the collection
        pagesResponses = []
        for i in range(pagesCount-1):
            try:
                response = self.session.get(self.url+'?offset=%i' % ((i+1)*24))
            except:
                progressBar('  Pages', pagesCount, pagesCount)
                return None
            pagesResponses.append(response)

            # Be kind to the server
            time.sleep(1)
            progressBar('  Pages', i+2, pagesCount)

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
        # Is it an img deviation?
        devType = deviation.xpath('.//span[@class="tt-fh-tc"]//a/@data-super-img')
        if len(devType) == 1:
            self.collection.append(Img(deviation, self.session))
            return

        # Is is a film deviation?
        devType = deviation.xpath('.//span[@class="tt-fh-tc"]//b[@class="film"]')
        if len(devType) == 1:
            self.collection.append(Film(deviation, self.session))
            return

        # Is it a text deviation? Currently no explict handler class
        devType = deviation.xpath('.//span[@class="tt-fh-tc"]//img[@class="lit"]')
        if len(devType) == 1:
            self.collection.append(Deviation('text', deviation, self.session))
            return

        # If inconclusive we must open the deviations page to determine its type
        # as there has been a case where an img deviation has no @data-super-img
        # attribute
        url     = deviation.xpath('.//span[@class="tt-fh-tc"]//a/@href')[0]
        page    = self.session.get(url)
        parser  = etree.HTMLParser()
        pageXML = etree.parse(StringIO(page.text), parser)

        # Is the deviation restricted content?
        restricted = pageXML.xpath('//div[@id="filter-warning"]')
        if len(restricted) == 1:
            self.collection.append(Deviation('restricted', deviation, self.session))
            return

        # Is there an img size?
        imgSize = pageXML.xpath(
            '//div[contains(@class,"dev-metainfo-details")]'\
            '/dl/dt[text()="Image Size"]')
        if len(imgSize) == 0:
             self.collection.append(Data(deviation, self.session, pageXML))
             return

        # Case on img and flash files that both have an imgSize
        flash = pageXML.xpath('//div[@id="flashed-in"]')
        if len(flash) == 1:
            self.collection.append(Data(deviation, self.session, pageXML))
            return
        else:
            self.collection.append(Img(deviation, self.session, pageXML))
            return

        # It it reaches here then the type is indeterminable
        self.collection.append(Deviation('unknown', deviation, self.session))


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
