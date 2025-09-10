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

	def set(self, io_0_source: enums.SignalSource, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:QSPI:IOZero:SOURce \n
		Snippet: driver.sbus.qspi.ioZero.source.set(io_0_source = enums.SignalSource.C1, serialBus = repcap.SerialBus.Default) \n
		Sets the input channel of the IO 0 line. \n
			:param io_0_source: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(io_0_source, enums.SignalSource)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:IOZero:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SignalSource:
		"""SBUS<*>:QSPI:IOZero:SOURce \n
		Snippet: value: enums.SignalSource = driver.sbus.qspi.ioZero.source.get(serialBus = repcap.SerialBus.Default) \n
		Sets the input channel of the IO 0 line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: io_0_source: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:IOZero:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.SignalSource)
