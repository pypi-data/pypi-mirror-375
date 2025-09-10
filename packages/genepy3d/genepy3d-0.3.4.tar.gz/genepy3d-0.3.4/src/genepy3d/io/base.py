from requests.auth import AuthBase

class CatmaidApiTokenAuth(AuthBase):
    """Attaches HTTP X-Authorization Token headers to the given Request.
    
    This class is used for Catmaid server authentication.
    
    Attributes:
        token (str): authentication string.
    
    """
    
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['X-Authorization'] = 'Token {}'.format(self.token)
        return r