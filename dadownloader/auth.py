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
        self.url = 'https://www.deviantart.com/users/login'
        self.newSession()
        pass

    def auth(self):
        """
        Attempt to generate an authenticated session for DeviantArt.

        An authenticated session is required to access restricted content on
        DeviantArt, such as mature deviations, and those flaged by their creator
        to only allow access from DeviantArt members.

        :rtype: requests.Session
        :return:
            If Auth was able to log in to DeviantArt, a session object is
            returned containing cookies authenticated against DeviantArt,
            otherwise an unauthenticated seesion object is returned.
        """
        # Check for authenticated cookies
        if os.path.isfile('cookies'):
            with open('cookies', 'rb') as f:
                self.session.cookies = pickle.load(f)

            # Check if they are authenticated against DeviantArt
            print('Checking cookies')
            status = self.verify()
            if status == 'GOOD':
                print('Cookies are good')
                return self.session
            elif status == 'BAD':
                # Delete the bad cookies
                os.remove('cookies')
                print('Cookies are bad')

        # Check for saved login credentials
        if os.path.isfile('credentials'):
            with open('credentials', 'r') as f:
                username = f.readline().strip()
                password = f.readline().strip()

            # Attempt to log in to DeviantArt
            print('Checking log in details')
            status = self.login(username, password)
            if status == 'GOOD':
                print('Log in details are good')
                return self.session
            elif status == 'BAD':
                # Delete the bad credentials
                os.remove('credentials')
                print('Log in details are bad')

        # If there are no saved details reqeust login credentials from the user
        print(\
            'If you want to access restricted content '\
            'please provide login detail.')
        username = raw_input('Username: ')
        password = getpass.getpass()

        # Attempt to log in to DeviantArt
        print('Checking log in details')
        status = self.login(username, password)
        if status == 'GOOD':
            print('Log in details are good')
            return self.session
        elif status == 'BAD':
            print('Log in details are bad. Continuing unauthenticated.')

        return self.session

    def newSession(self):
        """Create a new session for remote requests to DeviantArt"""

        userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) '\
                    'AppleWebKit/537.36 (KHTML, like Gecko) '\
                    'Chrome/39.0.2171.71 Safari/537.36'
        self.session                        = requests.Session()
        self.session.headers['User-Agent']  = userAgent

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

    def login(self, username, password):
        """
        Attempt to log in the current session to DeviantArt

        :param str username: DeviantArt username.
        :param str password: DeviantARt password.
        :rtype: str
        :return: If the user is able to log in to DeviantArt return 'GOOD',
            otherwise return 'BAD'.
        """
        username = username.strip()
        password = password.strip()

        # Create new/clean session
        self.newSession()

        # Check if credentials are empty
        if username == '':
            print(\
                'Your username is empty. '\
                'Continuing unauthenticated.')
            return session
        elif password == '':
            print(\
                'Your password is empty. '\
                'Continuing unauthenticated.')
            return self.session

        # Request the DeviantArt login page
        response = self.session.get(self.url, headers={'Referer': self.url})

        # Find cross-site scripting (XSS) variables requried for POST payload
        parser  = etree.HTMLParser()
        doc     = etree.parse(StringIO(response.text), parser)
        token   = doc.xpath('//*[@id="login"]/input[2]/@value')[0]
        key     = doc.xpath('//*[@id="login"]/input[3]/@value')[0]

        # Simulate an application/x-www-form-urlencoded POST request to login
        payload = {
            'ref': self.url,
            'username': username,
            'password': password,
            'remember_me': '1',
            'validate_token': token,
            'validate_key': key
        }
        self.session.post(self.url, data=payload, headers={'Referer': self.url})

        # Check log in details
        status = self.verify()
        if status == 'GOOD':
            # Write cookies to file for future re-use
            with open('cookies', 'w+b') as f:
                pickle.dump(self.session.cookies, f)
            # Write credentials to file for future re-use
            with open('credentials', 'w+b') as f:
                f.write(username)
                f.write('\n')
                f.write(password)
                f.write('\n')

        return status
