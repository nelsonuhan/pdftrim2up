import setuptools
import pypandoc

long_description = pypandoc.convert('README.md', 'rst')

setuptools.setup(
    name='pdftrim2up',
    version='0.2',
    description='''
        A quick-and-dirty script to trim and 2-up PDF documents onto US Letter
        paper in landscape orientation.
    ''',
    long_description=long_description,
    url='https://github.com/nelsonuhan/pdftrim2up',
    author='Nelson Uhan',
    author_email='nelson@uhan.me',
    license='MIT',
    packages=['pdftrim2up'],
    install_requires=['PyPDF2'],
    entry_points={
        'console_scripts': ['pdftrim2up=pdftrim2up.pdftrim2up:main'],
    }
)
