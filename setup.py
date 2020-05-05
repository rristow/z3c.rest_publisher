from setuptools import setup, find_packages
import os

version = '0.5'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='z3c.rest_publisher',
      version=version,
      description="This product has the base classes to implement a REST-Server using the concepts of Zope-traverser (IBrowserPublisher)",
      long_description=(
              read('README.md')
              + '\n\n' +
              read('CHANGES.txt')
      ),
      long_description_content_type='text/x-rst',
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='REST Zope IBrowserPublisher',
      author='Rodrigo Ristow',
      author_email='rodrigo@maxttor.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.app.publication',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
