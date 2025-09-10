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

	def set(self, source: enums.SignalSource, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:SOURce \n
		Snippet: driver.calculate.spectrum.plist.source.set(source = enums.SignalSource.C1, spectrum = repcap.Spectrum.Default) \n
		Selects the source of the peak table. You can select one of the traces that is enabled with 'Traces'. \n
			:param source: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.enum_scalar_to_str(source, enums.SignalSource)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.SignalSource:
		"""CALCulate:SPECtrum<*>:PLISt:SOURce \n
		Snippet: value: enums.SignalSource = driver.calculate.spectrum.plist.source.get(spectrum = repcap.Spectrum.Default) \n
		Selects the source of the peak table. You can select one of the traces that is enabled with 'Traces'. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: source: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.SignalSource)
