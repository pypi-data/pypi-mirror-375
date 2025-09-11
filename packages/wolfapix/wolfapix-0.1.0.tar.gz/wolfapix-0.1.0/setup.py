from setuptools import setup, find_packages

setup(
    name='wolfapix',
    version='0.1.0',
    description='Python async port of wolf.js',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'websockets',
        'PyYAML',
    ],
    python_requires='>=3.7',
)
