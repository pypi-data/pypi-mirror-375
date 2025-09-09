from constellation.base import *
from constellation.networking.net_client import *

class BasicOscilloscopeChannelState(InstrumentState):
	
	# __state_fields__ = (InstrumentState.__state_fields__+("div_volt", "offset_volt", "chan_en", "waveform"))
	__state_fields__ = ("div_volt", "offset_volt", "chan_en", "waveform")
	
	def __init__(self, log:plf.LogPile=None):
		super().__init__(log=log)
		
		self.add_param("div_volt", unit="V")
		self.add_param("offset_volt", unit="V")
		self.add_param("chan_en", unit="bool")
		
		self.add_param("waveform", unit="", is_data=True, value={"time_S":[], "volt_V":[]})

class BasicOscilloscopeState(InstrumentState):
	
	# __state_fields__ = (InstrumentState.__state_fields__ + ("first_channel", "num_channels", "ndiv_horiz", "ndiv_vert", "div_time", "offset_time", "channels"))
	__state_fields__ = ("first_channel", "num_channels", "ndiv_horiz", "ndiv_vert", "div_time", "offset_time", "channels")
	
	def __init__(self, first_channel:int, num_channels:int, ndiv_horiz, ndiv_vert, log:plf.LogPile=None):
		super().__init__(log=log)
		
		self.add_param("first_channel", unit="1", value=first_channel)
		self.add_param("num_channels", unit="1", value=num_channels)
		
		self.add_param("ndiv_horiz", unit="1", value=ndiv_horiz)
		self.add_param("ndiv_vert", unit="1", value=ndiv_vert)
		
		self.add_param("div_time", unit="s")
		self.add_param("offset_time", unit="s")
		
		self.add_param("channels", unit="", value=IndexedList(self.first_channel, self.num_channels, validate_type=BasicOscilloscopeChannelState, log=log))
		
		for ch_no in self.channels.get_range():
			self.channels[ch_no] = BasicOscilloscopeChannelState(log=log)

