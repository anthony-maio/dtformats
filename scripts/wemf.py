#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Windows (Enhanced) Metafile Format (WMF and EMF) files."""

import argparse
import logging
import os
import sys

from dtformats import output_writers
from dtformats import wemf


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Windows (Enhanced) Metafile files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Windows (Enhanced) Metafile file.')

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

  with open(options.source, 'rb') as file_object:
    file_object.seek(40, os.SEEK_SET)
    file_signature = file_object.read(4)

  if file_signature == b' EMF':
    wemf_file = wemf.EMFFile(debug=options.debug, output_writer=output_writer)
  else:
    wemf_file = wemf.WMFFile(debug=options.debug, output_writer=output_writer)

  wemf_file.Open(options.source)

  output_writer.WriteText(f'{wemf_file.FILE_TYPE:s} information:')

  wemf_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if Main():
    sys.exit(0)
  else:
    sys.exit(1)
