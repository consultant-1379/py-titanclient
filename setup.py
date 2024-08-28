#!/usr/bin/env python3

from setuptools import setup, find_packages

version = "1.4.0"

deps = [
    "PyYAML",
    "requests",
    "XlsxWriter==1.1.6",
    "arpeggio==1.9.0",
    "pdoc3==0.10.0",
    "prettytable",
    "click>=8.1.7",
    "scp>=0.13.1",
    "toml==0.10.2",
    "tag-expressions==1.1.0"]

main_func = "titanclient.cli.cli:top"
scripts = list(map(lambda c: f"{c}={main_func}", ["titanclient", "tcli"]))

setup(
    name='titanclient',
    author='essxptr',
    author_email='peter.soos@ericsson.com',
    description='A Python client library to interface with TitanSim',
    url='https://gerrit.ericsson.se/plugins/gitiles/IMS_NWST_ETH/py-titanclient',
    entry_points={"console_scripts": scripts},
    version=version,
    packages=find_packages(),
    install_requires=deps)
