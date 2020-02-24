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
    url='https://github.com/kblaj41/cloud_wrapper',
    license=license,
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
          'boto3',
          'botocore',
          'jsonmerge',
          'python-dateutil',
          'numpyencoder',
      ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
  ]
)
