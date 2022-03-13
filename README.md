# modbus-dl
**modbus-dl** is a simple Modbus TCP data logger implementation in Python based on [umodbus](https://github.com/AdvancedClimateSystems/uModbus).  

modbus-dl will connect to a live Modbus TCP Server accessible on the network, poll the required registers at a desired interval/scan rate and log the data to disk either in .csv or .json format.  

{Pre-requisite} there are two (2) important configuration files to setup for modbus-dl to work properly:  
&ensp;(1) a Modbus configuration file in .json format; this is where you define the Modbus TCP Server to connect to (IP:Port:ID), the scan rate, information about the logged data such as type (.csv or .json), file name prefix, etc.   
&ensp;(2) a Modbus template file in .csv format; this is where you define which register addresses to query, their read type (ex: Holding Registers, Input Registers) and data type (ex: float32, uint16, coil), you can translate the Modbus address into a more user-friendly tag name and even apply linear scaling if needed  
When calling modbus-dl, pass the path to these two (2) configuration files as arguments.  

Usage: 

&ensp;path/to/modbus-dl.py  
&ensp;&ensp;-c < path to Modbus configuration file (.json format) > (--config) [REQUIRED]  
&ensp;&ensp;-t < path to Modbus template file (.csv format) > (--template) [REQUIRED]  
&ensp;&ensp;-o < path to output log files, default uses 'data/' folder when not specified > (--output) [optional]  
&ensp;&ensp;-q to be quiet and to not display the interval Modbus reads, default False/verbose (--quiet) [optional]  
&ensp;&ensp;-n to make modbus-dl behave as a "real-time" Modbus TCP Client without data logging, default False/data logging enabled (--no-data-logging) [optional]  

Ex: ./modbus-dl.py -c config/modbus_config_10.json -t config/modbus_template_10.csv  

In the example above, we are telling modbus-dl to use the 'modbus_config_10.json' file located in the 'config/' folder and to use the 'modbus_template_10.csv' file also located in the 'config/' folder. The '-q' switch option was not provided so modbus-dl will NOT be quiet and instead will be verbose and display the queried data in the terminal prompt at each poll interval. The '-n' switch option was not provided so modbus-dl will perform its intended data logging function. Specifying the '-n' switch option will make modbus-dl be a simple "real-time" Modbus TCP Client; displaying the returned data at each poll interval but not performing any data logging (modbus-dl has the option to be used that way if data logging to the local file system is not required). The '-o' switch option was not specified so modbus-dl will default to storing the log files in the 'data/' folder. If specifying a different location, make sure the folder is created and does exist before using.    

You can view the content and format examples of the config and template files in the config/ folder.
You can also see samples of created log files in the data/ folder, this was run against a local Modbus TCP Server simulator using randomly generated data.

(1) Modbus configuration file in .json format   
&ensp;'server_ip': a correctly formatted string representing the IP address or hostname of the Modbus TCP Server to connect to; ex: "10.0.1.10" or "localhost"  
&ensp;'server_port': a strictly positive integer [1;65535] representing the TCP port where the Modbus TCP Server process is running; ex: 502  
&ensp;'server_id': a positive integer [0;255] representing the Modbus Server ID in use by the Modbus TCP Server; ex: 10  
&ensp;'server_timeout_seconds': a positive floating point representing the number of seconds to use as timeout when connecting to the Modbus TCP Server; ex: 3.0  
&ensp;'poll_interval_seconds': a positive floating point representing the time interval in seconds between two (2) consecutive Modbus polls (i.e. scan rate); ex: 1.0  
&ensp;'in_memory_records': a strictly positive integer (>0) representing the number of data records (timestamp) that modbus-dl will hold in memory before writing to disk in the log file; ex: 10  
&ensp;'file_rotation['max_file_records']': a strictly positive integer (>0) representing the maximum number of data records (timestamp) that a single log file will have before being rotated to a new file; ex: 30  
&ensp;'log_file_type': a string of either "csv" or "json" to tell modbus-dl which log file type to use  
&ensp;'log_file_name': a string with the desired prefix log file name; ex: "my_logged_data"  
&ensp;'json_indent': either null or a positive integer (>0) representing the desired indentation level to use with a "json" log_file_type; ex: null or 4  

(2) Modbus template file in .csv format  
&ensp; 'address': the Modbus register address (**zero-based**) to poll/query for a desired parameter    
&ensp; 'read_type': the Modbus function code to use for that address; ex: FC01, FC02, FC03, FC04 or Coil, DI, HR, IR   
&ensp; 'data_type': the data type to interpret the returned data; ex: float32, will also tell modbus-dl to request two (2) consecutive 16-bit registers  
&ensp; 'tag_name': the tag name corresponding to the queried address; ex: voltage or temperature  
&ensp; 'scaling_coeff': if needed, the scaling coefficient to apply on the raw data; scaled = scaling_coeff * raw + scaling_offset   
&ensp; 'scaling_offset': if needed, the scaling offset to apply on the raw data; scaled = scaling_coeff * raw + scaling_offset      
