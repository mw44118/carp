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
import logging
import os

import jinja2

log = logging.getLogger('carp')

def set_up_arguments():

    ap = argparse.ArgumentParser()

    ap.add_argument('-D', '--define', nargs="+", metavar="N")

    ap.add_argument(
        'carpfile',
        type=argparse.FileType('r'))

    return ap.parse_args()

if __name__ == '__main__':

    args = set_up_arguments()

    logging.basicConfig(level=logging.DEBUG)

    defined_values = dict([s.split('=') for s in args.define])

    j = jinja2.Template(args.carpfile.read())

    print(j.render(**defined_values))

