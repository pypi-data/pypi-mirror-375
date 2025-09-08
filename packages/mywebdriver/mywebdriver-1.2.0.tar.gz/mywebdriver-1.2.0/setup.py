import os
from setuptools import setup

version = '1.2.0'

with open("README.md", "r", encoding='utf-8') as fh:
    readme = fh.read()
    setup(
        name='mywebdriver',
        version=version,
        url='https://github.com/gabriellopesdesouza2002/mywebdriver',
        license='MIT License',
        author='Gabriel Lopes de Souza',
        long_description=readme,
        long_description_content_type="text/markdown",
        author_email='gabriellopesdesouza2002@gmail.com',
        keywords='A quick library to install your webdriver according to your browser version',
        description=u'A quick library to install your webdriver according to your browser version',
        
        packages= [
            os.path.join('mywebdriver', 'chrome'),
        ],
        
        install_requires= [
            'requests',
        ],
)
