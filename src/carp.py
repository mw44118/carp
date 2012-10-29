# vim: set expandtab ts=4 sw=4 filetype=python:

import abc
import argparse
import collections
import logging
import os
import shutil

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

class CarpLister(object):

    @staticmethod
    def find_carpdir():

        for d in walkup():

            if 'carpdir' in os.listdir(d):
                return os.path.join(d, 'carpdir')

    def set_up_args(self):

        ap = argparse.ArgumentParser(
            description='List available templates')

        ap.add_argument('--carpdir',
            help='Use this as the carp directory')

        return ap.parse_args()


    @classmethod
    def list_templates(cls):

        self = cls()

        args = self.set_up_args()

        carpdir = args.carpdir or self.find_carpdir()

        if not carpdir:
            print("no carpdir found!")
            return

        else:

            for tmpl in os.listdir(carpdir):

                print('{0}'.format(os.path.basename(tmpl)))


class CarpAdder(object):

    def set_up_args(self):

        ap = argparse.ArgumentParser(
            description='Add a template')

        ap.add_argument('--carpdir',
            help='Use this as the carp directory')

        ap.add_argument('file_to_add',
            help='This is the file to store')

        return ap.parse_args()

    @classmethod
    def add_template(cls):

        self = cls()

        args = self.set_up_args()
        carpdir = args.carpdir or self.find_carpdir()

        shutil.copyfile(args.file_to_add, carpdir)


class CarpRenderer(object):

    def set_up_args(self):

        ap = argparse.ArgumentParser(
            description='Render a template')

        ap.add_argument('--carpdir',
            help='Use this as the carp directory')

        ap.add_argument('template',
            help='This is the template to render')

        ap.add_argument('-D', '--define', nargs="+", metavar="N")

        return ap.parse_args()

    @classmethod
    def render(cls):

        self = cls()

        args = self.set_up_args()

        defined_values = dict([s.split('=') for s in args.define])

        j = jinja2.Template(args.carpfile.read())

        print(j.render(**defined_values))
