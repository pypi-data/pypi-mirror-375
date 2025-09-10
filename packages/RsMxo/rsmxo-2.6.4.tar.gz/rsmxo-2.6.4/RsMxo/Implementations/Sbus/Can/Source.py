from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, data_source: enums.SignalSource, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:CAN:SOURce \n
		Snippet: driver.sbus.can.source.set(data_source = enums.SignalSource.C1, serialBus = repcap.SerialBus.Default) \n
		Sets the source channel to which the line is connected. \n
			:param data_source: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(data_source, enums.SignalSource)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:CAN:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SignalSource:
		"""SBUS<*>:CAN:SOURce \n
		Snippet: value: enums.SignalSource = driver.sbus.can.source.get(serialBus = repcap.SerialBus.Default) \n
		Sets the source channel to which the line is connected. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data_source: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.SignalSource)
