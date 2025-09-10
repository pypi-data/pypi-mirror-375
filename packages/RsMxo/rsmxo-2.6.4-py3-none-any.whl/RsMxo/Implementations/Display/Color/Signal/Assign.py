from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AssignCls:
	"""Assign commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("assign", core, parent)

	def set(self, source: enums.SignalSource, color_table: enums.ColorTable) -> None:
		"""DISPlay:COLor:SIGNal:ASSign \n
		Snippet: driver.display.color.signal.assign.set(source = enums.SignalSource.C1, color_table = enums.ColorTable.FalseColors='FalseColors') \n
		Assigns a color table to the source waveform instead of a dedicated color. \n
			:param source: Signal name as returned by method RsMxo.Display.Color.Signal.catalog.
			:param color_table: String with the name of the color table. Valid values are: 'FalseColors', 'Spectrum', 'SingleEvent' and 'Temperature'.
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('source', source, DataType.Enum, enums.SignalSource), ArgSingle('color_table', color_table, DataType.Enum, enums.ColorTable))
		self._core.io.write(f'DISPlay:COLor:SIGNal:ASSign {param}'.rstrip())

	# noinspection PyTypeChecker
	def get(self, source: enums.SignalSource) -> enums.ColorTable:
		"""DISPlay:COLor:SIGNal:ASSign \n
		Snippet: value: enums.ColorTable = driver.display.color.signal.assign.get(source = enums.SignalSource.C1) \n
		Assigns a color table to the source waveform instead of a dedicated color. \n
			:param source: Signal name as returned by method RsMxo.Display.Color.Signal.catalog.
			:return: color_table: String with the name of the color table. Valid values are: 'FalseColors', 'Spectrum', 'SingleEvent' and 'Temperature'."""
		param = Conversions.enum_scalar_to_str(source, enums.SignalSource)
		response = self._core.io.query_str(f'DISPlay:COLor:SIGNal:ASSign? {param}')
		return Conversions.str_to_scalar_enum(response, enums.ColorTable)
