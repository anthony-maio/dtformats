# -*- coding: utf-8 -*-
"""Windows Defender scan DetectionHistory files."""

from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format


class WindowsDefenderScanDetectionHistoryFile(data_format.BinaryDataFile):
  """Windows Defender scan DetectionHistory file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
      'detection_history.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'detection_history.debug.yaml', custom_format_callbacks={
          'filetime': '_FormatIntegerAsFiletime'})

  _CATEGORY_NAME = {
      0: 'INVALID',
      1: 'ADWARE',
      2: 'SPYWARE',
      3: 'PASSWORDSTEALER',
      4: 'TROJANDOWNLOADER',
      5: 'WORM',
      6: 'BACKDOOR',
      7: 'REMOTEACCESSTROJAN',
      8: 'TROJAN',
      9: 'EMAILFLOODER',
      10: 'KEYLOGGER',
      11: 'DIALER',
      12: 'MONITORINGSOFTWARE',
      13: 'BROWSERMODIFIER',
      14: 'COOKIE',
      15: 'BROWSERPLUGIN',
      16: 'AOLEXPLOIT',
      17: 'NUKER',
      18: 'SECURITYDISABLER',
      19: 'JOKEPROGRAM',
      20: 'HOSTILEACTIVEXCONTROL',
      21: 'SOFTWAREBUNDLER',
      22: 'STEALTHNOTIFIER',
      23: 'SETTINGSMODIFIER',
      24: 'TOOLBAR',
      25: 'REMOTECONTROLSOFTWARE',
      26: 'TROJANFTP',
      27: 'POTENTIALUNWANTEDSOFTWARE',
      28: 'ICQEXPLOIT',
      29: 'TROJANTELNET',
      30: 'EXPLOIT',
      31: 'FILESHARINGPROGRAM',
      32: 'MALWARE_CREATION_TOOL',
      33: 'REMOTE_CONTROL_SOFTWARE',
      34: 'TOOL',
      36: 'TROJAN_DENIALOFSERVICE',
      37: 'TROJAN_DROPPER',
      38: 'TROJAN_MASSMAILER',
      39: 'TROJAN_MONITORINGSOFTWARE',
      40: 'TROJAN_PROXYSERVER',
      42: 'VIRUS',
      43: 'KNOWN',
      44: 'UNKNOWN',
      45: 'SPP',
      46: 'BEHAVIOR',
      47: 'VULNERABILTIY',
      48: 'POLICY',
      49: 'EUS',
      50: 'RANSOM',
      51: 'ASR'}

  _VALUE_DESCRIPTIONS = [
      {0: 'Threat identifier',
       1: 'Identifier'},
      {0: 'UnknownMagic1',
       1: 'Threat name',
       4: 'Category'},
      {0: 'UnknownMagic2',
       1: 'Resource type',
       2: 'Resource location',
       4: 'Threat tracking data size',
       5: 'Threat tracking data',
       6: 'Last threat status change time',
       12: 'Domain user1',
       14: 'Process name',
       18: 'Initial detection time',
       20: 'Remediation time',
       24: 'Domain user2'}]

  def _ReadThreatTrackingData(self, threat_tracking_data, file_offset):
    """Reads the threat tracking data.

    Args:
      threat_tracking_data (bytes): threat tracking data.
      file_offset (int): offset of the threat tracking data relative to
          the start of the file.

    Raises:
      IOError: if the threat tracking data cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'\nReading threat tracking data at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('uint32le')

    values_data_size = self._ReadStructureFromByteStream(
        threat_tracking_data, 0, data_type_map, 'values data size')

    if values_data_size != 1:
      values_data_offset = 4
      values_data_end_offset = values_data_size
    else:
      header = self._ReadThreatTrackingHeader(threat_tracking_data)

      values_data_offset = header.header_size + 4
      values_data_end_offset = header.total_data_size

    while values_data_offset < values_data_end_offset:
      _, data_size = self._ReadThreatTrackingValue(
          threat_tracking_data[values_data_offset:],
          file_offset + values_data_offset)
      values_data_offset += data_size

  def _ReadThreatTrackingHeader(self, threat_tracking_data):
    """Reads the threat tracking header.

    Args:
      threat_tracking_data (bytes): threat tracking data.

    Returns:
      threat_tracking_header: threat tracking header.

    Raises:
      IOError: if the threat tracking header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('threat_tracking_header')

    threat_tracking_header = self._ReadStructureFromByteStream(
        threat_tracking_data, 0, data_type_map, 'threat tracking header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('threat_tracking_header', None)
      self._DebugPrintStructureObject(threat_tracking_header, debug_info)

    return threat_tracking_header

  def _ReadThreatTrackingValue(self, threat_tracking_data, file_offset):
    """Reads the threat tracking value.

    Args:
      threat_tracking_data (bytes): threat tracking data.
      file_offset (int): offset of the threat tracking data relative to
          the start of the file.

    Returns:
      tuple[threat_tracking_value, int]: threat tracking value and data size.

    Raises:
      IOError: if the threat tracking value cannot be read.
    """
    data_type_map = self._GetDataTypeMap('threat_tracking_value')

    context = dtfabric_data_maps.DataTypeMapContext()

    threat_tracking_value = self._ReadStructureFromByteStream(
        threat_tracking_data, file_offset, data_type_map,
        'threat tracking value', context=context)

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('threat_tracking_value', None)
      self._DebugPrintStructureObject(threat_tracking_value, debug_info)

    return threat_tracking_value, context.byte_size

  def _ReadValue(self, file_object, file_offset):
    """Reads the value.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the value relative to the start of the file.

    Returns:
      object: value.

    Raises:
      IOError: if the value cannot be read.
    """
    data_type_map = self._GetDataTypeMap('detection_history_value')

    value, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'value')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('detection_history_value', None)
      self._DebugPrintStructureObject(value, debug_info)

    value_object = None
    if value.data_type in (
        0x00000000, 0x00000005, 0x00000006, 0x00000008):
      value_object = value.value_integer
    elif value.data_type == 0x0000000a:
      value_object = value.value_filetime
    elif value.data_type == 0x00000015:
      value_object = value.value_string
    elif value.data_type == 0x0000001e:
      value_object = value.value_guid
    elif value.data_type == 0x00000028:
      value_object = value.data

    return value_object

  def ReadFileObject(self, file_object):
    """Reads a Windows Defender scan DetectionHistory file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    value_tuples = []

    file_offset = 0
    while file_offset < self._file_size:
      value_object = self._ReadValue(file_object, file_offset)
      value_tuples.append((file_offset, value_object))

      file_offset = file_object.tell()

    if self._debug:
      value_index_set = 0
      value_index = 0
      for file_offset, value_object in value_tuples:
        if value_object == 'Magic.Version:1.2':
          if value_index_set < 2:
            value_index_set += 1
          value_index = 0

        if (value_index_set, value_index) == (2, 5):
          self._ReadThreatTrackingData(value_object, file_offset + 8)

        else:
          description = self._VALUE_DESCRIPTIONS[value_index_set].get(
              value_index, f'UNKNOWN_{value_index_set:d}_{value_index:d}')

          if (value_index_set, value_index) == (1, 4):
            category_name = self._CATEGORY_NAME.get(value_object, 'UNKNOWN')
            value_string = f'{value_object!s} ({category_name:s})'

          else:
            value_string = f'{value_object!s}'

          self._DebugPrintValue(description, value_string)

        value_index += 1
