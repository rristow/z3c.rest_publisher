import json

from wcore import interfaces
from zope.component import adapts, queryMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import TraversalException
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher


class APIData(BrowserPage):
    """ This is an auxiliary class to return REST data. Its necessary because the traverse expects q view-like object
    returning from publishTraverse.
    """

    def __init__(self, context, request, data):
        self.context = context
        self.request = request
        self.data = data

    def __call__(self):
        return json.dumps(self.data)


class APIBase(object):
    """ Base class for REST Objects """
    name = ""
    adapts(interfaces.IREST, IBrowserRequest)
    implements(IBrowserPublisher)

    # Add here another APIBase 'class' to traverse. e.g. {'members': APIClassMembers}
    content = {}

    def __init__(self, context, request, name):
        self.name = name
        self.context = context
        self.request = request

    def check_authentication(self):
        """  Overwrite this method to add a custom authentication for your REST API """
        return True

    def browserDefault(self, request):
        return self, ()

    def __call__(self):
        if not self.check_authentication():
            self.request.response.setStatus(403)
            return "Access denied"

        # Search for a method with the sme name as REQUEST_METHOD and call it
        method = self.request['REQUEST_METHOD'].lower()
        if hasattr(self, method):
            res = getattr(self, method)()
            return json.dumps(res)
        else:
            self.request.response.setStatus(500)
            return "The HTTP-method '%s' is not supported here" % method

    def publishTraverse(self, request, name):
        if not self.check_authentication():
            raise TraversalException("Access denied")

        # Traverse 1 - Check if this class has a method with the format {HTTP-Method}_{Name}
        method = self.request['REQUEST_METHOD'].lower()
        func = "{method}_{name}".format(method=method, name=name)
        if hasattr(self, func):
            ret = getattr(self, func)()
            return APIData(self.context, self.request, ret)

        # Traverse 2 - Check if the object has "child" APIBase class registered in content
        if name in self.content:
            return self.content[name](self.context, self.request, name)

        # Traverse 3 - Check if there is a catch all (*) to access the objects
        if '*' in self.content:
            return self.content["*"](self.context, self.request, name)

        # Traverse 4 - Fall back to views
        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view

        # Return a 404 Not Found error page
        raise NotFound(self.context, name, request)
