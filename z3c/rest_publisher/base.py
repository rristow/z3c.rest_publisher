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


from zope.publisher.browser import BrowserPage
from zope.browserpage import ViewPageTemplateFile


class RestDoc(BrowserPage):

    def __init__(self, rest_obj_root, request):
        self.context = rest_obj_root
        self.request = request

    def generate_doc_verb(self, name, url, obj):
        print "====generate_doc_verb - name:", name, "url:", url, "obj:", obj
        ret = []
        if name != '*':
            url = "%s/%s" % (url, name)

        for func_name in dir(obj):
            for allowed_method in obj.allowed_methods:
                func = None
                if func_name == allowed_method:
                    doc_name = name
                    verb = allowed_method
                    if name == '*':
                        doc_url = "%s/[ID]" % url
                    else:
                        doc_url = url
                    func = getattr(obj, func_name)
                elif func_name.startswith("%s_" % allowed_method):
                    verb, doc_name = func_name.split("_", 1)
                    func = getattr(obj, func_name)
                    doc_url = "%s/%s" % (url, doc_name)
                if func:
                    doc = [obj.__doc__] + func.__doc__.split("\n")
                    doc = {'name': doc_name,
                           'id': "%s_%s" % (verb, url),
                           'http_method': verb.upper(),
                           'url': doc_url,
                           'show_link': verb == 'get' and name != '*',
                           'doc': doc}
                    print "  ", doc
                    ret.append(doc)

        for child_name, child in obj.content.items():
            ret += self.generate_doc_verb(child_name, url=url, obj=child)
        return ret

    def __call__(self, *args, **kwargs):
        data = self.generate_doc_verb(self.context.name, url="",
                                      obj=self.context)
        return ViewPageTemplateFile('doc.pt')(instance=self, data=data)


class APIBase(object):
    """ Base class for REST Objects """
    name = ""
    adapts(interfaces.IREST, IBrowserRequest)
    implements(IBrowserPublisher)

    allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
    template_doc = "doc.html"
    doc_endpoint = 'help'

    # Add here another APIBase 'class' to traverse. e.g. {'members': APIClassMembers}
    content = {}

    def __init__(self, context, request, name):
        self.name = name
        self.context = context
        self.request = request

    def check_authentication(self, name):
        """  Overwrite this method to add a custom authentication for your REST API """
        return True

    def browserDefault(self, request):
        return self, ()

    def __call__(self):
        method = self.request['REQUEST_METHOD'].lower()
        if method not in self.allowed_methods:
            self.request.response.setStatus(403)
            return "The HTTP-method '%s' is not supported" % method

        if self.check_authentication(method):
            self.request.response.setStatus(403)
            return "Access denied"

        # Search for a method with the sme name as REQUEST_METHOD and call it
        if hasattr(self, method):
            res = getattr(self, method)()
            return json.dumps(res)
        else:
            self.request.response.setStatus(500)
            return "The HTTP-method '%s' is not supported here" % method

    def publishTraverse(self, request, name):
        if not self.check_authentication(name):
            raise TraversalException("Access denied")

        # Check call to documentation
        if name == self.doc_endpoint:
            return RestDoc(self, self.request)

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
