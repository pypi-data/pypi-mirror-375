from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, clk_source: enums.SignalSource, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZC:CLK:SOURce \n
		Snippet: driver.sbus.nrzc.clk.source.set(clk_source = enums.SignalSource.C1, serialBus = repcap.SerialBus.Default) \n
		Selects the source for the clock signal. \n
			:param clk_source: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(clk_source, enums.SignalSource)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:CLK:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SignalSource:
		"""SBUS<*>:NRZC:CLK:SOURce \n
		Snippet: value: enums.SignalSource = driver.sbus.nrzc.clk.source.get(serialBus = repcap.SerialBus.Default) \n
		Selects the source for the clock signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: clk_source: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZC:CLK:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.SignalSource)
