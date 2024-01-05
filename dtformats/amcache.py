# -*- coding: utf-8 -*-
"""Windows AMCache (AMCache.hve) files."""

import pyregf

from dtformats import data_format
from dtformats import errors


class WindowsAMCacheFile(data_format.BinaryDataFile):
  """Windows AMCache (AMCache.hve) file."""

  _APPLICATION_KEY_DESCRIPTIONS = {
      'ProgramId': 'Program identifier',
      'ProgramInstanceId': 'Program instance identifier'}

  _APPLICATION_FILE_KEY_DESCRIPTIONS = {}

  _FILE_REFERENCE_KEY_DESCRIPTIONS = {
      '0': 'Product name',
      '1': 'Company name',
      '3': 'Language code',
      '5': 'File version',
      '6': 'File size',
      '7': 'PE/COFF image size',
      '9': 'PE/COFF checksum',
      'c': 'File description',
      'd': 'PE/COFF image version',
      'f': 'PE/COFF compilation time',
      '11': 'File modification time',
      '12': 'File creation time',
      '15': 'Path',
      '100': 'Program identifier',
      '101': 'SHA-1'}

  _PROGRAM_KEY_DESCRIPTIONS = {
      '0': 'Name',
      '1': 'Version',
      '2': 'Publisher',
      '3': 'Language code',
      '6': 'Installation method',
      '7': 'Uninstallation key paths',
      'a': 'Installation time',
      'b': 'Uninstallation time',
      'd': 'Installation directories',
      'Files': 'File reference key identifiers'}

  _ROOT_KEY_NAMES = frozenset([
      '{11517b7c-e79d-4e20-961b-75a811715add}',
      '{356c48f6-2fee-e7ef-2a64-39f59ec3be22}'])

  def _GetValueDataAsObject(self, value):
    """Retrieves the value data as an object.

    Args:
      value (pyregf_value): value.

    Returns:
      object: data as a Python type.

    Raises:
      ParseError: if the value data cannot be read.
    """
    try:
      if value.type in (1, 2, 6):
        value_data = value.get_data_as_string()

      elif value.type in (4, 5, 11):
        value_data = value.get_data_as_integer()

      elif value.type == 7:
        value_data = list(value.get_data_as_multi_string())

      else:
        value_data = value.data

    except (IOError, OverflowError) as exception:
      raise errors.ParseError((
          f'Unable to read data from value: {value.name:s} with error: '
          f'{exception!s}'))

    return value_data

  def _ReadApplicationFileKey(self, application_file_key):
    """Reads an application file key.

    Args:
      application_file_key (pyregf_key): application file key.
    """
    if self._debug:
      self._DebugPrintText(f'Application File: {application_file_key.name:s}\n')

    for value in application_file_key.values:
      description = self._APPLICATION_FILE_KEY_DESCRIPTIONS.get(
          value.name, value.name)
      value_data = self._GetValueDataAsObject(value)

      if self._debug:
        self._DebugPrintValue(description, value_data)

    if self._debug:
      self._DebugPrintText('\n')

  def _ReadApplicationKey(self, application_key):
    """Reads an application key.

    Args:
      application_key (pyregf_key): application key.
    """
    if self._debug:
      self._DebugPrintText(f'Application: {application_key.name:s}\n')

    for value in application_key.values:
      description = self._APPLICATION_KEY_DESCRIPTIONS.get(
          value.name, value.name)
      value_data = self._GetValueDataAsObject(value)

      if self._debug:
        self._DebugPrintValue(description, value_data)

    if self._debug:
      self._DebugPrintText('\n')

  def _ReadFileKey(self, file_key):
    """Reads a File key.

    Args:
      file_key (pyregf_key): File key.
    """
    for volume_key in file_key.sub_keys:
      for file_reference_key in volume_key.sub_keys:
        self._ReadFileReferenceKey(file_reference_key)

  def _ReadFileReferenceKey(self, file_reference_key):
    """Reads a file reference key.

    Args:
      file_reference_key (pyregf_key): file reference key.
    """
    if self._debug:
      if '0000' in file_reference_key.name:
        sequence_number, mft_entry = file_reference_key.name.split('0000')
        mft_entry = int(mft_entry, 16)
        sequence_number = int(sequence_number, 16)
        self._DebugPrintText((
            f'File: {file_reference_key.name:s} '
            f'({mft_entry:d}-{sequence_number:d})\n'))
      else:
        self._DebugPrintText(f'File: {file_reference_key.name:s}\n')

    for value in file_reference_key.values:
      description = self._FILE_REFERENCE_KEY_DESCRIPTIONS.get(
          value.name, value.name)
      value_data = self._GetValueDataAsObject(value)

      if self._debug:
        if value.name == 'd':
          major_version = value_data >> 16
          minor_version = value_data & 0xffff
          value_data = f'{major_version:d}.{minor_version:d}'

        if value.name == 'f':
          self._DebugPrintPosixTimeValue(description, value_data)
        elif value.name in ('11', '12', '17'):
          self._DebugPrintFiletimeValue(description, value_data)
        else:
          self._DebugPrintValue(description, value_data)

    if self._debug:
      self._DebugPrintText('\n')

  def _ReadInventoryApplicationFileKey(self, inventory_application_file_key):
    """Reads a InventoryApplicationFile key.

    Args:
      inventory_application_file_key (pyregf_key): InventoryApplicationFile key.
    """
    for application_file_key in inventory_application_file_key.sub_keys:
      self._ReadApplicationFileKey(application_file_key)

  def _ReadInventoryApplicationKey(self, inventory_application_key):
    """Reads a InventoryApplication key.

    Args:
      inventory_application_key (pyregf_key): InventoryApplication key.
    """
    for application_key in inventory_application_key.sub_keys:
      self._ReadApplicationKey(application_key)

  def _ReadProgramKey(self, program_key):
    """Reads a program key.

    Args:
      program_key (pyregf_key): program key.
    """
    if self._debug:
      self._DebugPrintText(f'Program: {program_key.name:s}\n')

    for value in program_key.values:
      description = self._PROGRAM_KEY_DESCRIPTIONS.get(value.name, value.name)
      value_data = self._GetValueDataAsObject(value)

      if self._debug:
        if value.name in ('7', 'd', 'Files'):
          for string_value in value_data:
            self._DebugPrintValue(description, string_value)
            description = ''
        elif value.name in ('a', 'b'):
          self._DebugPrintPosixTimeValue(description, value_data)
        else:
          self._DebugPrintValue(description, value_data)

    if self._debug:
      self._DebugPrintText('\n')

  def _ReadProgramsKey(self, programs_key):
    """Reads a Programs key.

    Args:
      programs_key (pyregf_key): Programs key.
    """
    for program_key in programs_key.sub_keys:
      self._ReadProgramKey(program_key)

  def ReadFileObject(self, file_object):
    """Reads a Windows AMCache file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    regf_file = pyregf.file()
    regf_file.open_file_object(file_object)

    root_key = regf_file.get_root_key()
    root_key_name = root_key.get_name()
    if root_key_name.lower() not in self._ROOT_KEY_NAMES:
      return

    if root_key := regf_file.get_key_by_path('\\Root'):
      if file_key := root_key.get_sub_key_by_path('File'):
        self._ReadFileKey(file_key)

      if programs_key := root_key.get_sub_key_by_path('Programs'):
        self._ReadProgramsKey(programs_key)

      if inventory_application_key := root_key.get_sub_key_by_path(
          'InventoryApplication'):
        self._ReadInventoryApplicationKey(inventory_application_key)

      if inventory_application_file_key := root_key.get_sub_key_by_path(
          'InventoryApplicationFile'):
        self._ReadInventoryApplicationFileKey(inventory_application_file_key)
