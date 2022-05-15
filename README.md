# modbus-dl
**modbus-dl** is a simple Modbus TCP client and data logger implementation in Python based on [uModbus](https://github.com/AdvancedClimateSystems/uModbus).  

modbus-dl will connect to a live Modbus TCP Server accessible on the network, poll the required registers at a desired interval/scan rate and log the data to disk either in .csv or .json format.  

## Pre-requisite  
There are two (2) important configuration files to setup for modbus-dl to work properly:  
&ensp;(1) a Modbus configuration file in .json format; this is where you define the Modbus TCP Server to connect to (IP:Port:ID), the scan rate, information about the logged data such as type (.csv or .json), file name prefix, etc.   
&ensp;(2) a Modbus template file in .csv format; this is where you define which register addresses to query, their read type (ex: Holding Registers, Input Registers) and data type (ex: float32, uint16, coil), you can translate the Modbus address into a more user-friendly tag name and even apply linear scaling if needed.  
When calling modbus-dl, pass the path to these two (2) configuration files as arguments.  

## Usage  
```text
path/to/modbus-dl.py  
	-c < path to Modbus configuration file (.json format) > (--config) [REQUIRED]  
	-t < path to Modbus template file (.csv format) > (--template) [REQUIRED]  
	-o < path to output log files, default uses 'data/' folder when not specified > (--output) [optional]  
	-q to be quiet and to not display the interval Modbus reads, default False/verbose (--quiet) [optional]  
	-n to make modbus-dl behave as a "real-time" Modbus TCP Client without data logging, default False/data logging enabled (--no-data-logging) [optional]  
	-h to display the help message and exit (--help) [optional]  
```

## Configuration & Template files  
### (1) Modbus configuration file in .json format   
#### server_ip
&ensp;'server_ip': a correctly formatted string representing the IP address or hostname of the Modbus TCP Server to connect to; ex: "10.0.1.10" or "localhost"  
#### server_port
&ensp;'server_port': a strictly positive integer [1;65535] representing the TCP port where the Modbus TCP Server process is running; ex: 502  
#### server_id
&ensp;'server_id': a positive integer [0;255] representing the Modbus Server ID in use by the Modbus TCP Server; ex: 10  
#### server_timeout_seconds
&ensp;'server_timeout_seconds': a positive floating point representing the number of seconds to use as timeout when connecting to the Modbus TCP Server; ex: 3.0  
#### poll_interval_seconds
&ensp;'poll_interval_seconds': a positive floating point representing the time interval in seconds between two (2) consecutive Modbus polls (i.e. scan rate); ex: 1.0  
#### in_memory_records
&ensp;'in_memory_records': a strictly positive integer (>0) representing the number of data records (timestamps) that modbus-dl will hold in memory before writing to disk in the log file; ex: 10  
#### file_rotation['max_file_records']
&ensp;'file_rotation['max_file_records']': a strictly positive integer (>0) representing the maximum number of data records (timestamps) that a single log file will have before being rotated to a new file; ex: 30  
#### log_file_type
&ensp;'log_file_type': a string of either "csv" or "json" to define the log file type to use  
#### log_file_name
&ensp;'log_file_name': a string with the desired prefix log file name; ex: "my_logged_data"  
#### json_indent
&ensp;'json_indent': either null or a positive integer (>0) representing the desired indentation level to use with a "json" log_file_type; ex: null or 4  

### (2) Modbus template file in .csv format  
#### address
&ensp; 'address': the Modbus register address (**zero-based**) to poll/query for a desired parameter    
#### read_type
&ensp; 'read_type': the Modbus function code to use for that address; ex: FC01, FC02, FC03, FC04 or Coil, DI, HR, IR, see **Supported read types** section below   
#### data_type
&ensp; 'data_type': the data type to interpret the returned data; ex: float32, will also tell modbus-dl to request two (2) consecutive 16-bit registers, see **Supported data types** section below  
#### tag_name
&ensp; 'tag_name': the tag name corresponding to the queried address; ex: voltage or temperature  
#### scaling_coeff
&ensp; 'scaling_coeff': if needed, the scaling coefficient to apply on the raw data; scaled = scaling_coeff * raw + scaling_offset   
#### scaling_offset
&ensp; 'scaling_offset': if needed, the scaling offset to apply on the raw data; scaled = scaling_coeff * raw + scaling_offset  

## Example  
Ex:  
```bash
./modbus-dl.py -c config/modbus_config_10.json -t template/modbus_template_10.csv  
```

In the example above, we are telling modbus-dl to use the 'modbus_config_10.json' file located in the 'config/' folder and to use the 'modbus_template_10.csv' file located in the 'template/' folder. The '-q' switch option was not provided so modbus-dl will NOT be quiet and will instead be verbose and display the queried data in the terminal prompt at each poll interval. The '-n' switch option was not provided so modbus-dl will perform its intended data logging function. Specifying the '-n' switch option will make modbus-dl be a simple "real-time" Modbus TCP Client; displaying the returned data at each poll interval but not performing any data logging (modbus-dl has the option to be used that way if data logging to the local file system is not required). The '-o' switch option was not specified so modbus-dl will default to storing the log files in the 'data/' folder. If specifying a different location, make sure the folder is created and does exist before using.    

You can view the content and format examples of the config and template files in the config/ and template/ folders respectively.  
You can also see samples of created log files in the data/ folder, this was run against a local Modbus TCP Server simulator using randomly generated data.  

## Supported data types
### di (use with read_type of FC02 or DI, Read Discrete Inputs)
&ensp;&ensp;di: 1-bit digital/discrete input status, one (1) single register/address, 1 or 0, True or False, ON or OFF  
### coil (use with read_type of FC01 or Coil, Read Coils)
&ensp;&ensp;coil: 1-bit digital/discrete output coil status, one (1) single register/address, 1 or 0, True or False, ON or OFF  
### uint16 (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;uint16: 16-bit unsigned integer (unsigned short), one (1) single 16-bit register/address, values in range [0;65535], Big-Endian order [A B]  
### sint16 (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;sint16: 16-bit signed integer (signed short), one (1) single 16-bit register/address, values in range [−32,767;+32,767], Big-Endian order [A B]  
### float32 (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;float32: 32-bit IEEE 754 single precision (32-bit) floating-point, two (2) consecutive 16-bit registers/addresses, Big-Endian order [A B C D]  
### float64 (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;float64: 64-bit IEEE 754 double precision (64-bit) floating-point (double), four (4) consecutive 16-bit registers/addresses, Big-Endian order [A B C D E F G H]  
### packedbool (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;packedbool: "packed boolean", one (1) single 16-bit register/address, unpacks each one of the 16 bits in the register in Big-Endian order to determine each bit's value/status, either 1 or 0, True or False, ON or OFF  
### ruint16 (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;ruint16': "reversed" byte-swapped 16-bit unsigned integer (unsigned short), one (1) single 16-bit register/address, values in range [0;65535], Little-Endian order [B A]
### rsint16 (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;rsint16: "reversed" byte-swapped 16-bit signed integer (signed short), one (1) single 16-bit register/address, values in range [−32,767;+32,767], Little-Endian order [B A]
### rfloat32_byte_swap (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;rfloat32_byte_swap: "reversed" byte-swapped 32-bit IEEE 754 single precision (32-bit) floating-point, two (2) consecutive 16-bit registers/addresses, Mid-Big-Endian order [B A D C] # [A B C D] -> [B A] [D C]  
### rfloat32_word_swap (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;rfloat32_word_swap: "reversed" word-swapped 32-bit IEEE 754 single precision (32-bit) floating-point, two (2) consecutive 16-bit registers/addresses, Mid-Little-Endian order [C D A B] # [A B C D] -> [C D] [A B]  
### rfloat32_byte_word_swap (use with read_type of FC03/FC04 or HR/IR, Read Holding Registers/Read Input Registers)
&ensp;&ensp;rfloat32_byte_word_swap: "reversed" word-swapped AND byte-swapped 32-bit IEEE 754 single precision (32-bit) floating-point, two (2) consecutive 16-bit registers/addresses, Little-Endian order [D C B A] # [A B C D] -> [D C] [B A]  

## Supported read types (from uModbus)
### Modbus function code 01, FC01: [Read Coils](https://umodbus.readthedocs.io/en/latest/functions.html#read-coils)
### Modbus function code 02, FC02: [Read Discrete Inputs](https://umodbus.readthedocs.io/en/latest/functions.html#read-discrete-inputs)
### Modbus function code 03, FC03: [Read Holding Registers](https://umodbus.readthedocs.io/en/latest/functions.html#read-holding-registers)
### Modbus function code 04, FC04: [Read Input Registers](https://umodbus.readthedocs.io/en/latest/functions.html#read-input-registers)
