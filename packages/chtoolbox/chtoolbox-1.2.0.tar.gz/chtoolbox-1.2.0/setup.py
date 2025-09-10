"""MIT License

Copyright (c) 2025 Christian Hågenvik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the requirements from the requirements.txt file
requirements_path = Path(__file__).parent / 'requirements.txt'
with requirements_path.open() as requirements_file:
    requirements = requirements_file.read().splitlines()

# Read the contents of the README file
readme_path = Path(__file__).parent / 'README.md'
with readme_path.open() as readme_file:
    long_description = readme_file.read()

setup(
    name='chtoolbox',
    version='1.2.0',
    packages=find_packages(),
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chagenvik/chtoolbox'
)

