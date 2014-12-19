from urlparse           import urlparse
from os.path            import basename

class Deviation:
    """
    Identify files associated with a downloaded favourites library

    Inspect a <username>.json file as created by `dadl` and remove any files
    in the favourites libray tree that are not part of the library. This is
    the container for a single deviation in a favourites library for the
    `clean` program.

    :var str file: The filename of the deviation.
    :var str thumb: The filename of the thumbnail of the deviation.
    :var str description: The filename of the description for the deviation
        without extension.
    :var str[] imgs: List of filenames of all the image files used in the
        description.
    :var str avatar: The filename of the avatar of the creator for the
        deviation.
    """

    def __init__(self, deviation):
        """
        :param dict deviation: A dictionary object representation of the
            deviation.
        """
        type = deviation['type']
        if type == 'img':
            self.file   = deviation['img'].encode('ascii')
            self.thumb  = None
        elif type == 'film':
            self.file   = deviation['film'].encode('ascii')
            self.thumb  = deviation['thumb'].encode('ascii')
        elif type == 'data':
            self.file   = deviation['data'].encode('ascii')
            self.thumb  = deviation['thumb'].encode('ascii')
        else:
            self.file   = None
            self.thumb  = None

        parsedURL           = urlparse(deviation['url'])
        self.description    = basename(parsedURL[2])
        self.avatar         = deviation['avatar'].encode('ascii')
