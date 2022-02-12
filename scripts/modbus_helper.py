import os, socket, datetime, math
from umodbus.client import tcp
from data_helper import DataHelper

import pdb

class ModbusHelper(object):

	FUNCTION_CODES = {
		'01': ['1','01','FC01','coil','Coil','coils','Coils','RC','Coil-FC01'],			# function code 01: Read Coils
		'02': ['2','02','FC02','discrete','Discrete','di','DI','RDI','DI-FC02'], 			# function code 02: Read Discrete Inputs
		'03': ['3','03','FC03','holding','Holding','HR','RHR','HR-FC03'], 				# function code 03: Read Holding Registers
		'04': ['4','04','FC04','input register','input registers','Input Register',
				'Input Registers','IR','RIR','IR-FC04']									# function code 04: Read Input Registers
	}

	UMODBUS_TCP_CALL = {
		'01': tcp.read_coils,
		'02': tcp.read_discrete_inputs,
		'03': tcp.read_holding_registers,
		'04': tcp.read_input_registers
	}

	DATA_TYPES_REGISTER_COUNT = {
		'uint16': 1,
		'sint16': 1,
		'float32': 2,
		#'float64': 4, # unsupported at the moment
		#'packedbool': 1, # unsupported at the moment
		'di': 1,
		'coil': 1
	}

	# Method to parse a Modbus template .csv configuration file and build the various Modbus TCP calls the client shall send in an "optimized" way (optimized to reduce/minimize the number of calls)
	# it returns 2 elements: call_groups and interpreter_helper
	@classmethod
	def parse_template_build_calls(cls, full_path_to_modbus_template_csv):
		call_groups = {}
		interpreter_helper = {}
		template_lod = DataHelper.csv_to_lod(full_path_to_modbus_template_csv)
		
		# find unique/distinct read_type
		for read_entry in template_lod:
			read_address = read_entry['address']

			# skip entry if there is no address (mandatory field)
			if (not read_address) or (read_address == '') or (read_address is None):
				print('\n\t[WARNING] On item:',read_entry)
				print('\t[WARNING] Skipping item due to no address provided')
				continue

			read_type = str(read_entry['read_type'])
			read_tag_name = read_entry['tag_name']

			# skip entry if there is no read_type (mandatory field)
			if (not read_type) or (read_type == '') or (read_type is None):
				print('\n\t[WARNING] On item:',read_entry)
				print('\t[WARNING] Skipping item with address '+str(read_address)+' and tag_name "'+str(read_tag_name)+'"" due to no read_type provided\n')
				continue			
			
			# default to data_type of sint16 if user forgot to specify one
			# arbitrary choice to accomodate errors in the modbus_template...
			# logged data may be inaccurate if the real data_type is different from sint16
			read_data_type = read_entry['data_type']
			if (not read_data_type) or (read_data_type == '') or (read_data_type is None):
				print('\n\t[WARNING] No data_type specified in modbus_template for item:')
				print('\t\t',read_entry)
				print('\tAssuming default data_type of "sint16"')
				print('\t[WARNING] Logged data may be inaccurate for this item!')
				read_data_type = 'sint16'
			# skip entry if read_data_type is unknown or not currently supported
			if read_data_type not in ModbusHelper.DATA_TYPES_REGISTER_COUNT:
				print('\n\t[WARNING] On item:',read_entry)
				print('\t[WARNING] Skipping item with address '+str(read_address)+' and tag_name "'+str(read_tag_name)+'"" due to unknown or unsupported read_type of "'+str(read_data_type)+'"')
				print('\t[WARNING] Supported read_types are:',[str(i) for i in ModbusHelper.DATA_TYPES_REGISTER_COUNT])
				continue

			# create a default tag name if the user forgot to specify one
			if (not read_tag_name) or (read_tag_name == '') or (read_tag_name is None):
				print('\n\t[WARNING] No tag_name specified in modbus_template for item:')
				print('\t\t',read_entry)
				print('\tUsing default tag_name of: "'+read_type+'_address_'+str(read_address)+'_data_type_'+read_data_type+'"')

			# do I really need to look at scaling here if my goal is only to parse the configuration template and build the Modbus TCP calls???
			#address_read_scaling_coeff = read_entry['scaling_coeff']
			#address_read_scaling_offset = read_entry['scaling_offset']

			# lookup the read_type in ModbusHelper.FUNCTIONS_CODES and build the lookup table
			fc_lookup_table = {}			

			fc_found = False
			for fc in ModbusHelper.FUNCTION_CODES:
				if fc_found:
					break
				for fc_keyword in ModbusHelper.FUNCTION_CODES[fc]:
					if fc_keyword in read_type:
						fc_found = True
						if read_type not in fc_lookup_table:
							fc_lookup_table[read_type] = fc
						if fc not in call_groups:
							call_groups[fc] = []
							#interpreter_helper[fc] = {'addresses': [],'address_count_map': {},'address_data_type_map':{},'address_tag_name_map': {}}
							interpreter_helper[fc] = {'addresses': [],'address_maps': {}}

						#interpreter_helper[fc]['address_count_map'][int(read_address)] = ModbusHelper.DATA_TYPES_REGISTER_COUNT[read_data_type]
						#interpreter_helper[fc]['address_data_type_map'][int(read_address)] = read_data_type
						#interpreter_helper[fc]['address_tag_name_map'][int(read_address)] = read_tag_name
						interpreter_helper[fc]['address_maps'][int(read_address)] = {}
						interpreter_helper[fc]['address_maps'][int(read_address)]['count'] = ModbusHelper.DATA_TYPES_REGISTER_COUNT[read_data_type]
						interpreter_helper[fc]['address_maps'][int(read_address)]['data_type'] = read_data_type
						interpreter_helper[fc]['address_maps'][int(read_address)]['tag_name'] = read_tag_name
						interpreter_helper[fc]['address_maps'][int(read_address)]['scaling_coeff'] = read_entry['scaling_coeff']
						interpreter_helper[fc]['address_maps'][int(read_address)]['scaling_offset'] = read_entry['scaling_offset']

						for call_address in range(int(read_address),int(read_address)+ModbusHelper.DATA_TYPES_REGISTER_COUNT[read_data_type]):
							interpreter_helper[fc]['addresses'].append(call_address)
						break
		
		for fc in interpreter_helper:
			previous_address = None
			for address in sorted(interpreter_helper[fc]['addresses']):
				if previous_address is None:
					call_groups[fc].append({'start_address': address, 'register_count': 1})
				else:
					address_delta = address - previous_address
					if address_delta == 1:
						call_groups[fc][-1]['register_count'] += 1						
					else:
						call_groups[fc].append({'start_address': address, 'register_count': 1})
				previous_address = address

		return call_groups, interpreter_helper

