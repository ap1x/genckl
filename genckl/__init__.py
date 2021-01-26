__version__ = '1.0.0'

import sys
import argparse
from . import ckl

prog = 'genckl'
usage = prog+' [options] FILE [FILE ...]'
description = 'Generate a ckl file based on STIG zip and/or xccdf file(s)'
epilog = 'Full documentation available locally via: \'man genckl\''


def run():

    # setup arg parser
    parser = argparse.ArgumentParser(
        prog=prog, usage=usage, description=description, epilog=epilog)

    parser.add_argument('-o', '--output', default=sys.stdout,
                        help='output filename, defaults to standard output', metavar='FILE')
    parser.add_argument('-r', '--run-commands', action='store_true',
                        help='enable template command execution')
    parser.add_argument('-s', '--set-hostdata', action='store_true',
                        help='set checklist host data based on localhost')

    # NEEDFIX add support for yaml templates, csv might not always be so great
    parser.add_argument('-t', '--template', action='append',
                        help='checklist template filename, can be specified multiple times', metavar='FILE')
    # parser.add_argument('--template-dir', help='NOT IMPLEMENTED', metavar='DIR')  # NEEDFIX
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s '+__version__)
    parser.add_argument('input_files', nargs='+',
                        help='xccdf filename or STIG zip filename', metavar='FILE')

    # parse args
    args = parser.parse_args()

    try:
        # convert any given zip files to open xccdfs, create list of xccdfs
        xccdfs = []
        for input_file in args.input_files:
            if input_file[-4:] == '.zip':
                xccdfs.append(ckl.openstigzip(input_file))
            else:
                xccdfs.append(input_file)

        # create checklist, import all xccdfs
        checklist = ckl.Ckl()
        for xccdf in xccdfs:
            checklist.importxccdf(ckl.Xccdf(xccdf))

        # add all templates, running commands if enabled
        if args.template:
            for template in args.template:
                checklist.addtemplate(template, args.run_commands)

        # set host data if enabled
        if args.set_hostdata:
            checklist.sethostdata()

        # write out checklist
        checklist.write(args.output)

    # ignore ctrl-c
    except KeyboardInterrupt:
        pass

    # ignore broken pipe errors when writing to stdout
    except BrokenPipeError as err:
        if args.output == sys.stdout:
            pass
        else:
            raise err
