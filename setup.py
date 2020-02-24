from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='acssaw',
    version='0.1.0',
    description='Cloud Wrapper for running Analytics',
    long_description=readme,
    author='kblaj41',
    author_email='kblaj41@gmail.com',
    url='https://pypi.org/project/cloud_wrapper/',
    license=license,
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs'))
)
