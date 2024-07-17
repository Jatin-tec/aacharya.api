from setuptools import setup, find_packages

setup(
    name='llm_wrapper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'google-generativeai',
        'python-dotenv'
    ],
)
