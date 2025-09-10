"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path

# Import plugin's version
from retrosynthesis.constants import PLUGIN_VERSION

# Get current path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
	long_description = f.read()

# Get requirements
with open('requirements.txt') as f:
	requirements = f.read().splitlines()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
setup(
	name='scipion-chem-retrosynthesis',  # Required
	version=PLUGIN_VERSION,  # Required
	description='Scipion framework plugin for the use of retrosynthesis software tools',  # Required
	long_description=long_description,  # Optional
	url='https://github.com/scipion-chem/scipion-chem-retrosynthesis',  # Optional
	author='Martín Salinas',  # Optional
	author_email='martin.salinas@cnb.csic.es',  # Optional
	keywords='scipion retrosynthesis scipion-3.0 cheminformatics',  # Optional
	packages=find_packages(),
	install_requires=[requirements],
	entry_points={'pyworkflow.plugin': 'retrosynthesis = retrosynthesis'}#,
	#package_data={  # Optional
	#   'retrosynthesis': ['retrosynthesis_logo.png', 'protocols.conf'],
	#}
)