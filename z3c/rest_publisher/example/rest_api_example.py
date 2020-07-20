import json
import os
from z3c.rest_publisher.base import APIBase
from zope.publisher.interfaces import NotFound

# Read the DATA from file
f = open(os.path.join(os.path.dirname(__file__), "DB.json"))
DB = json.load(f)[0]


# Example with a object
class Headquarter(object):
    name = "The companie Group"
    city = "Neverland"
    state = "SC"
    mail = "info@thecompnia.com"


headquarter = Headquarter()


class SecureAPIBase(APIBase):
    """ A API Base class with custom authentication """
    querystring_verb_name = "verb"

    def check_authentication(self, name):
        """ Authenticate requests with basic-authentication user:demo, pwd:demo """
        return True
        # TODO
        cred = self.request._authUserPW()
        if cred and len(cred) == 2:
            user, pwd = self.request._authUserPW()
            if user == 'demo' and pwd == 'demo':
                return True


class APIUser(SecureAPIBase):
    """ /api/companies/IdX/sectors/IdY/users/IdZ - API for user IdZ in sector IdY in the company IdX """

    def verb_get(self):
        """ List details about this user """
        user = self.context
        return dict([(k, v) for (k, v) in user.items() if k in ["id", "firstname", "lastname", "mail", "admin"]])

    def verb_delete(self):
        """ Delete the user """
        user = self.context
        users_api = self.parent_api_obj
        users = users_api.context
        users.remove(user)
        return "user removed"

    def verb_patch(self):
        """ Update some attributes from user """
        user = self.context
        import pdb;
        pdb.set_trace()
        for k, v in self.request.form.items():
            user[k] = v
        return self.verb_get()

    def verb_post(self):
        """ Update all attributes from user """
        return self.verb_patch()


class APIUsers(SecureAPIBase):
    """ /api/companies/IdX/sectors/IdY/users - API for all users in sector IdY in the company IdX """

    def traverse_NAME(self, request, name):
        """ search for a user with id = name and return the API for the user object  """
        users = self.context
        user = [s for s in users if s['id'] == name]
        if user:
            return APIUser(context=user[0], request=request, name=name, parent_api_obj=self)
        else:
            raise NotFound(self.context, name, request)

    def verb_get(self):
        """ Get data from all users """
        users = self.context
        ret = []
        for u in users:
            ret.append({"id": u["id"], "firstname": u["firstname"], "admin": u["admin"]})
        return ret

    def verb_post(self):
        """ Add a new user """
        data = self.request.form
        users = self.context
        data["admin"] = data.get("admin", "FALSE").upper() == "TRUE"
        users.append(data)
        return self.verb_get()


class APISector(SecureAPIBase):
    """ /api/companies/IdX/sectors/IdY - API for sector IdY in the company IdX
    """

    def traverse_users(self, request, name):
        """ return the API for members objects  """
        sector = self.context
        return APIUsers(context=sector["users"], request=request, name=name, parent_api_obj=self)

    def verb_get(self):
        """ List details about this sector """
        sector = self.context
        return dict([(k, v) for (k, v) in sector.items() if k in ["id", "title"]])


class APISectors(SecureAPIBase):
    """ /api/companies/IdX/sectors/IdY - API for all sectors in the company IdX
    """

    def traverse_NAME(self, request, name):
        """ search for a sector with id = name and return the API for the sector object  """
        sectors = self.context
        sector = [s for s in sectors if s['id'] == name]
        if sector:
            return APISector(context=sector[0], request=request, name=name, parent_api_obj=self)
        else:
            raise NotFound(self.context, name, request)

    def verb_get(self):
        """ Get data from all sectors """
        sectors = self.context
        ret = []
        for c in sectors:
            ret.append({"id": c["id"], "title": c["title"], "users": [s["id"] for s in c["users"]]})
        return ret


class APICompany(SecureAPIBase):
    """ /api/companies/IdX - API for the company IdX
    """

    def traverse_sectors(self, request, name):
        """ return the API for sectors  """
        company = self.context
        return APISectors(context=company["sectors"], request=request, name=name, parent_api_obj=self)

    def verb_get(self):
        """ List details about this company """
        company = self.context
        return dict([(k, v) for (k, v) in company.items() if k in ["id", "title", "telephone", "mail"]])


class APICompanies(SecureAPIBase):
    """ /api/companies/ - API for all companies
    """

    def traverse_NAME(self, request, name):
        """ search for a company with id = name and return the API for the company object  """
        dbroot = self.context
        company = [c for c in dbroot['companies'] if c['id'] == name]
        if company:
            return APICompany(context=company[0], request=request, name=name, parent_api_obj=self)
        else:
            raise NotFound(self.context, name, request)

    def verb_get(self):
        """ Get data from all companies """
        dbroot = self.context
        ret = []
        for c in dbroot['companies']:
            ret.append({"id": c["id"], "title": c["title"], "sectors": [s["id"] for s in c["sectors"]]})
        return ret


class APIHeadquarter(SecureAPIBase):
    """ /api/headquarter - API for headquarter object
    """

    def verb_get(self):
        """ Get data from object headquarter """
        headquarter_obj = self.context
        ret = {}
        for obj_attr in ['name', 'city', 'state', 'mail']:
            ret[obj_attr] = getattr(headquarter_obj, obj_attr, "[Not_Found]")
        return ret


class APIRoot(SecureAPIBase):
    """ REST - Access the API as a view
    Check the README.txt for some examples how to test with curl, e.g.
    curl -X GET --user demo:demo  http://localhost:8080/api/companies
    """
    public = True

    def traverse_headquarter(self, request, name):
        """
        Return information from headquarter
        :return: APIHeadquarter
        """
        return APIHeadquarter(context=headquarter, request=request, name=name, parent_api_obj=self)

    def traverse_companies(self, request, name):
        return APICompanies(context=DB, request=request, name=name, parent_api_obj=self)

    def __init__(self, context, request):
        self.name = "testapi"
        self.context = context
        self.request = request
