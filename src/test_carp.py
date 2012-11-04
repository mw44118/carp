# vim: set expandtab ts=4 sw=4 filetype=python:

import os
import shutil
import tempfile
import textwrap
import unittest

import jinja2

import carp

class TestCarp(unittest.TestCase):

    def setUp(self):

        """
        Make a tree of folders and files like::

            {some temporary dir}/bogusproject/
                carpdir/
                src/bogusproject/
                    boguslib.py

        Finally, os.chdir() to::

            {temporary dir}/bogus-project/src/bogus-project/

        """

        self.tempdir = tempfile.mkdtemp()

        os.mkdir(os.path.join(self.tempdir, 'bogusproject'))
        os.mkdir(os.path.join(self.tempdir, 'bogusproject', 'carpdir'))
        os.mkdir(os.path.join(self.tempdir, 'bogusproject', 'src'))

        os.mkdir(os.path.join(
            self.tempdir, 'bogusproject', 'src', 'bogusproject'))


        boguslibfile = open(
            os.path.join(self.tempdir, 'bogusproject',
                'src', 'bogusproject', 'boguslib.py'),
            'w')

        boguslibfile.write(textwrap.dedent("""\
            # vim: set expandtab ts=4 sw=4 filetype=python:

            import logging

            log = logging.getLogger({{projname}})
            """))

        # Guarantee that it gets written out to disk.
        boguslibfile.close()

        os.chdir(os.path.join(
            self.tempdir,
            'bogusproject',
            'src',
            'bogusproject'))

    def tearDown(self):

        """
        Remove the tree of folders and files rooted at the temporary
        directory created in self.setUp().
        """

        # This may not work on windows; patches welcome!
        shutil.rmtree(self.tempdir)


    def test_everything(self):

        """
        List templates when there are none, then add a template, then
        list templates again, then render the template.
        """

        cl = carp.CarpLister()

        found_carpdir = cl.find_carpdir()

        self.assertEqual(
            found_carpdir,
            os.path.join(
                self.tempdir,
                'bogusproject',
                'carpdir'))

        found_templates = list(cl.yield_stored_templates(
            found_carpdir))

        self.assertFalse(found_templates)

        ca = carp.CarpAdder()

        ca.copy_template(
            os.path.join(
                self.tempdir, 'bogusproject', 'src', 'bogusproject',
                'boguslib.py'),
            found_carpdir)

        found_templates = list(cl.yield_stored_templates(
            found_carpdir))

        self.assertEqual(1, len(found_templates))

        # Just for fun, copy it in again, and see if that breaks
        # anything.

        ca.copy_template(
            os.path.join(
                self.tempdir, 'bogusproject', 'src', 'bogusproject',
                'boguslib.py'),
            found_carpdir)

        self.assertEqual(1, len(found_templates))

        self.assertIn('boguslib.py', found_templates)

        # Check the required variables for this template.

        ci = carp.CarpInfoGetter()

        required_variables = ci.get_info_on_template(
            found_carpdir, 'boguslib.py')

        self.assertEqual(set(['projname']), required_variables)

        # Now render the template!

        cr = carp.CarpRenderer()

        rendered_text = cr.render_template(
            found_carpdir,
            found_templates[0],
            {'projname':'bogus'})

        # Compare what carp rendered vs what we get if we render it
        # here.
        self.assertEqual(
            rendered_text.strip(),

            jinja2.Template(
                open(found_templates[0]).read()).render(
                    projname='bogus'))

if __name__ == '__main__':
    unittest.main()
