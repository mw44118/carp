from setuptools import find_packages, setup

setup(

    name='carp',

    version='0.0.3',

    description="Code templating scripts",

    author='W. Matthew Wilson',
    author_email='matt@tplus1.com',
    url='http://carp.readthedocs.org',
    license='BSD',

    packages=find_packages('src'),

    include_package_data=True,

    package_dir={'': 'src'},

    py_modules=['carp'],

    install_requires=[
        'clepy',
        'jinja2',
    ],

    entry_points={
        "console_scripts": [

            'carp-list = carp:CarpLister.list_templates',
            'carp-add = carp:CarpAdder.add_template',
            'carp-render = carp:CarpRenderer.render',
            'carp-info = carp:CarpInfoGetter.get_info',
        ]},
)
