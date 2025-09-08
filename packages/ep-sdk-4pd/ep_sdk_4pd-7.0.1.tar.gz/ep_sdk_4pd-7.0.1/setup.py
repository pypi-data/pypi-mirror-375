import os

from setuptools import setup, find_packages

PACKAGE = 'ep_sdk_4pd'
NAME = 'ep_sdk_4pd'
DESCRIPTION = '4paradigm Electricity Platform Service SDK Library for Python'
AUTHOR = '4paradigm Electricity Platform SDK'
AUTHOR_EMAIL = ''
URL = 'https://gitlab.4pd.io/electricityproject/electricity-platform-sdk'
VERSION = '7.0.1'
REQUIRES = ['requests']

LONG_DESCRIPTION = ''
if os.path.exists('./README.md'):
    with open('README.md', encoding='utf-8') as fp:
        LONG_DESCRIPTION = fp.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    # license='Apache License 2.0',
    url=URL,
    keywords=['4pd_electricity_platform'],
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    platforms='any',
    install_requires=REQUIRES,
    python_requires='>=3.6',
    classifiers=[
        # 'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        # 'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
    ],
)
