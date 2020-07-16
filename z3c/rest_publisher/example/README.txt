
This is a simple application to test the API.
The data is in the DB.json file


Install
-------

To use this example API just add the configure.zcml in your application, e.g.

<configure xmlns="http://namespaces.zope.org/zope">
  <include package="z3c.rest_publisher.example" />
</configure>

TESTS
-----
To test with curl, e.g.
curl -X GET    --user demo:demo  http://127.0.0.1:9095/testapi
curl -X GET    --user demo:demo  http://127.0.0.1:9095/testapi/headquarter
curl -X GET    --user demo:demo  http://127.0.0.1:9095/testapi/companies
curl -X GET    --user demo:demo  http://127.0.0.1:9095/testapi/companies/company1
curl -X GET    --user demo:demo  http://127.0.0.1:9095/testapi/companies/company1/sectors/sector2/users
curl -X GET    --user demo:demo  http://127.0.0.1:9095/testapi/companies/company1/sectors/sector2/users/user4
curl -X POST   --user demo:demo  http://127.0.0.1:9095/testapi/companies/company1/sectors/sector2/users -d 'id=user10&firstname=ana&lastname=smith&mail=ana@mail.com'
curl -X DELETE --user demo:demo  http://127.0.0.1:9095/testapi/companies/company1/sectors/sector2/users/user3
curl -X PATCH  --user demo:demo  http://127.0.0.1:9095/testapi/companies/company1/sectors/sector2/users/user4 -d 'firstname=My New Name!'

TESTS with querystring_verb_name
--------------------------------
Be aware that some applications just send the data with POST methods.
To avoid these limitations use the POST method in combination with the 'querystring_verb_name' option.
Check the documentation for more details.
e.g.

Test "querystring_verb_name='verb'" with:

curl -X POST   --user demo:demo  http://127.0.0.1:9095/testapi/companies/company1/sectors/sector2/users/user4?verb=PATCH  -d 'firstname=My New Name!'
