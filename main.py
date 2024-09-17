import calendar
import os
import sys
import traceback
from gurux_serial import GXSerial
from gurux_net import GXNet
from gurux_dlms.enums import ObjectType
from gurux_dlms.objects.GXDLMSObjectCollection import GXDLMSObjectCollection
import serial
from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader
from gurux_dlms.GXDLMSClient import GXDLMSClient
from gurux_common.GXCommon import GXCommon
from gurux_dlms.enums.DataType import DataType
import locale
from gurux_dlms.GXDateTime import GXDateTime
from gurux_dlms.internal._GXCommon import _GXCommon
from gurux_dlms import GXDLMSException, GXDLMSExceptionResponse, GXDLMSConfirmedServiceError, GXDLMSTranslator
from gurux_dlms import GXByteBuffer, GXDLMSTranslatorMessage, GXReplyData
from gurux_dlms.enums import RequestTypes, Security, InterfaceType
from gurux_dlms.secure.GXDLMSSecureClient import GXDLMSSecureClient
from gurux_dlms.objects import GXDLMSClock

import time
import tkinter as tk
from tkinter import END, ttk, filedialog
from datetime import datetime, timedelta
import threading
import tkinter.messagebox as msgbox
from tkinter import font
import ctypes




def rearrange_date_time(input_datetime):
    datetime_obj = datetime.fromisoformat(input_datetime)
    formatted_date = datetime_obj.strftime("%d-%m-%Y %H:%M:%S")
    return formatted_date

def read_rtc(obj):
    RTC = GXDLMSClock("0.0.1.0.0.255")
    rtc_val = obj.read(RTC, 2)
    rtc_str = str(rtc_val.value)  
    rtc = rearrange_date_time(rtc_str) 
    return rtc

def set_new_md_rtc(meter_rtc,rtc_duration):
    time_interval_minutes = int(rtc_duration)    
    meter_datetime = str(meter_rtc) 
    datetime_obj = datetime.fromisoformat(meter_datetime)
    last_day_of_month = calendar.monthrange(datetime_obj.year, datetime_obj.month)[1]
    last_day_datetime = datetime(datetime_obj.year, datetime_obj.month, last_day_of_month, 23, 59, 59)
    new_rtc_datetime = last_day_datetime - timedelta(minutes=time_interval_minutes)
    return new_rtc_datetime

def set_new_ls_rtc(meter_rtc):
    meter_datetime = str(meter_rtc) 
    datetime_obj = datetime.fromisoformat(meter_datetime)
    new_rtc_datetime = datetime_obj + timedelta(hours=24)
    return new_rtc_datetime

class SampleClient:
    @classmethod
    def main(cls, args, test_num, rtc_duration):
        logfile_path = "Rollover_log.txt"
        
        
        reader = None
        settings = GXSettings()
        client = None
        try:
            ret = settings.getParameters(args)
            if ret != 0:
                return
            if not isinstance(settings.media, (GXSerial, GXNet)):
                raise Exception("Unknown media type.")
				
            reader = GXDLMSReader(settings.client, settings.media, settings.trace, settings.invocationCounter)
            try:
                settings.media.open()
            except Exception as e:                
                error_message = str(ex)
                print("Error", error_message)
                
            reader.initializeConnection()
            reply = GXReplyData()
            clock1 = GXDLMSClock("0.0.1.0.0.255")
            rtc_val = reader.read(clock1, 2)
            rtc_str = str(rtc_val.value)                   
            print(f"RTC: {rearrange_date_time(rtc_str)}")
            
            if test_num == 1:  
                present_month_end = set_new_md_rtc(rtc_val.value, rtc_duration)
                clock1.time = GXDateTime(present_month_end)
                reader.write(clock1, 2)
                new_rtc = read_rtc(reader)
                print(f"RTC forced: {new_rtc}")

            if test_num == 2: 
                new_rtc = set_new_ls_rtc(rtc_val.value)      
                clock1.time = GXDateTime(new_rtc)                                
                reader.write(clock1, 2)
                new_rtc = read_rtc(reader)
                print(f"RTC forced: {new_rtc}")  

        except (ValueError, GXDLMSException, GXDLMSExceptionResponse, GXDLMSConfirmedServiceError) as ex:
            print(f"Error: {ex}")                
        except (KeyboardInterrupt, SystemExit):
            traceback.print_exc()
        except Exception as ex:
            print(f"Unexpected error: {ex}")
            traceback.print_exc()
        finally:
            if settings.media:
                settings.media.close()
            if reader:
                reader.close()
            print("-" * 20)
        


class RTC_forcing:
    def __init__(self, test_val, test_duration, bill_count, LS_days, args, stop_event) -> None:
        self.test_val = test_val
        self.test_duration = test_duration
        self.bill_count = bill_count
        self.LS_days = LS_days
        self.args = args
        self.stop_event = stop_event

    def printvals(self):
        print(f"Test Value: {self.test_val}")
        print(f"Test Duration: {self.test_duration}")
        print(f"Bill Count: {self.bill_count}")
        print(f"LS Days: {self.LS_days}")
    
    def start_test(self):
        try:
            if self.test_val == 1:  # Billing
                count = self.bill_count
                interval_label = "Bill count"
                test_num = 1
            elif self.test_val == 2:  # Daily Load Profile
                count = self.LS_days
                interval_label = "Days"
                test_num = 2
            elif self.test_val == 3:  # Run Both
                self._run_both()
                return

            self._run_test(count, interval_label, test_num)

        except KeyboardInterrupt:
            print("RTC forcing process interrupted.")
        finally:
            pass
            #print("<-- Completed -->")

    def _run_test(self, count, interval_label, test_num):
        for i in range(count):
            if self.stop_event.is_set():
                print("RTC forcing process stopped.")
                break
            print(f"{interval_label}: {i + 1}")
            SampleClient.main(self.args, test_num, self.test_duration)
            sleep_duration = self.test_duration * 60  # Convert minutes to seconds
            for _ in range(int(sleep_duration)):
                if self.stop_event.is_set():
                    break
                time.sleep(1)
            if self.stop_event.is_set():
                break
            

    def _run_both(self):
        print("Daily Load Profile")
        self._run_test(self.LS_days, "Days", 2)
        print("Billing")
        self._run_test(self.bill_count, "Bill count", 1)

