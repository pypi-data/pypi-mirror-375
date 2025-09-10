from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='investimentos-package',
    version='1.0.0',
    packages=find_packages(),
    description='Uma biblioteca para análise de investimentos',
    author='Rodrigo  Raiche',
    author_email='raicheposia@gmail.com',
    url='https://github.com/tadrianonet/investimentos',  
    license='MIT',  
    long_description=long_description,
    long_description_content_type='text/markdown'
)
