#  Created by Martin Strohalm

from setuptools import setup, find_packages

# get version
version = "0.10.1"

# get description
with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

# include additional files
package_data = {}

# set classifiers
classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3 :: Only',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Topic :: Scientific/Engineering',
    'Intended Audience :: Science/Research']

# main setup
setup(
    name = 'msread',
    version = version,
    description = 'Mass spectrometry data reading library',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/xxao/msread',
    author = 'Martin Strohalm',
    author_email = '',
    license = 'MIT',
    packages = find_packages(),
    package_data = package_data,
    classifiers = classifiers,
    install_requires = ['numpy'],
    zip_safe = False)
