# vim: set expandtab ts=4 sw=4 filetype=python:

import abc
import argparse
import collections
import logging
import os
import shutil

import clepy
import jinja2

log = logging.getLogger('carp')

class CarpLister(object):

    @staticmethod
    def find_carpdir():

        for d in clepy.walkup():

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

            for tmpl in self.yield_stored_templates(carpdir):
                print('{0}'.format(os.path.basename(tmpl)))


    def yield_stored_templates(self, carpdir):

        for tmpl in os.listdir(carpdir):
            yield(tmpl)


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

        self.copy_template(args.file_to_add, carpdir)


    def copy_template(self, file_to_add, carpdir):

        basename = os.path.basename(file_to_add)

        shutil.copyfile(
            file_to_add,
            os.path.join(
                carpdir,
                basename))


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

        print(self.render_template(args.template, defined_values))


    def render_template(self, template, values):

        j = jinja2.Template(open(template).read())

        return j.render(**values)

