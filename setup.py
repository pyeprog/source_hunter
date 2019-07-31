import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), 'r') as fp:
    readme = fp.read()

setup(
    name='source_hunter',
    packages=find_packages(exclude=("test",)),
    version='0.36',
    license='MIT',
    description='Tool for analysis of code dependency and calling relationship',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Waylong',
    author_email='pyeprog@foxmail.com',
    url='https://github.com/pyeprog/source-hunter',
    keywords=['source', 'dependency', 'calling', 'relationship', 'graph', 'analysis'],
    install_requires=[
        'graphviz',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': ['hunt=source_hunter.hunter:hunt']
    },
    include_package_data=True,
)
