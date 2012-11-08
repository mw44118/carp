# vim: set expandtab ts=4 sw=4 filetype=python:

import os
import shutil
import tempfile
import textwrap
import unittest

import jinja2

import carp

class TestCarpSingleFile(unittest.TestCase):

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

class TestCarpFolderTree(unittest.TestCase):

    """
    Copy a tree of folders and files and then render it.
    """

    def setUp(self):

        """
        Make a carpdir.

        Make a tree of files to copy in as a template.

        The tree looks like this::

            {{tempdir2}}/bogusproject/
                setup.py
                src/
                    bogusproject/
                        __init__.py

        """

        # tempdir1 holds the carpdir.
        self.tempdir1 = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.tempdir1, 'carpdir'))

        # tempdir2 holds the tree to be copied in.
        self.tempdir2 = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.tempdir2, 'bogusproject'))

        setup_file = open(
            os.path.join(
                self.tempdir2,
                'bogusproject',
                'setup.py'),
            'w')

        setup_file.write(textwrap.dedent("""\

            from setuptools import find_packages, setup

            setup(

                name='{{projname}}',

                version='0.0.1',

                packages=find_packages('src'),

                include_package_data=True,

                package_dir={'': 'src'},

                install_requires=[
                ],
            )
            """))

        setup_file.close()

        os.mkdir(os.path.join(self.tempdir2, 'bogusproject', 'src'))

        os.mkdir(os.path.join(
            self.tempdir2, 'bogusproject', 'src', 'bogusproject'))

        boguslibfile = open(
            os.path.join(self.tempdir2, 'bogusproject',
                'src', 'bogusproject', '__init__.py'),
            'w')

        boguslibfile.write(textwrap.dedent("""\
            # vim: set expandtab ts=4 sw=4 filetype=python:

            import logging

            log = logging.getLogger({{projname}})
            """))

        # Guarantee that it gets written out to disk.
        boguslibfile.close()

        # tempdir3 is where later I will render the tree.
        self.tempdir3 = tempfile.mkdtemp()

    def tearDown(self):

        """
        Clean up all the folders.
        """

        shutil.rmtree(self.tempdir1)
        shutil.rmtree(self.tempdir2)
        shutil.rmtree(self.tempdir3)

    def test_1(self):

        """
        Add the new project template.
        List templates again and verify the new project is added.

        Run carp-info on the new template and verify required
        parameters.

        Render the new template.

        Walk through the output and make sure that the template
        variables were replaced OK.

        """

        os.chdir(self.tempdir1)

        # Find the carp directory.

        cl = carp.CarpLister()

        found_carpdir = cl.find_carpdir()

        # Make sure we have no templates already stored.

        self.assertEqual(
            found_carpdir,
            os.path.join(
                self.tempdir1,
                'carpdir'))

        found_templates = list(cl.yield_stored_templates(
            found_carpdir))

        self.assertFalse(found_templates)

        # Add this template to carp.

        ca = carp.CarpAdder()

        ca.copy_template(
            os.path.join(
                self.tempdir2,
                'bogusproject'),
            found_carpdir)

        self.assertTrue(os.path.isdir(os.path.join(
            found_carpdir, 'bogusproject')))

        found_templates = list(cl.yield_stored_templates(
            found_carpdir))

        self.assertTrue(found_templates)
        self.assertIn('bogusproject', found_templates)

        # Check the required variables for this template (none).

        ci = carp.CarpInfoGetter()

        required_variables = ci.get_info_on_template(
            found_carpdir, 'bogusproject')

        self.assertEqual(list(required_variables), ['projname'])

        # Render it!

        cr = carp.CarpRenderer()

        # Verify carp blows up when you don't pass in a target
        # directory.

        with self.assertRaises(carp.TargetRequired) as ex:

            rendered_text = cr.render_template(
                found_carpdir,
                'bogusproject',
                {})

        # But it should succeed when you provide a place to render to.

        rendered_text = cr.render_template(
            found_carpdir,
            'bogusproject',
            {'projname':'BogusProject'},
            self.tempdir3)

        # Verify everything got rendered.

        self.assertTrue(os.path.isdir(os.path.join(self.tempdir3,
            'bogusproject')))

        self.assertTrue(os.path.isfile(os.path.join(self.tempdir3,
            'bogusproject', 'setup.py')))

        self.assertTrue(os.path.isdir(os.path.join(self.tempdir3,
            'bogusproject', 'src')))

        self.assertTrue(os.path.isdir(os.path.join(self.tempdir3,
            'bogusproject', 'src', 'bogusproject')))

        self.assertTrue(os.path.isfile(os.path.join(
            self.tempdir3, 'bogusproject', 'src', 'bogusproject',
            '__init__.py')))

if __name__ == '__main__':
    unittest.main()
