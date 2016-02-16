from setuptools import setup, find_packages

setup(
    name = 'vclock',
    version = '0.1',
    author = 'Ethan Frey',
    author_email = 'ethanfrey@noreply.github.com',
    url = 'https://github.com/ethanfrey/vclock',
    license = 'BSD',
    description = 'Python implementation of serializable vector clocks, designed for key-value stores',
    long_description = open('README.rst').read(),

    classifiers = [
        'Development Status :: 3- Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages = find_packages(),

    install_requires=[
        'future>=0.15.0'
    ],
)

