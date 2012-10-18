from setuptools import find_packages, setup

setup(

    name='carp',

    version='0.0.1',

    packages=find_packages('src'),

    include_package_data=True,

    package_dir={'': 'src'},

    # All of these are available on pypi, but really, it is probably
    # smart to have local copies.
    install_requires=[
        'clepy',
        'coverage',
        'IPython',
        'jinja2',
    ],

    scripts=[
        # 'src/ddsreminder/shell-scripts/run-dev-webapp',
        # 'src/ddsreminder/shell-scripts/run-scratch-webapp',
        # 'src/ddsreminder/shell-scripts/run-prod-webapp',
    ],

)
