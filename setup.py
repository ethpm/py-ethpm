#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import (
    setup,
    find_packages,
)


DIR = os.path.dirname(os.path.abspath(__file__))


readme = open(os.path.join(DIR, 'README.md')).read()


setup(
    name='ethpm',
    version='0.1.0',
    description="""Python abstraction for ERC190 packages.""",
    long_description_markdown_filename='README.md',
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/pipermerriam/ethereum-erc190',
    include_package_data=True,
    install_requires=[
        "web3==4.0.0b3",
        "eth-utils==0.7.1",
        "jsonschema==2.6.0",
        "cytoolz==0.8.2",
        "eth-tester==0.1.0b4",
        "py-evm==0.2.0a7",
    ],
    setup_requires=['setuptools-markdown'],
    py_modules=['ethpm'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
