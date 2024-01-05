#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse CUPS Internet Printing Protocol (IPP) files."""

import argparse
import logging
import sys

from dtformats import cups_ipp
from dtformats import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from CUPS IPP files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the CUPS IPP file.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  output_writer = output_writers.StdoutWriter()

  try:
    output_writer.Open()
  except IOError as exception:
    print(f'Unable to open output writer with error: {exception!s}')
    print('')
    return False

  cups_ipp_file = cups_ipp.CupsIppFile(
      debug=options.debug, output_writer=output_writer)

  cups_ipp_file.Open(options.source)

  print('CUPS Internet Printing Protocol (IPP) information:')
  print('')

  cups_ipp_file.Close()

  output_writer.WriteText('\n')
  output_writer.Close()

  return True


if __name__ == '__main__':
  if Main():
    sys.exit(0)
  else:
    sys.exit(1)
