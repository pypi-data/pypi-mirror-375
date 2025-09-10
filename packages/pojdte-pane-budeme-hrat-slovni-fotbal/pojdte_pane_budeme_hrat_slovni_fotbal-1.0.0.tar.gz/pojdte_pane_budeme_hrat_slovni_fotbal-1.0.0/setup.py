import sys
from setuptools import setup, find_packages

# get version from arguments start
#index = sys.argv.index('--version')
#sys.argv.pop(index)
#version = sys.argv.pop(index)
version = '1.0.0'

setup(
    name='pojdte-pane-budeme-hrat-slovni-fotbal',
    version=version,
    description='Potkali se u Kolína',
    long_description='''
    Jak skoupá je má  nenávist, když nedovedu střílet 
    jak skoupá je má hrdost někde na mezi
    místo jizev na duši jen fleky z rybích filet 
    a místo čáry života hovězí.
    ''',
    author='velci panove tacru',
    author_email='rozalie.bilkova@tacr.cz',
    packages=find_packages(),
    project_urls={
        'Documentation': 'https://youtu.be/QprFGNxrMj0?feature=shared'
    },
    install_requires=[
        'pojdte-pane-budeme-si-hrat',
        'pandas',
        'gspread',
        'numpy',
        'sentence-transformers',
        'nltk',
        'requests',
        'corpy',
        'unidecode'
        ]
)
