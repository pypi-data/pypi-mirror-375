from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, global_statistics_enable: bool, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:STATistics[:ENABle] \n
		Snippet: driver.measurement.statistics.enable.set(global_statistics_enable = False, measIndex = repcap.MeasIndex.Default) \n
		Enables statistics calculation for all measurements. \n
			:param global_statistics_enable: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(global_statistics_enable)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:STATistics:ENABle {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> bool:
		"""MEASurement<*>:STATistics[:ENABle] \n
		Snippet: value: bool = driver.measurement.statistics.enable.get(measIndex = repcap.MeasIndex.Default) \n
		Enables statistics calculation for all measurements. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: global_statistics_enable: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:STATistics:ENABle?')
		return Conversions.str_to_bool(response)
