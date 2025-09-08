"""
Setup file for eox_core Django plugin.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup

VERSION = "0.2.0"



setup(
    name="cms-jwt",
    python_requires='>=3.10',
    version=VERSION,
    
    packages=['cms_jwt_import_auth'],
    include_package_data=True,
    entry_points={
       "cms.djangoapp": [
            "cms_jwt = cms_jwt_import_auth.apps:CMSJWTImportAuthConfig",
        ],
    }
)
