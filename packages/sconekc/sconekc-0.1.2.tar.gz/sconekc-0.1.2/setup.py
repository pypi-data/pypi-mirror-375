# Copyright 2025 Scontain GmbH
# 
# Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files (the 
# “Software”), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to 
# permit persons to whom the Software is furnished to do so, subject to 
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='sconekc',
    version='0.1.2',
    author='Scontain GmbH, Germany',
    license='The MIT License',
    find_packages=find_packages(),
    install_requires=[
        'cryptography>=3.4.8',
        'requests>=2.25.1',
        'flask>=3.1.1'
    ],
    description='SCONEKC Module for Keycloak interaction',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['keycloak', 'scone', 'confidential', 'confidential computing', 'enclave'],
)
