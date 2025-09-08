# setup.py
from setuptools import setup, find_packages

setup(
    name='intake-nexgddp',
    version='1.0.4',
    description='Intake plugin for NEX-GDDP-CMIP6 via OpenVisus',
    author='Aashish Panta',
    packages=find_packages(),
    include_package_data=True,  # <-- important
    package_data={
        "intake_nexgddp": ["resources/*", "resources/**/*"],  # <-- include your config
    },
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
