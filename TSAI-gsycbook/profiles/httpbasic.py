import base64

from django.contrib.auth import authenticate, login, logout

#############################################################################
# Based on http://www.djangosnippets.org/snippets/243/ , modified because I had some problems
# using it with django-rest-interface, so I decided to make my own based on that one
# Important: there is no way to discard the cached credentials:

#"According to RFC 2616, existing browsers retain authentication information indefinitely. HTTP does not provide a 
#method for a server to direct clients to discard these cached credentials. 
#This means that there is no effective way to "log out" without closing the browser."
#
#[extracted from wikipedia: http://en.wikipedia.org/wiki/Basic_access_authentication]

def is_valid(request):
    """ Determines if the request has a correct password and user, returns false otherwise"""

    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        logout(request)
                        return True
    return False
    

