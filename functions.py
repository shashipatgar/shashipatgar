import os
import sys
import traceback
import locale
import threading
import time
import serial.tools.list_ports
import subprocess
from datetime import datetime
from gurux_dlms import GXTime

import tkinter as tk
from tkinter import ttk
from GXSettings import GXSettings
from gurux_serial import GXSerial
from gurux_net import GXNet
from gurux_dlms.enums import ObjectType, DataType, RequestTypes, Security, InterfaceType, DateTimeSkips
from gurux_dlms.objects import GXDLMSObjectCollection, GXDLMSClock, GXDLMSData, GXDLMSActionSchedule, GXDLMSActivityCalendar, GXDLMSDisconnectControl,GXDLMSLimiter
from gurux_dlms.objects.GXDLMSDayProfile import GXDLMSDayProfile
from gurux_dlms.objects.GXDLMSDayProfileAction import GXDLMSDayProfileAction
from gurux_dlms import (
     GXDLMSClient,  GXDateTime, 
    GXDLMSException, GXDLMSExceptionResponse, GXDLMSConfirmedServiceError,
     GXByteBuffer, GXDLMSTranslator, GXDLMSTranslatorMessage, GXReplyData
)



def log_to_file(message):
    log_file = "log.txt"
    with open(log_file, "a") as f:
        f.write(message + "\n")

def ascii_to_hex(input_string):
    hex_string = ''.join(hex(ord(char))[2:] for char in input_string)
    return hex_string.upper()



def read_meter(com_port, hls_password, auth_key, enc_key):
    cache_file_name = 'device_cache_read.xml'
    command = [
        'python', 'read.py', 
        '-S', com_port, 
        '-c', '48', 
        '-a', 'High', 
        '-P', hls_password, 
        '-C', 'AuthenticationEncryption', 
        '-T', '5A454E3132333435', 
        '-A', ascii_to_hex(auth_key), 
        '-B', ascii_to_hex(enc_key), 
        '-D', ascii_to_hex(hls_password)
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)        
        return result.stdout.splitlines() 
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)
        print("Command output:", e.output)
        print("Command stderr:", e.stderr)
        return []
    

def list_available_com_ports(com_port_menu, com_port_var):
    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    com_ports.append("Refresh")
    menu = com_port_menu['menu']
    menu.delete(0, 'end')  # Clear existing options
    for port in com_ports:
        menu.add_command(label=port, command=tk._setit(com_port_var, port))
    if com_ports:
        com_port_var.set(com_ports[0])


def run_tests(log_window):
    log_window.insert("end", "Tests started...\n")
    log_window.see("end")  # Auto-scroll to the end


def read_bill_date(reader,text):
    single_action_schedule = GXDLMSActionSchedule()
    reader.read(single_action_schedule, 4)
            
    # Accessing and printing attribute 4 (execution time list)
    execution_time_list = single_action_schedule.executionTime
    print(f"{text} Billing Date:")
    for execution_time in execution_time_list:
        print(execution_time)

#billing date change
def Bill_date(reader):
    single_action_schedule = GXDLMSActionSchedule()
    text1 = "Current"
    text2 = "New"
    read_bill_date(reader,text1)
    # Creating a new execution time (2nd day of every month at 00:00:00)
    new_execution_time = GXDateTime(datetime.now().replace(day=2, hour=0, minute=0, second=0, microsecond=0))
    new_execution_time.skip = DateTimeSkips.YEAR | DateTimeSkips.MONTH | DateTimeSkips.DAY_OF_WEEK                        
    single_action_schedule.executionTime = [new_execution_time]                    
    reader.write(single_action_schedule, 4)  
    read_bill_date(reader,text2)


#relay control mode change/ load limit function enable or disable
def controlMode(reader):
    dc = GXDLMSDisconnectControl("0.0.96.3.10.255") 
    val = reader.read(dc, 4)  
    print("Curent Control Mode: ",val)
    if val == 4:
        dc.controlMode = 0
    else:
        dc.controlMode = 4
    reader.write(dc, 4)
    val = reader.read(dc, 4) 
    print("New Control Mode: ",val)

#demand integration period change
def Demand_IP(reader):
    mdip = GXDLMSData('1.0.0.8.0.255')
    val = reader.read(mdip, 2) 
    print("Current Demand Integration Period:",val)
    if val == 1800:
        mdip.value = 900
    else:
        mdip.value = 1800
    reader.write(mdip, 2)  
    val = reader.read(mdip, 2)
    print("New Demand Integration Period:",val)  

    print("Demand Integration Period programming completed successfully")
    return 0

#load limit value change (now reading only)
def Load_limit(reader,settings):
     # Load limit (KW) programming
    load_limit = GXDLMSLimiter('0.0.17.0.0.255')
    val = reader.read(load_limit, 3)
    val2 = reader.read(load_limit, 4)
            
    print("Threshold Active:", val)
    print("Threshold Normal:", val2)
            
    # New value to set
    new_load_limit = val+100

    load_limit.thresholdNormal = new_load_limit

    # Write the updated load_limit
    e = GXReplyData()
    e.index = 4
    e.value = new_load_limit
    load_limit.setValue(settings,e)

    # Read back the value to verify 
    updated_val = reader.read(load_limit, 3)
    print("New Load limit (KW):", updated_val)

