
z3c.rest_publisher Package
==========================

Overview
--------

This product registers Zope-traverses (IBrowserPublisher) to implement basic REST requests in a simpler way.
This is done by registering traversable objects (IBrowserPublisher) to represent each method or level of the REST API.
No documents or folders will be accessed directly. It is necessary to create classes for each information to be accessed by the API.

For example, in the following request:

    curl http://localhost:8080/api/members/my_user

where
 - api - It's a view (inherited from APIBase) registered for ROOT
 - members - It's a object inherited from APIBase included in "api"
 - myuser - It's a object inherited from APIBase included in "members"

Install
-------

pip install z3c.rest_publisher

Configuration
-------------

1 - API Root
The starting point for the API is a traditional view registered in Zope ZCML. e.g.

```xml
<view
name="api"
for="zope.location.interfaces.IRoot"
type="zope.publisher.interfaces.browser.IBrowserRequest"
provides="zope.publisher.interfaces.browser.IBrowserPublisher"
factory=".rest_api.APIRoot"
permission="zope.Public"
allowed_attributes="publishTraverse browserDefault __call__">
</view>
```

Authentication
--------------

1 - Zope-Authentication
You can use traditional Zope systems for authentication, for example by changing permissions for the view

    permission="zope.Public"
    or
    permission="zope.ManageContent"

2 - Custom authentication

If you wish, you can include customized authentication for the API. Just overwrite the "check_authentication" method in the class.
For example, to implement a basic authentication:

    class APIRoot(APIBase):
        def check_authentication(self):
            user, pwd = self.request._authUserPW()
            return user == 'demo' and pwd == 'demo'

To test:

    curl --user demo:demo  http://localhost:8080/api/

REST functions
--------------

There are two ways to add a REST function to the Object.

1 - REST function as a method
Include a method in the format {HTTP-Method}_{Name} (lower-case), e.g.

    class APIRoot(APIBase):
        def get_list_admins(self):
            return [{'id': '1', 'firstname': 'Alberto', 'lastname': 'Santos-Dumont'},
                    {'id': '2', 'firstname': 'Edson', 'lastname': 'Arantes do Nascimento'}]
        def put_list_admins(self):
            return self.get_list_admins()

To test:

    curl -X GET http://localhost:8080/api/list_admins
    curl -X PUT http://localhost:8080/api/list_admins

2 - Concatenated REST objects
It is possible to create a new REST object and concatenate it with the current object.
This is the equivalent implementation from the previous method.

    class APIListAdmins(APIBase):
        def get(self):
            return [{'id': 'user1', 'firstname': 'Alberto', 'lastname': 'Santos-Dumont'},
                    {'id': 'user2', 'firstname': 'Edson', 'lastname': 'Arantes do Nascimento'}]
        def put(self):
            return self.get()

    class APIRoot(APIBase):
        content = {'list_admins': APIListAdmins}

To test:

    curl -X GET http://localhost:8080/api/list_admins
    curl -X PUT http://localhost:8080/api/list_admins

2.1 - REST function for objects (catch all)
To implement a "generic" traverse to access specific database objects, use the wildcard "*".

    class APIUSer(APIBase):
        def get(self):
            if self.name == 'user1'
                return {'id': 'user1', 'firstname': 'Alberto', 'lastname': 'Santos-Dumont'}
            elif self.name == 'user2':
                return {'id': 'user2', 'firstname': 'Edson', 'lastname': 'Arantes do Nascimento'}
            else:
                self.request.response.setStatus(404)
                return "User not found"

    class APIMembers(APIBase):
        content = {'*': APIUSer}

    class APIRoot(APIBase):
        content = {'members': APIListAdmins}


Be aware that curl just send data with POST methods. This is a limitation discussed in some posts.
To test these methods with curl, use the 'querystring_verb_name' option as documented. e.g.
querystring_verb_name=verb
curl -X POST --user demo:demo  http://127.0.0.1:9095/testapi/companies/company1/sectors/sector2/users/user4?verb=PATCH  --data-raw '{"firstname": "New Name"}'

To test:

    curl -X GET http://localhost:8080/api/members/user1
    
(Check more examples in example/README.txt)  

API documentation
-----------------

The class RestDoc provide a simple built-in documentation of all REST-APi methods. 
The default url is '[API_ROOT]/help' but you can change the property 'doc_endpoint' (APIBase) if you desire.


Example
-------

Please see "z3c.rest_publisher/example" for an example.
