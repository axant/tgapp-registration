# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires=[
    "TurboGears2 >= 2.3.1",
    "tgext.pluggable >= 0.7.1"
]

testpkgs=['WebTest >= 1.2.3',
          'nose',
          'coverage',
          'ming',
          'sqlalchemy',
          'zope.sqlalchemy',
          'repoze.who',
          'tw2.forms',
          'kajiki',
          'tgext.mailer'
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='tgapp-registration',
    version='0.9.2',
    description='Pluggable registration application for TurboGears2 with hooks for fine customization',
    long_description=README,
    author='Alessandro Molina',
    author_email='alessandro.molina@axant.it',
    url='https://github.com/axant/tgapp-registration',
    keywords='turbogears2.application',
    setup_requires=[],
    paster_plugins=[],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=testpkgs,
    extras_require={
       # Used by CI
       'testing': testpkgs,
    },
    include_package_data=True,
    package_data={'registration': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'registration': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
            ('templates/**.xhtml', 'kajiki', None),
            ('public/**', 'ignore', None)
    ]},
    entry_points="""
    """,
    dependency_links=[
        ],
    zip_safe=False
)
