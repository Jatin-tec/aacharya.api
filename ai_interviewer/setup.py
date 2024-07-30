from setuptools import setup, find_packages

setup(
    name='ai_interviewer',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'django',
        'langgraph',
        'some-llm-library',  # Replace with actual LLM library
    ],
    tests_require=[
        'pytest',
    ],
)
