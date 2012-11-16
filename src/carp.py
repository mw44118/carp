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

    def template_is_a_single_file(self, carpdir, template_name):

        return os.path.isfile(os.path.join(
            carpdir,
            template_name))

    def template_is_a_folder(self, carpdir, template_name):

        return os.path.isdir(os.path.join(
            carpdir,
            template_name))

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

            if os.path.isdir(os.path.join(carpdir, tmpl)) \
            and os.path.basename(tmpl) == '.svn':

                continue

            else:
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

    def copy_template(self, thing_to_add, carpdir):

        if os.path.isfile(thing_to_add):
            self.copy_single_file(thing_to_add, carpdir)

        elif os.path.isdir(thing_to_add):
            self.copy_folder(thing_to_add, carpdir)

    def copy_single_file(self, single_file, carpdir):

        basename = os.path.basename(single_file)

        shutil.copyfile(
            single_file,
            os.path.join(
                carpdir,
                basename))

    def copy_folder(self, folder, carpdir):

        basename = os.path.basename(folder)

        shutil.copytree(
            folder,
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

        ap.add_argument('target',
            help='This is the directory to copy stuff to.',
            nargs='?',
            default=None)

        return ap.parse_args()

    @classmethod
    def render(cls):

        self = cls()

        args = self.set_up_args()


        carpdir = args.carpdir or self.find_carpdir()

        defined_values = dict([s.split('=') for s in args.define]) \
        if args.define else {}

        print(self.render_template(carpdir, args.template,
            defined_values, args.target))

    def render_template(self, carpdir, template, values, target=None):

        if self.template_is_a_single_file(carpdir, template):

            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(carpdir),
                undefined=jinja2.StrictUndefined)

            j = env.get_template(template)

            return j.render(**values)

        elif self.template_is_a_folder(carpdir, template):

            if not target:

                raise TargetRequired("Provide a destination!")

            else:
                return self.render_folder(carpdir, template, values, target)


    def render_folder(self, carpdir, template, values, target):

        for dirpath, dirnames, filenames \
        in os.walk(os.path.join(os.path.join(carpdir, template))):

            parts = dirpath.partition(carpdir)

            stripped_dirpath = parts[-1].lstrip('/')

            target_dirpath = os.path.join(target, stripped_dirpath)

            rendered_target_dirpath = jinja2.Template(target_dirpath).render(**values)

            os.mkdir(rendered_target_dirpath)

            for filename in filenames:

                rendered_text = self.render_template(
                    dirpath,
                    filename,
                    values)

                rendered_filename = jinja2.Template(filename).render(**values)

                with open(os.path.join(
                    rendered_target_dirpath, rendered_filename), 'w') as f:

                    f.write(rendered_text)

        return target


class CarpInfoGetter(CarpScript):

    def set_up_args(self):

        ap = argparse.ArgumentParser(
            description='Get information on a stored template')

        ap.add_argument('--log-level', default='ERROR',
            choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])

        ap.add_argument('--carpdir',
            help='Use this as the carp directory')

        ap.add_argument('template',
            help='This is the template to get information on')

        return ap.parse_args()


    @classmethod
    def get_info(cls):

        self = cls()

        args = self.set_up_args()

        logging.basicConfig(level=args.log_level)

        carpdir = args.carpdir or self.find_carpdir()

        required_vars = self.get_info_on_template(carpdir,
            args.template)

        if not required_vars:

            print("{0} doesn't need any variables\n".format(
                args.template))

        else:

            print("{0} required variables\n".format(args.template))

            for var in required_vars:

                print("*  {0}".format(var))


    def get_info_on_template(self, carpdir, template_name):

        if self.template_is_a_single_file(carpdir, template_name):
            return self.get_info_on_single_file(carpdir, template_name)

        elif self.template_is_a_folder(carpdir, template_name):
            return self.get_info_on_folder(carpdir, template_name)

    def get_info_on_single_file(self, carpdir, template_name):

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(carpdir),
            undefined=jinja2.StrictUndefined)

        text = env.loader.get_source(env, template_name)

        ast = env.parse(text)

        return jinja2.meta.find_undeclared_variables(ast)


    def get_info_on_folder(self, carpdir, template_name):

        required_variables = set([])

        for dirpath, dirnames, filenames \
        in os.walk(os.path.join(carpdir, template_name)):

            for f in filenames:

                for var in self.get_required_variables_from_file_name(carpdir, f):
                    required_variables.add(var)

                for var in self.get_info_on_single_file(dirpath, f):
                    required_variables.add(var)

        return required_variables

    def get_required_variables_from_file_name(self, carpdir, file_name):

        env = jinja2.Environment()
        ast = env.parse(file_name)
        return jinja2.meta.find_undeclared_variables(ast)

class TargetRequired(ValueError):

    """
    You can not render a directory template without specifying where it
    goes.
    """
