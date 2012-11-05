# vim: set expandtab ts=4 sw=4 filetype=python:

import argparse
import csv
import logging

from {{projname}} import configwrapper

log = logging.getLogger({{projname}})

def set_up_arguments():

    ap = argparse.ArgumentParser()

    ap.add_argument('--limit', help='Only process this many rows')

    ap.add_argument('--dry-run', action='store_true',
        help='Do not really save anything to the database')

    ap.add_argument('config_file_name', help='Use this config')

    ap.add_argument('path_to_csv',
        help='This is the CSV to load into the database')

    return ap

def process_row(pgconn, row):

    """
    This is the meat.
    """

if __name__ == '__main__':

    ap = set_up_arguments()

    args = ap.parse_args()

    cw = configwrapper.ConfigWrapper.load_config(ags.config_file_name)

    cw.configure_logging()

    pgconn = cw.get_postgresql_connection()

    cr = csv.DictReader(open(args.path_to_csv))

    for i, row in enumerate(cr):

        if args.limit and i >= args.limit:
            log.info("Limit reached ({0} rows)".format(args.limit))
            break

        else:
            process_row(pgconn, row)

    if args.dry_run:
        log.info("DRY RUN: nothing saved")

    else:
        pgconn.commit()

    log.info("All done!")