class ModbusTCPClient:
	def __init__(self, server_ip=None, server_port=502, server_id=1, poll_interval=1):
		if server_ip is None:
			print('\t[ERROR] no server_ip argument provided to ModbusTCPClient instance')
			print('\t[ERROR] server_port, server_id and poll_interval arguments will default to 502, 1 and 1 second respectively if not specified')
			print('\t[ERROR] at a minimum, the ModbusTCPClient should know which IP to connect to')
			print('\t[ERROR] here are some examples:')
			print('\t[ERROR]\t\tmy_tcp_client = ModbusTCPClient("10.1.10.30")\t# connect to Modbus TCP Server @ 10.1.10.30 on default port 502 and with default ID 1')
			print('\t[ERROR]\t\tmy_tcp_client = ModbusTCPClient(server_ip="10.1.10.31", server_port=503, server_id=10, poll_interval=5)\t# connect to Modbus TCP Server @ 10.1.10.31 on port 503, with ID 10 and poll every 5 seconds')
			return
		else:
			self.modbus_tcp_server_ip_address = server_ip
		self.modbus_tcp_server_port = server_port
		self.modbus_tcp_server_id = server_id
		self.poll_interval = poll_interval
		self.call_groups = None
		self.interpreter_helper = None
		self.sock = None
		print('\t[INFO] Client will attempt to connect to Modbus TCP Server at:\t\t\t',str(self.modbus_tcp_server_ip_address))
		print('\t[INFO] Client will attempt to connect to Modbus TCP Server on port:\t\t',str(self.modbus_tcp_server_port))
		print('\t[INFO] Client will attempt to connect to Modbus TCP Server with Modbus ID:\t',str(self.modbus_tcp_server_id))
		print('\t[INFO] Client will attempt to poll the Modbus TCP Server every:\t\t\t',str(self.poll_interval)+' seconds')

	def load_template(self, full_path_to_modbus_template_csv=None):
		if full_path_to_modbus_template_csv is None:
			print('\t[ERROR] in ModbusTCPClient.load_template(): please make sure to provide a valid path to a modbus_template.csv file')
			return
		elif not os.path.isfile(full_path_to_modbus_template_csv):
			print('\t[ERROR] in ModbusTCPClient.load_template(): unable to find "'+str(full_path_to_modbus_template_csv)+'"')
			return
		else:
			self.call_groups, self.interpreter_helper = ModbusHelper.parse_template_build_calls(full_path_to_modbus_template_csv)

	def connect(self, timeout=10):
		socket.setdefaulttimeout(timeout)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
		self.sock.connect((self.modbus_tcp_server_ip_address, self.modbus_tcp_server_port))

	def interpret_response(self, response, fc, start_address):
		interpreted_response = {}
		skip_next = False
		for i in range(len(response)):
			address_index = i + start_address
			if fc in ['01', '02']:
				#interpreted_response[self.interpreter_helper[fc]['address_tag_name_map'][address_index]] = response[i]
				interpreted_response[self.interpreter_helper[fc]['address_maps'][address_index]['tag_name']] = response[i]
			else:
				if skip_next:
					skip_next = False
					continue								

				#given_data_type = self.interpreter_helper[fc]['address_data_type_map'][address_index]
				given_data_type = self.interpreter_helper[fc]['address_maps'][address_index]['data_type']
				if given_data_type == 'float32':
					float_32_items = response[i:i+2]
					float_32_binaries = [DataHelper.int_16_unsigned_to_binary(reg) for reg in float_32_items]
					rv = DataHelper.binary_32_to_ieee_754_single_precision_float(''.join(float_32_binaries))
					skip_next = True
				elif given_data_type == 'sint16':
					rv = DataHelper.int_16_unsigned_to_signed(response[i])
					skip_next = False
				elif given_data_type == 'uint16':
					rv = response[i]
					skip_next = False
				else:
					print('\t[ERROR] unsupported data_type of "'+str(given_data_type)+'"')
					skip_next = False
					continue

				# evaluate scaling to apply
				applied_coeff = self.interpreter_helper[fc]['address_maps'][address_index]['scaling_coeff']
				applied_offset = self.interpreter_helper[fc]['address_maps'][address_index]['scaling_offset']
				if (not applied_coeff) ^ (not applied_offset):
					one_scaling_null = True
					applied_coeff_null = not applied_coeff
					both_null_case = False
				elif (not applied_coeff) & (not applied_offset):
					both_null_case = True
				else:
					applied_coeff_null = (math.isnan(float(applied_coeff)) or (applied_coeff is None))
					one_scaling_null =  applied_coeff_null ^ (math.isnan(float(applied_offset)) or (applied_offset is None))
					both_null_case = (math.isnan(float(applied_coeff)) or (applied_coeff is None)) & (math.isnan(float(applied_offset)) or (applied_offset is None))
				if not both_null_case:
					if one_scaling_null:
						if applied_coeff_null:
							applied_coeff = 1
						else:
							applied_offset = 0
					rv = rv*float(applied_coeff) + float(applied_offset)

				interpreted_response[self.interpreter_helper[fc]['address_maps'][address_index]['tag_name']] = rv

		return interpreted_response
	
	def combine_tag_responses(self, lod):
		combined_responses = {}
		for resp in lod:
			for tag in resp:
				combined_responses[tag] = resp[tag]
		return combined_responses

	def cycle_poll(self, time_format = '%Y-%m-%d %H:%M:%S%z'):
		ts_local = datetime.datetime.now().astimezone()
		ts_utc = ts_local.astimezone(datetime.timezone.utc)
		all_interpreted_responses = [{'timestamp_utc': ts_utc.strftime(time_format), 'timestamp_local': ts_local.strftime(time_format)}]
		for modbus_call in self.call_groups:
			modbus_request = ModbusHelper.UMODBUS_TCP_CALL[modbus_call]
			for query in self.call_groups[modbus_call]:
				message = modbus_request(slave_id=self.modbus_tcp_server_id, starting_address=query['start_address'], quantity=query['register_count'])
				#print('\t[INFO] message =',str(message))

				# Response depends on Modbus function code.
				response = tcp.send_message(message, self.sock)
				#print('\t[INFO] response =', str(response))

				interpreted_response = self.interpret_response(response, modbus_call, query['start_address'])
				#print('\t[INFO] interpreted_response =', str(interpreted_response))
				all_interpreted_responses.append(interpreted_response)
		combined_responses = self.combine_tag_responses(all_interpreted_responses)
		print('\t[INFO] combined_responses =', str(combined_responses))
		return combined_responses

	def pretty_print_interpreted_response(self, to_print, max_items_per_line=5):
		headers = list(to_print.keys())		
		header_max_length = max([len(str(h)) for h in headers])		
		#print(' | '.join(str(x) for x in [h.ljust(header_max_length) for h in headers]))
		values = list(to_print.values())
		value_max_length = max([len(str(v)) for v in values])
		max_length = max(header_max_length,value_max_length)

		headers_padded = [h.ljust(max_length) for h in headers]
		values_padded = [str(v).ljust(max_length) for v in values]
		
		for i in range(0,len(headers_padded),max_items_per_line):			
			header_line = ' | '.join(str(x) for x in headers_padded[i:i+max_items_per_line])
			value_line = ' | '.join(str(v) for v in values_padded[i:i+max_items_per_line])
			sep_line = '-'.ljust(len(header_line),'-')
			print(header_line)
			print(value_line)
			print(sep_line)
		print('')