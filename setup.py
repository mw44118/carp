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
        'jinja2',
        'PyYAML',
    ],

    entry_points={
        "console_scripts": [
            'carp = carp:carp',
            'carp-list = carp:list_templates'
        ]},
)
