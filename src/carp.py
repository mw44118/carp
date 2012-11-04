# vim: set expandtab ts=4 sw=4 filetype=python:

import abc
import argparse
import collections
import logging
import os
import shutil

import clepy
import jinja2
import jinja2.meta

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('carp')

class CarpScript(object):

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def find_carpdir():

        for d in clepy.walkup():

            if 'carpdir' in os.listdir(d):
                return os.path.join(d, 'carpdir')

    @abc.abstractmethod
    def set_up_args(self):
        raise NotImplementedError


class CarpLister(CarpScript):

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


class CarpAdder(CarpScript):

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


class CarpRenderer(CarpScript):

    def set_up_args(self):

        ap = argparse.ArgumentParser(
            description='Render a stored template')

        ap.add_argument('--carpdir',
            help='Use this as the carp directory')

        ap.add_argument('--define',
            action='append',
            metavar="key=value",
            help='Define a value to use in the template, like '
                'projname=foo.  Can use multiple times.')

        ap.add_argument('template',
            help='This is the template to render')

        return ap.parse_args()

    @classmethod
    def render(cls):

        self = cls()

        args = self.set_up_args()

        carpdir = args.carpdir or self.find_carpdir()

        log.debug('args.define is {0}.'.format(args.define))

        defined_values = dict([s.split('=') for s in args.define]) \
        if args.define else {}

        print(self.render_template(carpdir, args.template,
            defined_values))


    def render_template(self, carpdir, template, values):

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(carpdir),
            undefined=jinja2.StrictUndefined)

        j = env.get_template(template)

        return j.render(**values)


class CarpInfoGetter(CarpScript):

    def set_up_args(self):

        ap = argparse.ArgumentParser(
            description='Get information on a stored template')

        ap.add_argument('--carpdir',
            help='Use this as the carp directory')

        ap.add_argument('template',
            help='This is the template to get information on')

        return ap.parse_args()

    @classmethod
    def get_info(cls):

        self = cls()

        args = self.set_up_args()

        carpdir = args.carpdir or self.find_carpdir()

        print("{0} required variables\n".format(args.template))

        for var in self.get_info_on_template(
            carpdir, args.template):

            print("*  {0}".format(var))


    def get_info_on_template(self, carpdir, template_name):

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(carpdir),
            undefined=jinja2.StrictUndefined)

        text = env.loader.get_source(env, template_name)

        ast = env.parse(text)

        return jinja2.meta.find_undeclared_variables(ast)

