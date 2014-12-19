from dadownloader.clean.collection import Collection
import json
import os
import shutil

class Favourites:
    """
    Remove redundent files from a downloaded favourites library

    Inspect a <username>.json file as created by `dadl` and remove any files
    in the favourites libray tree that are not part of the library. This is
    the root container for the `clean` program.

    :var str username: Username of the deviant whos downloaded favourites
        library we wish to clean.
    :var dadownloader.clean.collection.Collection[] collections: List of
        collections in the favourites library.
    """

    def __init__(self, username):
        """
        :param str username: Username of the deviant whos downloaded favourites
            library we wish to clean.
        """
        self.username       = username
        self.collections    = []

        # Identify current working directory
        cwd = os.getcwd()

        # make username working directory
        try:
            os.chdir(username)
        except:
            print('Cannot find '+self.username+'\'s favourites library.')

        # Build representation of favourites library
        try:
            jsonFile    = open(username+'.json')
            jsonObj     = json.load(jsonFile)
            for collection in jsonObj['collections']:
                self.collections.append(Collection(collection))
        except:
            print('Could not load '+username+'.json')
            self.collections = []

        # Return to original working directory
        os.chdir(cwd)

    def clean(self, remove=False):
        """
        Remove files that are not part of the favourites library

        :param bool remove: If True files that are identified to be not part of
            the collection will be deleted. Otherwise they will remain in place.
        """
        # Identify current working directory
        cwd = os.getcwd()

        # make username working directory
        try:
            os.chdir(self.username)
        except:
            return

        # Remove collections not part of library
        if remove:
            print('Removing non-library collections')
        else:
            print('Non-library collections')
        libCols = [col.name for col in self.collections]

        currCols = []
        for path in os.listdir('.'):
            if os.path.isdir(path):
                currCols.append(path)
        oldCols = list(set(currCols)-set(libCols))
        for oldCol in oldCols:
            print('  '+oldCol)
            if remove:
                shutil.rmtree(oldCol)

        # Clean each collection part of the library
        if remove:
            print('Removing non-library collection files')
        else:
            print('Non-library collection files')
        for collection in self.collections:
            collection.clean(remove)

        # Return to original working directory
        os.chdir(cwd)
