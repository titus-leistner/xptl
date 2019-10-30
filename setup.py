#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='xptl',
    version='0.2',
    author="Titus Leistner",
    author_email='research@titus-leistner.de',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    description="Experiment Tool for Hyper Parameter Searches",
    entry_points={
        'console_scripts': [
            'xptl=xptl.cli:main',
        ],
    },
    python_requires='>=3.7',
    license="GNU General Public License v3",
    packages=find_packages(include=['xptl']),
    install_requires=[],
    setup_requires=[],
    url='https://github.com/titus-leistner/xptl',
)