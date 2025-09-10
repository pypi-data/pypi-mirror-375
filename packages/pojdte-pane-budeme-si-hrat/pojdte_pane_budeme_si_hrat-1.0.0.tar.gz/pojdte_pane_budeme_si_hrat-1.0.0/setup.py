import sys
from setuptools import setup, find_packages

# get version from arguments start
#index = sys.argv.index('--version')
#sys.argv.pop(index)
#version = sys.argv.pop(index)
version = '1.0.0'

setup(
    name='pojdte_pane_budeme_si_hrat',
    version=version,
    description='Pojďte pane, budeme si hrát (tacrpy)',
    long_description='Co k tomu říct... Radši nic. ideálně vůbec nic. Jenom se z povzdálí dívejte a mlčte.',
    author='velci panove tacru',
    author_email='rozalie.bilkova@tacr.cz',
    packages=find_packages(),
    project_urls={
        'Documentation': 'https://youtu.be/1RulQYSl1aw?feature=shared'
    },
    install_requires=[
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