#meter mode programmin(Uni/Net)
def meter_mode(reader):
    metering_mode = GXDLMSData('0.0.94.96.19.255')
    val = reader.read(metering_mode, 2)

    if val == 0:
        print("Current Metering mode: Unidirectional")
        metering_mode.value = 1
    else:
        print("Current Metering mode: Bidirectional")
        metering_mode.value = 0

    reader.write(metering_mode, 2)
    val = reader.read(metering_mode, 2)

    if val == 0:
        print("Metering mode changed to Unidirectional")
    else:
        print("Metering mode changed to Bidirectional")

#payment mode change
def payment_mode(reader):
    payment_mode = GXDLMSData('0.0.94.96.20.255')
    val = reader.read(payment_mode, 2)

    if val == 1:
        print("Current Payment mode: Prepaid")
        payment_mode.value = 0
    else:
        print("Current Payment mode: Postpaid")
        payment_mode.value = 1

    reader.write(payment_mode, 2)
    val = reader.read(payment_mode, 2)

    if val == 1:
        print("Payment mode changed to Prepaid")
        payment_mode.value = 0
    else:
        print("Payment mode changed to Postpaid")

#profile capture IP programming
def Profle_capture_IP(reader):
    blocl_load_ip = GXDLMSData('1.0.0.8.4.255')
    val = reader.read(blocl_load_ip, 2)             
    print("Current Profle Capture Period:",val)
    if val == 1800:
        blocl_load_ip.value = 900
    else:
        blocl_load_ip.value = 1800
    reader.write(blocl_load_ip, 2)
    val = reader.read(blocl_load_ip, 2)             
    print("New Current Profle Capture Period:",val)  

#relay disconnect and connect
def relay_connect(reader):
    reply = GXReplyData() 
    dc = GXDLMSDisconnectControl("0.0.96.3.10.255")  
    val = reader.read(dc, 2)        
    if val :
        reader.readDataBlock(dc.remoteDisconnect(reader.client), reply)
        print("Relay disconnected")
    else:
        reader.readDataBlock(dc.remoteReconnect(reader.client),reply )
        print("Relay connected")


#rtc programming
def RTC_Programming(reader):
    RTC = GXDLMSClock()
    val = reader.read(RTC, 2)
    print("Current RTC value:", val.value)            
    RTC.time = GXDateTime(datetime.now())
    reader.write(RTC, 2)            
    new_val = reader.read(RTC, 2)
    print("New RTC value:", new_val.value)            
    print("RTC programming completed successfully")
    return 0

#TOD programming
def TOD(reader,settings):
    activity_calendar = GXDLMSActivityCalendar("0.0.13.0.0.255")

    # Reading attributes of GXDLMSActivityCalendar object
    for i in range(1, 11):
        reader.read(activity_calendar, i)

    # Print Day Profile Table Active
    print("Day Profile Table Active:")
    for day in activity_calendar.dayProfileTableActive:
        print(f"  Day ID: {day.dayId}")
        for action in day.daySchedules:
            print(f"    Start Time: {action.startTime}, Script Logical Name: {action.scriptLogicalName}, Script Selector: {action.scriptSelector}")

    # Print Day Profile Table Passive
    print("Day Profile Table Passive:")
    for day in activity_calendar.dayProfileTablePassive:
        print(f"  Day ID: {day.dayId}")
        for action in day.daySchedules:
            print(f"    Start Time: {action.startTime}, Script Logical Name: {action.scriptLogicalName}, Script Selector: {action.scriptSelector}")

    print("Time:", activity_calendar.time)

    # Create new Day Profile
    new_day_profile = GXDLMSDayProfile()
    new_day_profile.dayId = 0
    new_day_profile.daySchedules = [
        GXDLMSDayProfileAction(startTime=GXTime("00:00:00", "%H:%M:%S"), scriptLogicalName="0.0.10.0.100.255", scriptSelector=1),
        GXDLMSDayProfileAction(startTime=GXTime("10:00:00", "%H:%M:%S"), scriptLogicalName="0.0.10.0.100.255", scriptSelector=2)
    ]

    # Update the passive day profile table
    activity_calendar.dayProfileTablePassive = [new_day_profile]

    # Write updated activity calendar
    result = reader.write(activity_calendar, 10)

    # Activate the passive calendar using the appropriate method from the client
    # Assuming settings.client has a method to activate passive calendar
    if hasattr(settings.client, 'activatePassiveCalendar'):
        result = settings.client.activatePassiveCalendar(activity_calendar)
        if result:
            print("Passive calendar activated successfully.")
        else:
            print("Failed to activate passive calendar.")
    else:
        print("Method 'activatePassiveCalendar' not supported.")

    # Read active calendar
    reader.read(activity_calendar, 5)
    print("Updated Active Calendar:")
    for day in activity_calendar.dayProfileTableActive:
        print(f"  Day ID: {day.dayId}")
        for action in day.daySchedules:
            print(f"    Start Time: {action.startTime}, Script Logical Name: {action.scriptLogicalName}, Script Selector: {action.scriptSelector}")


def read_nameplate(reader):
    #sampleclient.main()
    results = []
    read_list = {"Meter Serial No.:": '0.0.96.1.0.255',
                         "Device ID: ": '0.0.96.1.2.255',                         
                         "Manufacturer Name: ":"0.0.96.1.1.255",
                         "Firmware: ": '1.0.0.2.0.255',
                         "Meter type: ": '0.0.94.91.9.255',
                         "Category: ": '0.0.94.91.11.255',
                         "Current rating: ":"0.0.94.91.12.255",
                         "Year of manufacturer: ":'0.0.96.1.4.255',
                         }
            
    for key, value in read_list.items():
                obj = GXDLMSData(value)
                val = reader.read(obj, 2)
                result = f"{key} {val}"
                print(result)
                results.append(result)
            
    return results   