#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 29 16:18:50 2023

@author: akshayghosh
"""

from setuptools import setup

setup(
    name='hockey_kde_2022_23',
    version='0.0.1',
    description='Module for NHL KDE analysis of the 2022-23 season',
    author='Akshay Ghosh',
    packages=['hockey_variability'],
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'requests',
        'scikit-learn',
        'hockey_rink',
        'datetime',
    ],
)
