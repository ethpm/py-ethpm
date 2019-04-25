#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import (
    setup,
    find_packages,
)


DIR = os.path.dirname(os.path.abspath(__file__))


readme = open(os.path.join(DIR, 'README.md')).read()

extras_require={
    'test': [
        'pytest>=3.2.1,<4',
        'pytest-ethereum>=0.1.3a.6,<1',
        'tox>=1.8.0,<2',
    ],
    'lint': [
        'black>=18.6b4,<19',
        'isort>=4.2.15,<5',   
        'flake8>=3.5.0,<4',
        'mypy<0.600',
    ],
    'doc': [
        'Sphinx>=1.5.5,<2',
        'sphinx_rtd_theme>=0.1.9,<2',
    ],
    'dev': [
        'bumpversion>=0.5.3,<1',
        'ipython>=7.2.0,<8',
        'pytest-watch>=4.1.0,<5',
        'twine',
        'wheel',
    ],
}

extras_require['dev'] = (
    extras_require['dev']
    + extras_require['test']
    + extras_require['lint']
    + extras_require['doc']
)

setup(
    name='ethpm',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='0.1.4-alpha.15',
    description="""Python abstraction for ERC190 packages.""",
    long_description_markdown_filename='README.md',
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/ethpm/py-ethpm',
    include_package_data=True,
    install_requires=[
        'eth-utils>=1.4.1,<2',
        'ipfsapi>=0.4.3,<1',
        'jsonschema>=2.6.0,<3',
        'protobuf>=3.0.0,<4',
        'rlp>=1.0.1,<2',
        'web3[tester]>=5.0.0a3,<6',
    ],
    setup_requires=['setuptools-markdown'],
    python_requires='>=3.6, <4',
    extras_require=extras_require,
    py_modules=['ethpm'],
    license='MIT',
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
