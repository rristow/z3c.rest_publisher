z3c.rest_publisher Package Readme
=========================

Overview
--------

This product uses the ZOPE / Plone infrastructure (basically traverse) to create a ReSTfull API. The data will be
accessed through APIBase objects that will be accessible by HTTP requests.

For example, in the following request:

    curl http://localhost:8080/testapi/companies/company1

- api - It's a Zope view (inherited from APIBase) registered for Site-ROOT
- companies - It's a object inherited from APIBase include in the "api" object
- company1 - It's a object inherited from APIBase include in the "companies" object
- The default method (in this case "verb_get") from company1 will be called and return the data (json). 

Install
-------

pip install z3c.rest_publisher

Configuration
-------------

1 - First create a base class for the API. Although this is not mandatory, this is the best way to overwrite the 
existing options.

from z3c.rest_publisher.base import APIBase

```python
class MyAPIBase(APIBase):
    # False (default) is used to avoid returning the default error page (HTML).
    raise_exceptions = False
    # it is possible to inform the verb in the query-string in case you can't use http-methods.
    # e.g. If querystring_verb_name='verb', send a POST request and add something like ?verb=PATCH in the query-string.
    querystring_verb_name = "verb"
    # if True it will make this API public (It will not check the 'check_authentication' method)
    public = False
    # All methods supported by this API
    allowed_methods = ['get', 'post', 'put', 'delete', 'patch']

    #def check_authentication(self, name):
    #    Add the custom authentication here
    #    return True

    # def format_output(self, data):
    #   overwrite this method use another format (default json), like: xml, txt, etc...

```

2 - Create the API-Root
The starting point for the API is a traditional view registered in Zope ZCML. e.g.

```python
class APIRoot(MyAPIBase):

    def verb_get(self):
        """ Get data from all users """
        return {"result": "Hello world!"}
```

2.1 - And register the API-Root

```xml
  <view
    name="testapi"
    for="zope.location.interfaces.IRoot"
    type="zope.publisher.interfaces.browser.IBrowserRequest"
    provides="zope.publisher.interfaces.browser.IBrowserPublisher"
    factory=".[myclass].APIRoot"
    permission="zope.Public"
    allowed_attributes="publishTraverse browserDefault __call__"
  ></view>
```

Tests e.g.

    curl -X GET http://127.0.0.1:8080/testapi
      {"result": "Hello world!"}

4 - Add more verbs
--------------------

To add an verb in the API, include a "verb_\[method]" function in the object.
The supported verbs are by default: 'get', 'post', 'put', 'delete' and 'patch'.  

```python
class APIRoot(MyAPIBase):

    def verb_post(self):
        """ Get data from all users """
        return {"result": "You sent a POST!"}
```

Tests e.g.

    curl -X POST http://127.0.0.1:8080/testapi
      {"result": "You sent a POST!"}


3 - Add more resources (traverse)
---------------------------------

To add a child API, include a "traverse_\[name]" function in the API-Class.
All 'traverse' functions should return a class inherited from APIBase.

```python
DB =  [{"id": "book1", "title": "My first book!"}, {"id": "book2", "title": "My second book!"}]
class APIBooks(MyAPIBase):
    def verb_get(self):
        return DB

class APIRoot(MyAPIBase):
    def traverse_books(self, request, name):
        return APIBooks(context=self.context, request=request, name=name, parent_api_obj=self)
```

4 - Add access to the objects (traverse)
----------------------------------------

To access an object in the resource, include a "traverse_NAME" function in the API-Class.
All 'traverse' functions should return a class inherited from APIBase.

```python
class APIBook(MyAPIBase):
    def verb_get(self):
        return self.context

class APIBooks(MyAPIBase):
    def traverse_NAME(self, request, name):
        book = [b for b in DB if b['id'] == name]
        if book:
            return APISector(context=book[0], request=request, name=name, parent_api_obj=self)
        else:
            raise NotFound(self.context, name, request)
```

Tests e.g.

    curl -X GET http://127.0.0.1:8080/testapi/books/book2
      {"id": "book2", "title": "My second book!"}


Authentication
--------------

1 - Zope-Authentication
You can use traditional Zope systems for authentication, for example by changing permissions for the view

    permission="zope.Public"
    or
    permission="zope.ManageContent"

2 - Custom authentication

If you wish, you can include customized authentication for the API. Just overwrite the "check_authentication" method in the class.
For example, to implement basic-authentication:

```python
class MyAPIBase(APIBase):
    def check_authentication(self, name):
       user, pwd = self.request._authUserPW()
       if user == 'demo' and pwd == 'demo':
            return True
```

Tests e.g.

    curl --user demo:demo  http://localhost:8080/testapi/

Example application
-------------------

Please check "z3c.rest_publisher/example" for a complete example.
