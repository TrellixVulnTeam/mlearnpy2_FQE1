#!/home/tommy/mypy/mypy/bin/python2
# encoding: utf8

"""
Conversion script to convert files from a previous
release version to the current version.

Usage: convert_h5file [-h|--help] [<files>...] [--save-backup] [-v|--verbose] [--release=<version>]

Options:
    <files>  List of files to be converted, can be a file pattern
    --save-backup  save backup version of file in old file format [default: False].
    --release=<version>   release version used to create the file to be converted [default: 0.0.1]
    -v, --verbose  print informative output to screen
    -h, --help     print this text
"""

import docopt
import os
import importlib
import sys

import h5py_wrapper.wrapper as h5w
import h5py_wrapper.lib as h5w_lib

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    # First get release version used to create the file to be converted
    version_stripped = args['--release'].replace('.', '')
    release_base_name = '_'.join(('h5py_wrapper', version_stripped))
    try:
        h5w_old = importlib.import_module('.'.join((release_base_name, 'wrapper')))
    except ImportError:
        h5w_lib.get_previous_version(args['--release'])
        h5w_old = importlib.import_module('.'.join((release_base_name, 'wrapper')))

    files = args['<files>'] or sys.stdin.read().splitlines()
    for fn in files:
        if args['--verbose']:
            print("Loading %s" % fn)
        d = h5w_old.load_h5(fn)

        # This step is necessary because the 0.0.1 release loads int and float types as numpy
        # datatypes, which are not supported as scalar datatypes by the 1.0 release version.
        if args['--verbose']:
            print("Checking for numpy datatypes in scalar values.")

        h5w_lib.convert_numpy_types_in_dict(d)

        if args['--save-backup']:
            if args['--verbose']:
                print("Saving backup file.")
            orig_name = os.path.splitext(fn)
            backup_name = ''.join(('_'.join((orig_name[0], version_stripped)), orig_name[1]))
            os.rename(fn, backup_name)

        if args['--verbose']:
            print("Saving file in new format.")
        h5w.save(fn, d, write_mode='w')
