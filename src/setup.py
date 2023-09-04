import os
import codecs

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

VERSION = None
with open(os.path.join(here, './common/__init__.py')) as f:
    for line in f:
        if line.startswith("VERSION"):
            VERSION = line[line.index("'") + 1: line.rindex("'")]
            break

if VERSION is None:
    print('Set VERSION first!')
    exit(1)

DESCRIPTION = 'python common toolkit'

setup(
    name='commonX',
    version=VERSION,
    description=DESCRIPTION,
    author='hect0x7',
    packages=find_packages(),
    long_description_content_type="text/markdown",
    long_description=long_description,
    requires=[
    ],
    keywords=['python', 'toolkit', 'postman'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    author_email='93357912+hect0x7@users.noreply.github.com',
    url='https://github.com/hect0x7/common',
)
