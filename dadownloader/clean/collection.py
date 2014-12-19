from dadownloader.clean.deviation   import Deviation
from lxml                           import etree
import os

class Collection:
    """
    Remove redundent files from a downloaded favourites collection

    Inspect a <username>.json file as created by `dadl` and remove any files
    in the favourites libray tree that are not part of the library. This is
    the container for a single collection in a favourites library for the
    `clean` program.

    :var str name: Name of the collection.
    :var dadownloader.clean.deviation.Deviation[] collection: List of deviations
        in the collection.
    """

    def __init__(self, collection):
        """
        :param dict collection: A dictionary object representation of the
            collection.
        """
        self.name       = collection['name'].encode('ascii')
        self.collection = []

        for deviation in collection['collection']:
            self.collection.append(Deviation(deviation))

    def clean(self, remove=False):
        """
        Remove files that are not part of the collection

        :param bool remove: If True files that are identified to be not part of
            the collection will be deleted. Otherwise they will remain in place.
        """
        # Identify current working directory
        cwd = os.getcwd()

        # make collection name working directory
        try:
            os.chdir(self.name)
        except:
            os.chdir(cwd)
            return

        print('  %s/' % self.name)

        # Clean avatars
        print(u'  \u251C\u2500 avatars/')
        libFiles = []
        for deviation in self.collection:
            libFiles.append(deviation.avatar)

        currFiles = []
        for path in os.listdir('avatars'):
            if os.path.isfile('avatars/'+path):
                currFiles.append(path)
        oldFiles = list(set(currFiles)-set(libFiles))
        for oldFile in oldFiles:
            print(u'  \u2502  \u251C\u2500 %s' % oldFile)
            if remove:
                os.remove('avatars/'+oldFile)

        # Clean descriptions
        print(u'  \u251C\u2500 descriptions/')
        libFiles = []
        for deviation in self.collection:
            libFiles.append(deviation.description+'.original')
            libFiles.append(deviation.description+'.html')

        currFiles = []
        for path in os.listdir('descriptions'):
            if os.path.isfile('descriptions/'+path):
                currFiles.append(path)
        oldFiles = list(set(currFiles)-set(libFiles))
        for oldFile in oldFiles:
            print(u'  \u2502  \u251C\u2500 %s' % oldFile)
            if remove:
                os.remove('descriptions/'+oldFile)

        # Clean img resources
        print(u'  \u2502  \u251C\u2500 imgs/')
        libFiles = []
        for deviation in self.collection:
            with open('descriptions/%s.html' % deviation.description) as f:
                parser  = etree.HTMLParser(remove_blank_text=True)
                pageXML = etree.parse(f, parser)
                imgs    = pageXML.xpath('//img/@src')
                imgs    = [os.path.basename(img) for img in imgs]
                libFiles = list(set(imgs) | set(libFiles))

        currFiles = []
        for path in os.listdir('descriptions/imgs'):
            if os.path.isfile('descriptions/imgs/'+path):
                currFiles.append(path)
        oldFiles = list(set(currFiles)-set(libFiles))
        for oldFile in oldFiles:
            print(u'  \u2502  \u2502  \u251C\u2500 %s' % oldFile)
            if remove:
                os.remove('descriptions/imgs/'+oldFile)

        # Clean thumbnails
        print(u'  \u251C\u2500 thumbs/')
        libFiles = []
        for deviation in self.collection:
            if deviation.thumb != None:
                libFiles.append(deviation.thumb)

        currFiles = []
        for path in os.listdir('thumbs'):
            if os.path.isfile('thumbs/'+path):
                currFiles.append(path)
        oldFiles = list(set(currFiles)-set(libFiles))
        for oldFile in oldFiles:
            print(u'  \u2502  \u251C\u2500 %s' % oldFile)
            if remove:
                os.remove('thumbs/'+oldFile)

        # Clean deviation files
        libFiles = []
        for deviation in self.collection:
            if deviation.file != None:
                libFiles.append(deviation.file)

        currFiles = filter(os.path.isfile, os.listdir('.'))
        oldFiles = list(set(currFiles)-set(libFiles))
        for oldFile in oldFiles:
            print(u'  \u251C\u2500 %s' % oldFile)
            if remove:
                os.remove(oldFile)

        # Return to original working directory
        os.chdir(cwd)
