from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='cloud_wrapper',
    version='0.2.2',
    description='Cloud Wrapper for running Analytics',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='kblaj41',
    author_email='kblaj41@gmail.com',
    url='https://github.com/kblaj41/cloud_wrapper',
    license="MIT License",
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
          'boto3',
          'botocore',
          'jsonmerge',
          'python-dateutil',
          'numpyencoder',
      ],
    entry_points={
        "console_scripts": [
            "realpython=cloud_wrapper.__main__:main",
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
