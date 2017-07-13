#!/usr/bin/python
##-------------------------------------------------------------------
## @copyright 2017 DennyZhang.com
## Licensed under MIT
##   https://raw.githubusercontent.com/DennyZhang/devops_public/master/LICENSE
##
## File : node_usage.py
## Author : Denny <denny@dennyzhang.com>
## Description : Show OS and process resource usage: CPU, RAM and disk
## Sample:
##         python ./node_usage.py
##             {"disk": {"disk_0": {"free_gb": "170.42", "total_gb": "377.83", "partition": "/", "used_percentage": "49.82%", "used_gb": "188.22"}, "free_gb": "170.42", "total_gb": "377.83", "used_percentage": "/ 49.82%(188.22gb/377.83gb)", "used_gb": "188.22"}, "hostname": "totvsjenkins", "ram": {"used_percentage": "8.79%(2.07gb/23.55gb)", "ram_buffers_gb": "8.17", "ram_available_gb": "21.40", "ram_total_gb": "23.55", "ram_used_gb": "2.07"}}
##
## --
## Created : <2017-05-22>
## Updated: Time-stamp: <2017-07-13 16:55:28>
##-------------------------------------------------------------------
import os, sys
import psutil
import argparse
import json
import socket
import subprocess

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

# http://www.programcreek.com/python/example/53878/psutil.disk_usage
def get_disk_usage(output_dict):
    my_dict = {}
    i = 0
    sum_total_gb = 0
    sum_used_gb = 0
    sum_free_gb = 0
    for part in psutil.disk_partitions(all=False):
        dist_entry_dict = {}
        usage = psutil.disk_usage(part.mountpoint)
        total_gb = float(usage.total)/(1024*1024*1024)
        used_gb = float(usage.used)/(1024*1024*1024)
        free_gb = float(usage.free)/(1024*1024*1024)

        sum_total_gb = sum_total_gb + total_gb
        sum_used_gb = sum_used_gb + used_gb
        sum_free_gb = sum_free_gb + free_gb

        dist_entry_dict["partition"] = part.mountpoint
        dist_entry_dict["total_gb"] = "{:.2f}".format(total_gb)
        dist_entry_dict["used_gb"] = "{:.2f}".format(used_gb)
        dist_entry_dict["free_gb"] = "{:.2f}".format(free_gb)
        current_used_percentage = float(dist_entry_dict["used_gb"])*100/float(dist_entry_dict["total_gb"])
        percent_ratio = "{:.2f}".format(current_used_percentage) + "%"
        dist_entry_dict["used_percentage"] = percent_ratio

        if "used_percentage" in my_dict:
            my_dict["used_percentage"] = "%s, %s %s(%sgb/%sgb)" % \
                                         (my_dict["used_percentage"], \
                                          part.mountpoint, percent_ratio,
                                          dist_entry_dict["used_gb"], dist_entry_dict["total_gb"])
        else:
            my_dict["used_percentage"] = "%s %s(%sgb/%sgb)" % \
                                         (part.mountpoint, percent_ratio, \
                                          dist_entry_dict["used_gb"], dist_entry_dict["total_gb"])

        my_dict["disk_%d" % i] = dist_entry_dict
        i = i + 1

    my_dict["total_gb"] = "{:.2f}".format(sum_total_gb)
    my_dict["used_gb"] = "{:.2f}".format(sum_used_gb)
    my_dict["free_gb"] = "{:.2f}".format(sum_free_gb)

    output_dict["disk"] = my_dict

def get_memory_usage(output_dict):
    my_dict = {}
    memory_usage = psutil.virtual_memory()
    memory_total_gb = float(memory_usage.total)/(1024*1024*1024)
    memory_used_gb = float(memory_usage.used)/(1024*1024*1024)
    memory_available_gb = float(memory_usage.available)/(1024*1024*1024)
    memory_buffers_gb = float(memory_usage.buffers)/(1024*1024*1024)
    my_dict["ram_total_gb"] = "{:.2f}".format(memory_total_gb)
    my_dict["ram_used_gb"] = "{:.2f}".format(memory_used_gb)
    my_dict["ram_available_gb"] = "{:.2f}".format(memory_available_gb)
    my_dict["ram_buffers_gb"] = "{:.2f}".format(memory_buffers_gb)
    percent_ratio = float(my_dict["ram_used_gb"])*100/float(my_dict["ram_total_gb"])
    my_dict["used_percentage"] = "%s(%sgb/%sgb)" % \
                                 ("{:.2f}".format(percent_ratio) + "%", \
                                  my_dict["ram_used_gb"], my_dict["ram_total_gb"])

    output_dict["ram"] = my_dict

# https://stackoverflow.com/questions/276052/how-to-get-current-cpu-and-ram-usage-in-python
def get_cpu_usage(output_dict):
    p = psutil.Process(os.getpid())
    output_dict["cpu_count"] = psutil.cpu_count()
    with open('/proc/loadavg') as f:
        content = f.readlines()
    output_dict["cpu_load"] = content[0].rstrip("\n")

def get_service_status(output_dict, service_command):
    command_output = subprocess.check_output(service_command.split(" "))
    output_dict["service_status"] = "Service Status: \n%s" % (command_output.decode("utf-8"))

def tail_log_file(output_dict, log_file, tail_log_num):
    log_message = "tail -n %d %s:" % (tail_log_num, log_file)
    # TODO: implement this logic
    log_message = "%s\nTODO: implement this logic\nhello, world\nthis is a test" % (log_message)
    output_dict["tail_log_file"] = log_message

def show_usage(service_command, log_file, tail_log_num):
    output_dict = {}
    output_dict['hostname'] = socket.gethostname()
    output_dict['ipaddress_eth0'] = get_ip_address()

    if service_command is not None:
        get_service_status(output_dict, service_command)

    if log_file is not None:
        tail_log_file(output_dict, log_file, tail_log_num)

    get_memory_usage(output_dict)
    get_disk_usage(output_dict)
    get_cpu_usage(output_dict)

    # show output as json
    print(json.dumps(output_dict))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check_service_command', required=False, \
                        help="What command to check service status. If not given, service check will be skipped", type=str)
    parser.add_argument('--log_file', required=False, \
                        help="Tail log file", type=str)
    parser.add_argument('--tail_log_num', required=False, default=20,\
                        help="Tail last multiple lines of log file", type=int)
    l = parser.parse_args()
    show_usage(l.pid_file, l.log_file, l.tail_log_num)
## File : node_usage.py ends
