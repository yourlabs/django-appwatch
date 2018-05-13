from setuptools import setup, find_packages
import os


# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='django-appwatch',
    version='0.0.0',
    description='Watch Django INSTALLED_APPS and copy files',
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://git.yourlabs.org/oss/django-appwatch',
    packages=['appwatch'],
    include_package_data=True,
    long_description=read('README.rst'),
    license='MIT',
    keywords='django',
    install_requires=[
    ],
    tests_require=['tox'],
    extras_require=dict(
        dev=[
          'django>=2.0',
        ],
    ),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