class BasicOscilloscopeCtg(Driver):
	
	def __init__(self, address:str, log:plf.LogPile, relay:CommandRelay=None, expected_idn="", max_channels:int=1, num_div_horiz:int=10, num_div_vert:int=8, dummy:bool=False, **kwargs):
		super().__init__(address, log, expected_idn=expected_idn, dummy=dummy, relay=relay, **kwargs)
		
		self.max_channels = max_channels
		
		self.state = BasicOscilloscopeState(self.first_channel, self.max_channels, num_div_horiz, num_div_vert, log=log)
		
		if self.dummy:
			self.init_dummy_state()
		
	def init_dummy_state(self) -> None:
		self.set_div_time(10e-3)
		self.set_offset_time(0)
		for ch in range(self.first_channel, self.first_channel+self.max_channels):
			self.set_div_volt(ch, 1)
			self.set_offset_volt(ch, 0)
			self.set_chan_enable(ch, True)
		
		self.remake_dummy_waves()
	
	def remake_dummy_waves(self) ->  None:
		''' Re-generates spoofed waveforms for each channel that is as realistic as
		possible for the given instrument state. Saves the waveform to the internal
		data tracker dict. Should be called each time a time or voltage parameter has
		been changed and the waveform data is queried.
		
		Returns:
			None
		'''
		
		# Loop over all channels
		for channel in range(self.first_channel, self.first_channel+self.max_channels):
		
			ampl = 1 # V
			freq = 40*(channel+1) # Hz
			npoints = 101
			
			# Create time series
			t_span = self.state.get(["ndiv_horiz"]) * self.state.get(["div_time"])
			t_start = -1*t_span/2+self.state.get(["offset_time"])
			t_series = np.linspace(t_start, t_start + t_span, npoints)
			
			# Create waveform
			wave = ampl * np.sin(t_series*2*np.pi*freq)
			
			# Trim waveform to represent clipping on real scope
			v_span = self.state.get(["ndiv_vert"]) * self.state.get(["channels", "div_volt"], indices=[channel])
			v_min = -1*v_span/2+self.state.get(["channels", "offset_volt"], indices=[channel])
			v_max = v_min + v_span
			wave_clipped = [np.max([np.min([element, v_max]), v_min]) for element in wave]
			
			# Return result
			self.state.channels[channel].waveform = {"time_s":t_series, "volt_V":wave_clipped}
	
	def dummy_responder(self, func_name:str, *args, **kwargs):
		''' Function expected to behave as the "real" equivalents. ie. write commands don't
		need to return anything, reads commands or similar should. What is returned here
		should mimic what would be returned by the "real" function if it were connected to
		hardware.
		'''
		
		# Put everything in a try-catch in case arguments are missing or similar
		try:
			
			# Check for known functions
			found = True
			adjective = ""
			match func_name:
				case "set_div_time":
					rval = None
				case "get_div_time":
					rval = self.state.get(["div_time"])
				case "set_offset_time":
					rval = None
				case "get_offset_time":
					rval = self.state.get(["offset_time"])
				case "set_div_volt":
					rval = None
				case "get_div_volt":
					rval = self.state.get(["channels", "div_volt"], indices=[args[0]])
				case "set_offset_volt":
					rval = None
				case "get_offset_volt":
					rval = self.state.get(["channels", "offset_volt"], indices=[args[0]])
				case "set_chan_enable":
					rval = None
				case "get_chan_enable":
					rval = self.state.get(["channels", "chan_en"], indices=[args[0]])
				case "get_waveform":
					self.remake_dummy_waves()
					rval = self.state.channels[args[0]].waveform
				case _:
					found = False
				
			
			# If function was found, label as recognized, else check match for general getter or setter
			if found:
				adjective = "recognized"
			else:
				if "set_" == func_name[:4]:
					rval = -1
					adjective = "set_"
				elif "get_" == func_name[:4]:
					rval = None
					adjective = "get_"
				else:
					rval = None
					adjective = "unrecognized"
				
			self.debug(f"Dummy responder sending >{protect_str(rval)}< to {adjective} function (>{func_name}<).")
			return rval
		except Exception as e:
			self.error(f"Failed to respond to dummy instruction. ({e})")
			return None
	
	@abstractmethod
	def set_div_time(self, time_s:float):
		self.modify_state(self.get_div_time, ["div_time"], time_s)
	
	@abstractmethod
	@enabledummy
	def get_div_time(self):
		return self.modify_state(None, ["div_time"], self._super_hint)
	
	
	@abstractmethod
	def set_offset_time(self, time_s:float):
		self.modify_state(self.get_offset_time, ["offset_time"], time_s)
		
	@abstractmethod
	@enabledummy
	def get_offset_time(self):
		return self.modify_state(None, ["offset_time"], self._super_hint)
	
	@abstractmethod
	def set_div_volt(self, channel:int, volt_V:float):
		self.modify_state(lambda: self.get_div_volt(channel), ["channels", "div_volt"], volt_V, indices=[channel])
		
	@abstractmethod
	@enabledummy
	def get_div_volt(self, channel:int):
		return self.modify_state(None, ["channels", "div_volt"], self._super_hint, indices=[channel])
	
	@abstractmethod
	def set_offset_volt(self, channel:int, volt_V:float):
		self.modify_state(lambda: self.get_offset_volt(channel), ["channels", "offset_volt"], volt_V, indices=[channel])
		
	@abstractmethod
	@enabledummy
	def get_offset_volt(self, channel:int):
		return self.modify_state(None, ["channels", "offset_volt"], self._super_hint, indices=[channel])
	
	@abstractmethod
	def set_chan_enable(self, channel:int, enable:bool):
		self.modify_state(lambda: self.get_chan_enable(channel), ["channels", "chan_en"], enable, indices=[channel])
		
	@abstractmethod
	@enabledummy
	def get_chan_enable(self, channel:int):
		return self.modify_state(None, ["channels", "chan_en"], self._super_hint, indices=[channel])
	
	@abstractmethod
	@enabledummy
	def get_waveform(self, channel:int):
		return self.modify_state(None, ["channels", "waveform"], self._super_hint, indices=[channel])
	
	def refresh_state(self):
		self.get_div_time()
		self.get_offset_time()
		for ch in range(self.first_channel, self.first_channel+self.max_channels):
			self.get_div_volt(ch)
			self.get_offset_volt(ch)
			self.get_chan_enable(ch)
	
	def apply_state(self):
		self.set_div_time(self.state.get(["div_time"]))
		self.set_offset_time(self.state.get(["offset_time"]))
		for ch in range(self.first_channel, self.first_channel+self.max_channels):
			self.set_div_volt(ch, self.state.get(["channels", "div_volt"], indices=[ch]))
			self.set_offset_volt(ch, self.state.get(["channels", "offset_volt"], indices=[ch]))
			self.set_chan_enable(ch, self.state.get(["channels", "chan_en"], indices=[ch]))
	
	def refresh_data(self):
		
		for ch in range(1, self.max_channels):
			self.get_waveform(ch)
	
class StdOscilloscopeCtg(BasicOscilloscopeCtg):
	
	# Measurement options
	MEAS_VMAX = 0
	MEAS_VMIN = 1
	MEAS_VAVG = 2
	MEAS_VPP  = 3
	MEAS_FREQ = 4
	
	# Statistics options for measurement options
	STAT_NONE = 0
	STAT_AVG = 1
	STAT_MAX = 2
	STAT_MIN = 3
	STAT_CURR = 4
	STAT_STD = 5
	
	def __init__(self, address:str, log:plf.LogPile, expected_idn="", dummy:bool=False, **kwargs):
		super().__init__(address, log, expected_idn=expected_idn, dummy=dummy, **kwargs)
	
	@abstractmethod
	def add_measurement(self):
		pass
	
	@abstractmethod
	def get_measurement(self):
		pass
	
	def refresh_state(self):
		super().refresh_state()
	
