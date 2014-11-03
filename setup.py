#!/usr/bin/env python
from setuptools import setup, find_packages

from oscar_sagepay import VERSION


setup(
    name='django-oscar-sagepay-direct',
    version=VERSION,
    url='https://github.com/tangentlabs/django-oscar-sagepay-direct',
    author="David Winterbottom",
    author_email="david.winterbottom@tangentlabs.co.uk",
    description="Integration with Sagepay Direct",
    long_description=open('README.rst').read(),
    license=open('LICENSE').read(),
    platforms=['linux'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    test_suite="tests",
    install_requires=[
        'requests>=1.0',
    ],
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Other/Nonlisted Topic'],
)
