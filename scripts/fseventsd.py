#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse MacOS fseventsd files."""

import argparse
import logging
import sys

from dtformats import fseventsd
from dtformats import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from MacOS fseventsd files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the MacOS fseventsd file.')

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

  log_file = fseventsd.FseventsFile(
      debug=options.debug, output_writer=output_writer)

  log_file.Open(options.source)

  print('MacOS fseventsd information:')
  print('')

  log_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if Main():
    sys.exit(0)
  else:
    sys.exit(1)
