import datetime
import json
import logging

from wcore import interfaces
from zope.browserpage import ViewPageTemplateFile
from zope.component import adapts, queryMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserPage
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import TraversalException
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher

logger = logging.getLogger(__name__)


class APIBase(object):
    """ Base class for REST Objects """
    adapts(IBrowserRequest)
    implements(IBrowserPublisher)

    # False (default) is used to avoid returning the default error page (HTML).
    raise_exceptions = False
    # it is possible to inform the verb in the query-string in case you can't use http-methods.
    # e.g. If querystring_verb_name='verb', send a POST request and add something like ?verb=PATCH in the query-string.
    querystring_verb_name = ""
    # Make this API public - It will not check the custom authentication
    public = False
    # All methods supported by this API
    allowed_methods = ['get', 'post', 'put', 'delete', 'patch']

    def __init__(self, context, request, name, parent_api_obj=None):
        self.context = context
        self.request = request
        self.name = name
        self.parent_api_obj = parent_api_obj

    def check_authentication(self, name):
        """  Overwrite this method to add a custom authentication for your REST API """
        return True

    @staticmethod
    def format_unsupported_value(value):
        """ Use this static function if there is a value that is not supported by the standard 'format_output'
        function """
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        elif isinstance(value, datetime.date):
            return value.isoformat()
        elif value is None:
            return ''
        else:
            return str(value)

    def format_output(self, data):
        """ format the output. default: json  """
        return json.dumps(data, default=self.format_unsupported_value)

    def browserDefault(self, request):
        return self, ()

    def error_verb(self, ex):
        """ Overwrite this function if you want specific action on verb errors """
        logger.error(ex, exc_info=True)
        if not self.raise_exceptions:
            self.request.response.setStatus(500)
            return "Server error (verb) - %s" % ex
        else:
            raise

    def error_traverse(self, ex, request, name):
        """ Overwrite this function if you want specific action on traverse errors """
        logger.error(ex, exc_info=True)
        raise

    def __call__(self):
        try:
            method = self.request['REQUEST_METHOD'].lower()
            if self.querystring_verb_name:
                method = self.request.get(self.querystring_verb_name, method).lower()

            if method not in self.allowed_methods:
                self.request.response.setStatus(403)
                return "The HTTP-method '%s' is not supported" % method

            if not self.public and not self.check_authentication(method):
                self.request.response.setStatus(403)
                return "Access denied"

            # Search for a method with the same name as REQUEST_METHOD and call it
            fnc = "verb_%s" % method
            if hasattr(self, fnc):
                res = getattr(self, fnc)()
                return self.format_output(res)
            else:
                self.request.response.setStatus(500)
                return "The HTTP-method '%s' is not supported here" % method
        except Exception as ex:
            return self.error_verb(ex)

    def publishTraverse(self, request, name):
        try:
            if not self.public and not self.check_authentication(name):
                raise TraversalException("Access denied")

            # Traverse 1 - Call traverse_{Name} to get one API-Object with the name {Name}
            method = self.request['REQUEST_METHOD'].lower()
            func = "traverse_{name}".format(name=name)
            if hasattr(self, func):
                obj = getattr(self, func)(request, name)
                return obj

            # Traverse 2 - Call traverse_NAME to return a child-object with the key = {name}
            func = "traverse_NAME"
            if hasattr(self, func):
                obj = getattr(self, func)(request, name)
                return obj

            # Traverse 3 - Fall back to views
            view = queryMultiAdapter((self.context, request), name=name)
            if view is not None:
                return view

            # Traverse 4 - If nothing found, this method will be called
            func = "traverse_DEFAULT"
            if hasattr(self, func):
                obj = getattr(self, func)(request, name)
                return obj
            # Return a 404 Not Found error page
            raise NotFound(self.context, name, request)
        except NotFound:
            raise
        except Exception as ex:
            return self.error_traverse(ex, request, name)
