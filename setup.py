from setuptools import setup, find_packages

config = {
    'name': 'isobenefit-cities',
    'description': 'generate infinite cities with isobenefit configurations.',
    'author': 'mitochevole',
    'url': 'https://github.com/mitochevole/isobenefit-cities.git',
    'packages': find_packages(),
    'version':'1.0'
}

setup(**config)
