# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup

import strictdoc

package_data = {}

data_files = []
start_point = os.path.join("strictdoc", "export", "html")
for root, dirs, files in os.walk(start_point):
    root_files = []
    for file in files:
        if file.endswith(".py") or file.endswith(".pyc"):
            continue
        root_files.append(os.path.join(root, file))
    if len(root_files) > 0:
        data_files.append((root, root_files))

with open("requirements.txt") as fp:
    REQUIREMENTS = fp.read()

with open("requirements.development.txt") as fp:
    REQUIREMENTS_DEVELOPMENT = {"development": fp.read()}

REQUIREMENTS_SETUP = [
    "wheel",
]


extras_require = {
    ':python_version >= "3.6" and python_version < "3.7"': [
        "dataclasses>=0.7,<0.8"
    ]
}

entry_points = {"console_scripts": ["strictdoc = strictdoc.cli.main:main"]}

setup_kwargs = {
    "name": "strictdoc",
    "version": strictdoc.__version__,
    "description": "Software for writing technical requirements and specifications.",
    "long_description": "Software for writing technical requirements and specifications.",
    "author": "Stanislav Pankevich",
    "author_email": "s.pankevich@gmail.com",
    "maintainer": "Stanislav Pankevich",
    "maintainer_email": "s.pankevich@gmail.com",
    "url": "https://github.com/stanislaw/strictdoc",
    "packages": find_packages(
        where=".",
        exclude=[
            "tests*",
        ],
    ),
    "package_data": package_data,
    # 'package_dir': {"": "strictdoc"},
    "data_files": data_files,
    "install_requires": REQUIREMENTS,
    "extras_require": REQUIREMENTS_DEVELOPMENT,
    "setup_requires": REQUIREMENTS_SETUP,
    "entry_points": entry_points,
    "python_requires": ">=3.6.2,<4.0.0",
}


setup(**setup_kwargs)