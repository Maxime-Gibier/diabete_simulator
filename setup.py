from setuptools import setup, find_packages

setup(
    name='insulin_pump_simulator',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'pika',
        'sqlite3',  # Note: sqlite3 is part of the standard library
    ],
)
