from setuptools import find_packages, setup

setup(

    name='carp',

    version='0.0.1',

    packages=find_packages('src'),

    include_package_data=True,

    package_dir={'': 'src'},

    install_requires=[
        'jinja2',
        'PyYAML',
    ],

    entry_points={
        "console_scripts": [

            'carp-list = carp:CarpLister.list_templates',
            'carp-add = carp:CarpAdder.add_template',
            'carp-render = carp.CarpRenderer.render',

        ]},
)
