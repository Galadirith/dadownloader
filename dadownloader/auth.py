import  requests
import  pickle
import  os
import  getpass
from    StringIO    import StringIO
from    lxml        import etree

class Auth:
    """
    Attempt to generate an authenticated session for DeviantArt.

    :param str url: https://www.deviantart.com/users/login
    :param requests.Session session: Session object through which all remote
        requests to DeviantArt should be made.
    """

    def __init__(self):
        self.url        = 'https://www.deviantart.com/users/login'
        self.session    = self.createSession()
        pass

    def auth(self):
        """
        Attempt to generate an authenticated session for DeviantArt.

        Check for a 'cookies' file in the calling directory. If no such file
        exists prompt the user for DeviantArt login credentials. An
        authenticated session is required to access ristricted content on
        DeviantArt, such as mature deviations, and those flaged by their creator
        to only allow access from DeviantArt members.

        :rtype: requests.Session
        :return:
            If a 'cookies' file exists in the calling directory, they are
            assumed to be a pickle dump of a valid cookiejar. Deterimine if they
            are authenticated cookies for DeviantArt. If they are not request
            login credentials.

            If valid credentials are provided, the returned object contains
            authenticated cookies.

            If no or invalid credentials are provided, the returned object will
            contain no authenticated cookies.
        """
        url     = self.url
        session = self.session

        # Check for authenticated cookies
        if os.path.isfile('cookies'):

            with open('cookies', 'rb') as f:
                session.cookies = pickle.load(f)

            status = self.verify()
            if status == 'GOOD':
                print('Cookies are good')
                return session
            elif status == 'BAD':
                print('Cookies are bad')

        # Start a new/clean session
        session = self.createSession()

        # Reqeust login credentials from the user
        print(\
            'If you want to access restricted content '\
            'please provide login credentials.')
        username = raw_input('Username: ')
        password = getpass.getpass()

        if username == '' or password == '':
            print(\
                'Your username or password is empty. '\
                'Continuing unauthenticated.')
            return session

        # Request the DeviantArt login page
        response = session.get(url, headers={'Referer': url})

        # Find cross-site scripting (XSS) variables requried for POST payload
        parser  = etree.HTMLParser()
        doc     = etree.parse(StringIO(response.text), parser)
        token   = doc.xpath('//*[@id="login"]/input[2]/@value')[0]
        key     = doc.xpath('//*[@id="login"]/input[3]/@value')[0]

        # Simulate an application/x-www-form-urlencoded POST request to login
        payload = {
            'ref': url,
            'username': username,
            'password': password,
            'remember_me': '1',
            'validate_token': token,
            'validate_key': key
        }
        session.post(url, data=payload, headers={'Referer': url})

        # Write cookies to file for future re-use
        with open('cookies', 'w+b') as f:
            pickle.dump(session.cookies, f)

        # Assign the new session to the instance field self.session
        self.session = session

        # Check for authenticated cookies
        status = self.verify()
        if status == 'BAD':
            print('Cookies are bad. Continuing unauthenticated.')

        return session

    def createSession(self):
        """Create a new session for remote requests to DeviantArt"""

        userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) '\
                    'AppleWebKit/537.36 (KHTML, like Gecko) '\
                    'Chrome/39.0.2171.71 Safari/537.36'
        session                         = requests.Session()
        session.headers['User-Agent']   = userAgent

        return session

    def verify(self):
        """
        Check if the current session is logged in to DeviantArt

        :rtype: str
        :return: If the session is logged in to DeviantArt return 'GOOD',
            otherwise return 'BAD'.
        """
        # Request the DeviantArt login page
        response = self.session.get(self.url, headers={'Referer': self.url})

        # Query element that only exists for loged in users
        parser  = etree.HTMLParser()
        doc     = etree.parse(StringIO(response.text), parser)
        login   = doc.xpath('//*[@id="oh-menu-deviant"]/a/span')
        if len(login) == 1:
            return 'GOOD'
        else:
            return 'BAD'
