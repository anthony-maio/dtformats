#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Windows (Task Scheduler) job files."""

import argparse
import logging
import sys

from dtformats import job
from dtformats import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from a Windows Job file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
          'path of the Windows Job file.'))

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

  job_file = job.WindowsTaskSchedulerJobFile(
      debug=options.debug, output_writer=output_writer)
  job_file.Open(options.source)

  task_configuration = job_file.GetWindowsTaskConfiguration()

  output_writer.WriteText('Windows Task Scheduler job information:\n')

  output_writer.WriteText(
      f'\tIdentifier\t\t: {task_configuration.identifier:s}\n')
  output_writer.WriteText(
      f'\tApplication name\t: {task_configuration.application_name:s}\n')
  output_writer.WriteText(
      f'\tParameters\t\t: {task_configuration.parameters:s}\n')

  output_writer.WriteText(
      f'\tAuthor\t\t\t: {task_configuration.author:s}\n')
  output_writer.WriteText(
      f'\tComment\t\t\t: {task_configuration.comment:s}\n')

  # TODO: print more task configuration information.

  output_writer.WriteText('\n')

  job_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if Main():
    sys.exit(0)
  else:
    sys.exit(1)
