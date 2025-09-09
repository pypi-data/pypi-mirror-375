from setuptools import find_packages, setup

from os import path
top_level_directory = path.abspath(path.dirname(__file__))
with open(path.join(top_level_directory, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

with open(path.join(top_level_directory, 'requirements.txt')) as file:
    required = file.read().splitlines()

setup(
    name='netbox-documents',
    version='0.7.4',
    description='Manage site, location, circuit and device diagrams and documents in Netbox',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jason Yates',
    author_email='me@jasonyates.co.uk',
    url='https://github.com/jasonyates/netbox-documents',
    install_requires=required,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords=['netbox', 'netbox-plugin', 'plugin'],
)
