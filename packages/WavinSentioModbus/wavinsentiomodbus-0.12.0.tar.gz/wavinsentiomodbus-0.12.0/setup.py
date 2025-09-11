import io
import os
import re

from setuptools import find_packages
from setuptools import setup

def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())

setup(
    name="WavinSentioModbus",
    url="https://github.com/wavingroup/WavinSentioModbus",
    license='MIT',

    author="Wavin T&I",
    author_email="support@wavin.com",

    description="Python API for interfacing with Wavin CCU-208",
    
    long_description=read("Readme.md"),
    long_description_content_type="text/markdown",

    packages=['WavinSentioModbus'],

    version="0.12.0",

    install_requires=['pyserial>=3.5', 'pymodbus>=3.11.2'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)