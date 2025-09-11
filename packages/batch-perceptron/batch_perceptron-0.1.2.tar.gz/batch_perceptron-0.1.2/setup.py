from setuptools import setup, find_packages

setup(
    name='batch_perceptron',
    version='0.1.2',
    author='ABDULLAH AL MAMUN',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scikit-learn'
    ],
    description='A batch perceptron implementation using numpy and scikit-learn',
    long_description=open('Readme.md').read(),
    entry_points={
        'console_scripts': [
            'batch-perceptron=batch_perceptron:Perceptron',
        ],
    },
)