#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md').read()

setup(
    name="django-oauth2-login-client",
    version="0.8.0",
    description="OAuth2 consumer for authentication by a django-oauth-toolkit site",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django oauth oauth2 client consumer central SSO',
    author="Richard Mansfield",
    author_email="richard@dragonfly.co.nz",
    url="https://github.com/dragonfly-science/django-oauth2-login-client",
    license='GPLv3+',
    packages=find_packages(),
    install_requires=[
        'django>=1.11',
        'requests-oauthlib>=1.2.0',
    ],
    zip_safe=False,
)
