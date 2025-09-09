from setuptools import setup, find_packages
from pathlib import Path
import re

def get_version():
    version_file = Path("fmtool/version.py")
    content = version_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\'](.+?)["\']', content)
    if match:
        return match.group(1)
    raise RuntimeError("Cannot find __version__ in fmtool/version.py")
setup(
name='fmtool',
version=get_version(),
author='Abbas Bachari',
author_email='abbas-bachari@hotmail.com',
description='Cross-platform Python file manager',
long_description=open('README.md', encoding='utf-8').read(),
long_description_content_type='text/markdown',
packages=find_packages(),
python_requires='>=3.8',
install_requires=[],
classifiers=[
'Programming Language :: Python :: 3',
'License :: OSI Approved :: MIT License',
'Operating System :: OS Independent',
],
)