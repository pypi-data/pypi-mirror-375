import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

testing_extras = [
    # For test site
    'django>=4.2',
    'wagtail>=7.1.1'
]

setup(
    extras_require={
        'testing': testing_extras
    },
)