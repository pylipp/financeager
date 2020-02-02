"""
financeager - command line tool for organizing finances
Copyright (C) 2017 Philipp Metzner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import find_packages, setup

with open("README.md") as readme:
    long_description = readme.read()

setup(
    name="financeager",
    use_scm_version=True,
    description="command line tool for organizing finances",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pylipp/financeager",
    author="Philipp Metzner",
    author_email="beth.aleph@yahoo.de",
    license="GPLv3",
    keywords="commandline finances",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.5",
        "Topic :: Office/Business :: Financial",
        "Topic :: Database",
        "Topic :: Utilities",
    ],
    packages=find_packages(exclude=["test"]),
    entry_points={"console_scripts": ["financeager = financeager.cli:main"]},
    setup_requires=[
        "setuptools_scm",
    ],
    install_requires=[
        "tinydb==3.2.1",
        "python-dateutil==2.6.0",
        "Flask==1.0.2",
        "Flask-RESTful==0.3.5",
        "requests>=2.20.0",
        "marshmallow==3.3.0",
    ],
    extras_require={
        "develop": [
            "twine>=1.11.0",
            "setuptools>=38.6.0",
            "wheel>=0.31.0",
            "coverage>=4.4.2",
            "pre-commit==1.14.4",
            "gitlint==0.12.0",
        ],
    },
)
