import os
import sys
import traceback
from gurux_serial import GXSerial
from gurux_net import GXNet
from gurux_dlms.enums import ObjectType
from gurux_dlms.objects.GXDLMSObjectCollection import GXDLMSObjectCollection
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

from datetime import datetime
from gurux_dlms.objects.GXDLMSDisconnectControl import GXDLMSDisconnectControl
from gurux_dlms.objects import GXDLMSClock, GXDLMSData, GXDLMSActionSchedule, GXDLMSActivityCalendar, GXDLMSLimiter
from gurux_dlms.enums.DateTimeSkips import DateTimeSkips

from gurux_dlms.objects.GXDLMSActivityCalendar import GXDLMSActivityCalendar
from gurux_dlms.objects.GXDLMSDayProfile import GXDLMSDayProfile
from gurux_dlms.objects.GXDLMSDayProfileAction import GXDLMSDayProfileAction
from gurux_dlms.enums import ClockStatus
from gurux_dlms import GXTime

from gurux_dlms.enums import ErrorCode
from gurux_dlms.objects.GXDLMSEmergencyProfile import GXDLMSEmergencyProfile
from gurux_dlms.objects.GXDLMSActionItem import GXDLMSActionItem

from functions import TOD,Bill_date,Profle_capture_IP,RTC_Programming,Demand_IP,Load_limit,controlMode,meter_mode,meter_mode,payment_mode,read_nameplate,relay_connect



def print_selected_tests(selected_tests, cmd_args1):
    #print("Selected Tests:")
    cmd_args = ["selectedTest.py"] + cmd_args1
    # for test in selected_tests:
    #     print(test)
    run_tests(selected_tests, cmd_args)

def run_tests(selected_tests, cmd_args):
    try:
        import pkg_resources
        # pylint: disable=broad-except
    except Exception:
        # It's OK if this fails.
        print("pkg_resources not found")

    class SampleClient:
        @classmethod
        def main(cls, args, selected_tests):
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
                except AttributeError as e:
                    error_message = f"Error: 'settings' or 'media' attribute not found. Details: {str(e)}"
                    print(error_message)
                except IOError as e:
                    error_message = f"I/O error occurred while opening media settings. Details: {str(e)}"
                    print(error_message)
                except Exception as e:
                    error_message = f"An unexpected error occurred while opening media settings. Details: {str(e)}"
                    print(error_message)
                else:
                    print("Media settings opened successfully.")
                #settings.media.open()
                reader.initializeConnection()
                reply = GXReplyData()

                # Run selected tests
                for test in selected_tests:
                    if test == "RTC Programming":
                        RTC_Programming(reader)
                    elif test == "Demand Integration Period":
                        Demand_IP(reader)                    
                    elif test == "Profle Capture Integration Period":
                        Profle_capture_IP(reader)
                    elif test == "Billing Dates":
                        Bill_date(reader)
                    elif test == "TOD (Read)":
                        TOD(reader,settings)
                    elif test == "Load limit set (Read)":
                        Load_limit(reader,settings)
                    elif test == "Disconnect Control":
                        controlMode(reader)
                    elif test == "Metering Mode":
                        meter_mode(reader)
                    elif test == "Payment Mode":
                        payment_mode(reader)
                    elif test == "Read":
                        read_nameplate(reader)
                    elif test == "Connect/Disconnect":
                        relay_connect(reader)
                    else:
                        print("No test selected")
                        return 0

            finally:
                if settings.media:
                    settings.media.close()
                if reader:
                    reader.close()

    SampleClient.main(cmd_args, selected_tests)

def relay_connection():
    try:
        reader = GXDLMSClient()
        settings = GXSettings()
        reader.connect(settings)
        reply = GXReplyData()
        
        dc = GXDLMSDisconnectControl("0.0.96.3.10.255")
        val = reader.read(dc, 2)
        
        if val:
            reader.readDataBlock(dc.remoteDisconnect(reader.client), reply)
        else:
            reader.readDataBlock(dc.remoteReconnect(reader.client), reply)
            
        print("Relay connection operation completed.")
    except Exception as e:
        print(f"Error in relay connection: {e}")

   





