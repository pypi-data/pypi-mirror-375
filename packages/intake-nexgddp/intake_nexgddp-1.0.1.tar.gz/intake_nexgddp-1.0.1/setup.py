# setup.py
from setuptools import setup, find_packages

setup(
    name='intake-nexgddp',
    version='1.0.1',
    description='Intake plugin for NEX-GDDP-CMIP6 via OpenVisus',
    author='Aashish Panta',
    packages=find_packages(),
    entry_points={
        'intake.source_plugins': [
            'nexgddp = intake_nexgddp.catalog',
        ]
    },
    install_requires=[
        'intake',
        'xarray',
        'numpy',
        'openvisus',
    ]
)
