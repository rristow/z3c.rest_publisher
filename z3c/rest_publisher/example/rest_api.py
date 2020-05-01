
from z3c.rest_publisher.base import APIBase

USERS_EXAMPLE = [
    {'id': 'id1', 'firstname': 'Alberto', 'lastname': 'Santos-Dumont', 'mail': 'alberto@airplane.com', 'admin': True},
    {'id': 'id2', 'firstname': 'Edson', 'lastname': 'Arantes do Nascimento', 'mail': 'pele@futebol.com', 'admin': False},
    {'id': 'id3', 'firstname': 'Alberto', 'lastname': 'Santos Dummont', 'mail': 'alberto@airplane.com', 'admin': True},
]

class APIMember(APIBase):
    """ /api/members/{user_id} - Access information about a specific member """

    def get(self):
        """ return the data from user """
        for user in USERS_EXAMPLE:
            if self.name == user[id]:
                return user
        self.request.response.setStatus(404)
        return {'return_code': 1, 'errors': ((1, 'Member not found!'),)}


class APIMembers(APIBase):
    """ /api/members - List information about all users
    """
    content = {'*': APIMember}

    def get(self):
        return USERS_EXAMPLE


class APIRoot(APIBase):
    """ REST - Access the API as a view
    To test it user:
    curl --user demo:demo  http://localhost:8080/api/members
    curl --user demo:demo  http://localhost:8080/api/members/id1
    """

    # register a REST-method called "members"
    content = {'members': APIMembers}

    def check_authentication(self):
        """ Authenticate requests with basic-authentication user:demo, pwd:demo """
        cred = self.request._authUserPW()
        if cred and len(cred) == 2:
            user, pwd = self.request._authUserPW()
            if user == 'demo' and pwd == 'demo':
                return True

    def get_list_admins(self):
        """ /api/list_admins - list all admin members """
        return [user for user in USERS_EXAMPLE if user['admin'] == True]

    def __init__(self, context, request):
        self.name = "api"
        self.context = context
        self.request = request
