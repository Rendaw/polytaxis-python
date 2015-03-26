from setuptools import setup

setup(
    name = 'polytaxis',
    version = '0.0.1',
    author = 'Rendaw',
    author_email = 'spoo@zarbosoft.com',
    url = 'https://github.com/Rendaw/polytaxis-python',
    download_url = 'https://github.com/Rendaw/polytaxis-python/tarball/v0.0.1',
    license = 'BSD',
    description = 'polytaxis reference implementation and ptmod utility',
    long_description = open('readme.md', 'r').read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
    ],
    py_modules = ['polytaxis', 'ptmod'],
    entry_points = {
        'console_scripts': [
            'ptmod = ptmod:main',
        ],
    },
)
