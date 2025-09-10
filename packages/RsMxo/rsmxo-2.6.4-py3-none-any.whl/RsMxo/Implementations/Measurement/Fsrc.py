from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FsrcCls:
	"""Fsrc commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fsrc", core, parent)

	def set(self, source: enums.SignalSource, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:FSRC \n
		Snippet: driver.measurement.fsrc.set(source = enums.SignalSource.C1, measIndex = repcap.MeasIndex.Default) \n
		Defines the first measurement source. The command is an alternative to method RsMxo.Measurement.Source.set. \n
			:param source: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(source, enums.SignalSource)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:FSRC {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default) -> enums.SignalSource:
		"""MEASurement<*>:FSRC \n
		Snippet: value: enums.SignalSource = driver.measurement.fsrc.get(measIndex = repcap.MeasIndex.Default) \n
		Defines the first measurement source. The command is an alternative to method RsMxo.Measurement.Source.set. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: source: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:FSRC?')
		return Conversions.str_to_scalar_enum(response, enums.SignalSource)
