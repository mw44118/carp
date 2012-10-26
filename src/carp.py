# vim: set expandtab ts=4 sw=4 filetype=python:

"""

Example usage::

    $ python src/carp.py \
    ./loader.py.carp \
    --define a=1 b=2 c="cats and dogs" \
    > ./loader.py

There is still plenty of work to be done, but this part seems to work
OK.

"""

import argparse
import glob
import logging
import os

import jinja2

log = logging.getLogger('carp')

def set_up_arguments():

    ap = argparse.ArgumentParser()

    ap.add_argument('-D', '--define', nargs="+", metavar="N")

    ap.add_argument(
        'template',
        type=argparse.FileType('r'))

    return ap.parse_args()

def carp():
    args = set_up_arguments()

    logging.basicConfig(level=logging.DEBUG)

    defined_values = dict([s.split('=') for s in args.define])

    j = jinja2.Template(args.carpfile.read())

    print(j.render(**defined_values))


def walkup():

    """
    Yield paths closer and closer to the to of the filesystem.
    """

    path = os.getcwd()

    at_top = False

    while not at_top:
        yield path
        parent_path = os.path.dirname(path)
        if parent_path == path:
            at_top = True
        else:
            path = parent_path


def find_carpdir():

    for d in walkup():

        if 'carpdir' in os.listdir(d):
            return os.path.join(d, 'carpdir')


def list_templates():

    carpdir = find_carpdir()

    if not carpdir:
        print("no carpdir found")
        return

    else:

        for tmpl in glob.glob('{0}/*.carp'.format(find_carpdir())):

            print('{0:20}'.format(tmpl))

