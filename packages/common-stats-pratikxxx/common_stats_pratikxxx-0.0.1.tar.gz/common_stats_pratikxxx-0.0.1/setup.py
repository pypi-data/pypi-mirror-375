from setuptools import setup, find_packages

setup(
    name='common_stats_pratikxxx',
    version='0.0.1',
    description='A simple library for basic statistical calculations',
    long_description=open('USAGE.md').read(),
    long_description_content_type='text/markdown',
    author='Pratik Chourasia',
    author_email='pratikchourasia1@email.com',
    packages=find_packages(),
    install_requires=[
        "pytest"
    ],
    license='MIT',
    python_requires='>=3.7',
)