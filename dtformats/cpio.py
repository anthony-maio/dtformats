# -*- coding: utf-8 -*-
"""Copy in and out (CPIO) archive format files."""

import os

from dtformats import data_format
from dtformats import data_range
from dtformats import errors


class CPIOArchiveFileEntry(data_range.DataRange):
  """CPIO archive file entry.

  Attributes:
    data_offset (int): offset of the data.
    data_size (int): size of the data.
    group_identifier (int): group identifier (GID).
    inode_number (int): inode number.
    mode (int): file access mode.
    modification_time (int): modification time, in number of seconds since
        January 1, 1970 00:00:00.
    path (str): path.
    size (int): size of the file entry data.
    user_identifier (int): user identifier (UID).
  """

  def __init__(self, file_object, data_offset=0, data_size=0):
    """Initializes a CPIO archive file entry.

    Args:
      file_object (file): file-like object of the CPIO archive file.
      data_offset (Optional[int]): offset of the data.
      data_size (Optional[int]): size of the data.
    """
    super(CPIOArchiveFileEntry, self).__init__(
        file_object, data_offset=data_offset, data_size=data_size)
    self.group_identifier = None
    self.inode_number = None
    self.mode = None
    self.modification_time = None
    self.path = None
    self.size = None
    self.user_identifier = None


