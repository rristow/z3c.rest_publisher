import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

def test_suite():
    return unittest.TestSuite([

        # Unit tests for your API
        doctestunit.DocFileSuite(
            'README.md', package='z3c.rest_publisher',
            setUp=testing.setUp, tearDown=testing.tearDown),

        #TODO

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
