"""
Setup file for eox_core Django plugin.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup,find_packages

VERSION = "0.13.0"



setup(
    name="social-auth-pipeline-app",
    python_requires='>=3.10',
    version=VERSION,
    
    packages=find_packages(),
    include_package_data=True,
    entry_points={
       "cms.djangoapp": [
            "cms_social = fullname_plugin.apps:SocialAuthPipelineCMSConfig",
        ],
       "lms.djangoapp": [
            "lms_social = fullname_plugin.apps:SocialAuthPipelineLMSConfig",
        ],
    }
)