class CPIOArchiveFile(data_format.BinaryDataFile):
  """CPIO archive file.

  Attributes:
    file_format (str): CPIO file format.
    size (int): size of the CPIO file data.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('cpio.yaml')

  # TODO: move path into structure.

  _CPIO_SIGNATURE_BINARY_BIG_ENDIAN = b'\x71\xc7'
  _CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN = b'\xc7\x71'
  _CPIO_SIGNATURE_PORTABLE_ASCII = b'070707'
  _CPIO_SIGNATURE_NEW_ASCII = b'070701'
  _CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM = b'070702'

  _CPIO_ATTRIBUTE_NAMES_ODC = (
      'device_number', 'inode_number', 'mode', 'user_identifier',
      'group_identifier', 'number_of_links', 'special_device_number',
      'modification_time', 'path_size', 'file_size')

  _CPIO_ATTRIBUTE_NAMES_CRC = (
      'inode_number', 'mode', 'user_identifier', 'group_identifier',
      'number_of_links', 'modification_time', 'path_size',
      'file_size', 'device_major_number', 'device_minor_number',
      'special_device_major_number', 'special_device_minor_number',
      'checksum')

  def __init__(self, debug=False, output_writer=None):
    """Initializes a CPIO archive file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CPIOArchiveFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._file_entries = None

    self.file_format = None
    self.size = None

  def _DebugPrintFileEntry(self, file_entry):
    """Prints file entry debug information.

    Args:
      file_entry (cpio_new_file_entry): file entry.
    """
    if self.file_format in ('bin-big-endian', 'bin-little-endian'):
      value_string = f'0x{file_entry.signature:04x}'
    else:
      value_string = f'{file_entry.signature!s}'

    self._DebugPrintValue('Signature', value_string)

    if self.file_format not in ('crc', 'newc'):
      self._DebugPrintValue('Device number', f'{file_entry.device_number:d}')

    self._DebugPrintValue('Inode number', f'{file_entry.inode_number:d}')

    self._DebugPrintValue('Mode', f'{file_entry.mode:o}')

    self._DebugPrintValue(
        'User identifier (UID)', f'{file_entry.user_identifier:d}')

    self._DebugPrintValue(
        'Group identifier (GID)', f'{file_entry.group_identifier:d}')

    self._DebugPrintValue('Number of links', f'{file_entry.number_of_links:d}')

    if self.file_format not in ('crc', 'newc'):
      self._DebugPrintValue(
          'Special device number', f'{file_entry.special_device_number:d}')

    self._DebugPrintValue(
        'Modification time', f'{file_entry.modification_time:d}')

    if self.file_format not in ('crc', 'newc'):
      self._DebugPrintValue('Path size', f'{file_entry.path_size:d}')

    self._DebugPrintValue('File size', f'{file_entry.file_size:d}')

    if self.file_format in ('crc', 'newc'):
      self._DebugPrintValue(
          'Device major number', f'{file_entry.device_major_number:d}')
      self._DebugPrintValue(
          'Device minor number', f'{file_entry.device_minor_number:d}')

      self._DebugPrintValue(
          'Special device major number',
          f'{file_entry.special_device_major_number:d}')
      self._DebugPrintValue(
          'Special device minor number',
          f'{file_entry.special_device_minor_number:d}')

      self._DebugPrintValue('Path size', f'{file_entry.path_size:d}')

      self._DebugPrintValue('Checksum', f'0x{file_entry.checksum:08x}')

  def _ReadFileEntry(self, file_object, file_offset):
    """Reads a file entry.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative to the start of
          the file-like object.

    Returns:
      CPIOArchiveFileEntry: a file entry.

    Raises:
      ParseError: if the file entry cannot be read.
    """
    if self.file_format == 'bin-big-endian':
      data_type_map = self._GetDataTypeMap('cpio_binary_big_endian_file_entry')
    elif self.file_format == 'bin-little-endian':
      data_type_map = self._GetDataTypeMap(
          'cpio_binary_little_endian_file_entry')
    elif self.file_format == 'odc':
      data_type_map = self._GetDataTypeMap('cpio_portable_ascii_file_entry')
    elif self.file_format in ('crc', 'newc'):
      data_type_map = self._GetDataTypeMap('cpio_new_ascii_file_entry')

    file_entry, file_entry_data_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file entry')

    file_offset += file_entry_data_size

    if self.file_format in ('bin-big-endian', 'bin-little-endian'):
      file_entry.modification_time = (
          (file_entry.modification_time.upper << 16) |
          file_entry.modification_time.lower)

      file_entry.file_size = (
          (file_entry.file_size.upper << 16) | file_entry.file_size.lower)

    if self.file_format == 'odc':
      for attribute_name in self._CPIO_ATTRIBUTE_NAMES_ODC:
        value = getattr(file_entry, attribute_name, None)
        try:
          value = int(value, 8)
        except ValueError:
          raise errors.ParseError((
              f'Unable to convert attribute: {attribute_name:s} into an '
              f'integer'))

        value = setattr(file_entry, attribute_name, value)

    elif self.file_format in ('crc', 'newc'):
      for attribute_name in self._CPIO_ATTRIBUTE_NAMES_CRC:
        value = getattr(file_entry, attribute_name, None)
        try:
          value = int(value, 16)
        except ValueError:
          raise errors.ParseError((
              f'Unable to convert attribute: {attribute_name:s} into an '
              f'integer'))

        value = setattr(file_entry, attribute_name, value)

    if self._debug:
      self._DebugPrintFileEntry(file_entry)

    path_data = file_object.read(file_entry.path_size)

    if self._debug:
      self._DebugPrintData('Path data', path_data)

    file_offset += file_entry.path_size

    # TODO: should this be ASCII?
    path = path_data.decode('ascii')
    path, _, _ = path.partition('\x00')

    if self._debug:
      self._DebugPrintValue('Path', path)

    if self.file_format in ('bin-big-endian', 'bin-little-endian'):
      padding_size = file_offset % 2
      if padding_size > 0:
        padding_size = 2 - padding_size

    elif self.file_format == 'odc':
      padding_size = 0

    elif self.file_format in ('crc', 'newc'):
      padding_size = file_offset % 4
      if padding_size > 0:
        padding_size = 4 - padding_size

    if self._debug:
      padding_data = file_object.read(padding_size)
      self._DebugPrintData('Path alignment padding', padding_data)

    file_offset += padding_size

    archive_file_entry = CPIOArchiveFileEntry(file_object)

    archive_file_entry.data_offset = file_offset
    archive_file_entry.data_size = file_entry.file_size
    archive_file_entry.group_identifier = file_entry.group_identifier
    archive_file_entry.inode_number = file_entry.inode_number
    archive_file_entry.modification_time = file_entry.modification_time
    archive_file_entry.path = path
    archive_file_entry.mode = file_entry.mode
    archive_file_entry.size = (
        file_entry_data_size + file_entry.path_size + padding_size +
        file_entry.file_size)
    archive_file_entry.user_identifier = file_entry.user_identifier

    file_offset += file_entry.file_size

    if self.file_format in ('bin-big-endian', 'bin-little-endian'):
      padding_size = file_offset % 2
      if padding_size > 0:
        padding_size = 2 - padding_size

    elif self.file_format == 'odc':
      padding_size = 0

    elif self.file_format in ('crc', 'newc'):
      padding_size = file_offset % 4
      if padding_size > 0:
        padding_size = 4 - padding_size

    if padding_size > 0:
      if self._debug:
        file_object.seek(file_offset, os.SEEK_SET)
        padding_data = file_object.read(padding_size)

        self._DebugPrintData('File data alignment padding', padding_data)

      archive_file_entry.size += padding_size

    if self._debug:
      self._DebugPrintText('\n')

    return archive_file_entry

  def _ReadFileEntries(self, file_object):
    """Reads the file entries from the cpio archive.

    Args:
      file_object (file): file-like object.
    """
    self._file_entries = {}

    file_offset = 0
    while file_offset < self._file_size or self._file_size == 0:
      file_entry = self._ReadFileEntry(file_object, file_offset)
      file_offset += file_entry.size
      if file_entry.path == 'TRAILER!!!':
        break

      if file_entry.path in self._file_entries:
        # TODO: alert on file entries with duplicate paths?
        continue

      self._file_entries[file_entry.path] = file_entry

    self.size = file_offset

  def Close(self):
    """Closes the CPIO archive file."""
    super(CPIOArchiveFile, self).Close()
    self._file_entries = None

  def FileEntryExistsByPath(self, path):
    """Determines if file entry for a specific path exists.

    Args:
      path (str): path of the file entry.

    Returns:
      bool: True if the file entry exists.
    """
    return False if not self._file_entries else path in self._file_entries

  def GetFileEntries(self, path_prefix=''):
    """Retrieves the file entries.

    Args:
      path_prefix (Optional[str]): path prefix.

    Yields:
      CPIOArchiveFileEntry: CPIO archive file entry.
    """
    if self._file_entries:
      for path, file_entry in self._file_entries.items():
        if path.startswith(path_prefix):
          yield file_entry

  def GetFileEntryByPath(self, path):
    """Retrieves a file entry for a specific path.

    Args:
      path (str): path of the file entry.

    Returns:
      CPIOArchiveFileEntry: CPIO archive file entry or None.
    """
    return False if not self._file_entries else self._file_entries.get(path, None)

  def ReadFileObject(self, file_object):
    """Reads binary data from a file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the format signature is not supported.
    """
    file_object.seek(0, os.SEEK_SET)
    signature_data = file_object.read(6)

    self.file_format = None
    if len(signature_data) > 2:
      if signature_data[:2] == self._CPIO_SIGNATURE_BINARY_BIG_ENDIAN:
        self.file_format = 'bin-big-endian'
      elif signature_data[:2] == self._CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN:
        self.file_format = 'bin-little-endian'
      elif signature_data == self._CPIO_SIGNATURE_PORTABLE_ASCII:
        self.file_format = 'odc'
      elif signature_data == self._CPIO_SIGNATURE_NEW_ASCII:
        self.file_format = 'newc'
      elif signature_data == self._CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM:
        self.file_format = 'crc'

    if self.file_format is None:
      raise errors.ParseError('Unsupported CPIO format.')

    self._ReadFileEntries(file_object)

    # TODO: print trailing data
