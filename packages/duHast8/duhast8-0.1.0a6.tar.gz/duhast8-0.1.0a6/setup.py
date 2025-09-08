# setup.py is required for local installation of the duHast package through:
# ipy -m pip install -e .

from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory/"README.md").read_text()

setup(
    package_dir={"": "./src"},
    packages=find_packages('./src'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    package_data={"duHast": ["lib/*.dll"]},
    #has_ext_modules=lambda: True,
    python_requires='>=3.4',
)