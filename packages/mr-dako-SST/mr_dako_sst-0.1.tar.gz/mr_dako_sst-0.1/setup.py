# pip install setuptools
from setuptools import setup,find_packages

setup(
    name='mr_dako_SST',
    version='0.1',
    author='Krishna Prasad ',
    author_email='kp8808711@gmail.com',
    description='This is speech to text application created by Krishna Prcleaasad'

)
packages = find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]