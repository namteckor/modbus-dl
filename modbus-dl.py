#!/usr/bin/python3

import sys, getopt, datetime
from scripts import modbus_helper

time_format = '%Y-%m-%d %H:%M:%S%z'

start_local = datetime.datetime.now().astimezone()
start_utc = start_local.astimezone(datetime.timezone.utc)
print('')
print('\t[INFO] start_local\t=', start_local.strftime(time_format))
print('\t[INFO] start_utc\t=', start_utc.strftime(time_format))
print('')

argv = sys.argv[1:]

short_options = 'c:t:o:qn' 
long_options =  ['config=','template=','output=','quiet','no-data-logging']

try:
	opts, args = getopt.getopt(argv,short_options,long_options)
except getopt.error as err:
	print('\tERROR!')
	print('\tUsage: modbus-dl.py -c <path to Modbus configuration file (.json format)> [REQUIRED]')
	print('\t\t'+'-t <path to Modbus template file (.csv format)> [REQUIRED]')
	print('\t\t'+'-o <path to output log files> [optional]')
	print('\t\t'+'-q <to be quiet and to not display the interval Modbus reads, default False> [optional]')
	print('\t\t'+'-n to make modbus-dl behave as a "real-time" Modbus TCP Client without data logging [optional]')
	print(str(err))
	sys.exit()

list_of_options_passed = []
for item in opts:
	list_of_options_passed.append(item[0])

if ('-c' not in list_of_options_passed) and ('--config' not in list_of_options_passed):
	print('\tERROR!')
	print('\tMissing required argument -c or --config <path to Modbus configuration file (.json format)> [REQUIRED]')
	print('')
	print('\tUsage: modbus-dl.py -c <path to Modbus configuration file (.json format)> [REQUIRED]')
	print('\t\t'+'-t <path to Modbus template file (.csv format)> [REQUIRED]')
	print('\t\t'+'-o <path to output log files> [optional]')
	print('\t\t'+'-q <to be quiet and to not display the interval Modbus reads, default False> [optional]')
	print('\t\t'+'-n to make modbus-dl behave as a "real-time" Modbus TCP Client without data logging [optional]')
	sys.exit()
elif ('-t' not in list_of_options_passed) and ('--template' not in list_of_options_passed):
	print('\tERROR!')
	print('\tMissing required argument -t or --template <path to Modbus template file (.csv format)> [REQUIRED]')
	print('')
	print('\tUsage: modbus-dl.py -c <path to Modbus configuration file (.json format)> [REQUIRED]')
	print('\t\t'+'-t <path to Modbus template file (.csv format)> [REQUIRED]')
	print('\t\t'+'-o <path to output log files> [optional]')
	print('\t\t'+'-q <to be quiet and to not display the interval Modbus reads, default False> [optional]')
	print('\t\t'+'-n to make modbus-dl behave as a "real-time" Modbus TCP Client without data logging [optional]')
	sys.exit()

# Set some defaults
be_quiet = False
output_log_files_location = None
data_logging = True

for opt, arg in opts:
	if opt in ('-c', '--config'):
		modbus_config_location = str(arg)
	elif opt in ('-t', '--template'):
		modbus_template_location = str(arg)
	elif opt in ('-o', '--output'):
		output_log_files_location = str(arg)
	elif opt in ('-q','--quiet'):
		be_quiet = True
	elif opt in ('-n','--no-data-logging'):
		data_logging = False
	else:
		print('\tERROR!')
		print('\tUsage: modbus-dl.py -c <path to Modbus configuration file (.json format)> [REQUIRED]')
		print('\t\t'+'-t <path to Modbus template file (.csv format)> [REQUIRED]')
		print('\t\t'+'-o <path to output log files> [optional]')
		print('\t\t'+'-q <to be quiet and to not display the returned data at each interval read, default False> [optional]')
		print('\t\t'+'-n to make modbus-dl behave as a "real-time" Modbus TCP Client without data logging [optional]')
		print(str(err))
		sys.exit()

modbus_logger = modbus_helper.ModbusTCPDataLogger(
		full_path_to_modbus_config_json=modbus_config_location, 
		full_path_to_modbus_template_csv=modbus_template_location, 
		full_path_to_logged_data=output_log_files_location, 
		quiet=be_quiet,
		data_logging=data_logging
	)		