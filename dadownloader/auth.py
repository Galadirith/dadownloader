import  requests
import  pickle
import  os
import  getpass
from    StringIO    import StringIO
from    lxml        import etree


def auth():
    """
    Attempt to generate an authenticated session for DeviantArt.

    auth() will check for a 'cookies' file in the calling directory. If no such
    file exists prompt the user for DeviantArt login credentials. An
    authenticated session is required to access several types of content on
    DeviantArt, such as mature deviations, and those flaged by their creator to
    only allow access from DeviantArt members.

    :rtype: requests.Session
    :return:
        If a 'cookies' file exists in the calling directory, auth will assume
        this is a pickle dump of a valid cookiejar and return an object with
        cookies set from the 'cookies' file regardless of the parameters passed.

        If valid credentials are provided, the returned object contains
        authenticated cookies.

        If no or invalid credentials are provided, the returned object will
        contain no authenticated cookies.
    """
    url         =   'https://www.deviantart.com/users/login'
    userAgent   =   'Mozilla/5.0 (Windows NT 6.1; WOW64) '\
                    'AppleWebKit/537.36 (KHTML, like Gecko) '\
                    'Chrome/39.0.2171.71 Safari/537.36'
    session                         = requests.Session()
    session.headers['User-Agent']   = userAgent

    # Assume authenticated cookies exist if 'cookies' file exists
    if os.path.isfile('cookies'):
        with open('cookies', 'rb') as f:
            session.cookies = pickle.load(f)
        return session

    print('To access restricted content please provide login credentials')
    username = raw_input('Username: ')
    password = getpass.getpass()

    if username == '' or password == '':
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

    return session
