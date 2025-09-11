from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '2.0.1'
DESCRIPTION = 'Time profiler'
LONG_DESCRIPTION = 'Time profiler.'

# Setting up
setup(
    name="tm_profiler",
    version=VERSION,
    author="NorchaHack (Normunds Pureklis)",
    author_email="<norchahack@gmail.com>",
    license="MIT",
    python_requires=">=2.7",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'profiler', 'time', 'time profiler'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
