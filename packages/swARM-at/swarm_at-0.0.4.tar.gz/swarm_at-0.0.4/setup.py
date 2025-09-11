import os
from setuptools import setup, find_packages

setup(
    name='swARM_at',
    version='0.0.4',
    packages=find_packages(),
    install_requires=[
        'pyserial>=3.4'
    ],
    author='Joffrey Herard',
    author_email='joffrey.herard@gmail.com',
    description='Une bibliothèque pour la communication avec des modules LoRa via des commandes AT.',
    long_description=open('README.md').read()+'\n\n\n'+open('CHANGELOG.md').read(),
    long_description_content_type='text/markdown',
    keywords='LoRa AT command RAK3172',
    url='https://gitlab.com/Apocalypzer/swarm_at',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: MIT License',
    ]
)