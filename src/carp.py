# vim: set expandtab ts=4 sw=4 filetype=python:

import argparse

import jinja2

def set_up_arguments():

    ap = argparse.ArgumentParser()

    ap.add_argument('-D', '--define')
    ap.add_argument('scriptname')

    return ap.parse_args()

if __name__ == '__main__':

    args = set_up_arguments()


