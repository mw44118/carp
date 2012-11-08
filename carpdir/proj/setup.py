from setuptools import find_packages, setup

setup(

    name='{{projname}}',

    version='0.0.1',

    description="Something awesome",

    # Replace these if you are not me.
    author='W. Matthew Wilson',
    author_email='matt@tplus1.com',

    url='http://{{projname | lower}}.readthedocs.org',

    license='BSD',

    packages=find_packages('src'),

    include_package_data=True,

    package_dir={'': 'src'},

    install_requires=[
    ],

    entry_points={
        "console_scripts": []
    },
)
