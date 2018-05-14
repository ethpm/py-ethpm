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
        'pytest>=3.2.1',
        'tox>=1.8.0',
    ],
    'lint': [
        'flake8==3.5.0',
        'mypy<0.600',
    ],
    'doc': [
        'Sphinx>=1.5.5,<2.0.0',
        'sphinx_rtd_theme>=0.1.9',
    ],
    'dev': [
        'pytest-watch>=4.1.0,<5',
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
    version='0.1.0',
    description="""Python abstraction for ERC190 packages.""",
    long_description_markdown_filename='README.md',
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/ethpm/py-ethpm',
    include_package_data=True,
    install_requires=[
        'cytoolz==0.9.0',
        'eth-keys==0.2.0b3',
        'eth-tester==0.1.0b24',
        'eth-utils==1.0.2',
        'jsonschema==2.6.0',
        'py-evm==0.2.0a11',
        'rlp==0.6.0',
        'web3==4.2.0',
    ],
    setup_requires=['setuptools-markdown'],
    python_requires='>=3.5, <4',
    extras_require=extras_require,
    py_modules=['ethpm'],
    license='MIT',
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
