from setuptools import setup, find_packages

setup(
    name='aether.client',
    version='0.1.0',
    description='Cliente para reportar acciones a Aether',
    author='Aether',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'requests'
    ],
)