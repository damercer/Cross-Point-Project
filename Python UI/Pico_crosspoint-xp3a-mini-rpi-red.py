#
# Hardware specific interface functions
# For pi pico Cross Point Exp Board Mini SMD
# Three analog + 2 AWG channel scope
# For Mini breadboard Ver Red2 and Red3
CPRevDate = "(1-14-2026)"
# Written using Python version 3.10, Windows OS 
#
try:
    import serial
    import serial.tools.list_ports
except:
    root.update()
    showwarning("WARNING","Serial Library not installed?!")
    root.destroy()
    exit()
#
from tkinter import scrolledtext
#
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    import os
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    GeminiModel = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
except:
    showwarning("WARNING","google-generativeai or python-dotenv not installed? Run: pip install google-generativeai python-dotenv")
#
# adjust for your specific hardware by changing these values in the alice.init file
ADC_Cal = 3.25
VOpenCircuit = 2.4
AWGPeakToPeak = 4.095 # MCP4822 raw swing
VPlus = 0 # place holder for measured VDD
VMinus = 0 # place holder for measured VEE
#
AWGRes = 4095 # For 8 bits, 4095 for 12 bits, 1023 for 10 bits
ConfigFileName = "alice-last-config.cfg"
# Change this to link to a custom Help page.

CHANNELS = 3 # Number of supported Analog input channels
AWGChannels = 2 # Number of supported Analog output channels
PWMChannels = 0 # Number of supported PWM output channels
DigChannels = 8 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 #
EnableAWGNoise = 0 #
UseSoftwareTrigger = 1
AllowFlashFirmware = 1
Tdiv.set(10)

AWG_Amp_Mode.set(0)
TestResStatus = IntVar()
TestResDisp = IntVar()
#### Int variables to check if we want to connect/disconnect to a jumper in the different regions(Top Left, Bottom Left, Top Right, Bottom Right)
OnOff_RC = IntVar()
OnOff_TL = IntVar()
OnOff_BL = IntVar()
OnOff_TR = IntVar()
OnOff_BR = IntVar()

#### The original Matrix Screen with Cross Point Interface
MatrixStatus = IntVar()
MatrixStatus.set(0)
BOMStatus = IntVar()
BOMStatus.set(0)
AuxBoard = IntVar()
AuxBoard.set(0)
ExtBoard = IntVar()
ExtBoard.set(0)
#### The new Breadboard simulator Screen with Breadboard canvas and Cross Point Interface
BreadboardStatus = IntVar()
BreadboardStatus.set(0)
# initial X Y size of BB graphic, 11 pixels per grid point?
BBwidth = 520
BBheight = 440
BBGridSize = 46
BBFont = 6
CANVASwidthBB = BBwidth     # BB canvas width
CANVASheightBB = BBheight # BB canvas height
# set Jumper colors
#JPcolors = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Maroon", "Pink", "Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Maroon", "Pink"]
JPcolors = [ "#ff0000", "#00ff00", "#0000ff", "#ff8000", "#00ffff", "#ff00ff", "#8080ff", "#ffff00",
             "#800000", "#008000", "#000080", "#905000", "#00b0b0", "#800080", "#4040a0", "#b0b000" ]
#### The variable tells what Jumpers 1-16 are connected to
Jumper_Connections = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

#### The variable contains the circle IDs, each of which represent the jumper connections
Jumper_Connections_circles = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

#### The variable keeps track of what locations of the breadboards are occupied.
Breadboard_Store = [
                    ### TL Region
                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], 
                    ### BL Region
                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
                    ### TR Region
                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
                    ### BR Region
                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],]

### The variable contains the graphical represention of the jumper connections through an adjacency list
circle_adjacency_list = {}
ComponentList = []
########
# BB pin graphical location variables
TL1XY = [0,0]
BL1XY = [0,0]
TR1XY = [0,0]
BR1XY = [0,0]
JP1XY = [0,0]
JP9XY = [0,0]
AINHXY = [0,0]
# Possible power nodes
VPower = []
UnRouted = []
VPower_id = []
VPowerConnections = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
PWConnString = ""
# Component lists
R_List = []
C_List = []
L_List = []
D_List = []
M_List = []
Q_List = []
U_List = []
SVB = 0
#
AWG_Amp_Mode.set(0)
DevID = "Pi Pico Cross Point Mini"
SerComPort = 'Auto'
HWRevOne = "None"
TimeSpan = 0.01
InterpRate = 4
EnableInterpFilter.set(1)
MaxSampleRate = SAMPLErate = 333333*InterpRate
ATmin = 8 # set minimum DAC update rate to 8 uSec
MaxAWGSampleRate = 1.0 / (ATmin / 1000000) # set to 1 / 8 uSec
AWGSampleRate = MaxAWGSampleRate
LSBsizeA = LSBsizeB = LSBsizeC = LSBsize = ADC_Cal/4096.0
HardwareBuffer = 2048 # Max hardware waveform buffer size
MinSamples = 2048 # capture sample buffer size
AWGBuffLen = 2048 # Max DAC hardware waveform buffer size
Cycles = 1
SMPfft = MinSamples*InterpRate # Set FFT size based on fixed acquisition record length
#
VBuffA = numpy.ones(MinSamples*InterpRate)
VBuffB = numpy.ones(MinSamples*InterpRate)
VBuffC = numpy.ones(MinSamples*InterpRate)
VBuffD = numpy.ones(MinSamples*InterpRate)
VBuffG = numpy.ones(MinSamples*InterpRate)
MBuff = numpy.ones(MinSamples*InterpRate)
MBuffX = numpy.ones(MinSamples*InterpRate)
MBuffY = numpy.ones(MinSamples*InterpRate)
VmemoryA = numpy.ones(MinSamples*InterpRate) # The memory for averaging
VmemoryB = numpy.ones(MinSamples*InterpRate) # The memory for averaging
VmemoryC = numpy.ones(MinSamples*InterpRate)
VmemoryD = numpy.ones(MinSamples*InterpRate)
#
TextCurrent_filepath = " "
IACMString = "+2.5"
IA_Mode.set(1)
#
# Breadboard pin maping for Mimi Red SMD layout
#
TL1 = "CA0"; TL2 = "CA1"; TL3 = "CA2"; TL4 = "CA3"; TL5 = "CA4"; TL6 = "CA5"; TL7 = "CA12"; TL8 = "CA13"
BL1 = "CA14"; BL2 = "CA15"; BL3 = "CA6"; BL4 = "CA7"; BL5 = "CA8"; BL6 = "CA9"; BL7 = "CA10"; BL8 = "CA11"
TL9 = "CB0"; TL10 = "CB1"; TL11 = "CB2"; TL12 = "CB3"; TL13 = "CB4"; TL14 = "CB5"; TL15 = "CB12"; TL16 = "CB13"
BL9 = "CB14"; BL10 = "CB15"; BL11 = "CB6"; BL12 = "CB7"; BL13 = "CB8"; BL14 = "CB9"; BL15 = "CB10"; BL16 = "CB11"
BL17 = "CE2"; TL17 = "CE0"; TR1 = "CE1"

TR2 = "CC0"; TR3 = "CC1"; TR4 = "CC2"; TR5 = "CC3"; TR6 = "CC4"; TR7 = "CC5"; TR8 = "CC12"; TR9 = "CC13"
BR1 = "CC14"; BR2 = "CC15"; BR3 = "CC6"; BR4 = "CC7"; BR5 = "CC8"; BR6 = "CC9"; BR7 = "CC10"; BR8 = "CC11"
TR10 = "CD0"; TR11 = "CD1"; TR12 = "CD2"; TR13 = "CD3"; TR14 = "CD4"; TR15 = "CD5"; TR16 = "CD12"; TR17 = "CD13"
BR9 = "CD14"; BR10 = "CD15"; BR11 = "CD6"; BR12 = "CD7"; BR13 = "CD8"; BR14 = "CD9"; BR15 = "CD10"; BR16 = "CD11"

AINH = "CE14"; BINH = "CE15"; CINH = "CE6"
AWG1 = "CE7"; AWG2 = "CE8"
JP5 = "CE3"; JP6 = "CE9"; JP7 = "CE10"; JP8 = "CE11"
JP9 = "CE4"; JP10 = "CE5"; JP11 = "CE12"; JP12 = "CE13"
BR17 = "CF0" # A Placeholder for un-connectd BB pin
### CompSpinBoxList are now separated into their respective regions
JumperSpinBoxList = ("JP1", "JP2", "JP3", "JP4", "JP5", "JP6", "JP7", "JP8",
                     "JP9", "JP10", "JP11", "JP12", "JP13", "JP14", "JP15", "JP16")
CompSpinBoxList_RC = ("AWG1", "AWG2", "AINH", "BINH", "CINH", "TL17", "BL17", "TR1", "JP5", "JP6", "JP7", "JP8","JP9", "JP10", "JP11", "JP12")
CompSpinBoxList_TL = ("TL1", "TL2", "TL3", "TL4", "TL5", "TL6", "TL7", "TL8", "TL9", "TL10", "TL11", "TL12", "TL13", "TL14", "TL15", "TL16")
CompSpinBoxList_BL = ("BL1", "BL2", "BL3", "BL4", "BL5", "BL6", "BL7", "BL8", "BL9", "BL10", "BL11", "BL12", "BL13", "BL14", "BL15", "BL16")
CompSpinBoxList_TR = ("TR2", "TR3", "TR4", "TR5", "TR6", "TR7", "TR8", "TR9", "TR10", "TR11", "TR12", "TR13", "TR14", "TR15", "TR16", "TR17")
CompSpinBoxList_BR = ("BR1", "BR2", "BR3", "BR4", "BR5", "BR6", "BR7", "BR8", "BR9", "BR10", "BR11", "BR12", "BR13", "BR14", "BR15", "BR16")

##
NotesString = "Nodes JP1-8 can connect directly to BB pins TL1-16, BL1-16 (left hand BB)\nNodes JP9-16 can connect directly to BB pins TR2-17, BR1-16 (right hand BB)\nBB pins TL17, BL17 and TR1 can connect to any of JP1-4 and JP13-16\nNodes JP1-4 can connect directly to any of JP9-12 (and JP5-8*)\nNodes JP13-16 can connect directly to any of JP5-8 (and JP9-12*)\nAINH, BINH, CINH, AWG1, AWG2 can connect directly to any of JP1-4 and JP13-16"
##
'''
Tests all the pins by conneting DAC and ADC to each pin with a jumper

Utilizes ManualMatrix() to set jumpers, AWGSendWave() to send signals, and Get_Data()
to retrieve the signal

Notes:
JP1-8 can connet to TL1-16 and BL1-16
JP9-16 can connect to TR2-17 and BR1-16
TL17, BL17, TR1 can connect to any JP1-4 and JP13-16
BR17 is not connected to any amalog matrix input
'''

## Navigate to Help web pages
def HelpLTspice(): # Change this as file location changes

    webbrowser.open("https://mercerxlab.notion.site/LTSpice-SCB-Guides-with-Example-Implementation-24c0f9dca44b80c48206db052092e88d",new=2)
#
def HelpSelfTest(): # Change this as file location changes

    webbrowser.open("https://mercerxlab.notion.site/SCB-Self-Testing-Protocol-24c0f9dca44b80aa860cdfb9986f3886",new=2)
#
def HelpDigital(): # Change this as file location changes

    webbrowser.open("https://mercerxlab.notion.site/SCB-Digital-Capabilities-24c0f9dca44b80fb8f59db6e9003f568",new=2)
#
def HelpFiles(): # How to open local help files
    #global

    file_path = os.path.abspath("Calibration%20Procedure.pdf")
    file_name = "file:///" + file_path
    # print(file_name)
    webbrowser.open(file_name,new=2)
#
### With the given jumper, Component location(ex. "TL7"), and on or off(represented by 1 or 0)
### set the corresponding JumperString, CompString and On/Off switch based on the information 
def set_connection(jumper, comp, onoff):
    global JumperString, CompString, OnOff

    if comp[0:2] == "TL" and comp != "TL17":
        JumperString[1].set(jumper)
        CompString[1].set(comp)
        if onoff == 0:
            ManualReSet_TL()
        else:
            ManualSet_TL()

    elif comp[0:2] == "BL" and comp != "BL17":
        JumperString[2].set(jumper)
        CompString[2].set(comp)
        if onoff == 0:
            ManualReSet_BL()
        else:
            ManualSet_BL()

    elif comp[0:2] == "TR" and comp != "TR1":
        JumperString[3].set(jumper)
        CompString[3].set(comp)
        if onoff == 0:
            ManualReSet_TR()
        else:
            ManualSet_TR()

    elif comp[0:2] == "BR":
        JumperString[4].set(jumper)
        CompString[4].set(comp)
        if onoff == 0:
            ManualReSet_BR()
        else:
            ManualSet_BR()

    else:
        JumperString[0].set(jumper)
        CompString[0].set(comp)
        if onoff == 0:
            ManualReSet_RC()
        else:
            ManualSet_RC()
#
def BB_test():
    """
    Tests all pins in each region of a breadboard by connecting AWG1 and AINH
    through jumpers and measuring the resulting voltage.
    Logs pass/fail based on expected voltage threshold (3.9V - 4.1V).
    """
    global ser, CompString, JumperString, OnOffString, NumConn
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root
    global AwgAOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    Failed = 0
    FailedPins.config(font="Arial 14 bold", foreground="green", text = "Running")
    PassString = "All BB Pins Passed"
    #reset matrix switches to all open
    ResetMatrix()
    # Configure AWG channel A DC 4.0 V
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(0)
    AWGAAmplEntry.delete(0,"end")
    AWGAAmplEntry.insert(0, 0.0)
    AWGAOffsetEntry.delete(0,"end")
    AWGAOffsetEntry.insert(0,4.0)
    ## Send waveform
    MakeAWGwaves()
    # Select just Scope Channel A
    ShowC1_V.set(1)
    ShowC2_V.set(0)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 1
    #
    VOLTAGE_MIN = 3.9
    VOLTAGE_MAX = 4.1

    regions = ["TL", "BL", "TR", "BR"]

    for region in regions:
        upper_range = 17 if region[0] == "T" else 16

        if region[1] == "L":
            adc_jumper = "JP2"
            dac_jumper = "JP1"
            set_connection(dac_jumper, "TL9", 1)
            set_connection(dac_jumper, "BL9", 1)
        else:
            adc_jumper = "JP15"
            dac_jumper = "JP16"
            set_connection(dac_jumper, "TR9", 1)
            set_connection(dac_jumper, "BR9", 1)

        # Set up DAC
        set_connection(dac_jumper, "AWG1", 1)

        # Set up ADC
        set_connection(adc_jumper, "AINH", 1)
        
        for i in range(1, upper_range + 1):
            pin = region + str(i)

            # Connect test BB pin to ADC
            set_connection(adc_jumper, pin, 1)

            # get data
            Get_Data()
            VDC = numpy.mean(VBuffA)

            if VOLTAGE_MIN < VDC < VOLTAGE_MAX:
                print("{:.2f} V - Pin {} Passed!".format(VDC, pin))
            else:
                Failed = Failed + 1
                ErrorString = "{:.2f} V - Pin {} Failed!".format(VDC, pin)
                print(ErrorString)
                FailedPins.config(font="Arial 10 bold", foreground="red", text = ErrorString)
            # Disconnect test pin
            set_connection(adc_jumper, pin, 0)
            #
            root.update()
    if Failed == 0:
        FailedPins.config(font="Arial 14 bold", foreground="green", text = PassString)
        root.update()

    ####   
    ResetMatrix()
    #### 
#
def UpdateGainOffsetValues():
    global CHANNELS
    global InGainA, InGainB, InOffA, InOffB, InGainC, InGainD, InOffC, InOffD
    global CHAVGainEntry, CHAVOffsetEntry, CHBVGainEntry, CHBVOffsetEntry
    global CHCVGainEntry, CHCVOffsetEntry, CHDVGainEntry, CHDVOffsetEntry
    
    if CHANNELS >= 1:
        try:
            InOffA = float(eval(CHAVOffsetEntry.get()))
        except:
            CHAVOffsetEntry.delete(0,END)
            CHAVOffsetEntry.insert(0, InOffA)
        try:
            InGainA = float(eval(CHAVGainEntry.get()))
        except:
            CHAVGainEntry.delete(0,END)
            CHAVGainEntry.insert(0, InGainA)
    if CHANNELS >= 2:
        try:
            InGainB = float(eval(CHBVGainEntry.get()))
        except:
            CHBVGainEntry.delete(0,END)
            CHBVGainEntry.insert(0, InGainB)
        try:
            InOffB = float(eval(CHBVOffsetEntry.get()))
        except:
            CHBVOffsetEntry.delete(0,END)
            CHBVOffsetEntry.insert(0, InOffB)
    if CHANNELS >= 3:
        try:
            InGainC = float(eval(CHCVGainEntry.get()))
        except:
            CHCVGainEntry.delete(0,END)
            CHCVGainEntry.insert(0, InGainC)
        try:
            InOffC = float(eval(CHCVOffsetEntry.get()))
        except:
            CHCVOffsetEntry.delete(0,END)
            CHCVOffsetEntry.insert(0, InOffC)
#
def self_calibrate(): 
    global RDGain, RDOffset, Rint, ResDivStatus, FWRevOne, ser
    global VBuffA, VBuffB, VBuffC, Voff, R1, R2
    global TRACESread, PassFailSelfCal, SVB

    PassFailSelfCal.config(font="Arial 14 bold", foreground="green", text = "Running")
    #reset avoids an AWG channel skewing read voltage
    ResetMatrix()
    SVB = 1
    # Set AWG A On with Shape DC 
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(0)
    AWGAAmplEntry.delete(0,"end")
    AWGAAmplEntry.insert(0, 0.0)
    # Select all three scope channels, you can do all three at the same time
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(1)
    SelectChannels()
    TRACESread = 3
    #reset gain / offset to read potentiometer offset
    ReSetAGO()
    ReSetBGO()
    ReSetCGO()
    UpdateGainOffsetValues()
    root.update() # update screen
    #wait to let V stabilize, then get data
    time.sleep(0.1)
    Get_Data()
    #if statement avoids numpy.mean runtime error
    if VBuffA.size>0 and VBuffB.size>0 and VBuffC.size>0:
        #use average of reading channels as offset value
        Voffset = (numpy.mean(VBuffA+VBuffB+VBuffC))/3
        if ResDivStatus.get() == 0: # Use assumed 2.45 V offset voltage
            OffsetMin = 2.35
            OffsetMax = 2.65
        else: # Get entered offset voltage
            OffsetMin = UnitConvert(Voff.get()) - 0.1
            OffsetMax = OffsetMin + 0.3
        if OffsetMin <=  Voffset <= OffsetMax:
            print("Voltage {:.2f} within calibration range 2.35-2.65".format(Voffset))
            ##send 0V DC for offset calculation
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0,0.0)
            MakeAWGwaves() # AWGAMakeDC()
            #
            root.update() # update screen
            if FWRevOne == "Red3": # Use external test resistor connected to GND
                ser.write(b'? 0 0 0 0\n') # Res switches to closed
                set_connection("JP1", "JP11", 1) # connect resistor to JP1
            else: #connect AWG1 0V DC to all channels to calculate offset
                set_connection("JP1", "AWG1", 1)
            #
            set_connection("JP1", "AINH", 1)
            set_connection("JP1", "BINH", 1)
            set_connection("JP1", "CINH", 1)

            #wait for voltage to settle before getting data
            time.sleep(0.1)
            Get_Data()
            
            #offset values are distance to 0, or VBuffX-0 = VBuffX
            OffsetA = numpy.mean(VBuffA)
            OffsetB = numpy.mean(VBuffB)
            OffsetC = numpy.mean(VBuffC)

            #Now send 4V DC for gain adjustment
            if FWRevOne == "Red3": # 
                ser.write(b'? 1 0 0 0\n') # Res switches to Open
                set_connection("JP1", "JP11", 0) # disconnect resistor from JP1
                set_connection("JP1", "AWG1", 1)
            else: #connect AWG1 
                set_connection("JP1", "AWG1", 1)
            #
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0,4.0)
            MakeAWGwaves() # AWGAMakeDC()
            time.sleep(0.1)

            if ResDivStatus.get() == 0: #
                #set initial gain from RDGain calc in gain / offset menu:
                Y = 680000 #R1 value 
                Z = 330000 #R2 value
                # ZE = (Z * Rint) / (Z + Rint)  
            else:
                # RDbutton() # get R1 and R2 entered values
                X = UnitConvert(Voff.get())
                Y = UnitConvert(R1.get())
                Z = UnitConvert(R2.get())
            # Calculate
            RDGain =  (Y + Z) / Z
            AGain = RDGain
            BGain = RDGain
            CGain = RDGain
            #set A gain / offset
            RDOffset = OffsetA
            RDSetAGO()
            #set B gain / offset
            RDOffset = OffsetB
            RDSetBGO()
            #set C gain / offset
            RDOffset = OffsetC
            RDSetCGO()
            UpdateGainOffsetValues()
                
            # Measue 4.0 V with calculated Gain and measured offset
            time.sleep(0.1)
            Get_Data()
            FSA = numpy.mean(VBuffA)
            FSB = numpy.mean(VBuffB)
            FSC = numpy.mean(VBuffC)
            #set A gain / offset
            RDOffset = OffsetA
            RDGain = AGain = (4.0/FSA) * AGain
            RDSetAGO()
            #set B gain / offset
            RDOffset = OffsetB
            RDGain = BGain = (4.0/FSB) * BGain
            RDSetBGO()
            #set C gain / offset
            RDOffset = OffsetC
            RDGain = CGain = (4.0/FSC) * CGain
            RDSetCGO()
            UpdateGainOffsetValues()
            #Now go back and check offset with new gain and adjust as necessary
            ##send 0V DC for offset calculation
            if FWRevOne == "Red3": # Use external test resistor connected to GND
                ser.write(b'? 0 0 0 0\n') # Res switches to closed
                set_connection("JP1", "JP11", 1) # connect resistor to JP1
            else: #connect AWG1 0V DC to all channels to calculate offset
                set_connection("JP1", "AWG1", 1)
            #
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0,0.0)
            MakeAWGwaves() # AWGAMakeDC()
            #wait for voltage to settle before getting data
            time.sleep(0.1)
            Get_Data()
            Azero = numpy.mean(VBuffA)
            Bzero = numpy.mean(VBuffB)
            Czero = numpy.mean(VBuffC)
            #set A gain / offset
            RDOffset = OffsetA = OffsetA + (Azero/AGain)
            RDGain = AGain
            RDSetAGO()
            #set B gain / offset
            RDOffset = OffsetB = OffsetB + (Bzero/BGain)
            RDGain = BGain
            RDSetBGO()
            #set C gain / offset
            RDOffset = OffsetC = OffsetC + (Czero/CGain)
            RDGain = CGain
            RDSetCGO()
            UpdateGainOffsetValues()
            #Now go back and check Gain again with new offset and adjust as necessary
            ##send 4V DC for offset calculation
            if FWRevOne == "Red3": #
                ser.write(b'? 1 0 0 0\n') # Res switches to Open
                set_connection("JP1", "JP11", 0) # disconnect resistor from JP1
                set_connection("JP1", "AWG1", 1)
            else: #connect AWG1 
                set_connection("JP1", "AWG1", 1)
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0,4.0)
            MakeAWGwaves() # AWGAMakeDC()
            #wait for voltage to settle before getting data
            time.sleep(0.1)
            Get_Data()
            #
            FSA = numpy.mean(VBuffA)
            FSB = numpy.mean(VBuffB)
            FSC = numpy.mean(VBuffC)
            #set A gain / offset
            RDOffset = OffsetA
            RDGain = AGain = (4.0/FSA) * AGain
            RDSetAGO()
            #set B gain / offset
            RDOffset = OffsetB
            RDGain = BGain = (4.0/FSB) * BGain
            RDSetBGO()
            #set C gain / offset
            RDOffset = OffsetC
            RDGain = CGain = (4.0/FSC) * CGain
            RDSetCGO()
            UpdateGainOffsetValues()
            PassFailSelfCal.config(font="Arial 14 bold", foreground="green", text = "Finished!")
            root.update() # update screen
        else:
            PassFailSelfCal.config(font="Arial 14 bold", foreground="red", text = "Offset Error")
            root.update() # update screen
            print("Voltage {:.2f} not within calibration range 2.45-2.55".format(Voffset))
    else:
        print("Error reading scope channels")
    ResetMatrix()
    SVB = 0
#       
# Cross point matrix functions
def ReadNetlist(nfp):
    global FileString

    if ".cir" in nfp or ".net" in nfp:
        pass
    else:
        nfp = askopenfilename(defaultextension = ".cir", filetypes=[("Net List files", ".cir .net")])
        FileString.delete(0,"end")
        FileString.insert(0,nfp)
    #
    try: # First check if net list is UTF-16-LE
        NetList = open(nfp, 'r', encoding='utf-16-le')     
        Rawlines = NetList.readlines()
        if len(Rawlines) == 1: # Actually miss read as utf-16 so try utf-8
            NetList.close()
            NetList = open(nfp, 'r', encoding='utf-8')
            Rawlines = NetList.readlines()
            print("Found file as UTF-8")
        #
        else:
            print("Found file as UTF-16-LE")
    except: # If fails then must be UTF-8
        NetList.close()
        NetList = open(nfp, 'r', encoding='utf-8')
        Rawlines = NetList.readlines()
        print("Found file as UTF-8")
    NetList.close()
    return(Rawlines)
    
    # print(Rawlines)``

def ParseNetlist(lines):
    global VPower, R_List, C_List, L_List, D_List, M_List, Q_List, U_List
    global ComponentList
    # Clear all Lists
    VPower = []
    UnRouted = []
    R_List = []
    C_List = []
    L_List = []
    D_List = []
    M_List = []
    Q_List = []
    U_List = [] 
    # create a list of strings for all cross_point instance lines in netlist
    # ignore the rest
    ComponentList = []
    for line in lines:
        # Select only the lines that contain "cross_point"
        if ".subckt" in line:
            break
        if "cross_point" in line:
            ComponentList.append(line.split())
        SplitLine = []
        SplitLine = line.split()
        # if a source has V in name
        # and one or the other terminal nodes names have a V
        if len(SplitLine) > 0:
            FirstPart = SplitLine[0]
            if "V" == FirstPart[0]:
                if "V" in SplitLine[1]:
                    if SplitLine[1] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[1])
                if "V" in SplitLine[2]:
                    if SplitLine[2] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[2])
                if "COM" in SplitLine[1]:
                    if SplitLine[1] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[1])
                if "COM" in SplitLine[2]:
                    if SplitLine[2] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[2])
                if "0" == SplitLine[1]:
                    if SplitLine[1] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[1])
                if "0" == SplitLine[2]:
                    if SplitLine[2] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[2])
            if "R" == FirstPart[0]:
                R_List.append(SplitLine)
            if "C" == FirstPart[0]:
                if "cross_point" in SplitLine:
                    pass
                else:
                    C_List.append(SplitLine)
            if "L" == FirstPart[0]:
                L_List.append(SplitLine)
            if "D" == FirstPart[0]:
                D_List.append(SplitLine)
            if "M" == FirstPart[0]:
                M_List.append(SplitLine)
            if "Q" == FirstPart[0]:
                Q_List.append(SplitLine)
            if "U" in FirstPart:
                U_List.append(SplitLine)

    # print("Found these possible Power nodes: ", VPower)
#
#
def WhichChip(CompPin): # determine which cross point chip is used A-E

    ChipNum = 0
    # print("Which Chip ", CompPin)
    if isinstance(CompPin, int):
        return 0
    else:
        if "CA" in CompPin:
            ChipNum = 1
        if "CB" in CompPin:
            ChipNum = 2
        if "CC" in CompPin:
            ChipNum = 3
        if "CD" in CompPin:
            ChipNum = 4
        if "CE" in CompPin:
            ChipNum = 5
        return ChipNum
##
def ConfigCrossPointFile():
    global FileString

    netlist = FileString.get()
    ResetMatrix()
    ParseNetlist(ReadNetlist(netlist)) # list of all subcircuit instances found
    ConfigCrossPoint()
##
def ConfigCrossPointEditor():
    global BOMtext

    lines = BOMtext.get(1.0, END)
    lines = lines.splitlines()
    ResetMatrix()
    ParseNetlist(lines) # list of all subcircuit instances found
    ConfigCrossPoint()
##
def ConfigCrossPoint():
    global ser, FileString, NumConn, ErrConn, BBblack, AuxBoard
    global VPower, VPowerConnections, PWConnString, VPower_id
    global ComponentList, TL1XY, BL1XY, TR1XY, BR1XY
    global BBwidth, BBheight, BBGridSize, breadboard_canvas
    
    # ResetMatrix()
    # ser.write(b'x\n') # Reset all cross point switches to open
    CompNum = len(ComponentList) # number of subcircuits
    index = 0
    connects = 0
    Errors = 0
    ErrorString = ""
    time.sleep(0.01)
    while index < CompNum:
        CompPins = ComponentList[index]
        # check if this cross point is connected to one of the possible Power rails
        for PWR in range ( 0, len(VPower), 1):
            if VPower[PWR] in CompPins:
                Vpin = CompPins[0]
                Vpin = Vpin.replace("X","")
                Vpin = Vpin.replace(chr(167),"")# remove §
                VPowerConnections[PWR].append(Vpin)
                # print( "Found ", VPower[PWR], " connected to ", Vpin)
        index = index + 1
        if "JP" in CompPins[1]:
            Jumper = CompPins[1] # First net is Jumper bus
            JmpNum = int(Jumper.replace("JP","")) - 1 # extract number 0-15
            try:
                XPin = eval(CompPins[2]) # is Second net a component BB pin
                xpin = CompPins[2]
                xpin = xpin.replace("X","")
                xpin = xpin.replace(chr(167),"")# remove §
            except:
                # for case where synbol instance name is the BB pin 
                xpin = CompPins[0]
                xpin = xpin.replace("X","")
                xpin = xpin.replace(chr(167),"")# remove §
                XPin = eval(xpin)
            #
            if XPin == 0: # cross point connected to node 0?
                xpin = CompPins[0]
                xpin = xpin.replace("X","")
                xpin = xpin.replace(chr(167),"")# remove §
                XPin = eval(xpin)
                # print(XPin,xpin)
            ##########
            updateBreadboardConnection(JmpNum, xpin, 1)
            ##########

            if "L" in xpin:
                if xpin != "TL17":
                    if JmpNum > 7:
                        ErrorString = "Jumper JP " + str(JmpNum) + " out of range in " + str(CompPins)
                        print(ErrorString)
                        Errors = Errors + 1
                        continue
                else: # BB pin TL17 can connect to any of JP1-4 and JP13-16
                    if JmpNum > 3 and JmpNum < 12:
                        ErrorString = "Jumper JP " + str(JmpNum) + " out of range in " + str(CompPins)
                        print(ErrorString)
                        Errors = Errors + 1
                        continue
                    if JmpNum > 7:
                        JmpNum = JmpNum - 8
                    # print(xpin, XPin, JmpNum)
            elif "R" in xpin:
                if xpin != "TR1":
                    if JmpNum < 7 or JmpNum > 15:
                        ErrorString = "Jumper JP " + str(JmpNum) + " out of range in " + str(CompPins)
                        print(ErrorString)
                        Errors = Errors + 1
                        continue
                    JmpNum = JmpNum - 8
                else: # BB pin TR1 can connect to any of JP1-4 and JP13-16
                    if JmpNum > 3 and JmpNum < 12:
                        ErrorString = "Jumper JP " + str(JmpNum) + " out of range in " + str(CompPins)
                        print(ErrorString)
                        Errors = Errors + 1
                        continue
                    if JmpNum > 7:
                        JmpNum = JmpNum - 8
            #
            ChipNum = WhichChip(XPin) # Find which switch chip 1-5
            if ChipNum == 5 and JmpNum > 7:
                JmpNum = JmpNum - 8
            if ChipNum > 0:
                CmpNum = only_numerics(XPin) # extract number 0-15
                if AuxBoard.get() == 0:
                    CommStr = ("X " + str(JmpNum) + " " + str(CmpNum) + " " + str(ChipNum) + " 1")
                else: # Send Aux board command
                    CommStr = ("Y " + str(JmpNum) + " " + str(CmpNum) + " " + str(ChipNum) + " 1")
                SendStr = CommStr + '\n'
                SendByt = SendStr.encode('utf-8')
                try:
                    ser.write(SendByt)
                except:
                    pass
                connects = connects + 1
            else:
                ErrorString = "Error Unknown switch chip number for? " + str(xpin)
                print(ErrorString)
                Errors = Errors + 1
    NumConn.config(text = "Number of Connections = " + str(connects)) #+ " Errors = " + str(Errors))
    ErrConn.config(text = "Number of Errors = " + str(Errors))
    #
    # Show Power / GND wires if any
    # DrawPowerWires()
#
##
def ResetMatrix(TClear = 0):
    global ser, FileString, NumConn, ErrConn, BOMStatus, BOMtext
    global JumperString, CompString, AuxBoard
    global J_Connections_Labels
    global Jumper_Connections, Jumper_Connections_circles
    global breadboard_canvas, Breadboard_Store, circle_adjacency_list
    global VPower, VPowerConnections, PWConnString
    global BBwidth, BBheight, BBGridSize, VPower_id

    if BOMStatus.get() > 0 and TClear == 0:
        BOMtext.delete("1.0", END) # Clear all text
        DrawBreadBoardGraphic() # Clear and redraw BB graphic
    
    try:
        # Clear power nodes
        VPower = []
        UnRouted = []
        VPowerConnections = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        PWConnString = ""
        for PWR in range(0, len(VPower_id), 1):
            breadboard_canvas.delete(VPower_id[PWR])
        ### All of the labels and strings are reset to their first/original input
        JumperString[0].set("JP1")
        CompString[0].set("AWG1")

        JumperString[1].set("JP1")
        CompString[1].set("TL1")

        JumperString[2].set("JP1")
        CompString[2].set("BL1")

        JumperString[3].set("JP9")
        CompString[3].set("TR2")

        JumperString[4].set("JP9")
        CompString[4].set("BR1")

        # FileString.delete(0,"end")
        # FileString.insert(0,"")

        NumConn.config(text = "Number of Connections ")
        ErrConn.config(text = "Number of Errors ")
        ####
        ### All of the regions are disconnected/set to 0
        OnOff_RC.set(0)
        OnOff_TL.set(0)
        OnOff_BL.set(0)
        OnOff_TR.set(0)
        OnOff_BR.set(0)
        ### 
        ### Empty all of the jumper connections
        Jumper_Connections = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        ###

        for i in range(0, 16, 1):
            ### Loop through all 16 jumpers and ensure that the corresponding text says "No connections"
            J_Connections_Labels[i].config(text = "No connections")

            ### For each jumper, remove the circle that represents a jumper connection
            for (_, breadboard_info, center, circle) in Jumper_Connections_circles[i]:
                breadboard_canvas.delete(circle)

                ### For the remaining connections to the same jumper, ensure that the current connection is remove by deleting the line associated
                if breadboard_info[0] != -1:
                    for (line_id, circle_id) in circle_adjacency_list[circle]:
                        breadboard_canvas.delete(line_id)
                        circle_adjacency_list[circle_id].remove((line_id, circle))

        Breadboard_Store = [
                    ### TL Region
                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], 
                    
                    ### BL Region
                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
                    
                    ### TR Region
                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
                    
                    ### BR Region
                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],]
            
        Jumper_Connections_circles = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        try:
            if AuxBoard.get() == 0:
                ser.write(b'x\n') # Reset all cross point switches to open
            else:
                ser.write(b'y\n') # Reset all Aux cross point switches to open
        except:
            pass
    except:
        try:
            if AuxBoard.get() == 0:
                ser.write(b'x\n') # Reset all cross point switches to open
            else:
                ser.write(b'y\n') # Reset all Aux cross point switches to open
        except:
            pass
##
def BrowsNetFile():
    global FileString, NetList
    
    NetList = askopenfilename(defaultextension = ".cir", filetypes=[("Net List files", ".cir .net")])
    FileString.delete(0,"end")
    FileString.insert(0,NetList)
##
def DumpNetList():
    global Jumper_Connections

    filename = asksaveasfilename(defaultextension = ".cir", filetypes=[("Net Lists", "*.cir")])
    DataFile = open(filename, 'w')
    Xi = 1
    for i in range(0, 16, 1):
        for j in range(0, len(Jumper_Connections[i]), 1):
            CompPin = Jumper_Connections[i][j]
            if ("TL" in CompPin ) or ("BL" in CompPin) or ("TR" in CompPin) or ("BR" in CompPin):
                DataFile.write("X" + CompPin + " JP" + str(i+1) + " " + CompPin + " cross_point\n" )
            else:
                DataFile.write("X" + str(Xi) + " JP" + str(i+1) + " " + CompPin + " cross_point\n" )
                Xi = Xi + 1
    DataFile.close()
#
def MergNetList():
    global Jumper_Connections, BOMtext, VPowerConnections, VPower

    Xi = NC = 1
    # List all jumper connections
    for i in range(0, 16, 1):
        for j in range(0, len(Jumper_Connections[i]), 1):
            CompPin = Jumper_Connections[i][j]
            if ("TL" in CompPin ) or ("BL" in CompPin) or ("TR" in CompPin) or ("BR" in CompPin):
                IsConn = 0
                for PWR in range ( 0, len(VPower), 1):
                    if len(VPowerConnections[PWR]) > 0:
                        for Pins in range ( 0, len(VPowerConnections[PWR]), 1):
                            if CompPin in VPowerConnections[PWR][Pins]:
                                PwPin = VPower[PWR]
                                IsConn = 1
                                TxtLine = CompPin + " JP" + str(i+1) + " " + PwPin + " cross_point\n"
                if IsConn == 0:             
                    # TxtLine = "X" + str(Xi) + " JP" + str(i+1) + " " + CompPin + " cross_point\n"
                    TxtLine = CompPin + " JP" + str(i+1) +  " cross_point\n"
                    Xi = Xi + 1
            else:
                # TxtLine ="X" + str(Xi) + " JP" + str(i+1) + " " + CompPin + " cross_point\n"
                TxtLine = CompPin + " JP" + str(i+1) +  " cross_point\n"
##                if CompPin == "AWG1":
##                    BOMtext.insert(END, "VAWG1 AWG1 0 0\n")
##                if CompPin == "AWG2":
##                    BOMtext.insert(END, "VAWG2 AWG2 0 0\n")
                Xi = Xi + 1
            BOMtext.insert(END, TxtLine)
# Add dummy supplies for power and gnd and AWG
##    BOMtext.insert(END, "VDD VDD 0 +5\n")
##    BOMtext.insert(END, "VEE VEE 0 -5\n")
#            
def updateBreadboardConnection(JmpNum, CompPin, OnOff):
    global Jumper_Connections
    global J_Connections_Labels

    ### Grab the existing connections to the specified jumper
    ### along with the corresponding jumper label to the breadboard screen
    ### also determine if the Component is already connected to the Jumper
    Jmp_arr = Jumper_Connections[JmpNum]
    Jmp_label = J_Connections_Labels[JmpNum]
    connected = CompPin in Jmp_arr

    ### If we want to disconnect AND the connection exists,
    ### then we remove the component pin from the specified jumper.
    if OnOff == 0:
        if connected:
            Jmp_arr.remove(CompPin)
            ###
            modifyBreadboardCanvas(JmpNum, CompPin, OnOff)
            ###
            ### If there are no connections to the jumper
            if len(Jmp_arr) == 0:
                Jmp_label.config(text="No connections")
            ### otherwise
            else:
                Jmp_label.config(text=", ".join(Jmp_arr))

    ### If we want to connect AND the connection does not exist,
    ### then we add the component pin to the specificed jumper.
    else:
        if not connected:
            Jmp_arr.append(CompPin)
            Jmp_label.config(text=", ".join(Jmp_arr))
            ###
            modifyBreadboardCanvas(JmpNum, CompPin, OnOff)
            ###
##
def modifyBreadboardCanvas(JmpNum, CompPin, OnOff):
    global JPcolors, breadboard_canvas, Jumper_Connections_circles, circle_adjacency_list
    global BBwidth, BBheight, BBGridSize
    global TL1XY, BL1XY, TR1XY, BR1XY, JP1XY, JP9XY, AINHXY

    #### The initial (x,y) mouse click location
    # Calculate Xstep and YStep size for 50 X 40 0.1" grid,
    ## ~11 pixels per grid point?
    XStep = YStep = BBwidth/BBGridSize
    HStep = int(0.4 * XStep)
    ColumHight = (4 * XStep) + HStep # Default to 5 pin high
    start_point = (0, 0)

    ### How much we want to vary the x and y direction of
    ### the mouse click location
    x_offset = 0
    y_offset = 0

    ### Width of the Jumper circle
    width = 3

    ### Region index -> -1: Reading Channels/Voltage,
    ### 0: TL, 1: BL, 2: TR, 3: BR
    index = -1

    ### Depending on the region we are connecting to,
    ### we will have a starting pixel location
    if "JP" in CompPin:
        # print("Found a JP in CompPins", CompPin)
        JPnum = int(CompPin.replace("JP","")) # extract number 1-6
        if JPnum < 9:
            YLoc = 6 + JPnum
            start_point = (2*XStep, (YLoc*XStep))
            width = 5
            ColumHight = HStep
        else:
            YLoc = 6 + JPnum - 8
            start_point = (44*XStep, (YLoc*XStep))
            width = 5
            ColumHight = HStep
    ### AWG1 
    if "AWG1" in CompPin:
        start_point = (19*XStep, (22*XStep)+ HStep)
        width = 5
        ColumHight = XStep + HStep

    ### AWG2 
    elif "AWG2" in CompPin:
        start_point = (20*XStep, (22*XStep)+ HStep)
        width = 5
        ColumHight = XStep + HStep

    ### AINH 
    elif "AINH" in CompPin:
        start_point = (13*XStep, (22*XStep)+ HStep)
        width = 5
        ColumHight = XStep + HStep

    ### BINH 
    elif "BINH" in CompPin:
        start_point = (15*XStep, (22*XStep)+ HStep)
        width = 5
        ColumHight = XStep + HStep

    ### CINH 
    elif "CINH" in CompPin:
        start_point = (17*XStep, (22*XStep)+ HStep)
        width = 5
        ColumHight = XStep + HStep

    ### TL1 starts 
    elif "TL" in CompPin:
        start_point = (TL1XY[0]*XStep, TL1XY[1]*XStep)
        x_offset = int(CompPin[2:])-1
        index = 0

    ### BL1 starts 
    elif "BL" in CompPin:
        start_point = (BL1XY[0]*XStep, BL1XY[1]*XStep)
        x_offset = int(CompPin[2:])-1
        index = 1
    
    ### TR1 starts 
    elif "TR" in CompPin:
        start_point = (TR1XY[0]*XStep, TR1XY[1]*XStep)
        x_offset = int(CompPin[2:])-1
        index = 2

    ### BR1 starts 
    elif "BR" in CompPin:
        start_point = (BR1XY[0]*XStep, BR1XY[1]*XStep)
        x_offset = int(CompPin[2:])-1
        index = 3

    #### If we are connecting
    if OnOff:
        #### If we are at region TL, BL, TR, or BR
        if index != -1:
            #### At each region, there are 5 different locations to place our components. Find the closest open spot, if one exists
##            while y_offset < 5 and Breadboard_Store[index][y_offset][x_offset]:
##                y_offset+=1
##            
##            ### No more space on the column comp pin
##            if y_offset == 5:
##                return

            #### Otherwise, we will now occupy the location
            Breadboard_Store[index][y_offset][x_offset] = 1
            
            ### Each region (ex. TL1 <-> TL2) are separated by XStep pixels
            ### At each region, the 5 different location are separated by roughly 21 pixels
            x = start_point[0]+XStep*x_offset
            y = start_point[1]+XStep*y_offset
            
            start_point = (x, y)
    
        ### At the starting point, we will add a jumper connection through a circle
        
        # 
        if JmpNum > 8 :
            circle_id = breadboard_canvas.create_rectangle(start_point[0]-HStep, start_point[1]-HStep, start_point[0]+HStep, start_point[1]+ColumHight, outline=JPcolors[JmpNum], fill=JPcolors[JmpNum], stipple="gray50")
        else:
            circle_id = breadboard_canvas.create_rectangle(start_point[0]-HStep, start_point[1]-HStep, start_point[0]+HStep, start_point[1]+ColumHight, outline=JPcolors[JmpNum], fill=JPcolors[JmpNum], stipple="gray75")
        Jumper_Connections_circles[JmpNum].append((CompPin, (index, y_offset, x_offset), (start_point[0], start_point[1]), circle_id))

        #### If we are at region TL, BL, TR, or BR
        if index != -1:

            ### If the circle is not already existed, add it to the adjacency list
            if circle_id not in circle_adjacency_list:
                circle_adjacency_list[circle_id] = []
            
            ### For other components connected to the same jumper, we will now connect to our current component through a line
##            for (_, Breadboard_info, Center, Circle) in Jumper_Connections_circles[JmpNum]:
##                if Breadboard_info[0] != -1 and circle_id != Circle:
##                    #### The circles(jumper connections) are nodes and lines(comp location connections) are edges
##                    line_id = breadboard_canvas.create_line(x,y, Center[0], Center[1], fill=JPcolors[JmpNum], width=4)
##                    circle_adjacency_list[circle_id].append((line_id, Circle))
##                    circle_adjacency_list[Circle].append((line_id, circle_id))
    
    ### If we are disconnecting
    else:
        for (Connection, Breadboard_info, Center, Circle) in Jumper_Connections_circles[JmpNum]:
            ### We will remove the jumper connection/node
            if CompPin == Connection:
                breadboard_canvas.delete(Circle)
                Jumper_Connections_circles[JmpNum].remove((Connection, Breadboard_info, Center, Circle))

                #### If we are at region TL, BL, TR, or BR
                if Breadboard_info[0] != -1:

                    #### The location on the breadboard is now free
                    Breadboard_Store[Breadboard_info[0]][Breadboard_info[1]][Breadboard_info[2]] = 0

                    #### We will remove any existing edges from the adjacency list
                    for (line_id, circle_id) in circle_adjacency_list[Circle]:
                        breadboard_canvas.delete(line_id)
                        circle_adjacency_list[circle_id].remove((line_id, Circle))
                    circle_adjacency_list[Circle] = []
                break
##
def ManualMatrix(JumperString, CompString, OnOff):
    global ser, NumConn, AuxBoard #OnOffString, NumConn

    Errors = 0
    try:
        Jumper = JumperString.get()
    except:
        Jumper = JumperString
    JmpNum = int(Jumper.replace("JP","")) - 1 # extract number 0-15
    try:
        CompPin = CompString.get()
    except:
        CompPin = CompString
    
    if "JP" in Jumper:
        ##########
        updateBreadboardConnection(JmpNum, CompPin, OnOff)
        ##########
        if "L" in CompPin:
            if CompPin != "TL17":
                if JmpNum > 7:
                    print("Jumper JP " + str(JmpNum) + " out of range in " , CompPin)
                    Errors = Errors + 1
            else: # BB pin TL17 can connect to any of JP1-4 and JP13-16
                if JmpNum > 3 and JmpNum < 12:
                    print("Jumper JP " + str(JmpNum) + " out of range in " , CompPin)
                    Errors = Errors + 1
                if JmpNum > 7:
                    JmpNum = JmpNum - 8
                # print(CompPin, JmpNum)
        elif "R" in CompPin:
            if CompPin != "TR1":
                if JmpNum < 7 or JmpNum > 15:
                    print("Jumper JP " + str(JmpNum) + " out of range in " , CompPin)
                    Errors = Errors + 1
                JmpNum = JmpNum - 8
            else: # BB pin TR1 can connect to any of JP1-4 and JP13-16
                if JmpNum > 3 and JmpNum < 12:
                    print("Jumper JP " + str(JmpNum) + " out of range in " , CompPin)
                    Errors = Errors + 1
                if JmpNum > 7:
                    JmpNum = JmpNum - 8
        #
    #print(Jumper, CompPin)
    if Errors > 0:
        NumConn.config(text = "Error: Jumper out of range! " + str(CompPin) + " " + str(Jumper))
        return
    Xpin = eval(CompPin)
    # print(Xpin, CompPin)
    ChipNum = WhichChip(Xpin) # Second net is Component pin
    if ChipNum == 5 and JmpNum > 7:
        JmpNum = JmpNum - 8
    if ChipNum > 0:
        CmpNum = only_numerics(Xpin) # extract number 0-7
        if AuxBoard.get() == 0:
            CommStr = ("X " + str(JmpNum) + " " + str(CmpNum) + " " + str(ChipNum) + " " + str(OnOff))
        else: # send Aux board command
            CommStr = ("Y " + str(JmpNum) + " " + str(CmpNum) + " " + str(ChipNum) + " " + str(OnOff))
        SendStr = CommStr + '\n'
        SendByt = SendStr.encode('utf-8')
        try:
            ser.write(SendByt)
        except:
            pass

#### The following ManualMatrix functions are created for the divided regions in the breadboard screen
##
def ManualSet_RC():
    global CompString, JumperString, BOMStatus, BOMtext, SVB
    ManualMatrix(JumperString[0], CompString[0], 1)
    if BOMStatus.get() > 0 and SVB == 0:
        Jumper = JumperString[0].get()
        Comp = CompString[0].get()
        R_Line = Comp + " " + Jumper + " cross_point\n"
        BOMtext.insert(END, R_Line)
##
def ManualSet_TL():
    global CompString, JumperString, BOMStatus, BOMtext, SVB
    ManualMatrix(JumperString[1], CompString[1], 1)
    if BOMStatus.get() > 0 and SVB == 0:
        Jumper = JumperString[1].get()
        Comp = CompString[1].get()
        R_Line = Comp + " " + Jumper + " cross_point\n"
        BOMtext.insert(END, R_Line)

##
def ManualSet_BL():
    global CompString, JumperString, BOMStatus, BOMtext, SVB
    ManualMatrix(JumperString[2], CompString[2], 1)
    if BOMStatus.get() > 0 and SVB == 0:
        Jumper = JumperString[2].get()
        Comp = CompString[2].get()
        R_Line = Comp + " " + Jumper + " cross_point\n"
        BOMtext.insert(END, R_Line)
##
def ManualSet_TR():
    global CompString, JumperString, BOMStatus, BOMtext, SVB
    ManualMatrix(JumperString[3], CompString[3], 1)
    if BOMStatus.get() > 0 and SVB == 0:
        Jumper = JumperString[3].get()
        Comp = CompString[3].get()
        R_Line = Comp + " " + Jumper + " cross_point\n"
        BOMtext.insert(END, R_Line)
##
def ManualSet_BR():
    global CompString, JumperString, BOMStatus, BOMtext, SVB
    ManualMatrix(JumperString[4], CompString[4], 1)
    if BOMStatus.get() > 0 and SVB == 0:
        Jumper = JumperString[4].get()
        Comp = CompString[4].get()
        R_Line = Comp + " " + Jumper + " cross_point\n"
        BOMtext.insert(END, R_Line)
##
def ManualReSet_RC():
    global CompString, JumperString
    ManualMatrix(JumperString[0], CompString[0], 0)
##
def ManualReSet_TL():
    global CompString, JumperString
    ManualMatrix(JumperString[1], CompString[1], 0)
##
def ManualReSet_BL():
    global CompString, JumperString
    ManualMatrix(JumperString[2], CompString[2], 0)
##
def ManualReSet_TR():
    global CompString, JumperString
    ManualMatrix(JumperString[3], CompString[3], 0)
##
def ManualReSet_BR():
    global CompString, JumperString
    ManualMatrix(JumperString[4], CompString[4], 0)
##
def ManualMatrix_RC():
    global CompString, JumperString
    ManualMatrix(JumperString[0], CompString[0], OnOff_RC.get())
##
def ManualMatrix_RC():
    global CompString, JumperString
    ManualMatrix(JumperString[0], CompString[0], OnOff_RC.get())
##
def ManualMatrix_TL():
    global CompString, JumperString
    ManualMatrix(JumperString[1], CompString[1], OnOff_TL.get())
##
def ManualMatrix_BL():
    global CompString, JumperString
    ManualMatrix(JumperString[2], CompString[2], OnOff_BL.get())
##
def ManualMatrix_TR():
    global CompString, JumperString
    ManualMatrix(JumperString[3], CompString[3], OnOff_TR.get())
##
def ManualMatrix_BR():
    global CompString, JumperString
    ManualMatrix(JumperString[4], CompString[4], OnOff_BR.get())
## Check Boxes
def ManualCheck_RC():
    global OnOffString, OnOff
    if OnOff[0].get() == 0:
        OnOffString[0].config(style="Disab.TCheckbutton")
    else:
        OnOffString[0].config(style="Enab.TCheckbutton")
##
def ManualCheck_TL():
    global OnOffString, OnOff
    if OnOff[1].get() == 0:
        OnOffString[1].config(style="Disab.TCheckbutton")
    else:
        OnOffString[1].config(style="Enab.TCheckbutton")
##
def ManualCheck_BL():
    global OnOffString, OnOff
    if OnOff[2].get() == 0:
        OnOffString[2].config(style="Disab.TCheckbutton")
    else:
        OnOffString[2].config(style="Enab.TCheckbutton")
##
def ManualCheck_TR():
    global OnOffString, OnOff
    if OnOff[3].get() == 0:
        OnOffString[3].config(style="Disab.TCheckbutton")
    else:
        OnOffString[3].config(style="Enab.TCheckbutton")
##
def ManualCheck_BR():
    global OnOffString, OnOff
    if OnOff[4].get() == 0:
        OnOffString[4].config(style="Disab.TCheckbutton")
    else:
        OnOffString[4].config(style="Enab.TCheckbutton")
##
def DrawBBHoles(Xd, Yd, Yorg, XStep, PinW, Top):
    global breadboard_canvas, BBFont
    for Xi in range(0,17,1):
        ColNum = str(Xi+1)
        if Top == 1:
            breadboard_canvas.create_text(Xd, Yd-PinW, text = ColNum, fill="black", anchor='s', font=("arial", BBFont, "bold"))
        for Yi in range(0,5,1):
            breadboard_canvas.create_rectangle(Xd-PinW, Yd+PinW, Xd+PinW, Yd-PinW, fill="black", outline="gray", width=1)
            Yd = Yd + XStep
        if Top == 0:
            Yd = Yd - XStep
            breadboard_canvas.create_text(Xd, Yd+PinW, text = ColNum, fill="black", anchor='n', font=("arial", BBFont, "bold"))
        Yd = Yorg
        Xd = Xd + XStep
##
def DrawBreadBoardGraphic():
    global BBwidth, BBheight, BBGridSize, breadboard_canvas, FontSize
    global TL1XY, BL1XY, TR1XY, BR1XY, JP1XY, JP9XY, AINHXY, PWConnString
    global VPowerConnections, VPower, PWConnString, VPower_id, BBblack
    global COLORwhite, COLORblack, GUITheme, Jumper_Connections
    global XlabLogo_image, NotesString

    if "Sun Valley Dark" in GUITheme:
        BBblack = "#ffffff" # 100% white
    else:
        BBblack = "#000000" # 100% black
    
    breadboard_canvas.delete(ALL) # remove all items
    # print("Just Cleared BB Canvas")
    # Calculate Xstep and YStep size for 50 X 40 0.1" square grid,
    # ~11 pixels per grid point?
    XStep = YStep = BBwidth/BBGridSize
    HStep = int(XStep/2)
    PinW = int(0.3 * XStep)
    # Draw BB outlines
    Xorg = Yorg = 4 * XStep
    Xd = 22 * XStep
    Yd = 17 * XStep
    MidY = (BL1XY[1] - 1) * XStep
    breadboard_canvas.create_rectangle(Xorg, Yorg, Xd, Yd, fill="white", outline="black", width=2)
    Xorg = 24 * XStep
    Xd = 42 * XStep
    breadboard_canvas.create_rectangle(Xorg, Yorg, Xd, Yd, fill="white", outline="black", width=2)
    # Left mounting holes
    Xorg = int(6 * XStep)
    Yorg = int(10.5 * XStep)
    Dia = int(XStep * 0.75)
    breadboard_canvas.create_oval(Xorg-Dia, Yorg-Dia, Xorg+Dia, Yorg+Dia, outline="black", fill="white", width=2)
    Xorg = int(20 * XStep)
    breadboard_canvas.create_oval(Xorg-Dia, Yorg-Dia, Xorg+Dia, Yorg+Dia, outline="black", fill="white", width=2)
    # Right mounting holes
    Xorg = int(26 * XStep)
    breadboard_canvas.create_oval(Xorg-Dia, Yorg-Dia, Xorg+Dia, Yorg+Dia, outline="black", fill="white", width=2)
    Xorg = int(40 * XStep)
    breadboard_canvas.create_oval(Xorg-Dia, Yorg-Dia, Xorg+Dia, Yorg+Dia, outline="black", fill="white", width=2)
    # Left slot
    Xorg = int(7 * XStep)
    Xd = int(19 * XStep)
    breadboard_canvas.create_rectangle(Xorg, Yorg-Dia, Xd, Yorg+Dia, fill="white", outline="black", width=2)
    # Rigth Slot
    Xorg = int(27 * XStep)
    Xd = int(39 * XStep)
    breadboard_canvas.create_rectangle(Xorg, Yorg-Dia, Xd, Yorg+Dia, fill="white", outline="black", width=2)
    # Start with TL1 at Grid X = 5 and Y = 5
    TL1XY = [5,5]
    #
    Xorg = Xd = Yorg = Yd = 5 * XStep
    DrawBBHoles(Xd, Yd, Yorg, XStep, PinW, 1)
    # Next BL1 at Grid X = 5 and Y = 12
    BL1XY = [5,12]
    #
    Xorg = Xd = 5 * XStep
    Yorg = Yd = 12 * XStep
    DrawBBHoles(Xd, Yd, Yorg, XStep, PinW, 0)
    # Next TR1 at Grid X = 27 and Y = 5
    TR1XY = [25,5]
    #
    Xorg = Xd = 25 * XStep
    Yorg = Yd = 5 * XStep
    DrawBBHoles(Xd, Yd, Yorg, XStep, PinW, 1)
    # Next BR1 at Grid X = 27 and Y = 12
    BR1XY = [25,12]
    #
    Xorg = Xd = 25 * XStep
    Yorg = Yd = 12 * XStep
    DrawBBHoles(Xd, Yd, Yorg, XStep, PinW, 0)
    # Top Power Rail
    Xorg = 8 * XStep
    Yorg = int(0.5 * XStep)
    Xd = 38 * XStep
    Yd = int(3.5 * XStep)
    breadboard_canvas.create_rectangle(Xorg, Yorg, Xd, Yd, fill="white", outline="black", width=2)
    breadboard_canvas.create_line(Xorg+HStep, Yorg+HStep, Xd-HStep, Yorg+HStep, fill="red", width=2)
    breadboard_canvas.create_text(Xd+XStep+HStep, Yorg+HStep, text = "+5V", fill="red", font=("arial", FontSize, "bold"))
    breadboard_canvas.create_line(Xorg+HStep, Yd-HStep, Xd-HStep, Yd-HStep, fill="blue", width=2)
    breadboard_canvas.create_text(Xd+XStep+HStep, Yd-HStep, text = "GND", fill=BBblack, font=("arial", FontSize, "bold"))
    #
    Xorg = Xd = 9 * XStep
    Yorg = Yd = int(1.5 * XStep)
    for Xi in range(0,5,1):
        for Yi in range(0,5,1):
            breadboard_canvas.create_rectangle(Xd-PinW, Yd+PinW, Xd+PinW, Yd-PinW, fill="black", outline="gray", width=1)
            Xd = Xd + XStep
        Xd = Xd + XStep
    Xorg = Xd = 9 * XStep
    Yorg = Yd = int(2.5 * XStep)
    for Xi in range(0,5,1):
        for Yi in range(0,5,1):
            breadboard_canvas.create_rectangle(Xd-PinW, Yd+PinW, Xd+PinW, Yd-PinW, fill="black", outline="gray", width=1)
            Xd = Xd + XStep
        Xd = Xd + XStep
    # Bottom Power Rail
    Xorg = 8 * XStep
    Yorg = 18 * XStep
    Xd = 38 * XStep
    Yd = 21 * XStep
    breadboard_canvas.create_rectangle(Xorg, Yorg, Xd, Yd, fill="white", outline="black", width=2)
    breadboard_canvas.create_line(Xorg+HStep, Yorg+HStep, Xd-HStep, Yorg+HStep, fill="red", width=2)
    breadboard_canvas.create_text(Xd+XStep+HStep, Yorg+HStep, text = "GND", fill=BBblack, font=("arial", FontSize, "bold"))
    breadboard_canvas.create_line(Xorg+HStep, Yd-HStep, Xd-HStep, Yd-HStep, fill="blue", width=2)
    breadboard_canvas.create_text(Xd+XStep+HStep, Yd-HStep, text = "-5V", fill="blue", font=("arial", FontSize, "bold"))
    Xorg = Xd = 9 * XStep
    Yorg = Yd = 19 * XStep
    for Xi in range(0,5,1):
        for Yi in range(0,5,1):
            breadboard_canvas.create_rectangle(Xd-PinW, Yd+PinW, Xd+PinW, Yd-PinW, fill="black", outline="gray", width=1)
            Xd = Xd + XStep
        Xd = Xd + XStep
    Xorg = Xd = 9 * XStep
    Yorg = Yd = 20 * XStep
    for Xi in range(0,5,1):
        for Yi in range(0,5,1):
            breadboard_canvas.create_rectangle(Xd-PinW, Yd+PinW, Xd+PinW, Yd-PinW, fill="black", outline="gray", width=1)
            Xd = Xd + XStep
        Xd = Xd + XStep
    # AWG / Scope points
    AINHXY = [12,22]
    #
    Xorg = 12 * XStep
    Xd = 21 * XStep 
    Yorg = 22 * XStep
    Yd = 24 * XStep
    breadboard_canvas.create_rectangle(Xorg, Yorg, Xd, Yd, fill="white", outline="black", width=2)
    Xorg = 20 * XStep
    Yorg = 23 * XStep
    Xd = 22 * XStep
    Xt = 24 * XStep
    Yd = 27 * XStep
    breadboard_canvas.create_rectangle(Xorg-PinW, Yorg+PinW, Xorg+PinW, Yorg-PinW, fill="black", outline="gray", width=1)
    breadboard_canvas.create_line(Xorg, Yorg, Xorg, Yd, fill=BBblack, width=3)
    breadboard_canvas.create_line(Xorg, Yd, Xd, Yd, fill=BBblack, width=3, arrow="last")
    breadboard_canvas.create_text(Xt, Yd, text = "AWG2", fill=BBblack, font=("arial", FontSize, "bold"))
    Xorg = 19 * XStep
    Yd = 28 * XStep
    breadboard_canvas.create_rectangle(Xorg-PinW, Yorg+PinW, Xorg+PinW, Yorg-PinW, fill="black", outline="gray", width=1)
    breadboard_canvas.create_line(Xorg, Yorg, Xorg, Yd, fill=BBblack, width=3)
    breadboard_canvas.create_line(Xorg, Yd, Xd, Yd, fill=BBblack, width=3, arrow="last")
    breadboard_canvas.create_text(Xt, Yd, text = "AWG1", fill=BBblack, font=("arial", FontSize, "bold"))
    Xorg = 17 * XStep
    Yd = 29 * XStep
    breadboard_canvas.create_rectangle(Xorg-PinW, Yorg+PinW, Xorg+PinW, Yorg-PinW, fill="black", outline="gray", width=1)
    breadboard_canvas.create_line(Xorg, Yorg, Xorg, Yd, fill=BBblack, width=3)
    breadboard_canvas.create_line(Xorg, Yd, Xd, Yd, fill=BBblack, width=3, arrow="last")
    breadboard_canvas.create_text(Xt, Yd, text = "CINH", fill=BBblack, font=("arial", FontSize, "bold"))
    Xorg = 15 * XStep
    Yd = 30 * XStep
    breadboard_canvas.create_rectangle(Xorg-PinW, Yorg+PinW, Xorg+PinW, Yorg-PinW, fill="black", outline="gray", width=1)
    breadboard_canvas.create_line(Xorg, Yorg, Xorg, Yd, fill=BBblack, width=3)
    breadboard_canvas.create_line(Xorg, Yd, Xd, Yd, fill=BBblack, width=3, arrow="last")
    breadboard_canvas.create_text(Xt, Yd, text = "BINH", fill=BBblack, font=("arial", FontSize, "bold"))
    Xorg = 13 * XStep
    Yd = 31 * XStep
    breadboard_canvas.create_rectangle(Xorg-PinW, Yorg+PinW, Xorg+PinW, Yorg-PinW, fill="black", outline="gray", width=1)
    breadboard_canvas.create_line(Xorg, Yorg, Xorg, Yd, fill=BBblack, width=3)
    breadboard_canvas.create_line(Xorg, Yd, Xd, Yd, fill=BBblack, width=3, arrow="last")
    breadboard_canvas.create_text(Xt, Yd, text = "AINH", fill=BBblack, font=("arial", FontSize, "bold"))
    # Left and Right Jumper Headers
    JP1XY = [2,7]
    JP9XY = [44,7]
    #
    Xorg = 2 * XStep
    Yorg = Yd = 7 * XStep
    Yb = 15 * XStep
    breadboard_canvas.create_rectangle(Xorg-XStep, Yorg-YStep, Xorg+XStep, Yb, fill="white", outline="black", width=2)
    for Yi in range(0,8,1):
        breadboard_canvas.create_rectangle(Xorg-PinW, Yd+PinW, Xorg+PinW, Yd-PinW, fill="black", outline="gray", width=1)
        Yd = Yd + XStep
    #
    Xorg = 44 * XStep
    Yd = 7 * XStep
    breadboard_canvas.create_rectangle(Xorg-XStep, Yorg-YStep, Xorg+XStep, Yb, fill="white", outline="black", width=2)
    for Yi in range(0,8,1):
        breadboard_canvas.create_rectangle(Xorg-PinW, Yd+PinW, Xorg+PinW, Yd-PinW, fill="black", outline="gray", width=1)
        Yd = Yd + XStep
    ### Now redraw matrix connections
    for i in range(0, 16, 1):
        for j in range(0, len(Jumper_Connections[i]), 1):
            # print(Jumper_Connections[i])
            CompPin = Jumper_Connections[i][j]
            modifyBreadboardCanvas(i, CompPin, 1)
    # Show Power / GND wires if any
    # DrawPowerWires()
    # Place XLab logo
    try:
        Xd = 3 * XStep
        Yd = 32 * XStep
        breadboard_canvas.create_image((Xd, Yd), image=XlabLogo_image) # 500 , 375 
        # breadboard_canvas.image = breadboard_image
    except:
        pass
    # Place connection notes
    Xd = 3 * XStep
    Yd = 37 * XStep
    breadboard_canvas.create_text(Xd, Yd, text=NotesString, anchor='nw', fill=BBblack, font=("arial", FontSize, "bold"))
##
def MakeBreadboardScreen():
    global breadboardwindow, BreadboardStatus, AuxBoard, ExtBoard
    global BBwidth, BBheight, BBGridSize, CANVASwidthBB, CANVASheightBB
    global J_Connections_Labels, PassFailSelfCal, PassFailSvBB
    global FileString, NumConn, CPRevDate, SWRev, HWRevOne, FWRevOne
    global CompString, JumperString, OnOff, OnOffString, FailedPins
    global FrameBG, BorderSize, ErrConn, ShowBallonHelp
    global JumperSpinBoxList, XlabLogo_image
    global CompSpinBoxList_RC, CompSpinBoxList_TL, CompSpinBoxList_BL, CompSpinBoxList_TR, CompSpinBoxList_BR
    global click_loc, breadboard_image, JPcolors, breadboard_canvas

    style = Style() # This accesses the ttk Style object
    style.configure("Prompt.TEntry", fieldbackground="white", foreground="black")
    
    if BreadboardStatus.get() == 0:
        try:
            XlabLogo_image = PhotoImage(file='./XLab-logo.png') #
            # image size in pixels is 50 X 50
            # XlabLogo_image =  XlabLogo_image.zoom(2, 2)
            # XlabLogo_image = XlabLogo_image.subsample(3,3)
        except:
            pass
        BreadboardStatus.set(1)
        CANVASwidthBB = BBwidth     # BB canvas width
        CANVASheightBB = BBheight # BB canvas height
        ### Set the size and shape of the Breadboard window 
        breadboardwindow = Toplevel()
        breadboardwindow.title("Software Breadboard Connections " + CPRevDate)
        breadboardwindow.protocol("WM_DELETE_WINDOW", DestroyBreadboardScreen)
        breadboardwindow.resizable(TRUE,TRUE)
        # breadboardwindow.geometry('+300+300')
        breadboardwindow.configure(background=FrameBG, borderwidth=BorderSize)
        
        ### The labels that tells the connections for each jumper
        J_Connections_Labels = []

        ### The Component string tells us what to connect to the jumper
        CompString = []
        OnOffString = []
        ### The Jumper string tells us what jumper we are dealing with
        JumperString = []

        ManualMatrix_funcs = [ManualMatrix_RC, ManualMatrix_TL, ManualMatrix_BL, ManualMatrix_TR, ManualMatrix_BR]
        ManualCheck_funcs = [ManualCheck_RC, ManualCheck_TL, ManualCheck_BL, ManualCheck_TR, ManualCheck_BR]
        ManualSet_funcs = [ManualSet_RC, ManualSet_TL, ManualSet_BL, ManualSet_TR, ManualSet_BR]
        ManualReSet_funcs = [ManualReSet_RC, ManualReSet_TL, ManualReSet_BL, ManualReSet_TR, ManualReSet_BR]
        regions = ["XC", "TL", "BL", "TR", "BR"]

        CompSpinBoxList_arr = [CompSpinBoxList_RC, CompSpinBoxList_TL, CompSpinBoxList_BL, CompSpinBoxList_TR, CompSpinBoxList_BR]
        JumperSpinBoxList_arr = [JumperSpinBoxList[0:4]+JumperSpinBoxList[12:17], JumperSpinBoxList[0:8], JumperSpinBoxList[0:8], JumperSpinBoxList[8:16], JumperSpinBoxList[8:16]]
        
        OnOff = [OnOff_RC, OnOff_TL, OnOff_BL, OnOff_TR, OnOff_BR]
        
        #### LEFT SIDE OF SCREEN ####

        ### The following is the original Matrix window of the Cross Point Interface

        matrixwindow = Frame(breadboardwindow, borderwidth=BorderSize, relief=FrameRelief)
        matrixwindow.pack(side=LEFT, fill=BOTH, expand=NO)
        toptext = "Cross Point Interface " + FWRevOne
        toplab = Label(matrixwindow,text=toptext, style="A12B.TLabel")
        toplab.grid(row=0, column=0, columnspan=4, sticky=W)
        mcl1 = Label(matrixwindow,text="LTspice Netlist File")
        mcl1.grid(row=1, column=0, columnspan=2, sticky=W)
        FileString = Entry(matrixwindow, width=50)
        FileString.bind("<Return>", ConfigCrossPointFile)
        FileString.grid(row=2, column=0, columnspan=4, sticky=W)
        FileString.delete(0,"end")
        FileString.insert(0,"")
        NumConn = Label(matrixwindow,text="Number of Connections ")
        NumConn.grid(row=3, column=0, columnspan=4, sticky=W)
        ErrConn = Label(matrixwindow,text="Number of Errors ")
        ErrConn.grid(row=4, column=0, columnspan=4, sticky=W)
        Browsebutton = Button(matrixwindow, text="Browse", style="W8.TButton", command=BrowsNetFile)
        Browsebutton.grid(row=5, column=0, columnspan=1, sticky=W, pady=4)
        #
        Sendbutton = Button(matrixwindow, text="Send", style="W6.TButton", command=ConfigCrossPointFile)
        Sendbutton.grid(row=5, column=1, columnspan=1, sticky=W, pady=4)
        # 
        resetmxbutton = Button(matrixwindow, text="Reset", style="W6.TButton", command=ResetMatrix)
        resetmxbutton.grid(row=5, column=2, columnspan=1, sticky=W, pady=4)
        #
        dumpnetsbutton = Button(matrixwindow, text="Save Nets", style="W10.TButton", command=DumpNetList)
        dumpnetsbutton.grid(row=6, column=0, columnspan=1, sticky=W, pady=4)
        #
        if ExtBoard.get() == 1:
            SelBoard = Checkbutton(matrixwindow, text="Exp Board", variable = AuxBoard, onvalue = 1, offvalue = 0, width=10)
            SelBoard.grid(row=6, column=1, columnspan=1, sticky=W, pady=4)
        #
        Helpmenu = Menubutton(matrixwindow, text="Help", style="W6.TButton")
        Helpmenu.menu = Menu(MeasmenuA, tearoff = 0 )
        Helpmenu["menu"]  = Helpmenu.menu
        Helpmenu.menu.add_command(label="LTspice Guide", foreground="blue", command=HelpLTspice)
        Helpmenu.menu.add_command(label="Self Test Guide", foreground="blue", command=HelpSelfTest)
        Helpmenu.menu.add_command(label="Digital Guide", foreground="blue", command=HelpDigital)
        Helpmenu.grid(row=6, column=2, columnspan=1, sticky=W, pady=6)
        #
        if ShowBallonHelp > 0:
            try:
                Browsebutton_tip = CreateToolTip(Browsebutton, 'Select LTspice net list file')
            except:
                donothing()
            try:
                Sendbutton_tip = CreateToolTip(Sendbutton, 'Send net list connections to BB')
            except:
                donothing()
            try:
                resetmxbutton_tip = CreateToolTip(resetmxbutton, 'Reset all BB connections to open')
            except:
                donothing()
            try:
                dumpnetsbutton_tip = CreateToolTip(dumpnetsbutton, 'Save all BB connections to a file')
            except:
                donothing()
            try:
                Helpmenu_tip = CreateToolTip(Helpmenu, 'Access Help pages')
            except:
                donothing()
        ### The loop simply divides the Component String, Jumper String, and On/Off switch into different regions
        for region in range(0, 5, 1):
            cpcl1 = Label(matrixwindow,text=f"{regions[region]} Comp Pin")
            cpcl1.grid(row=2*region + 7, column=0, columnspan=1, sticky=W)

            jpcl1 = Label(matrixwindow,text="Jumper")
            jpcl1.grid(row=2*region + 7, column=1, columnspan=1, sticky=W)
       
            oncl1 = Label(matrixwindow,text="Off")
            oncl1.grid(row=2*region + 7, column=2, columnspan=1, sticky=W)
            oncl2 = Label(matrixwindow,text="On")
            oncl2.grid(row=2*region + 7, column=3, columnspan=1, sticky=W)
        
            #### The component label is added in the specified region
            CompString.append(Combobox(matrixwindow, state="readonly", width=6, values=CompSpinBoxList_arr[region]))
            CompString[region].grid(row=2*region + 8, column=0, columnspan=1, sticky=W)
            ####

            if region == 0:
                CompString[region].set("AWG1")
            else:
                if regions[region] != "TR":
                    CompString[region].set(f"{regions[region]}1")
                else:
                    CompString[region].set(f"{regions[region]}2")

            #### The jumper label is added in the specified region
            JumperString.append(Combobox(matrixwindow, state="readonly", width=6, values=JumperSpinBoxList_arr[region]))
            JumperString[region].grid(row=2*region + 8, column=1, columnspan=1, sticky=W)
            ####

            if regions[region] != "TR" and regions[region] != "BR":
                JumperString[region].set("JP1")
            else:
                JumperString[region].set("JP9")

            #### The On/Off check box is added in the specified region
            ## OnOffString.append(Checkbutton(matrixwindow, variable = OnOff[region], onvalue = 1, offvalue = 0, width=2, command=ManualCheck_funcs[region]))
            ## OnOffString[region].grid(row=2*region + 8, column=2, columnspan=1, sticky=W)
            ## ManualCheck_funcs[region]()
            ####
            Resetbutton = Button(matrixwindow, image=RoundRedBtn, command=ManualReSet_funcs[region])
            Resetbutton.grid(row=2*region + 8, column=2, sticky=W)
            Setbutton = Button(matrixwindow, image = RoundGrnBtn, command=ManualSet_funcs[region])
            Setbutton.grid(row=2*region + 8, column=3, sticky=W)
            ## Setbutton = Button(matrixwindow, text="Set", style="W6.TButton", command=ManualMatrix_funcs[region])
            ## Setbutton.grid(row=2*region + 8, column=3, sticky=W, pady=4)

        ##### Calibrate Button Section
        #
        if HWRevOne != "None":
            SelfCalibrateButton = Button(matrixwindow, text="Calibrate", style="W10.TButton", command=self_calibrate)
            SelfCalibrateButton.grid(row=17, column=0, columnspan=1, sticky=W, pady =1)
            PassFailSelfCal = Label(matrixwindow,text="")
            PassFailSelfCal.grid(row=17, column=1, columnspan=4, sticky=W, pady=1)
            #### Self Test Button Section
            #
            SelfTestbutton = Button(matrixwindow, text="Self Test", style="W10.TButton", command=BB_test)
            SelfTestbutton.grid(row=18, column=0, columnspan=1, sticky=W, pady=1)
            FailedPins = Label(matrixwindow,text="")
            FailedPins.grid(row=18, column=1, columnspan=4, sticky=W, pady=1)
        #####
        if ShowBallonHelp > 0:
            try:
                SelfCalibrateButton_tip = CreateToolTip(SelfCalibrateButton, 'Calibrate Scope input resistor dividers')
            except:
                donothing()
            try:
                SelfTestbutton_tip = CreateToolTip(SelfTestbutton, 'Run Continuity Self Test.')
            except:
                donothing()
        BOMButton = Button(matrixwindow, text="Open Text UI", style="W16.TButton", command=MakeBOMScreen)
        BOMButton.grid(row=19, column=0, columnspan=1, sticky=W, pady=1)
        #
        VerifyButton = Button(matrixwindow, text="Schematic Vs BB", style="W17.TButton", command=VerifyCompsFile)
        VerifyButton.grid(row=20, column=0, columnspan=2, sticky=W, pady=1)
        PassFailSvBB = Label(matrixwindow,text="")
        PassFailSvBB.grid(row=20, column=2, columnspan=4, sticky=W, pady=1)
        

        if HWRevOne == "Red3":
            TestResButton = Button(matrixwindow, text="Man Test Resistor", style="W17.TButton", command=MakeTestResWindow)
            TestResButton.grid(row=21, column=0, columnspan=2, sticky=W, pady=1)


    # --- PROMPT BOX ---
       # --- CLASSIC TK SETUP ---
        import tkinter as tk_base  # Ensure we have access to classic widgets

        # 1. CREATE STYLE FOR CURSOR
        # This fixes the cursor color for the ttk Entry
        style = Style()
        style.configure("Prompt.TEntry", 
                        fieldbackground="white", 
                        foreground="black", 
                        insertcolor="black", # <--- FIXES VISIBLE CURSOR
                        insertwidth=2)

        # 2. CREATE DRAGGABLE PANED WINDOW
        # This allows you to drag the divider up/down to resize the chat
        chat_paner = tk_base.PanedWindow(matrixwindow, 
                                        orient=tk_base.VERTICAL, 
                                        sashwidth=6, 
                                        sashrelief=tk_base.RAISED, 
                                        bg=FrameBG)
        chat_paner.grid(row=22, column=0, columnspan=4, sticky="nsew", padx=5, pady=10)
        
        # Give row 22 all the weight so it fills the bottom area
        matrixwindow.rowconfigure(22, weight=1)

        # 3. CHAT HISTORY (Top Pane)
        global ChatHistory
        ChatHistory = scrolledtext.ScrolledText(
            chat_paner, # Parent is the paner
            height=10, 
            state='disabled', 
            wrap='word', 
            bg="white", 
            foreground="black", 
            insertbackground="black", 
            font=("Arial", 10)
        )
        
        # Add to paned window
        chat_paner.add(ChatHistory, minsize=100)

        # 4. PROMPT INPUT AREA (Bottom Pane)
        # We use a frame to hold the Label and Entry together in the bottom pane
        input_container = tk_base.Frame(chat_paner, bg=FrameBG)
        
        PromptLabel = Label(input_container, text="User Prompt:", style="A12B.TLabel")
        PromptLabel.pack(side=tk_base.TOP, anchor=tk_base.W, pady=(5, 0))

        global PromptBox
        # Using Style "Prompt.TEntry" defined above
        PromptBox = Entry(input_container, style="Prompt.TEntry")
        PromptBox.pack(side=tk_base.TOP, fill=tk_base.X, pady=(0, 10))
        
        # Add frame to paned window
        chat_paner.add(input_container, minsize=80)

        # 5. CONFIGURE TAGS
        ChatHistory.tag_configure("user_tag", foreground="#0078d4", font=("Arial", 10, "bold"))
        ChatHistory.tag_configure("ai_tag", foreground="#2b88d8", font=("Arial", 10, "bold"))
        ChatHistory.tag_configure("text_tag", foreground="black", font=("Arial", 10))
        ChatHistory.tag_configure("status_tag", foreground="gray", font=("Arial", 10, "italic"))

        # 6. BINDINGS & FOCUS
        PromptBox.bind("<Return>", handle_user_prompt)
        PromptBox.focus_set()


        ############################## 
        ### MIDDLE SIDE OF SCREEN ####
        #### The top part of the middle section is the simulated image of the breadboard
        breadboard_connections = Frame(breadboardwindow, borderwidth=BorderSize, relief=FrameRelief)
        breadboard_connections.pack(side=LEFT, fill=BOTH, expand=YES)
        #
        image_section = Frame(breadboard_connections, borderwidth=BorderSize, relief=FrameRelief)
        image_section.pack(side=TOP, fill=BOTH, expand=YES)
        #
        breadboard_canvas = Canvas(image_section, width=CANVASwidthBB, height=CANVASheightBB, cursor='cross')
        breadboard_canvas.pack(side=TOP, fill=BOTH, expand=YES)
        #
        breadboard_canvas.bind('<Configure>', BBCAresize)
        breadboard_canvas.bind('<1>', onBBClick)
        breadboard_canvas.bind('<3>', onBBClick)
        DrawBreadBoardGraphic()
        ####
        #### Bottom of the middle Section currently tells the pixel location of our mouse click
        buttons_section = Frame(breadboard_connections, borderwidth=BorderSize, relief=FrameRelief)
        buttons_section.pack(side=TOP, fill=BOTH, expand=NO)

        test22 = Label(buttons_section,text="Interactive Mouse")
        test22.grid(row=0, column=0, columnspan=4, sticky=W)

        click_loc = Label(buttons_section,text="Click Location")
        click_loc.grid(row=1, column=1, columnspan=4, sticky=W)

        #####
        ##############################
        #### RIGHT SIDE OF SCREEN ####
        ### The right side of the screen goes through all 16 Jumpers and sets up the initial connections through text labels
        J_all_connections = Frame(breadboardwindow, borderwidth=BorderSize, relief=FrameRelief)
        J_all_connections.pack(side=RIGHT, fill=BOTH, expand=NO)

        J_all_topLabel = Label(J_all_connections,text="Jumper 1-16 Connections ", style="A12B.TLabel")
        J_all_topLabel.grid(row=0, column=0, columnspan=4, sticky=W)

        for i in range(0, 16, 1):
            J = Label(J_all_connections,font="Arial 10 bold",text=f"Jumper {i+1}: ", foreground = JPcolors[i])
            J.grid(row=2*(i)+1, column=0, columnspan=4, sticky=W)

            J_connections = Label(J_all_connections,font="Arial 8 bold", borderwidth=2, text="No connections")
            J_connections.grid(row=2*(i+1), column=0, columnspan=4, sticky=W)

            J_Connections_Labels.append(J_connections)

        ##############################

        # Add this at the end of the function to set focus on startup
        PromptBox.focus_set()
#
def BBCAresize(event):
    global breadboard_canvas, BBwidth, BBheight, CANVASwidthBB, CANVASheightBB
    global BBFont, FontSize, BBGridSize
    
    CANVASwidthBB = event.width - 4
    CANVASheightBB = event.height - 4
    BBwidth = CANVASwidthBB # new grid width
    BBheight = CANVASheightBB # new grid height
    BBFont = int(0.6 * BBwidth/BBGridSize)
    DrawBreadBoardGraphic()
    UpDateBOMScreen()
#
## Display the location on the BB of the mouse click.
def onBBClick(event):
    global BBwidth, BBheight, BBGridSize, breadboard_canvas, FontSize
    global TL1XY, BL1XY, TR1XY, BR1XY, JP1XY, JP9XY, AINHXY
    global JumperString, CompString, OnOff
    global click_loc, BOMStatus, BOMtext

    # Calculate Xstep and YStep size for 50 X 40 0.1" grid, 11 pixels per grid point?
    XStep = YStep = BBwidth/BBGridSize
    HStep = int(XStep/2)
    # Find extent of four BB regions
    TLwidth = 18 * XStep
    TLheight = 6 * XStep
    TLMinX = (TL1XY[0] * XStep) - HStep
    TLMaxX = TLMinX + TLwidth
    TLMinY = (TL1XY[1] * XStep) - HStep
    TLMaxY = TLMinY + TLheight
    #
    BLMinX = (BL1XY[0] * XStep) - HStep
    BLMaxX = BLMinX + TLwidth
    BLMinY = (BL1XY[1] * XStep) - HStep
    BLMaxY = BLMinY + TLheight
    #
    TRMinX = (TR1XY[0] * XStep) - HStep
    TRMaxX = TRMinX + TLwidth
    TRMinY = (TR1XY[1] * XStep) - HStep
    TRMaxY = TRMinY + TLheight
    #
    BRMinX = (BR1XY[0] * XStep) - HStep
    BRMaxX = BRMinX + TLwidth
    BRMinY = (BR1XY[1] * XStep) - HStep
    BRMaxY = BRMinY + TLheight
    # Find extent of left and right jumper regions
    JLwidth = 2* XStep
    JLheight = 9 * XStep
    JLMinX = (JP1XY[0] * XStep) - HStep
    JLMaxX = JLMinX + JLwidth
    JLMinY = (JP1XY[1] * XStep) - HStep
    JLMaxY = JLMinY + JLheight
    #
    JRMinX = (JP9XY[0] * XStep) - HStep
    JRMaxX = JRMinX + JLwidth
    JRMinY = (JP9XY[1] * XStep) - HStep
    JRMaxY = JRMinY + JLheight
    # Find extent of Scope AWG pin regions
    INwidth = 9 * XStep
    INheight = 2 * XStep
    INMinX = (AINHXY[0] * XStep) - HStep
    INMaxX = INMinX + INwidth
    INMinY = (AINHXY[1] * XStep) - HStep
    INMaxY = INMinY + INheight
    #
    CursorX = event.x
    CursorY = event.y
    # Find which BB pin was clicked on
    if CursorX > TLMinX and CursorX < TLMaxX and CursorY > TLMinY and CursorY < TLMaxY:
        GridX = 1 + int((CursorX - TLMinX) / XStep)
        PinClicked = "TL" + str(GridX)
        CompString[1].set(PinClicked)
        PinBB = "Clicked on " + PinClicked
    elif CursorX > BLMinX and CursorX < BLMaxX and CursorY > BLMinY and CursorY < BLMaxY:
        GridX = 1 + int((CursorX - TLMinX) / XStep)
        PinClicked = "BL" + str(GridX)
        CompString[2].set(PinClicked)
        PinBB = "Clicked on " + PinClicked
    elif CursorX > TRMinX and CursorX < TRMaxX and CursorY > TRMinY and CursorY < TRMaxY:
        GridX = 1 + int((CursorX -TRMinX) / XStep)
        PinClicked = "TR" + str(GridX)
        CompString[3].set(PinClicked)
        PinBB = "Clicked on " + PinClicked
    elif CursorX > BRMinX and CursorX < BRMaxX and CursorY > BRMinY and CursorY < BRMaxY:
        GridX = 1 + int((CursorX -TRMinX) / XStep)
        PinClicked = "BR" + str(GridX)
        CompString[4].set(PinClicked)
        PinBB = "Clicked on " + PinClicked
    elif CursorX > JLMinX and CursorX < JLMaxX and CursorY > JLMinY and CursorY < JLMaxY:
        GridY = 1 + int((CursorY - JLMinY) / XStep)
        PinClicked = "JP" + str(GridY)
        if GridY < 5:
            JumperString[0].set(PinClicked)
        JumperString[1].set(PinClicked)
        JumperString[2].set(PinClicked)
        PinBB = "Clicked on " + PinClicked
    elif CursorX > JRMinX and CursorX < JRMaxX and CursorY > JRMinY and CursorY < JRMaxY:
        GridY = 9 + int((CursorY - JLMinY) / XStep)
        PinClicked = "JP" + str(GridY)
        if GridY > 12:
            JumperString[0].set(PinClicked)
        JumperString[3].set(PinClicked)
        JumperString[4].set(PinClicked)
        PinBB = "Clicked on " + PinClicked
    elif CursorX > INMinX and CursorX < INMaxX and CursorY > INMinY and CursorY < INMaxY:
        GridX = 1 + int((CursorX - INMinX) / XStep)
        PinClicked = "AINH" # default to
        if GridX == 1:
            PinClicked = "AINH"
        elif GridX == 4:
            PinClicked = "BINH"
        elif GridX == 6:
            PinClicked = "CINH"
        elif GridX == 8:
            PinClicked = "AWG1"
        elif GridX == 9:
            PinClicked = "AWG2"
        #
        CompString[0].set(PinClicked)
        PinBB = "Clicked on " + PinClicked
    else:
        PinBB = ""
    #
    if event.num == 1:
        click_loc.config(text = PinBB, font=("arial", FontSize, "bold"))
    elif event.num == 3:
        if BOMStatus.get() > 0:
            PinClicked = PinClicked + " "
            BOMtext.insert(INSERT, PinClicked)
##
def DestroyBreadboardScreen():
    global breadboardwindow, BreadboardStatus

    BreadboardStatus.set(0)
    breadboardwindow.destroy()
#
def MakeBOMScreen():
    global BOMwindow, BOMStatus, BOMtext, CPRevDate

    if BOMStatus.get() == 0:
        BOMStatus.set(1)
        ### Set the size and shape of the Placement window 
        BOMwindow = Toplevel()
        BOMwindow.title("Comp Placement " + CPRevDate)
        BOMwindow.protocol("WM_DELETE_WINDOW", DestroyBOMScreen)
        BOMwindow.resizable(TRUE,TRUE)
        BOMwindow.geometry("500x700")
        #
        BOMwindow.configure(background=FrameBG, borderwidth=BorderSize)
        #
        BOMtext = scrolledtext.ScrolledText(BOMwindow, wrap=WORD, undo=True, maxundo=-1, font="arial")
        BOMtext.pack(expand=True, fill='both')
        #
        menubar = Menu(BOMwindow)
        BOMwindow.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=TextNew_file)
        file_menu.add_command(label="Open", command=TextOpen_file)
        file_menu.add_command(label="Save", command=TextSave_file)
        file_menu.add_command(label="Save As...", command=TextSave_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=DestroyBOMScreen)
        
        command_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Commands", menu=command_menu)
        command_menu.add_command(label="Auto Placer", command=AutoPlacer)
        command_menu.add_command(label="Send From Editor", command=ConfigCrossPointEditor)
        command_menu.add_command(label="Update Components", command=UpDateBOMScreen)
        command_menu.add_command(label="Step Through Comp", command=StepThroughComps)
        command_menu.add_command(label="Merg Jumper Nets", command=MergNetList)
        command_menu.add_command(label="Schmatic Vs BB from Editor", command=VerifyCompsEditor)
        command_menu.add_command(label="Scan for comp", command=ScanBBpins)
#AutoPlacer()
def DestroyBOMScreen():
    global BOMwindow, BOMStatus

    BOMStatus.set(0)
    BOMwindow.destroy()
#
def DrawCompOval(Step, Xh1, Yh1, Xh2, Yh2, CmpName):
    global breadboard_canvas, BBFont, BBblack
    global TL1XY, BL1XY, TR1XY, BR1XY, JP1XY, JP9XY, AINHXY

    # draw oval around two pins?
    HStep = Step/2
    Deg = 270
    Xwidth = Step
    Ywidth = Step
    if Xh1 > 0 and Yh1 > 0 and Xh2 > 0 and Yh2 > 0:
        Xp1 = Xh1; Xp2 = Xh2
        Xcen = (Xh1 + Xh2)/2
        Ycen = (Yh1 + Yh2)/2
        if Yh1 == Yh2: # Hor comp?
            Xwidth = 0
            Ywidth = Step
            Deg = 0
            if Ycen < (BR1XY[1] * Step):
                if "Q" in CmpName or "M" in CmpName:
                    Yh1 = Yh2 = Ycen = (TL1XY[1] + 2) * Step # Center hole
                    breadboard_canvas.create_oval(Xcen-2, Yh1-2, Xcen+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                else:
                    Yh1 = (TL1XY[1] + 2) * Step # 1, 3 One grid below top
                    Yh2 = (TL1XY[1] + 2) * Step #
                    Ycen = (Yh1 + Yh2)/2
            else:
                if "Q" in CmpName or "M" in CmpName:
                    Yh1 = Yh2 = Ycen = (BL1XY[1] + 2) * Step # Center hole
                    breadboard_canvas.create_oval(Xcen-2, Yh1-2, Xcen+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                else:
                    Yh1 = (BR1XY[1] + 2) * Step # 3, 1 One grid above bottom
                    Yh2 = (BR1XY[1] + 2) * Step
                    Ycen = (Yh1 + Yh2)/2
            #
            if abs(Xh1 - Xh2) < (Step+HStep): # in adjacent col?
                if "C" in CmpName:
                    Xwidth = Step * 1.1
                else:
                    Xwidth = Step * 0.8
        elif Xh1 == Xh2: # Vert comp?:
            Xwidth = Step
            Ywidth = 0
        #
        SpLine = True
        if (Xh1 - Xh2) < 0 and (Yh1 - Yh2) < 0: # UL to LR
            Line1 = [Xh1, Yh1, Xcen+Xwidth, Ycen-Ywidth, Xh2, Yh2]
            Line2 = [Xh1, Yh1, Xcen-Xwidth, Ycen+Ywidth, Xh2, Yh2]
        elif (Xh1 - Xh2) > 0 and (Yh1 - Yh2) > 0: # LR to UL
            Line1 = [Xh1, Yh1, Xcen+Xwidth, Ycen-Ywidth, Xh2, Yh2]
            Line2 = [Xh1, Yh1, Xcen-Xwidth, Ycen+Ywidth, Xh2, Yh2]
        elif (Xh1 - Xh2) < 0 and (Yh1 - Yh2) > 0: # LL to UR
            Line1 = [Xh1, Yh1, Xcen+Xwidth, Ycen+Ywidth, Xh2, Yh2]
            Line2 = [Xh1, Yh1, Xcen-Xwidth, Ycen-Ywidth, Xh2, Yh2]
        elif (Xh1 - Xh2) > 0 and (Yh1 - Yh2) < 0: # UR to LL
            Line1 = [Xh1, Yh1, Xcen+Xwidth, Ycen+Ywidth, Xh2, Yh2]
            Line2 = [Xh1, Yh1, Xcen-Xwidth, Ycen-Ywidth, Xh2, Yh2]
        else:
            Line1 = [Xh1, Yh1, Xcen+Xwidth, Ycen+Ywidth, Xh2, Yh2]
            Line2 = [Xh1, Yh1, Xcen-Xwidth, Ycen-Ywidth, Xh2, Yh2]
        #
        if "R" in CmpName: # and Xh1 == Xh2:
            Ytop = min(Yh1, Yh2)
            Ybot = max(Yh1, Yh2)
            if (Xh1 - Xh2) < 0 and (Yh1 - Yh2) < 0: # UL to LR
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            elif (Xh1 - Xh2) > 0 and (Yh1 - Yh2) > 0: # LR to UL
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            elif (Xh1 - Xh2) < 0 and (Yh1 - Yh2) > 0: # LL to UR
                Xtop = max(Xh1, Xh2)
                Xbot = min(Xh1, Xh2)
            elif (Xh1 - Xh2) > 0 and (Yh1 - Yh2) < 0: # UR to LL
                Xtop = max(Xh1, Xh2)
                Xbot = min(Xh1, Xh2)
            else:
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            Dx = abs(Xtop - Xbot)
            Dy = abs(Ytop - Ybot)
            Line1 = [Xtop,Ytop]
            if Dy > Dx: # More vert
                Line1.append(Xcen)
                Line1.append(Ytop)
                Line = [0,0.7, 0.4,0.9, -0.4,1.3, 0.4,1.7, -0.4,2.1, 0,2.3]
                for point in range ( 0, len(Line), 2):
                    Line1.append((Line[point] * Step) + Xcen)
                    Line1.append((Line[point+1] * Step) + Ytop)
                Line1.append(Xcen)
                Line1.append(Ybot)
                Line1.append(Xbot)
                Line1.append(Ybot)
            else: # More Horz
                Line = [0.7,0, 0.9,0.4, 1.3,-0.4, 1.7,0.4, 2.1,-0.4, 2.3,0]
                if Yh1 == Yh2:
                    Line1.append(Xtop)
                    Line1.append(Ytop-HStep)
                    for point in range ( 0, len(Line), 2):
                        Line1.append((Line[point] * Step) + Xtop)
                        Line1.append((Line[point+1] * Step) + Ycen - HStep)
                else:
                    Line1.append(Xtop)
                    Line1.append(Ycen)
                    for point in range ( 0, len(Line), 2):
                        Line1.append((Line[point] * Step) + Xtop)
                        Line1.append((Line[point+1] * Step) + Ycen)
                if Yh1 == Yh2:
                    Line1.append(Xbot)
                    Line1.append(Ybot-HStep)
                else:
                    Line1.append(Xbot)
                    Line1.append(Ycen)
                Line1.append(Xbot)
                Line1.append(Ybot)
            # print(Line1)
            Line2 = [Xh1, Yh1, Xh1, Yh1]
            SpLine = False
        elif "C" in CmpName: # and Xh1 == Xh2:
            Ytop = min(Yh1, Yh2)
            Ybot = max(Yh1, Yh2)
            if (Xh1 - Xh2) < 0 and (Yh1 - Yh2) < 0: # UL to LR
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            elif (Xh1 - Xh2) > 0 and (Yh1 - Yh2) > 0: # LR to UL
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            elif (Xh1 - Xh2) < 0 and (Yh1 - Yh2) > 0: # LL to UR
                Xtop = max(Xh1, Xh2)
                Xbot = min(Xh1, Xh2)
            elif (Xh1 - Xh2) > 0 and (Yh1 - Yh2) < 0: # UR to LL
                Xtop = max(Xh1, Xh2)
                Xbot = min(Xh1, Xh2)
            else:
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            Dx = abs(Xtop - Xbot)
            Dy = abs(Ytop - Ybot)
            Line1 = [Xtop,Ytop]
            if Dy > Dx: # More vert
                Line1.append(Xcen)
                Line1.append(Ytop)
                Line = [0,1.3, 0.4,1.3, -0.4,1.3]
                for point in range ( 0, len(Line), 2):
                    Line1.append((Line[point] * Step) + Xcen)
                    Line1.append((Line[point+1] * Step) + Ytop)
                # print(Line1)
                Line2 = [Xbot, Ybot, Xcen, Ybot]
                Line = [0,1.7, 0.4,1.7, -0.4,1.7]
                for point in range ( 0, len(Line), 2):
                    Line2.append((Line[point] * Step) + Xcen)
                    Line2.append((Line[point+1] * Step) + Ytop)
            else: # More Horz
                Line = [1.3,0, 1.3,0.4, 1.3,-0.4]
                if Yh1 == Yh2:
                    Line1.append(Xtop)
                    Line1.append(Ytop-HStep)
                    for point in range ( 0, len(Line), 2):
                        Line1.append((Line[point] * Step) + Xtop)
                        Line1.append((Line[point+1] * Step) + Ycen - HStep)
                else:
                    Line1.append(Xtop)
                    Line1.append(Ycen)
                    for point in range ( 0, len(Line), 2):
                        Line1.append((Line[point] * Step) + Xtop)
                        Line1.append((Line[point+1] * Step) + Ycen)
                # print(Line1)
                Line2 = [Xbot, Ybot]
                Line = [1.7,0, 1.7,0.4, 1.7,-0.4]
                if Yh1 == Yh2:
                    Line2.append(Xbot)
                    Line2.append(Ybot-HStep)
                    for point in range ( 0, len(Line), 2):
                        Line2.append((Line[point] * Step) + Xtop)
                        Line2.append((Line[point+1] * Step) + Ycen - HStep)
                else:
                    Line2.append(Xbot)
                    Line2.append(Ycen)
                    for point in range ( 0, len(Line), 2):
                        Line2.append((Line[point] * Step) + Xtop)
                        Line2.append((Line[point+1] * Step) + Ycen)
            SpLine = False
        elif "D" in CmpName: # A end is Xh1, Yh1 
            Ytop = min(Yh1, Yh2)
            Ybot = max(Yh1, Yh2)
            if (Xh1 - Xh2) < 0 and (Yh1 - Yh2) < 0: # UL to LR
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            elif (Xh1 - Xh2) > 0 and (Yh1 - Yh2) > 0: # LR to UL
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            elif (Xh1 - Xh2) < 0 and (Yh1 - Yh2) > 0: # LL to UR
                Xtop = max(Xh1, Xh2)
                Xbot = min(Xh1, Xh2)
            elif (Xh1 - Xh2) > 0 and (Yh1 - Yh2) < 0: # UR to LL
                Xtop = max(Xh1, Xh2)
                Xbot = min(Xh1, Xh2)
            else:
                Xtop = min(Xh1, Xh2)
                Xbot = max(Xh1, Xh2)
            Dx = abs(Xtop - Xbot)
            Dy = abs(Ytop - Ybot)
            if Dy > Dx: # More vert
                if Yh1 < Yh2:
                    Line1 = [Xtop, Ytop, Xcen, Ytop]
                    Line2 = [Xbot, Ybot, Xcen, Ybot]
                    LineA = [0,1.0, 0.4,1.0, 0,1.8, -0.4,1.0, 0,1.0]
                    LineK = [0,1.8, 0.4,1.8, -0.4,1.8]
                else:
                    Line1 = [Xbot, Ybot, Xcen, Ybot]
                    Line2 = [Xtop, Ytop, Xcen, Ytop]
                    LineA = [0,1.8, 0.4,1.8, 0,1.0, -0.4,1.8, 0,1.8]
                    LineK = [0,1.0, 0.4,1.0, -0.4,1.0]
                for point in range ( 0, len(LineA), 2):
                    Line1.append((LineA[point] * Step) + Xcen)
                    Line1.append((LineA[point+1] * Step) + Ytop)
                for point in range ( 0, len(LineK), 2):
                    Line2.append((LineK[point] * Step) + Xcen)
                    Line2.append((LineK[point+1] * Step) + Ytop)
            else: # More Horz
                if Xh1 < Xh2:
                    Line1 = [Xtop, Ytop]
                    Line2 = [Xbot, Ybot]
                    LineA = [1.0,0, 1.0,0.4, 1.8,0, 1.0,-0.4, 1.0,0]
                    LineK = [1.8,0, 1.8,0.4, 1.8,-0.4]
                    if Yh1 == Yh2:
                        VertOff = HStep
                        Line1.append(Xtop)
                        Line1.append(Ytop-HStep)
                        Line2.append(Xbot)
                        Line2.append(Ybot-HStep)
                    else:
                        VertOff = 0
                        Line1.append(Xtop)
                        Line1.append(Ycen)
                        Line2.append(Xbot)
                        Line2.append(Ycen)
                else:
                    Line1 = [Xbot, Ybot]
                    Line2 = [Xtop, Ytop]
                    LineA = [1.8,0, 1.8,0.4, 1.0,0, 1.8,-0.4, 1.8,0]
                    LineK = [1.0,0, 1.0,0.4, 1.0,-0.4]
                    if Yh1 == Yh2:
                        VertOff = HStep
                        Line1.append(Xbot)
                        Line1.append(Ybot-HStep)
                        Line2.append(Xtop)
                        Line2.append(Ytop-HStep)
                    else:
                        VertOff = 0
                        Line1.append(Xbot)
                        Line1.append(Ycen)
                        Line2.append(Xtop)
                        Line2.append(Ycen)
                for point in range ( 0, len(LineA), 2):
                    Line1.append((LineA[point] * Step) + Xtop)
                    Line1.append((LineA[point+1] * Step) + Ycen - VertOff)
                for point in range ( 0, len(LineK), 2):
                    Line2.append((LineK[point] * Step) + Xtop)
                    Line2.append((LineK[point+1] * Step) + Ycen - VertOff)
            SpLine = False
        breadboard_canvas.create_line(Line1, smooth=SpLine, fill=BBblack, width=2)
        breadboard_canvas.create_line(Line2, smooth=SpLine, fill=BBblack, width=2)
        breadboard_canvas.create_oval(Xp1-2, Yh1-2, Xp1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
        breadboard_canvas.create_oval(Xp2-2, Yh2-2, Xp2+2, Yh2+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
        breadboard_canvas.create_text(Xcen, Ycen, text = CmpName, angle=Deg, fill="red", font=("arial", BBFont, "bold"))
#
def FindPowerRail(X1, X2, Y1, Y2, MidY, GrNum, Step, G):
    global TL1XY, BL1XY, TR1XY

    HStep = Step/2
    XL = (TL1XY[0] + 4) * Step
    XR = (TR1XY[0] + 12) * Step
    MidX = (XR + XL) / 2
    NX1 = NX2 = X1
    # Swap X1, X2 if X1 == 0
    if X1 == 0 and Y1 == 0:
        X1 = X2
        Y1 = Y2
        X2 = 0
        Y2 = 0
    # Set Y values
    if Y2 < MidY and Y2 > 0: # In Top resion
        NY2 = ((TL1XY[1] - 4 + G) * Step) + HStep
        NY1 = (TL1XY[1] * Step) # - HStep
    else:
        NY1 = ((BL1XY[1] + 4) * Step)
        NY2 = ((BL1XY[1] + 8 - G) * Step) # + HStep

    if Y1 < MidY and Y1 > 0: # In Bottom region
        NY2 = ((TL1XY[1] - 4 + G) * Step) + HStep
        NY1 = (TL1XY[1] * Step) # - HStep
    else:
        NY1 = ((BL1XY[1] + 4) * Step)
        NY2 = ((BL1XY[1] + 8 - G) * Step) # + HStep
    # determine X values
    if X1 > 0 and Y1 > 0: # Power wire BB holes always sent as X1, Y1
        NX1 = NX2 = X1
    # Check if Left of left edge or Right of right edge
        if GrNum == 16: # Check if falls on empty spot
            NX2 = NX2 + Step
        elif GrNum == 10 and NX2 < MidX:
            NX2 = NX2 + Step
        elif GrNum == 2:
            NX2 = NX2 - Step
        elif GrNum == 8 and NX2 > MidX:
            NX2 = NX2 - Step
        if NX2 < XL:
            NX2 = XL
        elif NX2 > XR:
            NX2 = XR
    #
    return(NX1, NX2, NY1, NY2)
#
def FindBBPin(xpin, Step): # Finds X Y of BB hole in pixels
    global TL1XY, BL1XY, TR1XY, BR1XY

    X1 = Y1 = GrNum = 0 # return 0 if we don't find a matching hole
    if "TL" in xpin:
        GrNum = eval(xpin.replace("TL",""))
        X1 = (TL1XY[0] + GrNum - 1) * Step
        Y1 = ((TL1XY[1] + 4 ) * Step) # + HStep
    if "BL" in xpin:
        GrNum = eval(xpin.replace("BL",""))
        X1 = (BL1XY[0] + GrNum - 1) * Step
        Y1 = (BL1XY[1] * Step) # + HStep
    if "TR" in xpin:
        GrNum = eval(xpin.replace("TR",""))
        X1 = (TR1XY[0] + GrNum - 1) * Step
        Y1 = ((TR1XY[1] + 4 ) * Step) # + HStep
    if "BR" in xpin:
        GrNum = eval(xpin.replace("BR",""))
        X1 = (BR1XY[0] + GrNum - 1) * Step
        Y1 = (BR1XY[1] * Step) # + HStep
    return(X1, Y1, GrNum)
#
def UpDateBOMScreen():
    AddCompScreen(0)
    DrawPowerWires(0)
    
#
def StepThroughComps():
    AddCompScreen(1)
    DrawPowerWires(1)
#
def AddCompScreen(SingleStep):
    global VPower, R_List, C_List, L_List, D_List, M_List, Q_List, U_List
    global U_Connections, VPowerConnections, VPower, UnRouted
    global ComponentList, BOMtext, BOMStatus, BBblack
    global BBwidth, BBheight, BBGridSize, breadboard_canvas, FontSize, BBFont
    global TL1XY, BL1XY, TR1XY, BR1XY, JP1XY, JP9XY, AINHXY

    if BOMStatus.get() == 0:
        return # MakeBOMScreen()
    # Calculate Xstep and YStep size for 50 X 40 0.1" grid, 11 pixels per grid point?
    XStep = YStep = BBwidth/BBGridSize
    HStep = XStep/2
    MidY = (BL1XY[1] - 1) * XStep
    # Clear all text
    BOMtext.delete("1.0", END)
    # List resistors
    for R in range (0, len(R_List), 1):
        Rterm = R_List[R]
        Rname = Rterm[0]
        Rterm1 = Rterm[1]
        Rterm2 = Rterm[2]
        RValue = Rterm[3]
        #
        R_Line = Rname + " "
        xpin1 = xpin2 = ""
        Xh1 = Yh1 = Xh2 = Yh2 = GrNum = 0
        if ("TL" in Rterm1 ) or ("BL" in Rterm1) or ("TR" in Rterm1) or ("BR" in Rterm1):
            R_Line = R_Line + Rterm1 + " "
            Xh1, Yh1, GrNum = FindBBPin(Rterm1, XStep)
        if ("TL" in Rterm2 ) or ("BL" in Rterm2) or ("TR" in Rterm2) or ("BR" in Rterm2):
            R_Line = R_Line + Rterm2 + " "
            Xh2, Yh2, GrNum = FindBBPin(Rterm2, XStep)
        # print(Rterm1, " ", Rterm2)
        if Xh1 == 0 and Yh1 == 0 and Xh2 == 0 and Yh2 == 0: 
            for xp in range (0, len(ComponentList), 1 ):
                if "V" in Rterm1 or "0" == Rterm1:
                    pass
                elif Rterm1 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin1 = CompPins[0]
                    xpin1 = xpin1.replace("X","")
                    xpin1 = xpin1.replace(chr(167),"")# remove §
                    R_Line = R_Line + xpin1 + " "
                    if Xh1 == 0 and Yh1 == 0:
                        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
                if "V" in Rterm2 or "0" == Rterm2:
                    pass
                elif Rterm2 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin2 = CompPins[0]
                    xpin2 = xpin2.replace("X","")
                    xpin2 = xpin2.replace(chr(167),"")# remove §
                    R_Line = R_Line + xpin2 + " "
                    if Xh2 == 0 and Yh2 == 0:
                        Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
        #
        if "V" in Rterm1:
            R_Line = R_Line + Rterm1 + " "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
        if "V" in Rterm2:
            R_Line = R_Line + Rterm2 + " "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
        if "0" == Rterm1 or "COM" == Rterm1 or "GND" == Rterm1:
            Rterm1 = "GND"
            R_Line = R_Line + "GND "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
        if "0" == Rterm2 or "COM" == Rterm2 or "GND" == Rterm2:
            Rterm2 = "GND"
            R_Line = R_Line + "GND "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
        #
        R_Line = R_Line + RValue
        BOMtext.insert(END, R_Line + '\n')
        DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Rname)
        if SingleStep > 0:
            Xm = abs(Xh1 + Xh2) / 2
            Ym = abs(Yh1 + Yh2) / 2
            CompPointer = breadboard_canvas.create_line(Xm+20, Ym-20, Xm, Ym, fill="red", arrow="last", width=2)
            R_Line = "Place " + RValue +  " Resistor " + Rname + " Between "
            R_Line = R_Line + Rterm1 + " and " + Rterm2
            askokcancel("Place",R_Line)
            breadboard_canvas.delete(CompPointer)
    # List capacitors
    for C in range (0, len(C_List), 1):
        Cterm = C_List[C]
        Cname = Cterm[0]
        Cterm1 = Cterm[1]
        Cterm2 = Cterm[2]
        CValue = Cterm[3]
        C_Line = Cname + " "
        xpin1 = xpin2 = ""
        Xh1 = Yh1 = Xh2 = Yh2 = 0
        if ("TL" in Cterm1 ) or ("BL" in Cterm1) or ("TR" in Cterm1) or ("BR" in Cterm1):
            C_Line = C_Line + Cterm1 + " "
            Xh1, Yh1, GrNum = FindBBPin(Cterm1, XStep)
        if ("TL" in Cterm2 ) or ("BL" in Cterm2) or ("TR" in Cterm2) or ("BR" in Cterm2):
            C_Line = C_Line + Cterm2 + " "
            Xh2, Yh2, GrNum = FindBBPin(Cterm2, XStep)
        # print(Cterm1[0], " ", Cterm2[0])
        if Xh1 == 0 and Yh1 == 0 and Xh2 == 0 and Yh2 == 0:
            for xp in range (0, len(ComponentList), 1 ):
                if "V" in Cterm1 or "0" == Cterm1:
                    donothing()
                elif Cterm1 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin1 = CompPins[0]
                    xpin1 = xpin1.replace("X","")
                    xpin1 = xpin1.replace(chr(167),"")# remove §
                    C_Line = C_Line + xpin1 + " "
                    if Xh1 == 0 and Yh1 == 0:
                        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
                if "V" in Cterm2 or "0" == Cterm2:
                    donothing()
                elif Cterm2 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin2 = CompPins[0]
                    xpin2 = xpin2.replace("X","")
                    xpin2 = xpin2.replace(chr(167),"")# remove §
                    C_Line = C_Line + xpin2 + " "
                    if Xh2 == 0 and Yh2 == 0:
                        Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
        if "V" in Cterm1:
            C_Line = C_Line + Cterm1 + " "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
        if "V" in Cterm2:
            C_Line = C_Line + Cterm2 + " "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
        if "0" == Cterm1 or "COM" == Cterm1 or "GND" == Cterm1:
            Cterm1 = "GND"
            C_Line = C_Line + "GND "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
        if "0" == Cterm2 or "COM" == Cterm2 or "GND" == Cterm2:
            Cterm2 = "GND"
            C_Line = C_Line + "GND "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
        C_Line = C_Line + CValue
        BOMtext.insert(END, C_Line + '\n')
        DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Cname)
        if SingleStep > 0:
            Xm = abs(Xh1 + Xh2) / 2
            Ym = abs(Yh1 + Yh2) / 2
            CompPointer = breadboard_canvas.create_line(Xm+20, Ym-20, Xm, Ym, fill="red", arrow="last", width=2)
            C_Line = "Place " + CValue +  " Capacitor " + Cname + " Between "
            C_Line = C_Line + Cterm1 + " and " + Cterm2
            askokcancel("Place",C_Line)
            breadboard_canvas.delete(CompPointer)
    # List inductors
    for L in range (0, len(L_List), 1):
        Lterm = L_List[L]
        Lname = Lterm[0]
        Lterm1 = Lterm[1]
        Lterm2 = Lterm[2]
        LValue = Lterm[3]
        L_Line = Lname + " "
        xpin1 = xpin2 = ""
        Xh1 = Yh1 = Xh2 = Yh2 = 0
        if ("TL" in Lterm1 ) or ("BL" in Lterm1) or ("TR" in Lterm1) or ("BR" in Lterm1):
            L_Line = L_Line + Lterm1 + " "
            Xh1, Yh1, GrNum = FindBBPin(Lterm1, XStep)
        if ("TL" in Lterm2 ) or ("BL" in Lterm2) or ("TR" in Lterm2) or ("BR" in Lterm2):
            L_Line = L_Line + Lterm2[0] + " "
            Xh2, Yh2, GrNum = FindBBPin(Lterm2, XStep)
        # print(Rterm1[0], " ", Rterm2[0])
        if Xh1 == 0 and Yh1 == 0 and Xh2 == 0 and Yh2 == 0:
            for xp in range (0, len(ComponentList), 1 ):
                if "V" in Lterm1 or "0" == Lterm1:
                    pass
                elif Lterm1 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin1 = CompPins[0]
                    xpin1 = xpin1.replace("X","")
                    xpin1 = xpin1.replace(chr(167),"")# remove §
                    L_Line = L_Line + xpin1 + " "
                    if Xh1 == 0 and Yh1 == 0:
                        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
                if "V" in Lterm2 or "0" == Lterm2:
                    pass
                elif Lterm2 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin2 = CompPins[0]
                    xpin2 = xpin2.replace("X","")
                    xpin2 = xpin2.replace(chr(167),"")# remove §
                    L_Line = L_Line + xpin2 + " "
                    if Xh2 == 0 and Yh2 == 0:
                        Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
        if "V" in Lterm1:
            L_Line = L_Line + Lterm1 + " "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
        if "V" in Lterm2:
            L_Line = L_Line + Lterm2 + " "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
        if "0" == Lterm1 or "COM" == Lterm1 or "GND" == Lterm1:
            L_Line = L_Line + "GND "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
        if "0" == Rterm2 or "COM" == Lterm2 or "GND" == Lterm2:
            L_Line = L_Line + "GND "
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
        L_Line = L_Line + LValue
        BOMtext.insert(END, L_Line + '\n')
        DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Lname)
        if SingleStep > 0:
            Xm = abs(Xh1 + Xh2) / 2
            Ym = abs(Yh1 + Yh2) / 2
            CompPointer = breadboard_canvas.create_line(Xm+20, Ym-20, Xm, Ym, fill="red", arrow="last", width=2)
            L_Line = "Place " + LValue +  " Inductor " + Lname + " Between "
            L_Line = L_Line + Lterm1 + " and " + Lterm2
            askokcancel("Place",L_Line)
            breadboard_canvas.delete(CompPointer)
    # List Diodes
    for D in range (0, len(D_List), 1):
        Dterm = D_List[D]
        Dname = Dterm[0]
        Dterm1 = Dterm[1]
        Dterm2 = Dterm[2]
        DValue = Dterm[3]
        D_Line = Dname + " "
        Polarity = "* "
        xpin1 = xpin2 = ""
        Xh1 = Yh1 = Xh2 = Yh2 = 0
        # print(Dterm)
        if ("TL" in Dterm1 ) or ("BL" in Dterm1) or ("TR" in Dterm1) or ("BR" in Dterm1):
            D_Line = D_Line + Dterm1 + " "
            Polarity = Polarity + "A " + Dterm1 + " "
            Xh1, Yh1, GrNum = FindBBPin(Dterm1, XStep)
            if "V" in Dterm2:
                D_Line = D_Line + Dterm2 + " "
                Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
            elif "0" == Dterm2 or "COM" == Dterm2 or "GND" == Dterm2:
                D_Line = D_Line + "GND "
                Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
            else:
                Xh2, Yh2, GrNum = FindBBPin(Dterm2, XStep)
                D_Line = D_Line + Dterm2 + " "
        elif ("TL" in Dterm2 ) or ("BL" in Dterm2) or ("TR" in Dterm2) or ("BR" in Dterm2):
            Polarity = Polarity + "K " + Dterm2 + " "
            Xh2, Yh2, GrNum = FindBBPin(Dterm2, XStep)
            if "V" in Dterm1:
                D_Line = D_Line + Dterm1 + " "
                Xh2, Xh1, Yh2, Yh1 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
            if "0" == Dterm1 or "COM" == Dterm1 or "GND" == Dterm1:
                D_Line = D_Line + "GND "
                Xh2, Xh1, Yh2, Yh1 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
            else:
                Xh1, Yh1, GrNum = FindBBPin(Dterm1, XStep)
                D_Line = D_Line + Dterm1 + " "
            D_Line = D_Line + Dterm2 + " "
        # 
        if Xh1 == 0 and Yh1 == 0 and Xh2 == 0 and Yh2 == 0:
            for xp in range (0, len(ComponentList), 1 ):
                if "V" in Dterm1 or "0" == Dterm1[0] or "GND" == Dterm1[0]:
                    pass
                elif Dterm1 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin1 = CompPins[0]
                    xpin1 = xpin1.replace("X","")
                    xpin1 = xpin1.replace(chr(167),"")# remove §
                    Polarity = Polarity + "A " + xpin1 + " "
                    D_Line = D_Line + xpin1 + " "
                    if Xh1 == 0 and Yh1 == 0:
                        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
                    if "V" in Dterm2:
                        D_Line = D_Line + Dterm2 + " "
                        Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
                    if "0" == Dterm2 or "COM" == Dterm2 or "GND" == Dterm2:
                        Dterm2 == "GND"
                        D_Line = D_Line + "GND "
                        Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
                if "V" in Dterm2 or "0" == Dterm2 or "GND" == Dterm2:
                    pass
                elif Dterm2 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin2 = CompPins[0]
                    xpin2 = xpin2.replace("X","")
                    xpin2 = xpin2.replace(chr(167),"")# remove §
                    Polarity = Polarity + "K " + xpin2 + " "
                    if Xh2 == 0 and Yh2 == 0:
                        Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
                    if "V" in Dterm1:
                        D_Line = D_Line + Dterm1 + " "
                        Xh2, Xh1, Yh2, Yh1 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
                    if "0" == Dterm1 or "COM" == Dterm1 or "GND" == Dterm1:
                        Dterm1 == "GND"
                        D_Line = D_Line + "GND "
                        Xh2, Xh1, Yh2, Yh1 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
                    D_Line = D_Line + xpin2 + " "
        D_Line = D_Line + Polarity
        BOMtext.insert(END, D_Line + '\n')
        DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Dname)
        if SingleStep > 0:
            Xm = abs(Xh1 + Xh2) / 2
            Ym = abs(Yh1 + Yh2) / 2
            CompPointer = breadboard_canvas.create_line(Xm+20, Ym-20, Xm, Ym, fill="red", arrow="last", width=2)
            D_Line = "Place " + DValue +  " Diode " + Lname + " Between "
            D_Line = D_Line + Dterm1 + " and " + Dterm2
            askokcancel("Place",D_Line)
            breadboard_canvas.delete(CompPointer)
    # List MOS Transistors
    for M in range (0, len(M_List), 1):
        Mterm = M_List[M]
        Mname = Mterm[0]
        Mterm1 = Mterm[1]
        Mterm2 = Mterm[2]
        Mterm3 = Mterm[3]
        M_Line = Mname + " "
        Polarity = "* "
        # print(Mterm, " ", M_Line)
        xpin1 = xpin2 = xpin3 = ""
        Xh1 = Yh1 = Xh2 = Yh2 = Xh3 = Yh3 = 0
        if ("TL" in Mterm1 ) or ("BL" in Mterm1) or ("TR" in Mterm1) or ("BR" in Mterm1):
            M_Line = M_Line + Mterm1 + " "
            Polarity = Polarity + "D " + Mterm1 + " "
            Xh1, Yh1, GrNum = FindBBPin(Mterm1, XStep)
        if ("TL" in Mterm2 ) or ("BL" in Mterm2) or ("TR" in Mterm2) or ("BR" in Mterm2):
            M_Line = M_Line + Mterm2 + " "
            Polarity = Polarity + "G " + Mterm2 + " "
            Xh2, Yh2, GrNum = FindBBPin(Mterm2, XStep)
        if ("TL" in Mterm3 ) or ("BL" in Mterm3) or ("TR" in Mterm3) or ("BR" in Mterm3):
            M_Line = M_Line + Mterm3 + " "
            Polarity = Polarity + "S " + Mterm3 + " "
            Xh3, Yh3, GrNum = FindBBPin(Mterm3, XStep)
        if Xh1 == 0 and Yh1 == 0 and Xh2 == 0 and Yh2 == 0 and Xh3 == 0 and Yh3 == 0:
            for xp in range (0, len(ComponentList), 1 ):
                if "V" in Mterm1 or "0" == Mterm1:
                    Dpin = Mterm1
                elif Mterm1 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin1 = CompPins[0]
                    xpin1 = xpin1.replace("X","")
                    xpin1 = xpin1.replace(chr(167),"")# remove §
                    Polarity = Polarity + "D " + xpin1 + " "
                    Dpin = xpin1
                    if Xh1 == 0 and Yh1 == 0:
                        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
                if "V" in Mterm2 or "0" == Mterm2:
                    Gpin = Mterm2
                elif Mterm2 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin2 = CompPins[0]
                    xpin2 = xpin2.replace("X","")
                    xpin2 = xpin2.replace(chr(167),"")# remove §
                    Polarity = Polarity + "G " + xpin2 + " "
                    xpin2
                    if Xh2 == 0 and Yh2 == 0:
                        Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
                if "V" in Mterm3 or "0" == Mterm3:
                    Spin = Mterm3
                elif Mterm3 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin3 = CompPins[0]
                    xpin3 = xpin3.replace("X","")
                    xpin3 = xpin3.replace(chr(167),"")# remove §
                    Polarity = Polarity + "S " + xpin3 + " "
                    Spin = xpin3
                    if Xh3 == 0 and Yh3 == 0:
                        Xh3, Yh3, GrNum = FindBBPin(xpin3, XStep)
        if "V" in Mterm1:
            Dpin = Mterm1
            Xh1 = Xh2 - XStep
            Yh1 = Yh2 # + XStep
        if "V" in Mterm2:
            Gpin = Mterm2
        if "V" in Mterm3:
            Spin = Mterm3
            Xh3 = Xh2 + XStep
            Yh3 = Yh2 # + XStep
        if "0" == Mterm1 or "COM" == Mterm1 or "GND" == Mterm1:
            Dpin = "GND"
            Xh1 = Xh2 - XStep
            Yh1 = Yh2 # + XStep
        if "0" == Mterm2 or "COM" == Mterm2 or "GND" == Mterm2:
            Gpin = "GND"
        if "0" == Mterm3 or "COM" == Mterm3 or "GND" == Mterm3:
            Spin = "GND"
            Xh3 = Xh2 - XStep
            Yh3 = Yh2 # + XStep
        M_Line = M_Line + Dpin + " " + Gpin + " " + Spin + " " + Polarity
        BOMtext.insert(END, M_Line + '\n')
        Xm = max([Xh1, Xh2, Xh3])
        Ym = max([Yh1, Yh2, Yh3])
        Xn = min([Xh1, Xh2, Xh3])
        Yn = min([Yh1, Yh2, Yh3])
        #
        DrawCompOval(XStep, Xm, Ym, Xn, Yn, Mname)
        if SingleStep > 0:
            Xm = Xh3 + XStep
            Yn = Yh2 + (2*XStep)
            CompPointer = breadboard_canvas.create_line(Xm, Yh1, Xh2, Yn, fill="red", arrow="last", width=2)
            M_Line = "Place " + MValue +  " MOS " + Mname + " Between "
            Polarity = "* D " + Mterm1 + " "
            Polarity = Polarity + "G " + Mterm2 + " "
            Polarity = Polarity + "S " + Mterm3 + " "
            M_Line = M_Line + Polarity
            askokcancel("Place",M_Line)
            breadboard_canvas.delete(CompPointer)
    # List Q BJTs
    for Q in range (0, len(Q_List), 1):
        Qterm = Q_List[Q]
        Qname = Qterm[0]
        Qterm1 = Qterm[1]
        Qterm2 = Qterm[2]
        Qterm3 = Qterm[3]
        Qterm4 = Qterm[4]
        Qvalue = Qterm[5]
        Q_Line = Qname + " "
        Polarity = "* "
        # print(Rterm1[0], " ", Rterm2[0])
        xpin1 = xpin2 = xpin3 = ""
        Xh1 = Yh1 = Xh2 = Yh2 = Xh3 = Yh3 = 0
        if ("TL" in Qterm1 ) or ("BL" in Qterm1) or ("TR" in Qterm1) or ("BR" in Qterm1):
            Q_Line = Q_Line + Qterm1 + " "
            Polarity = Polarity + "C " + Qterm1 + " "
            Xh1, Yh1, GrNum = FindBBPin(Qterm1, XStep)
        if ("TL" in Qterm2 ) or ("BL" in Qterm2) or ("TR" in Qterm2) or ("BR" in Qterm2):
            Q_Line = Q_Line + Qterm2 + " "
            Polarity = Polarity + "B " + Qterm2 + " "
            Xh2, Yh2, GrNum = FindBBPin(Qterm2, XStep)
        if ("TL" in Qterm3 ) or ("BL" in Qterm3) or ("TR" in Qterm3) or ("BR" in Qterm3):
            Q_Line = Q_Line + Qterm3 + " "
            Polarity = Polarity + "E " + Qterm3 + " "
            Xh3, Yh3, GrNum = FindBBPin(Qterm3, XStep)
        if Xh1 == 0 and Yh1 == 0 and Xh2 == 0 and Yh2 == 0 and Xh3 == 0 and Yh3 == 0:
            for xp in range (0, len(ComponentList), 1 ):
                if "V" in Qterm1 or "0" == Qterm1:
                    Cpin = Qterm1
                if Qterm1 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin1 = CompPins[0]
                    xpin1 = xpin1.replace("X","")
                    xpin1 = xpin1.replace(chr(167),"")# remove §
                    Polarity = Polarity + "C " + xpin1 + " "
                    Cpin = xpin1
                    if Xh1 == 0 and Yh1 == 0:
                        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
                if "V" in Qterm2 or "0" == Qterm2:
                    Bpin = Qterm2
                elif Qterm2 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin2 = CompPins[0]
                    xpin2 = xpin2.replace("X","")
                    xpin2 = xpin2.replace(chr(167),"")# remove §
                    Polarity = Polarity + "B " + xpin2 + " "
                    Bpin = xpin2
                    if Xh2 == 0 and Yh2 == 0:
                        Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
                if "V" in Qterm3 or "0" == Qterm3:
                    Epin = Qterm3
                elif Qterm3 in ComponentList[xp]:
                    CompPins = ComponentList[xp]
                    xpin3 = CompPins[0]
                    xpin3 = xpin3.replace("X","")
                    xpin3 = xpin3.replace(chr(167),"")# remove §
                    Polarity = Polarity + "E " + xpin3 + " "
                    Epin = xpin3
                    if Xh3 == 0 and Yh3 == 0:
                        Xh3, Yh3, GrNum = FindBBPin(xpin3, XStep)
        if "V" in Qterm1:
            Cpin = Qterm1
            Xh1 = Xh2 - XStep
            Yh1 = Yh2 # + XStep
        if "V" in Qterm2:
            Bpin = Qterm2
        if "V" in Qterm3:
            Xh3 = Xh2 + XStep
            Yh3 = Yh2 # + XStep
            Epin = Qterm3
        if "0" == Qterm1 or "COM" == Qterm1 or "GND" == Qterm1:
            Cpin = "GND"
            Xh1 = Xh2 - XStep
            Yh1 = Yh2 # + XStep
        if "0" == Qterm2 or "COM" == Qterm2 or "GND" == Qterm2:
            Bpin = "GND"
        if "0" == Qterm3 or "COM" == Qterm3 or "GND" == Qterm3:
            Epin = "GND"
            Xh3 = Xh2 + XStep
            Yh3 = Yh2 # + XStep
        Q_Line = Q_Line + Cpin + " " + Bpin + " " + Epin + " " + Qvalue + " " + Polarity
        BOMtext.insert(END, Q_Line + '\n')
        # print(Xh1, Yh1, Xh2, Yh2, Xh3, Yh3, Q_List[Q])
        Xm = max([Xh1, Xh2, Xh3])
        Ym = max([Yh1, Yh2, Yh3])
        Xn = min([Xh1, Xh2, Xh3])
        Yn = min([Yh1, Yh2, Yh3])
        #
        DrawCompOval(XStep, Xm, Ym, Xn, Yn, Qname)
        if SingleStep > 0:
            Xm = Xh3 + XStep
            Yn = Yh2 + (2*XStep)
            CompPointer = breadboard_canvas.create_line(Xm, Yh1, Xh2, Yn, fill="red", arrow="last", width=2)
            Q_Line = "Place " + Qvalue +  " BJT " + Qname + " Between "
            Polarity = "* C " + Qterm1 + " "
            Polarity = Polarity + "B " + Qterm2 + " "
            Polarity = Polarity + "E " + Qterm3 + " "
            Q_Line = Q_Line + Polarity
            askokcancel("Place",Q_Line)
            breadboard_canvas.delete(CompPointer)
    # List U ICs
    for U in range (0, len(U_List), 1):
        Uterm = U_List[U]
        # U_Line = U_List[U]
        CmpName = U_List[U][0]
        CmpName = CmpName.replace("X","")
        CmpName = CmpName.replace(chr(167),"")# remove §
        U_Line = CmpName + " "
        #
        xpin = ""
        Xm = Ym = 0
        Xn = Yn = BBheight
        for trm in range(0, len(Uterm), 1):
            Uterm1 = Uterm[trm]
            if ("TL" in Uterm1 ) or ("BL" in Uterm1) or ("TR" in Uterm1) or ("BR" in Uterm1):
                U_Line = U_Line + Uterm1 + " "
                if "TL" in Uterm1:
                    GrNum = eval(Uterm1.replace("TL",""))
                    Xh1 = (TL1XY[0] + GrNum - 1) * XStep
                    Yh1 = ((TL1XY[1] + 4 ) * XStep) # + HStep
                    breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                    Xm = int(max([Xh1, Xm]))
                    Ym = int(max([Yh1, Ym]))
                    Xn = int(min([Xh1, Xn]))
                    Yn = int(min([Yh1, Yn]))
                if "BL" in Uterm1:
                    GrNum = eval(Uterm1.replace("BL",""))
                    Xh1 = (BL1XY[0] + GrNum - 1) * XStep
                    Yh1 = (BL1XY[1] * XStep) + XStep
                    breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                    Xm = int(max([Xh1, Xm]))
                    Ym = int(max([Yh1, Ym]))
                    Xn = int(min([Xh1, Xn]))
                    Yn = int(min([Yh1, Yn]))
                if "TR" in Uterm1:
                    GrNum = eval(Uterm1.replace("TR",""))
                    Xh1 = (TR1XY[0] + GrNum - 1) * XStep
                    Yh1 = ((TR1XY[1] + 4 ) * XStep) # + HStep
                    breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                    Xm = int(max([Xh1, Xm]))
                    Ym = int(max([Yh1, Ym]))
                    Xn = int(min([Xh1, Xn]))
                    Yn = int(min([Yh1, Yn]))
                if "BR" in Uterm1:
                    GrNum = eval(Uterm1.replace("BR",""))
                    Xh1 = (BR1XY[0] + GrNum - 1) * XStep
                    Yh1 = (BR1XY[1] * XStep) + XStep
                    breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                    Xm = int(max([Xh1, Xm]))
                    Ym = int(max([Yh1, Ym]))
                    Xn = int(min([Xh1, Xn]))
                    Yn = int(min([Yh1, Yn]))
            else:
                for xp in range (0, len(ComponentList), 1 ):
                    if Uterm1 in ComponentList[xp]:
                        CompPins = ComponentList[xp]
                        xpin1 = CompPins[0]
                        xpin1 = xpin1.replace("X","")
                        xpin1 = xpin1.replace(chr(167),"")# remove §
                        U_Line = U_Line + xpin1 + " "
                        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
                        Xm = int(max([Xh1, Xm]))
                        Ym = int(max([Yh1, Ym]))
                        Xn = int(min([Xh1, Xn]))
                        Yn = int(min([Yh1, Yn]))
        if Xm == 0 and Ym == 0 and Xn == BBheight and Yn == BBheight:   
            for xp in range (0, len(ComponentList), 1 ):
                for trm in range(0, len(Uterm), 1):
                    Uterm1 = Uterm[trm]
                    if Uterm1 in ComponentList[xp]:
                        CompPins = ComponentList[xp]
                        xpin = CompPins[0]
                        xpin = xpin.replace("X","")
                        xpin = xpin.replace(chr(167),"")# remove §
                        U_Line = U_Line + xpin + " "
                        if "TL" in xpin:
                            GrNum = eval(xpin.replace("TL",""))
                            Xh1 = (TL1XY[0] + GrNum - 1) * XStep
                            Yh1 = ((TL1XY[1] + 4 ) * XStep) # + HStep
                            breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                            Xm = int(max([Xh1, Xm]))
                            Ym = int(max([Yh1, Ym]))
                            Xn = int(min([Xh1, Xn]))
                            Yn = int(min([Yh1, Yn]))
                        if "BL" in xpin:
                            GrNum = eval(xpin.replace("BL",""))
                            Xh1 = (BL1XY[0] + GrNum - 1) * XStep
                            Yh1 = (BL1XY[1] * XStep) # + XStep
                            breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                            Xm = int(max([Xh1, Xm]))
                            Ym = int(max([Yh1, Ym]))
                            Xn = int(min([Xh1, Xn]))
                            Yn = int(min([Yh1, Yn]))
                        if "TR" in xpin:
                            GrNum = eval(xpin.replace("TR",""))
                            Xh1 = (TR1XY[0] + GrNum - 1) * XStep
                            Yh1 = ((TR1XY[1] + 4 ) * XStep) # + HStep
                            breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                            Xm = int(max([Xh1, Xm]))
                            Ym = int(max([Yh1, Ym]))
                            Xn = int(min([Xh1, Xn]))
                            Yn = int(min([Yh1, Yn]))
                        if "BR" in xpin:
                            GrNum = eval(xpin.replace("BR",""))
                            Xh1 = (BR1XY[0] + GrNum - 1) * XStep
                            Yh1 = (BR1XY[1] * XStep) # + XStep
                            breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                            Xm = int(max([Xh1, Xm]))
                            Ym = int(max([Yh1, Ym]))
                            Xn = int(min([Xh1, Xn]))
                            Yn = int(min([Yh1, Yn]))
#
        BOMtext.insert(END, U_Line + '\n')
        Xcen = int((Xm + Xn) / 2)
        Ycen = int((Ym + Yn) / 2)
        breadboard_canvas.create_rectangle(Xm+HStep, Ym+4, Xn-HStep, Yn-4, outline="black", width=2)
        breadboard_canvas.create_text(Xcen, Ycen, text = CmpName , fill="red", font=("arial", BBFont, "bold"))
        if SingleStep > 0:
            CompPointer = breadboard_canvas.create_line(Xcen+20, Ycen-20, Xcen, Ycen, fill="red", arrow="last", width=2)
            R_Line = "Place " + U_Line
            askokcancel("Place",R_Line)
            breadboard_canvas.delete(CompPointer)
    # Place any UnRouted fly wires
    if len(UnRouted) > 0:
        # print(UnRouted)
        for fw in range ( 0, len(UnRouted), 1):
            UcNode = UnRouted[fw]
            matching_indices = [index for index, item in enumerate(UnRouted) if UcNode[0] in item]
            # print(matching_indices)
            Nd1 = matching_indices[0]
            Nd2 = matching_indices[1]
            xpin1 = UnRouted[Nd1][1]
            xpin2 = UnRouted[Nd2][1]
            Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
            Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
            # print(Xh1, Yh1, Xh2, Yh2)
            if Yh1 == Yh2: # Horizontal shift one hole up or down
                if Yh1 < MidY:
                    Yh1 = Yh1 - XStep
                    Yh2 = Yh2 - XStep
                else:
                    Yh1 = Yh1 + XStep
                    Yh2 = Yh2 + XStep
                Ycen = int((Yh1 + Yh2) / 2) - XStep
                Xcen = int((Xh1 + Xh2) / 2)
            elif Xh1 == Xh2: # Vert
                Ycen = int((Yh1 + Yh2) / 2)
                Xcen = int((Xh1 + Xh2) / 2) + XStep
            else:
                Ycen = int((Yh1 + Yh2) / 2) - XStep
                Xcen = int((Xh1 + Xh2) / 2) + XStep
            line = [Xh1, Yh1, Xcen, Ycen, Xh2, Yh2]
            breadboard_canvas.create_line(line, smooth=True, fill="green", width=4)
            breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
            breadboard_canvas.create_oval(Xh2-2, Yh2-2, Xh2+2, Yh2+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
            if SingleStep > 0:
                CompPointer = breadboard_canvas.create_line(Xcen+20, Ycen-20, Xcen, Ycen, fill="red", arrow="last", width=2)
                Q_Line = "Place Wire Jumper Between "
                Q_Line = Q_Line + xpin1 + " and " + xpin2
                askokcancel("Place",Q_Line)
                breadboard_canvas.delete(CompPointer)
#
##
def DrawPowerWires(SingleStep):
    global BBblack, VPower, VPowerConnections, breadboard_canvas
    global TL1XY, BL1XY, TR1XY, BR1XY, VPower_id, ComponentList
    global BBwidth, BBGridSize

    # Show Power / GND wires if any
    XStep = YStep = BBwidth/BBGridSize
    HStep = int(XStep/2)
    PinW = int(0.3 * XStep)
    Xd = 6 * XStep
    Yd = 33 * XStep
    VPower_id = []
    WireColor = BBblack
    MidY = (BL1XY[1] - 1) * XStep
    VIndex = 1
    for PWR in range ( 0, len(VPower), 1):
        if len(VPowerConnections[PWR]) > 0:
            PWConnString = "Found "
            if VPower[PWR] == "0":
                PwrNode = "GND"
            else:
                PwrNode = VPower[PWR]
            for Pins in range ( 0, len(VPowerConnections[PWR]), 1):
                PWConnString = PWConnString + VPowerConnections[PWR][Pins] + " "
                #
                Xh1 = Yh1 = Xh2 = Yh2 = 0
                PinStr = VPowerConnections[PWR][Pins]
                # print(PinStr)
                Xh1, Yh1, GrNum = FindBBPin(PinStr, XStep)
                #
                if "V" in VPower[PWR]:
                    Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
                    if Yh1 < MidY:
                        WireColor = "red"
                    else:
                        WireColor = "blue"
                if "GND" == VPower[PWR] or "COM" == VPower[PWR] or "0" == VPower[PWR]:
                    Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
                    WireColor = BBblack
                MidLineX = abs(Xh1 + Xh2)/2
                MidLineY = abs(Yh1 + Yh2)/2
                PWRLine = [Xh1, Yh1, MidLineX+XStep, MidLineY, Xh2, Yh2]
                Power_id = breadboard_canvas.create_line(PWRLine, smooth=TRUE, fill=WireColor, width=4)
                VPower_id.append(Power_id)
                Power_id = breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                VPower_id.append(Power_id)
                Power_id = breadboard_canvas.create_oval(Xh2-2, Yh2-2, Xh2+2, Yh2+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                VPower_id.append(Power_id)
                X_Line = PinStr + " " + PwrNode + " NC_01 cross_point\n"
                BOMtext.insert(END, X_Line)
                if SingleStep > 0:
                    CompPointer = breadboard_canvas.create_line(MidLineX+20, MidLineY-20, MidLineX, MidLineY, fill="red", arrow="last", width=2)
                    R_Line = "Place Wire Jumper Between "
                    R_Line = R_Line + PinStr + " and " + PwrNode
                    askokcancel("Place",R_Line)
                    breadboard_canvas.delete(CompPointer)
                #
            PWConnString = PWConnString + "connected to " + PwrNode
            Power_id = breadboard_canvas.create_text(Xd, Yd, text = PWConnString, anchor='w', fill=BBblack, font=("arial", FontSize, "bold"))
            VPower_id.append(Power_id)
            Yd = Yd + XStep
        # else:
        # Add Power / Ground
        # print(VPower)
        V_Line = "V" + str(VIndex) + " " + VPower[PWR] + " GND 5\n"
        VIndex = VIndex + 1
        BOMtext.insert(END, V_Line)            
#
## hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, ser, ConfigFileName, FWRevOne
    
    RUNstatus.set(0)
    Closed = 1
    # 
    try:
        ser.write(b'Gx\n') # Turn off AWG
        ser.write(b'gx\n') # turn off PWM
        ser.write(b'x\n') # Reset all cross point switches to open
        if FWRevOne == "Red3":
            ser.write(b'? 1 0 0 0\n') # set Test Res switches to open
        # try to write last config file, Don't crash if running in Write protected space
        BSaveConfig(ConfigFileName)
        # May need to be changed for specific hardware port
        ser.close()
        # exit
    except:
        donothing()

    root.destroy()
    exit()
#
# Set Scope Sample Rate based on Horz Time Scale
#
def DummySetSampleRate():
    global TimeSpan, MaxSampleRate, SHOWsamples, InterpRate, Tdiv
    global TrigSource, TriggerEdge, TriggerInt, SAMPLErate, TimeDiv, ser

    TimeDiv = UnitConvert(TMsb.get())
#
def SetSampleRate():
    global TimeSpan, SHOWsamples, InterpRate, Tdiv
    global MaxSampleRate, SAMPLErate, TimeDiv, ser

    try:
        TimeDiv = UnitConvert(TMsb.get())
    except:
        pass
    #print("TimeDiv = ", TimeDiv)
    if TimeDiv < 0.000099:
        ser.write(b't3\n') # 90.909 KSPS
    elif TimeDiv > 0.000099 and TimeDiv < 0.000199:
        ser.write(b't3\n') # 90.909 KSPS
    elif TimeDiv > 0.000199 and TimeDiv < 0.0005:
        ser.write(b't3\n') # 90.909KSPS
    elif TimeDiv >= 0.0005 and TimeDiv < 0.001:
        ser.write(b't3\n') # 90.909 KSPS
    elif TimeDiv >= 0.001 and TimeDiv < 0.002:
        ser.write(b't8\n') # 62.5 KSPS
    elif TimeDiv >= 0.002 and TimeDiv < 0.005:
        ser.write(b't16\n') # 31.250 KSPS
    elif TimeDiv >= 0.005 and TimeDiv < 0.01:
        ser.write(b't32\n') # 15.625 KSPS
    elif TimeDiv >= 0.01 and TimeDiv < 0.02:
        ser.write(b't100\n') # 10 KSPS
    elif TimeDiv >= 0.02 and TimeDiv < 0.05:
        ser.write(b't200\n') # 5 KSPS
    elif TimeDiv >= 0.05 and TimeDiv < 0.10:
        ser.write(b't500\n') # 2 KSPS
    elif TimeDiv >= 0.1 and TimeDiv < 0.20:
        ser.write(b't1000\n') # 1 KSPS
    else:
        ser.write(b't2000\n') # 500 SPS
    #
    time.sleep(0.005)
    #
#
def only_numerics(seq):
    seq_type= type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))
#
# Main function to request and receive a set of ADC samples
#
def Get_Data():
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global TgInput, VBuffA, VBuffB, VBuffC, VBuffD, VBuffG
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on, COLORtraceD
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    global TRIGGERentry, TRIGGERsample, SaveDig, CHANNELS, TRACESread

    # Get data from Pi Pico + MCP
    #
    SaveDig = False
    if D0_is_on or D1_is_on or D2_is_on or D3_is_on or D4_is_on or D5_is_on or D6_is_on or D7_is_on:
        SaveDig = True
        Get_Dig()
        COLORtraceD = "#800000"   # 80% red
    else:
        SaveDig = False
    #
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() == 0:
        TRACESread = 2 # A and B
        Get_Data_Two()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() == 0 and ShowC3_V.get() > 0:
        TRACESread = 2 # A and C
        Get_Data_Two()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        TRACESread = 2 # B and C
        Get_Data_Two()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() == 0 and ShowC3_V.get() == 0:
        TRACESread = 1 # A
        Get_Data_One()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() > 0 and ShowC3_V.get() == 0:
        TRACESread = 1 # B
        Get_Data_One()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() == 0 and ShowC3_V.get() > 0:
        TRACESread = 1 # C
        Get_Data_One()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        TRACESread = 3 # A and B and C
        Get_Data_Three()
    elif SaveDig:
        pass
    else:
        return
    # do external Gain / Offset calculations before software triggering
    if ShowC1_V.get() > 0:
        VBuffA = numpy.array(VBuffA)
        VBuffA = (VBuffA - InOffA) * InGainA
    if ShowC2_V.get() > 0 and CHANNELS >= 2:
        VBuffB = numpy.array(VBuffB)
        VBuffB = (VBuffB - InOffB) * InGainB
    if ShowC3_V.get() > 0 and CHANNELS >= 3:
        VBuffC = numpy.array(VBuffC)
        VBuffC = (VBuffC - InOffC) * InGainC
#
def Get_Buffer():
    global Wait, ser, MaxSampleRate, InterpRate, SAMPLErate
    global ABuff, iterCount, SampleTime, MinSamples, TRACESread
    
    time.sleep(Wait)
    ratestring = str(ser.readline())
    # print("Raw string ", ratestring)
    if "stReal=" in ratestring: #
        DTime = ratestring.replace("b'stReal=","")
        DTime = DTime.replace("\\\\","")
        DTime = DTime.replace("r","")
        DTime = DTime.replace("n","")
        DTime = DTime.replace("\\","")
        DTime = DTime.replace("'","")
        # print(DTime, UnitConvert(DTime)/MinSamples)
        SampleTime = (UnitConvert(DTime)/MinSamples) * 1.0e-6 # convert to uSec
        # set actual samplerate from returned time per sample
        MaxSampleRate = SAMPLErate = int((1.0/SampleTime)*InterpRate)
        # print("Sample Time: ", SampleTime)
        # print("Sample Rate = ", SAMPLErate )
    #
    #StartTime = time.time()
    VBuffRaw = []
    ABuff = []
    time.sleep(Wait*TRACESread)
    ### Wait to buffer enough samples to satisfy the entire frame
    # print("iterCount = ", iterCount)
    Count = 0
    Chunk = TRACESread * MinSamples
    ## 1 chan 324, 108, 36
    ## 2 chan 640, 320, 160
    ## 3,4 chan 500, 250
    ByTwo = 640 # 500
    ByFour = 320 # 250
    ByEight = 160
    if TRACESread == 2:
        ByTwo = 640
        ByFour = 320
        ByEight = 160
    if TRACESread > 1:
        Chunk = Chunk + MinSamples
    waiting0 = ser.in_waiting
    #print("Serial Length:", waiting0)
    while waiting0 >= 1:
        # print("Number Bytes waiting = ", waiting0)
        # read in chunks divisible by 3
        # Read an integer as two bytes, big-endian
        time.sleep(0.020)
        waiting0 = ser.in_waiting
        if waiting0 > Chunk:
            VBuffRaw = ser.read(Chunk)
            Count = Count + Chunk
        elif waiting0 > MinSamples:
            VBuffRaw = ser.read(MinSamples)
            Count = Count + MinSamples
        elif waiting0 > ByTwo:
            VBuffRaw = ser.read(ByTwo)
            Count = Count + ByTwo
        elif waiting0 > ByFour:
            VBuffRaw = ser.read(ByFour)
            Count = Count + ByFour
        elif waiting0 > ByEight:
            if TRACESread == 2:
                VBuffRaw = ser.read(ByEight)
                Count = Count + ByEight
            else:
                VBuffRaw = ser.read(waiting0)
                Count = Count + waiting0
        else:
            VBuffRaw = ser.read(waiting0)
            Count = Count + waiting0
        # if TRACESread == 4:
            # print("Count = ", Count)
        # print("Length AB: Raw: ", len(ABuff), len(VBuffRaw))
        index = 0
        while index < len(VBuffRaw):
            ABuff.append(VBuffRaw[index])
            index = index + 1
        # Count = Count + waiting0
        waiting0 = ser.in_waiting
        #print("Serial Length:", waiting0)
        # time.sleep(Wait)
        if Count >= iterCount: # Sample Buffer now full
            # print("Count = ", Count, "iterCount = ", iterCount)
            break
    #print("Frames = ", Frams)
    #EndTime = time.time()
    #Elapsed = EndTime - StartTime
    #print("Elapsed Time = ", Elapsed)
    # if TRACESread == 4:
    # print("received Bytes = ", Count)
    # print("Length: ", len(ABuff))
#
def Get_Dig():
    global VBuffA, VBuffB, VBuffC, VBuffD
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global LoopBack, LBsb, InterpRate
    global MaxSampleRate, SAMPLErate, EnableInterpFilter
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    SetSampleRate()
    Wait = 0.02
    #
    ser.write(b'7') # capture just dig channels
    #
    time.sleep(Wait)
    ratestring = str(ser.readline())
    # print("Raw string ", ratestring)
    if "stReal=" in ratestring: #
        DTime = ratestring.replace("b'stReal=","")
        DTime = DTime.replace("\\\\","")
        DTime = DTime.replace("r","")
        DTime = DTime.replace("n","")
        DTime = DTime.replace("\\","")
        DTime = DTime.replace("'","")
        # print(DTime, UnitConvert(DTime)/MinSamples)
        SampleTime = (UnitConvert(DTime)/MinSamples) * 1.0e-6 # convert to uSec
        # set actual samplerate from returned time per sample
        MaxSampleRate = SAMPLErate = int((1.0/SampleTime)*InterpRate)
        # print("Sample Time: ", SampleTime)
        # print("Sample Rate = ", SAMPLErate )
    # 
    iterCount = (MinSamples * 1) # 1 byte for 8 digital channels
    #
    #StartTime = time.time()
    VBuffRaw = []
    ABuff = []
    time.sleep(Wait)
    ### Wait to buffer enough samples to satisfy the entire frame
    # print("iterCount = ", iterCount)
    Count = 0
    waiting0 = ser.in_waiting
    #print("Serial Length:", waiting0)
    while waiting0 >= 1:
        # print("Number Bytes waiting = ", waiting0)
        # read in chunks divisible by 3
        # Read an integer as two bytes, big-endian
        time.sleep(0.010)
        waiting0 = ser.in_waiting
        if waiting0 > MinSamples:
            VBuffRaw = ser.read(MinSamples)
            Count = Count + MinSamples
        elif waiting0 > 324:
            VBuffRaw = ser.read(324)
            Count = Count + 324
        elif waiting0 > 108:
            VBuffRaw = ser.read(108)
            Count = Count + 108
        elif waiting0 > 36:
            VBuffRaw = ser.read(36)
            Count = Count + 36
        else:
            VBuffRaw = ser.read(waiting0)
            Count = Count + waiting0
        # print("Count = ", Count)
        # print("Length AB: Raw: ", len(ABuff), len(VBuffRaw))
        index = 0
        while index < len(VBuffRaw):
            ABuff.append(VBuffRaw[index])
            index = index + 1
        # Count = Count + waiting0
        waiting0 = ser.in_waiting
        #print("Serial Length:", waiting0)
        # time.sleep(Wait)
        if Count >= iterCount: # Sample Buffer now full
            # print("Count = ", Count, "iterCount = ", iterCount)
            break
    #
    #EndTime = time.time()
    #Elapsed = EndTime - StartTime
    #print("Elapsed Time = ", Elapsed)
    # print("received Bytes = ", Count)
    # print("Length: ", len(ABuff))
    #
    waiting0 = ser.in_waiting
    if waiting0 > 0:
        # print("Serial Length:", waiting0)
        dump = ser.read(waiting0)
    #Frams = 0
    index = 0
    VBuffG = []
    # Interpolate 
    while index < len(ABuff): # build array 
        pointer = 0
        while pointer < InterpRate:
            VBuffG.append(ABuff[index])
            pointer = pointer + 1
        index = index + 1
    # Extract Digital buffers if needed
    VBuffG = numpy.array(VBuffG) * 1
    if SaveDig:
        VBuffG = VBuffG.astype(int)
        if D0_is_on:
            DBuff0 = VBuffG & 1
        if D1_is_on:
            DBuff1 = VBuffG & 2
            DBuff1 = DBuff1 / 2
        if D2_is_on:
            DBuff2 = VBuffG & 4
            DBuff2 = DBuff2 / 4
        if D3_is_on:
            DBuff3 = VBuffG & 8
            DBuff3 = DBuff3 / 8
        if D4_is_on:
            DBuff4 = VBuffG & 16
            DBuff4 = DBuff4 / 16
        if D5_is_on:
            DBuff5 = VBuffG & 32
            DBuff5 = DBuff5 / 32
        if D6_is_on:
            DBuff6 = VBuffG & 64
            DBuff6 = DBuff6 / 64
        if D7_is_on:
            DBuff7 = VBuffG & 128
            DBuff7 = DBuff7 / 128
        #
    else:
        SaveDig = False
        DBuff0 = []
        DBuff1 = []
        DBuff2 = []
        DBuff3 = []
        DBuff4 = []
        DBuff5 = []
        DBuff6 = []
        DBuff7 = []
#
def Get_Data_One():
    global VBuffA, VBuffB, VBuffC, VBuffD, VBuff1
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global LoopBack, LBsb, TRACESread, Wait, iterCount
    global MaxSampleRate, SAMPLErate, EnableInterpFilter, InterpRate
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    SetSampleRate()
    Wait = 0.02
    if SAMPLErate <= 4000:
        Wait = 0.08
    #
    if ShowC1_V.get() > 0:
        ser.write(b'A0\n') # capture on A1
    elif ShowC2_V.get() > 0:
        ser.write(b'A1\n') # capture on A2
    elif ShowC3_V.get() > 0:
        ser.write(b'A2\n') # capture on A3
    else:
        return
    ser.write(b'1') # capture one channel
    #
    iterCount = (MinSamples * 2) # 2 bytes for one channel
    #
    Get_Buffer()
    #
    VBuff1=[]
    waiting0 = ser.in_waiting
    if waiting0 > 0:
        # print("Serial Length:", waiting0)
        dump = ser.read(waiting0)
    #Frams = 0
    index = 0
    while index < MinSamples: # len(ABuff)-2:
        #Frams = Frams + 1
        # Get CH 1 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff1.append(data)
        index = index + 1
    #
    VBuffG=[]
    #
    # Interpolate data samples by 4X
    #
    index = 0
    if ShowC1_V.get() > 0:
        VBuffA=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (InterpRate, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffA = VBuffA[InterpRate:SHOWsamples+InterpRate]
        #
    elif ShowC2_V.get() > 0:
        VBuffB=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (InterpRate, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffB = VBuffB[InterpRate:SHOWsamples+InterpRate]
        #
    elif ShowC3_V.get() > 0:
        VBuffC=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffC.append(float(samp) * LSBsizeC)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffC)
        if EnableInterpFilter.get() == 1:
            VBuffC = numpy.pad(VBuffC, (InterpRate, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffC = VBuffC[InterpRate:SHOWsamples+4]
        #
    elif ShowC4_V.get() > 0:
        VBuffD=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffD)
        if EnableInterpFilter.get() == 1:
            VBuffD = numpy.pad(VBuffD, (InterpRate, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffD = VBuffD[InterpRate:SHOWsamples+InterpRate]
        #
    else:
        return
#
def Get_Data_Two():
    global VBuffA, VBuffB, VBuffC, VBuffD, ABuff
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC,  LSBsizeD
    global LoopBack, LBsb, Wait, iterCount
    global MaxSampleRate, SAMPLErate, EnableInterpFilter, InterpRate
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    SetSampleRate()
    Wait = 0.015
    if SAMPLErate <= 4000:
        Wait = 0.08
    ### send command to readout data
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0: # capture on A1 and A2
        ser.write(b'A0\n') 
        ser.write(b'B1\n')
    elif ShowC1_V.get() > 0 and ShowC3_V.get() > 0: # capture on A1 and A3
        ser.write(b'A0\n')
        ser.write(b'B2\n')
    elif ShowC1_V.get() > 0 and ShowC4_V.get() > 0: # capture on A1 and A4
        ser.write(b'A0\n') 
        ser.write(b'B3\n')
    elif ShowC2_V.get() > 0 and ShowC3_V.get() > 0: # capture on A2 and A3
        ser.write(b'A1\n') 
        ser.write(b'B2\n')
    elif ShowC2_V.get() > 0 and ShowC4_V.get() > 0: # capture on A2 and A4
        ser.write(b'A1\n') 
        ser.write(b'B3\n')
    elif ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on A3 and A4
        ser.write(b'A2\n') 
        ser.write(b'B3\n')
    else:
        return
    ser.write(b'2') # capture two channels
    #
    iterCount = (MinSamples * 4) # 4 bytes for two channels
    #
    Get_Buffer()
    #
    VBuff1=[]
    VBuff2=[]
    waiting0 = ser.in_waiting
    if waiting0 > 0:
        # print("Serial Length:", waiting0)
        dump = ser.read(waiting0)
    #Frams = 0
    index = 0
    while index < MinSamples: # len(ABuff)-2:
        #Frams = Frams + 1
        # Get CH 1 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff1.append(data)
        index = index + 1
    index = index + MinSamples # skip ahead MinSamples
    while index < 3 * MinSamples:
        # Get CH 2 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff2.append(data)
        index = index + 1
    #
    #print("Frames = ", Frams)
    #
    VBuffG=[]
    #
    # Interpolate data samples by 4X
    #
    index = 0
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0: # capture on A and B
        VBuffA=[]
        VBuffB=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffB.append(float(samp) * LSBsizeB)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (InterpRate, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffB = numpy.pad(VBuffB, (InterpRate, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffA = VBuffA[InterpRate:SHOWsamples+InterpRate]
            VBuffB = VBuffB[InterpRate:SHOWsamples+InterpRate]
        #
    elif ShowC1_V.get() > 0 and ShowC3_V.get() > 0: # capture on A and C
        VBuffA=[]
        VBuffC=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (InterpRate, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (InterpRate, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffA = VBuffA[InterpRate:SHOWsamples+InterpRate]
            VBuffC = VBuffC[InterpRate:SHOWsamples+InterpRate]
        #
    elif ShowC2_V.get() > 0 and ShowC3_V.get() > 0: # capture on B and C
        VBuffB=[]
        VBuffC=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (InterpRate, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (InterpRate, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffB = VBuffB[InterpRate:SHOWsamples+InterpRate]
            VBuffC = VBuffC[InterpRate:SHOWsamples+InterpRate]
        #
    elif ShowC1_V.get() > 0 and ShowC4_V.get() > 0: # capture on A and D
        VBuffA=[]
        VBuffD=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (InterpRate, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (InterpRate, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffA = VBuffA[InterpRate:SHOWsamples+InterpRate]
            VBuffD = VBuffD[InterpRate:SHOWsamples+InterpRate]
        #
    elif ShowC2_V.get() > 0 and ShowC4_V.get() > 0: # capture on B and D
        VBuffB=[]
        VBuffD=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff2[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (InterpRate, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (InterpRate, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffB = VBuffB[InterpRate:SHOWsamples+InterpRate]
            VBuffD = VBuffD[InterpRate:SHOWsamples+InterpRate]
        #
    elif ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on C and D
        VBuffC=[]
        VBuffD=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffC.append(float(samp) * LSBsizeC)
                samp = VBuff2[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffC)
        if EnableInterpFilter.get() == 1:
            VBuffC = numpy.pad(VBuffC, (InterpRate, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (InterpRate, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffC = VBuffC[InterpRate:SHOWsamples+InterpRate]
            VBuffD = VBuffD[InterpRate:SHOWsamples+InterpRate]
        #
    else:
        return
#    
def Get_Data_Three():
    global VBuffA, VBuffB, VBuffC, VBuffD, ABuff
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC
    global LoopBack, LBsb, Wait, iterCount
    global MaxSampleRate, SAMPLErate, EnableInterpFilter, InterpRate
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    SetSampleRate()
    Wait = 0.015
    if SAMPLErate <= 4000:
        Wait = 0.08
    # 
    # send command to readout data
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0: # capture on A1 A2 and A3
        ser.write(b'A0\n') 
        ser.write(b'B1\n')
        ser.write(b'C2\n')
    elif ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC4_V.get() > 0: # capture on A1 A2 and A4
        ser.write(b'A0\n') 
        ser.write(b'B1\n')
        ser.write(b'C3\n')
    elif ShowC2_V.get() > 0 and ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on A2 A3 and A4
        ser.write(b'A1\n') 
        ser.write(b'B2\n')
        ser.write(b'C3\n')
    elif ShowC1_V.get() > 0 and ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on A1 A3 and A4
        ser.write(b'A0\n') 
        ser.write(b'B2\n')
        ser.write(b'C3\n')
    else:
        #print("none of the cases found?")
        return
    time.sleep(0.015)
    ser.write(b'3') # capture three channels
    #
    iterCount = (MinSamples * 6) # 6 bytes for three channels
    #
    Get_Buffer()
    #
    VBuff1=[]
    VBuff2=[]
    VBuff3=[]
    #
    waiting0 = ser.in_waiting
    if waiting0 > 0:
        # print("Serial Length:", waiting0)
        dump = ser.read(waiting0)
    #Frams = 0
    index = 0
    while index < MinSamples: # len(ABuff)-2:
        #Frams = Frams + 1
        # Get CH 1 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff1.append(data)
        index = index + 1
    index = index + MinSamples # skip ahead MinSamples
    while index < 3 * MinSamples:
        # Get CH 2 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff2.append(data)
        index = index + 1
    index = index + MinSamples # skip ahead MinSamples
    while index < 5 * MinSamples:
        # Get CH 3 data
        try:
            inputHigh = ABuff[index]
            inputLow = ABuff[index+ MinSamples]
        except:
            inputHigh = 0
            inputLow = 0
        data = ((inputHigh*256)+inputLow)
        VBuff3.append(data)
        index = index + 1
    #
    #print("Frames = ", Frams)
    #
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0: # capture on A B and C
        VBuffA=[]
        VBuffB=[]
        VBuffC=[]
        #
        # Interpolate data samples by 4X
        #
        index = 0
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff3[index]
                VBuffC.append(float(samp) * LSBsizeC)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (InterpRate, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffB = numpy.pad(VBuffB, (InterpRate, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (InterpRate, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffA = VBuffA[InterpRate:SHOWsamples+InterpRate]
            VBuffB = VBuffB[InterpRate:SHOWsamples+InterpRate]
            VBuffC = VBuffC[InterpRate:SHOWsamples+InterpRate]
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC4_V.get() > 0: # capture on A B and D
        VBuffA=[]
        VBuffB=[]
        VBuffD=[]
        #
        # Interpolate data samples by 4X
        #
        index = 0
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff3[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (InterpRate, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffB = numpy.pad(VBuffB, (InterpRate, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (InterpRate, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffA = VBuffA[InterpRate:SHOWsamples+InterpRate]
            VBuffB = VBuffB[InterpRate:SHOWsamples+InterpRate]
            VBuffD = VBuffD[InterpRate:SHOWsamples+InterpRate]
    if ShowC2_V.get() > 0 and ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on B C and D
        VBuffB=[]
        VBuffC=[]
        VBuffD=[]
        #
        # Interpolate data samples by 4X
        #
        index = 0
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                samp = VBuff3[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (InterpRate, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (InterpRate, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (InterpRate, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffB = VBuffB[InterpRate:SHOWsamples+InterpRate]
            VBuffC = VBuffC[InterpRate:SHOWsamples+InterpRate]
            VBuffD = VBuffD[InterpRate:SHOWsamples+InterpRate]
    if ShowC1_V.get() > 0 and ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on A B and D
        VBuffA=[]
        VBuffC=[]
        VBuffD=[]
        #
        # Interpolate data samples by 4X
        #
        index = 0
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < InterpRate:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                samp = VBuff3[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (InterpRate, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (InterpRate, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (InterpRate, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffA = VBuffA[InterpRate:SHOWsamples+InterpRate]
            VBuffC = VBuffC[InterpRate:SHOWsamples+InterpRate]
            VBuffD = VBuffD[InterpRate:SHOWsamples+InterpRate]
#
# Hardware Help
#
def PrintID():
    global ser
    
    ser.write(b'I\n') # request board ID
    time.sleep(0.05)
    #print("sent I, wating for response")
    if ser.in_waiting > 0:
        IDstring = str(ser.readline())
        ID = IDstring.replace("b'","")
        ID = ID.replace("\\\\","")
        ID = ID.replace("r","")
        ID = ID.replace("n","")
        ID = ID.replace("\\","")
        ID = ID.replace("'","")
        print("ID string ", ID)
#
def PingID():
    global ser
    
    ser.write(b'I\n') # request board ID
    time.sleep(0.05)
    #print("sent I, wating for response")
    if ser.in_waiting > 0:
        IDstring = str(ser.readline())
        ID = IDstring.replace("b'","")
        ID = ID.replace("\\\\","")
        ID = ID.replace("r","")
        ID = ID.replace("n","")
        ID = ID.replace("\\","")
        ID = ID.replace("'","")
        # print("ID string ", ID)
#
def SetBufferLength(NewLength):
    global ser, MinSamples, MaxSamples, InterpRate, HardwareBuffer

    if NewLength > HardwareBuffer:
        NewLength = HardwareBuffer
    MinSamples = NewLength
    MaxSamples = MinSamples * InterpRate
    ## send Scope Buffer Length
    SendStr = 'b' + str(MinSamples) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
    # ser.write(b'b1024\n')  
    time.sleep(0.005)
    #print("set Scope Samples: ", MinSamples)
#
# try to connect to Arduino Pi Pico board
#
def ConnectDevice():
    global SerComPort, DevID, MaxSamples, SAMPLErate, MinSamples, AWGSampleRate
    global ExtBoard, AWGPeakToPeak, Vsys
    global bcon, FWRevOne, HWRevOne, MaxSampleRate, MaxAWGSampleRate, ser, SHOWsamples
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv, ATmin
    global CHAsb, CHBsb, TMsb, LSBsizeA, LSBsizeB, ADC_Cal, LSBsize
    global d0btn, d1btn, d2btn, d3btn, d4btn, d5btn, d6btn, d7btn

    # print("SerComPort: ", SerComPort)
    FWRevOne = HWRevOne = "Blank"
    if DevID == "No Device" or DevID == "Pi Pico Cross Point Mini":
        #
        if SerComPort == 'Auto':
            ports = serial.tools.list_ports.comports()
            for port in ports: # ports:
                # looking for this ID: USB\VID_2E8A&PID_000A
                if "VID:PID=2E8A:000A" in port[2]:
                    print("Found: ", port[0])
                    SerComPort = port[0]
        # Setup instrument connection
                    print("Trying to open ", SerComPort)
                    try:
                        ser = serial.Serial(SerComPort)  # open serial port
                        ser.baudrate = 2000000 # Dummy number USB runs at max supported speed
        # Check if hardware ID string matched target?
                        ser.write(b'I\n') # request board ID
                        time.sleep(0.005)
                        IDstring = str(ser.readline())
                        ID = IDstring.replace("b'","")
                        ID = ID.replace("\\\\","")
                        ID = ID.replace("\\r","")
                        ID = ID.replace("\\n","")
                        # ID = ID.replace("\\","")
                        ID = ID.replace("'","")
                        print("ID string ", ID)
                        if ID == "Pi Pico Cross Point Mini Red" :
                            break
                    except:
                        print("Port already in use?", SerComPort)
                        MakeBreadboardScreen()
                        return(False)
        else:
            print("Trying to open ", SerComPort)
            try:
                ser = serial.Serial(SerComPort)  # open serial port
                ser.baudrate = 2000000 # Dummy number USB runs at max supported speed
# Check if hardware ID string matched target?
                ser.write(b'I\n') # request board ID
                time.sleep(0.005)
                IDstring = str(ser.readline())
                ID = IDstring.replace("b'","")
                ID = ID.replace("\\\\","")
                ID = ID.replace("\\r","")
                ID = ID.replace("\\n","")
                #  ID = ID.replace("\\","")
                ID = ID.replace("'","")
                print("ID string ", ID)
                #
            except:
                print("Port already in use?", SerComPort)
                MakeBreadboardScreen()
                return(False)
        try:
            if ser is None:
                print('Device not found!')
                Bcloseexit()
                #exit()
        except:
            MakeBreadboardScreen()
            return(False)
        FWRevOne = ID
        #
        if ID == "Pi Pico Cross Point Mini Red3" :
            print("Firmware supports Expansion boards")
            ExtBoard.set(1)
            AWGPeakToPeak = 8.11 # MCP4822 with 2X output buffer amp
            FWRevOne = "Red3"
            HWRevOne = DevID = "Red3"
        elif ID == "Pi Pico Cross Point Mini Red2" :
            print("Firmware supports Expansion boards")
            ExtBoard.set(1)
            AWGPeakToPeak = 4.095 # MCP4822
            FWRevOne = "Red2"
            HWRevOne = DevID = "Red2"
        else:
            print("Firmware does not support Expansion boards")
            ExtBoard.set(0)
            FWRevOne = "Red1"
            HWRevOne = DevID = "Red1"
        #
        ser.write(b'V\n') # Read Back VDD (.3.) supply voltage
        time.sleep(0.005)
        VDDstring = str(ser.readline())
        # print("VDD string ", VDDstring)
        if "V=" in VDDstring: #
            VDD = VDDstring.replace("b'V=","")
            VDD = VDD.replace("\\\\","")
            VDD = VDD.replace("r","")
            VDD = VDD.replace("n","")
            VDD = VDD.replace("\\","")
            VDD = VDD.replace("'","")
            Vsys = (int(VDD) * LSBsize) * 3.0 # 1/3 voltage divider
            print("Board Vsys = ", Vsys)
        #
        ser.write(b't3\n') # send Scope sample time in uSec
        time.sleep(0.005)
        print("set dt: 3 uSec")
        MaxSampleRate = SAMPLErate = 333333*InterpRate
        #
        SendStr = 'T' + str(ATmin) + '\n'
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        # ser.write(b'T8\n') # send AWG sample time in uSec
        time.sleep(0.005)
        print("set at: ", ATmin , " uSec")
        AWGSampleRate = MaxAWGSampleRate = 1.0 / (ATmin / 1000000)
        #
        ser.write(b'Gx\n') # default with both AWG off
        ser.write(b'gx\n') 
        ## send Scope Buffer Length
        SendStr = 'b' + str(MinSamples) + '\n'
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        # ser.write(b'b1024\n')  
        time.sleep(0.005)
        print("set Scope Samples: ", MinSamples)
        #
        #
        ser.write(b'N1024\n') # send AWG A Buffer Length
        ser.write(b'M1024\n') # send AWG B Buffer Length 
        time.sleep(0.005)
        print("set AWG Samples: 1024")
        #
        # ser.write(b'p500000\n')
        ser.write(b'R0\n') # default with AWG reset off
        ser.write(b'r0\n') # default with AWG pointer at loc 0
        #
        ser.write(b'Sx\n') # turn off AWG A by default
        MaxSamples = 4096 # assume 4X interpolation
#
        ResetMatrix() # Reset all cross point switches to open
        ser.write(b'? 1 0 0 0\n') # Res switches to open
        print("Get a sample: ")
        Get_Data() # grap a check set of samples
        print("After Interp ", len(VBuffA), len(VBuffB))
        SHOWsamples = len(VBuffA)
        # make cross point control screen

        ######
        MakeBreadboardScreen()
        ######

        return(True) # return a logical true if sucessful!
    else:
        MakeBreadboardScreen()
        return(False)
#
def UpdateFirmware():
    global ser, Sucess, bcon

    if askyesno("Load Firmware?", "Do You Wish to load firmware on this board?"):
        try:
            ser.baudrate = 1200 # Opening serial port at 1200 Baud for a short while will reset board
            time.sleep(0.05)
            if ser.in_waiting > 0:
                IDstring = str(ser.readline()) # read something
                print(IDstring)
            time.sleep(0.05)
            ser.close()
            Sucess = False
            bcon.configure(text="Recon", style="RConn.TButton")
        except:
            pass
        # if this worked a USB drive window should open.
#
# AWG Stuff
#
def AWGASendWave(AWG3):
    global ser, AWGARecLength, AWGBuffLen, AWGRes, HWRevOne
    global AWGAAmplvalue, AWGAOffsetvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    # scale values to send to 0 to 255 8 bits
    AWG3 = numpy.array(AWG3) * 0.5 # scale by 1/2
    if HWRevOne == "Red3":
        # Get Low and High voltage levels and shift for -4 to +4 swing
        AWGAAmplvalue = AWGAAmplvalue + 3.98
        AWGAOffsetvalue = AWGAOffsetvalue + 3.98
    MinCode = int((AWGAAmplvalue / AWGPeakToPeak) * AWGRes)
    if MinCode < 0:
        MinCode = 0
    if MinCode > AWGRes:
        MinCode = AWGRes
    MaxCode = int((AWGAOffsetvalue / AWGPeakToPeak) * AWGRes)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > AWGRes:
        MaxCode = AWGRes
    # print("MaxCode = ", MaxCode, "MinCode = ", MinCode)
    # Scale to high and low voltage values
    Gain = MaxCode - MinCode
    Offset = int((MaxCode + MinCode)/2)
    AWG3 = (AWG3 * Gain) + Offset
    n = 0
    AWG1 = []
    while n < len(AWG3):
        AWG1.append(int(AWG3[n]))
        n = n + 1
    AWG1 = numpy.array(AWG1)
    #
    AWGARecLength = len(AWG1)
    if AWGARecLength > AWGBuffLen:
        AWGARecLength = AWGBuffLen
    if len(AWG1) < AWGBuffLen:
        # ser.write(b'B1024\n') # send AWG Buffer Length
        SendStr = 'N' + str(len(AWG1)) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        SendStr = 'N' + str(AWGBuffLen) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #    
    #AWG1 = AWG1.tobytes()
    index = 0
    while index < AWGARecLength:
        data = AWG1[index]
        # send buffer index and waveform sample data
        SendStr = 'L' + str(index) + 'D' + str(data) + '\n'
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
##    
def AWGBSendWave(AWG3):
    global ser, AWGBLastWave, AWGBRecLength, AWGBuffLen, AWGRes
    global AWGBAmplvalue, AWGBOffsetvalue, AWGPeakToPeak, HWRevOne
    # Expect array values normalized from -1 to 1
    # AWG3 = numpy.roll(AWG3, -68)
    AWGBLastWave = numpy.array(AWG3)
    AWG3 = numpy.array(AWG3) * 0.5 # scale by 1/2
    if HWRevOne == "Red3":
        # Get Low and High voltage levels and shift for -4 to +4 swing
        AWGBAmplvalue = AWGBAmplvalue + 3.98
        AWGBOffsetvalue = AWGBOffsetvalue + 3.98
    MinCode = int((AWGBAmplvalue / AWGPeakToPeak) * AWGRes)
    if MinCode < 0:
        MinCode = 0
    if MinCode > AWGRes:
        MinCode = AWGRes
    MaxCode = int((AWGBOffsetvalue / AWGPeakToPeak) * AWGRes)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > AWGRes:
        MaxCode = AWGRes
    #
    Gain = MaxCode - MinCode
    Offset = int((MaxCode + MinCode)/2)
    AWG3 = (AWG3 * Gain) + Offset
    n = 0
    AWG1 = []
    while n < len(AWG3):
        AWG1.append(int(AWG3[n]))
        n = n + 1
    AWG1 = numpy.array(AWG1)
    #
    AWGBRecLength = len(AWG1)
    if AWGBRecLength > AWGBuffLen:
        AWGBRecLength = AWGBuffLen
    if len(AWG1) < AWGBuffLen:
        SendStr = 'M' + str(len(AWG1)) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        SendStr = 'M' + str(AWGBuffLen) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #    
    #AWG1 = AWG1.tobytes()
    index = 0
    while index < AWGBRecLength:
        data = AWG1[index]
        #
        SendStr = 'l' + str(index) + 'D' + str(data) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
##
def BAWGSync():
    global AWGSync

    if AWGSync.get() > 0:
        ser.write(b'R1\n') # turn on sync
    else:
        ser.write(b'R0\n') # turn off sync
#
def SetAwgSampleRate():
    global AWGAFreqEntry, AWGBFreqEntry, FSweepMode, MaxAWGSampleRate
    global AWGBuffLen, AWGSampleRate, AWGBuffLen, MaxRepRate

    BAWGAFreq()
    # BAWGBFreq()

    MaxRepRate = numpy.ceil(MaxAWGSampleRate / AWGBuffLen)
    FreqA = UnitConvert(AWGAFreqEntry.get())
##    FreqB = UnitConvert(AWGBFreqEntry.get())
##    if FreqB < FreqA:
##        FreqA = FreqB
    Cycles = 1
    #print("MaxRepRate = ", MaxRepRate)
    #print("FreqA = ", FreqA)
    # if FSweepMode.get() == 1: # If doing a frequency sweep only make new AWG A sine wave
    if FreqA < MaxRepRate:
        CycFrac = FreqA/MaxRepRate
        #print("Cycles = ", CycFrac)
        if CycFrac > 0.9:
            CycFrac = 0.9
        FreqA = FreqA * CycFrac
# Set the AWG buffer Rep rate (Freq for one cycle of buffer)
    SetAwgSampleFrequency(FreqA)
    AWGRepRate = FreqA
    # AWGSampleRate = FreqA * AWGBuffLen
        # AWGSampleRate = FreqB * MaxSamples
    # 
#
def SetAwgSampleFrequency(FreqANum):
    global AWGBuffLen, AWGSampleRate, MaxAWGSampleRate, ATmin
    #
    NewSampleRate = FreqANum * AWGBuffLen # Samples per second
    if NewSampleRate > MaxAWGSampleRate:
        NewSampleRate = MaxAWGSampleRate
    NewAT = int(1000000/NewSampleRate) # in uSec
    if NewAT < ATmin:
        NewAT = ATmin
    if NewAT > 500:
        NewAT = 500
    SendStr = 'T' + str(NewAT) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    # print(SendByt)
    ser.write(SendByt) #
    AWGSampleRate = int(1000000/NewAT)
    # print("AWGSampleRate = ", AWGSampleRate)
#
# for built in firmware waveforms...
#
def SetAwgA_Ampl(Ampl): # used to toggle on / off AWG output
    global ser, AwgBOnOffBt, AwgaOnOffLb, AwgbOnOffLb

    #AwgBOnOffBt.config(state=DISABLED)
    #AwgaOnOffLb.config(text="AWG Output ")
    #AwgbOnOffLb.config(text=" ")
    if Ampl == 0:
        ser.write(b'Gx\n')
    else:
        ser.write(b'Go\n')
#
def SetAwgB_Ampl(Ampl): # used to toggle on / off AWG output
    global ser, AwgBOnOffBt, AwgAOnOffBt, AwgaOnOffLb, AwgbOnOffLb

    #AwgBOnOffBt.config(state=DISABLED)
    #AwgaOnOffLb.config(text="AWG Output ")
    #AwgbOnOffLb.config(text=" ")
    if Ampl == 0:
        ser.write(b'gx\n')
    else:
        AwgAOnOffBt.config(text='ON', style="Run.TButton")
        ser.write(b'go\n')
#
## Make the current selected AWG waveform
#
##AwgString1 = "Sine"
##AwgString2 = "Triangle"
##AwgString3 = "Ramp Up"
##AwgString4 = "Ramp Down"
##AwgString5 = "Stair Up"
##AwgString6 = "Stair Down"
##AwgString7 = "Stair Up-Down"
AwgString9 = "Cosine"
AwgString10 = "Full Wave Sine"
AwgString11 = "Half Wave Sine"
AwgString12 = "Fourier Series"
AwgString13 = "Schroeder Chirp"
AwgString14 = "Sine Power Pulse"
#
## Make or update the current selected AWG waveform
def MakeAWGwaves(): # re make awg waveforms in case something changed
    global AWGAShape, AWGAShapeLabel, AWGBShape, AWGBShapeLabel
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGASymmetryEntry, AWGADutyCycleEntry
    global AWGAAmplvalue, AWGBOffsetvalue, AWGBAmplvalue, AWGBOffsetvalue, AWGAFreqvalue
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBSymmetryEntry, AWGBDutyCycleEntry
    global FSweepMode, MaxSampleRate, BisCompA
    global AwgString1, AwgString2, AwgString3, AwgString4, AwgString5, AwgString6
    global AwgString7, AwgString8, AwgString9, AwgString10, AwgString11, AwgString12
    global AwgString13, AwgString14, AwgString15, AwgString16
    
    if FSweepMode.get() == 1: # If doing a frequency sweep only make new AWG A sine wave
        if AWGAShape.get()==1:
            AWGAMakeSine()
            AWGAShapeLabel.config(text = AwgString1) # change displayed value
        return
# Shape list        
    if AWGAShape.get()== 0:
        AWGAMakeDC()
        AWGAShapeLabel.config(text = "DC") # change displayed value
    elif AWGAShape.get()==1:
        AWGAMakeSine()
        AWGAShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGAShape.get()==2:
        AWGAMakeSquare()
        AWGAShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGAShape.get()==3:
        AWGAMakeTriangle()
        AWGAShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGAShape.get()==4:
        AWGAMakePulse()
        AWGAShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGAShape.get()==5:
        AWGAMakeRampDn()
        AWGAShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGAShape.get()==6:
        AWGAMakeRampUp()
        AWGAShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGAShape.get()==7:
        AWGAMakeStair()
        AWGAShapeLabel.config(text = AwgString7) # change displayed value
    elif AWGAShape.get()==8:
        AWGAMakeSinc()
        AWGAShapeLabel.config(text = AwgString8) # change displayed value
    elif AWGAShape.get()==9:
        AWGAMakeSine()
        AWGAShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGAShape.get()==10:
        AWGAMakeFullWaveSine()
        AWGAShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGAShape.get()==11:
        AWGAMakeHalfWaveSine()
        AWGAShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGAShape.get()==12:
        AWGAMakeFourier()
        AWGAShapeLabel.config(text = AwgString12) # change displayed value
    elif AWGAShape.get()==13:
        SetAwgSampleRate()
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
        AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
        NrTones = int(eval(AWGADutyCycleEntry.get()))
        ampl = 3.0/NrTones
        if ampl > 0.25:
            ampl = 0.25
        AWGASendWave(SchroederPhase(MaxSamples, NrTones, ampl))
        AWGAShapeLabel.config(text = AwgString13) # change displayed value
    elif AWGAShape.get()==14:
        SetAwgSampleRate()
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
        AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
        Power = int(eval(AWGADutyCycleEntry.get()))
        Power = Power / 100.0
        ampl = 1
        AWGASendWave(SinePower(100, Power, 180, ampl))
        AWGAShapeLabel.config(text = AwgString14) # change displayed value
    else:
        AWGAShapeLabel.config(text = "Other Shape") # change displayed value
#
    if BisCompA.get() == 1:
        SetBCompA()
#
    if AWGBShape.get() == 0:
        AWGBMakeDC()
        AWGBShapeLabel.config(text = "DC") # change displayed value
    elif AWGBShape.get() == 1:
        AWGBMakeSine()
        AWGBShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGBShape.get() == 2:
        AWGBMakeSquare()
        AWGBShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGBShape.get() == 3:
        AWGBMakeTriangle()
        AWGBShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGBShape.get() == 4:
        AWGBMakePulse()
        AWGBShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGBShape.get()==5:
        AWGBMakeRampDn()
        AWGBShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGBShape.get()==6:
        AWGBMakeRampUp()
        AWGBShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGBShape.get()==7:
        AWGBMakeStair()
        AWGBShapeLabel.config(text = AwgString7) # change displayed value
    elif AWGBShape.get()==8:
        AWGBMakeSinc()
        AWGBShapeLabel.config(text = AwgString8) # change displayed value
    elif AWGBShape.get()==9:
        AWGBMakeSine()
        AWGBShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGBShape.get()==10:
        AWGBMakeFullWaveSine()
        AWGBShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGBShape.get()==11:
        AWGBMakeHalfWaveSine()
        AWGBShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGBShape.get()==12:
        AWGBMakeFourier()
        AWGBShapeLabel.config(text = AwgString12) # change displayed value
    elif AWGBShape.get()==13:
        SetAwgSampleRate()
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
        AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
        NrTones = int(eval(AWGBDutyCycleEntry.get()))
        ampl = 3.0/NrTones
        if ampl > 0.25:
            ampl = 0.25
        AWGBSendWave(SchroederPhase(MaxSamples, NrTones, ampl))
        AWGBShapeLabel.config(text = AwgString13) # change displayed value
    else:
        AWGBShapeLabel.config(text = "Other Shape") # change displayed value
#
    time.sleep(0.01)
#
# Hardware Specific PWM control functions
#
def PWM1_On_Off():
    global PWM1_is_on, ser

    if PWM1_is_on:
        #print("Set pwm on")
        ser.write(b'so\n')
    else:
        #print("Set pwm off")
        ser.write(b'sx\n')
#
def UpdatePWM1():
    global PWMDivEntry1, PWMWidthEntry1, PWMLabel1, ser

    PWMLabel1.config(text = "PWM Frequency")

    FreqValue = int(UnitConvert(PWMDivEntry1.get()))
    #PeriodValue = int(( 133e6 / 256 ) / FreqValue)
    #print("FreqValue = ", FreqValue, "PeriodValue = ",PeriodValue)
    ByteStr = 'p' + str(FreqValue) + "\n"
    SendByt = ByteStr.encode('utf-8')
    ser.write(SendByt)
    time.sleep(0.1)
    
    DutyCycle = int(PWMWidthEntry1.get())
    #WidthFraction = float((DutyCycle/100.0))
    #Width = int(PeriodValue * WidthFraction)
    ByteStr = 'm' + str(DutyCycle) + "\n"
    SendByt = ByteStr.encode('utf-8')
    ser.write(SendByt)
    time.sleep(0.1)
#
# Hardware Specific Trigger functions
#
def SendTriggerLevel():
    global TRIGGERlevel, ser, RUNstatus, AWGPeakToPeak
    # Min and Max trigger level specific to hardware
    if TRIGGERlevel > 4.0:
        TRIGGERlevel = 4.0
        TRIGGERentry.delete(0,"end")
        TRIGGERentry.insert(0, ' {0:.2f} '.format(4.0))
    if TRIGGERlevel < 0.0:
        TRIGGERlevel = 0.0
        TRIGGERentry.delete(0,"end")
        TRIGGERentry.insert(0, ' {0:.2f} '.format(0.0))
# Adjust trigger level.
# representa a 8-bit number (0-255) sent to DAC

# Set Horz possition from entry widget
def SetHorzPoss():
    global HozPossentry, ser

    HzSteps = int(float(HozPossentry.get()))
    Hz_Value = 511-HzSteps
    if Hz_Value > 256:
        T_High = 1
        T_Low = Hz_Value - 256
    else:
        T_High = 0
        T_Low = Hz_Value
#
# Set Internal / External triggering bits
def BTrigIntExt():
    global TgSource, TriggerInt

    if TgSource.get() == 0:
        TriggerInt = 0x00 # bit 7 0x00 = Internal
    if TgSource.get() == 1:
        TriggerInt = 0x80 # bit 7 0x80 = External
# Set Triggering source bits
def BSetTriggerSource():
    global TgInput, TrigSource, TriggerInt

    if TgInput.get() == 1:
        TrigSource = 0x00 # bit 4 0x00 = Channel A
    if TgInput.get() == 2:
        TrigSource = 0x10 # bit 4 0x10 = Channel B
    if TgInput.get() == 0:
        TriggerInt = 0x40 # bit 6 0x40 No Triggers (free-run)?
# Set Trigger edge bits
def BSetTrigEdge():
    global TgEdge, TriggerEdge
    
    if TgEdge.get() == 0:
        TriggerEdge = 0x00 # bit 5 0x00 = Rising Edge
    else:
        TriggerEdge = 0x20 # bit 5 0x20 = Falling Edge
#
## Text Editor stuff here
def TextNew_file():
    global BOMtext, TextCurrent_filepath
    
    BOMtext.delete(1.0, END)
#
def TextOpen_file():
    global BOMtext, TextCurrent_filepath
    
    filepath = askopenfilename(defaultextension=".txt", initialfile=TextCurrent_filepath,
                                filetypes=[("Circuit Files", "*.cir"),
                                               ("Text Files", "*.txt"),
                                                ("All Files", "*.*")])
    if filepath:
        TextCurrent_filepath = filepath
        try:
            with open(filepath, "r") as file:
                content = file.read()
                BOMtext.delete(1.0, END)
                BOMtext.insert(END, content)
            #.title(f"Simple Text Editor - {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
#
def TextSave_file():
    global TextCurrent_filepath
    
    filepath = TextCurrent_filepath
    if filepath:
        TextWrite_to_file(filepath)
    else:
        TextSave_file_as()
#
def TextSave_file_as():
    global BOMtext, TextCurrent_filepath
    
    filepath = asksaveasfilename(defaultextension=".cir",
                                    filetypes=[("Circuit Files", "*.cir"),
                                               ("Text Files", "*.txt"),
                                                ("All Files", "*.*")])
    if filepath:
        TextWrite_to_file(filepath)
        TextCurrent_filepath = filepath
        #
#
def TextWrite_to_file(filepath):
    global BOMtext

    try:
        with open(filepath, "w", encoding='utf-8') as file:
            file.write(BOMtext.get(1.0, END))
    except Exception as e:
        showwarning("Error", f"Could not save file: {e}")
#
##
def VerifyCompsFile():
    global FileString

    netlist = FileString.get()
    ResetMatrix()
    ParseNetlist2(ReadNetlist(netlist)) # list of all subcircuit instances found
    VerifyComps()
##
def VerifyCompsEditor():
    global BOMtext

    lines = BOMtext.get(1.0, END)
    lines = lines.splitlines()
    ResetMatrix()
    ParseNetlist2(lines) # list of all subcircuit instances found
    VerifyComps()
##
def ParseNetlist2(CmpList):
    global VPower, UnRouted, RL_OneList, RR_OneList, RL_TwoList, RR_TwoList, CL_OneList
    global CR_OneList, CL_TwoList, CR_TwoList, DL_OneList, DR_OneList, DL_TwoList
    global DR_TwoList, QL_List, QR_List, UL_List, UR_List
    global U_Connections, XCPList
    global ComponentList, VPowerConnections, UnRouted
    global FileString

    # netlist = FileString.get()
    # ResetMatrix()
    # CmpList = ReadNetlist(netlist) # list of all subcircuit instances found
    #
    VPower = []
    UnRouted = []
    RL_OneList = []
    RR_OneList = []
    RL_TwoList = []
    RR_TwoList = []
    CL_OneList = []
    CR_OneList = []
    CL_TwoList = []
    CR_TwoList = []
    DL_OneList = []
    DR_OneList = []
    DL_TwoList = []
    DR_TwoList = []
    QL_List = []
    QR_List = []
    UL_List = []
    UR_List = []
    # 
    XCPList = []
    ComponentList = []
    UIndex = 0
    TLIndex = BLIndex = 1
    TRIndex = BRIndex = 2
    TopQL = TopQR = 1 # Start first device in bottom region?
    JPIndex = 1
    XIndex = 1
    VIndex = 1
    for line in CmpList:
        if ".subckt" in line: # Stop when you get to sub circuits
            break
        if "cross_point" in line: # Select the lines that contain "cross_point"
            XCPList.append(line)
            ComponentList.append(line.split())
        SplitLine = []
        SplitLine = line.split()
        # if a source has V in name
        # and one or the other terminal nodes names have a V
        if len(SplitLine) > 0:
            FirstPart = SplitLine[0]
            if "V" == FirstPart[0]:
                if "V" in SplitLine[1]:
                    if SplitLine[1] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[1])
                if "V" in SplitLine[2]:
                    if SplitLine[2] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[2])
                if "COM" in SplitLine[1]:
                    if SplitLine[1] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[1])
                if "COM" in SplitLine[2]:
                    if SplitLine[2] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[2])
                if "0" == SplitLine[1]:
                    if SplitLine[1] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[1])
                if "0" == SplitLine[2]:
                    if SplitLine[2] in VPower:
                        donothing()
                    else:
                        VPower.append(SplitLine[2])
            if "R" == FirstPart[0]: # Find all resistors
                JmpNum = 0
                if "JP" in SplitLine[1]:
                    Jumper = SplitLine[1] # First net is Jumper bus
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                elif "JP" in SplitLine[2]:
                    Jumper = SplitLine[2] # First net is Jumper bus
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                if JmpNum > 0 and JmpNum < 9: # Comp on left
                    if "V" in SplitLine[1] or "V" in SplitLine[2]:
                        RL_OneList.append(SplitLine)
                    elif SplitLine[1] == "0" or SplitLine[2] == "0":
                        RL_OneList.append(SplitLine)
                    else:
                        RL_TwoList.append(SplitLine)
                elif JmpNum > 8 and JmpNum < 17: # Comp on right
                    if "V" in SplitLine[1] or "V" in SplitLine[2]:
                        RR_OneList.append(SplitLine)
                    elif SplitLine[1] == "0" or SplitLine[2] == "0":
                        RR_OneList.append(SplitLine)
                    else:
                        RR_TwoList.append(SplitLine)
                elif JmpNum == 0: # Already placed?
                    if "R" in SplitLine[1] or "R" in SplitLine[2]:
                        if "V" in SplitLine[1] or "V" in SplitLine[2]:
                            RR_OneList.append(SplitLine)
                        elif SplitLine[1] == "0" or SplitLine[2] == "0":
                            RR_OneList.append(SplitLine)
                        else:
                            RR_TwoList.append(SplitLine)
                    else:
                        if "V" in SplitLine[1] or "V" in SplitLine[2]:
                            RL_OneList.append(SplitLine)
                        elif SplitLine[1] == "0" or SplitLine[2] == "0":
                            RL_OneList.append(SplitLine)
                        else:
                            RL_TwoList.append(SplitLine)
            if "C" == FirstPart[0] or "L" == FirstPart[0]: # Find all capacitors and inductors
                JmpNum = 0
                if "JP" in SplitLine[1]:
                    Jumper = SplitLine[1] # First net is Jumper bus
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                elif "JP" in SplitLine[2]:
                    Jumper = SplitLine[2] # First net is Jumper bus
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                if JmpNum > 0 and JmpNum < 9:
                    if "V" in SplitLine[1] or "V" in SplitLine[2]:
                        CL_OneList.append(SplitLine)
                    elif SplitLine[1] == "0" or SplitLine[2] == "0":
                        CL_OneList.append(SplitLine)
                    else:
                        CL_TwoList.append(SplitLine)
                elif JmpNum > 8 and JmpNum < 17:
                    if "V" in SplitLine[1] or "V" in SplitLine[2]:
                        CR_OneList.append(SplitLine)
                    elif SplitLine[1] == "0" or SplitLine[2] == "0":
                        CR_OneList.append(SplitLine)
                    else:
                        CR_TwoList.append(SplitLine)
                elif JmpNum == 0: # Already placed?
                    if "R" in SplitLine[1] or "R" in SplitLine[2]:
                        if "V" in SplitLine[1] or "V" in SplitLine[2]:
                            CR_OneList.append(SplitLine)
                        elif SplitLine[1] == "0" or SplitLine[2] == "0":
                            CR_OneList.append(SplitLine)
                        else:
                            CR_TwoList.append(SplitLine)
                    else:
                        if "V" in SplitLine[1] or "V" in SplitLine[2]:
                            CL_OneList.append(SplitLine)
                        elif SplitLine[1] == "0" or SplitLine[2] == "0":
                            CL_OneList.append(SplitLine)
                        else:
                            CL_TwoList.append(SplitLine)
            if "D" == FirstPart[0]: # Find all diodes
                JmpNum = 0
                if "JP" in SplitLine[1]:
                    Jumper = SplitLine[1] # 
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                elif "JP" in SplitLine[2]:
                    Jumper = SplitLine[2] # 
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                if JmpNum > 0 and JmpNum < 9:
                    if "V" in SplitLine[1] or "V" in SplitLine[2]:
                        DL_OneList.append(SplitLine)
                    elif SplitLine[1] == "0" or SplitLine[2] == "0":
                        DL_OneList.append(SplitLine)
                    else:
                        DL_TwoList.append(SplitLine)
                elif JmpNum > 8 and JmpNum < 17:
                    if "V" in SplitLine[1] or "V" in SplitLine[2]:
                        DR_OneList.append(SplitLine)
                    elif SplitLine[1] == "0" or SplitLine[2] == "0":
                        DR_OneList.append(SplitLine)
                    else:
                        DR_TwoList.append(SplitLine)
                elif JmpNum == 0: # Already placed?
                    if "R" in SplitLine[1] or "R" in SplitLine[2]:
                        if "V" in SplitLine[1] or "V" in SplitLine[2]:
                            DR_OneList.append(SplitLine)
                        elif SplitLine[1] == "0" or SplitLine[2] == "0":
                            DR_OneList.append(SplitLine)
                        else:
                            DR_TwoList.append(SplitLine)
                    else:
                        if "V" in SplitLine[1] or "V" in SplitLine[2]:
                            DL_OneList.append(SplitLine)
                        elif SplitLine[1] == "0" or SplitLine[2] == "0":
                            DL_OneList.append(SplitLine)
                        else:
                            DL_TwoList.append(SplitLine)
            if "Q" == FirstPart[0] or "M" == FirstPart[0]: # Find all 3 term transostors
                JmpNum = 0
                if "JP" in SplitLine[1]:
                    Jumper = SplitLine[1] # 
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                elif "JP" in SplitLine[2]:
                    Jumper = SplitLine[2] # 
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                elif "JP" in SplitLine[3]:
                    Jumper = SplitLine[3] # 
                    JmpNum = int(Jumper.replace("JP","")) # extract number 1-16
                if JmpNum > 0 and JmpNum < 9:
                    QL_List.append(SplitLine)
                elif JmpNum > 8 and JmpNum < 17:
                    QR_List.append(SplitLine)
                elif JmpNum == 0: # Already placed?
                    if "R" in SplitLine[1] or "R" in SplitLine[2]:
                        QR_List.append(SplitLine)
                    else:
                        QL_List.append(SplitLine)
            if "U" in FirstPart: # Find all other IC
                    UL_List.append(SplitLine)
#
def AutoPlacer(): # VERY Experimental
    global BOMtext
    global VPower, UnRouted, RL_OneList, RR_OneList, RL_TwoList, RR_TwoList, CL_OneList
    global CR_OneList, CL_TwoList, CR_TwoList, DL_OneList, DR_OneList, DL_TwoList
    global DR_TwoList, QL_List, QR_List, UL_List, UR_List
    global U_Connections, XCPList
    global ComponentList, VPowerConnections, UnRouted
    global FileString
    #
    netlist = FileString.get()
    if ".cir" in netlist or ".net" in netlist:
        pass
    else:
        netlist = askopenfilename(defaultextension = ".cir", filetypes=[("Net List files", ".cir .net")])
        FileString.delete(0,"end")
        FileString.insert(0,netlist)
    #
    ParseNetlist2(ReadNetlist(netlist)) # list of all subcircuit instances found
    # 
    UIndex = 0
    TLIndex = BLIndex = 1
    TRIndex = BRIndex = 2
    TopQL = TopQR = 1 # Start first device in bottom region?
    JPIndex = 1
    XIndex = 1
    VIndex = 1
## Clear all text in Editor
    BOMtext.delete("1.0", END)
## Left Side BB for jumpers 1-8
    # List two BB pin resistors on Left side
    for R in range (0, len(RL_TwoList), 1):
        Rterm = RL_TwoList[R]
        Rname  = Rterm[0]
        Rterm1 = Rterm[1]
        Rterm2 = Rterm[2]
        RValue = Rterm[3]
        if "JP" not in Rterm1:
            UnRhole = "TL" + str(TLIndex)
            UnRouted.append([Rterm1, UnRhole])
        if "JP" not in Rterm2:
            UnRhole = "BL" + str(TLIndex)
            UnRouted.append([Rterm2, UnRhole])
        #
        R_Line = Rname + " " 
        R_Line = R_Line + "TL" + str(TLIndex) + " " + "BL" + str(TLIndex) + " "
        X_Line = "X" + str(XIndex) + " " + Rterm1 + " " + "TL" + str(TLIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        X_Line = "X" + str(XIndex) + " " + Rterm2 + " " + "BL" + str(TLIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        TLIndex = TLIndex + 1
        BLIndex = BLIndex + 1
        #
        R_Line = R_Line + RValue + "\n" 
        BOMtext.insert(END, R_Line)
    # List two BB capacitors / inductors Left side
    for C in range (0, len(CL_TwoList), 1):
        Cterm = CL_TwoList[C]
        Cname  = Cterm[0]
        Cterm1 = Cterm[1]
        Cterm2 = Cterm[2]
        CValue = Cterm[3]
        if "JP" not in Cterm1:
            UnRhole = "TL" + str(TLIndex)
            UnRouted.append([Cterm1, UnRhole])
        if "JP" not in Cterm2:
            UnRhole = "BL" + str(TLIndex)
            UnRouted.append([Cterm2, UnRhole])
        #
        C_Line = Cname + " " # 
        C_Line = C_Line + "TL" + str(TLIndex) + " " + "BL" + str(TLIndex) + " "
        X_Line = "X" + str(XIndex) + " " + Cterm1 + " " + "TL" + str(TLIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        X_Line = "X" + str(XIndex) + " " + Cterm2 + " " + "BL" + str(TLIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        TLIndex = TLIndex + 1
        BLIndex = BLIndex + 1
        #
        C_Line = C_Line + CValue + "\n" 
        BOMtext.insert(END, C_Line)
    # Add two BB pin Diodes 
    for D in range (0, len(DL_TwoList), 1):
        Dterm = DL_TwoList[D]
        Dname  = Dterm[0]
        Dterm1 = Dterm[1]
        Dterm2 = Dterm[2]
        DValue = Dterm[3]
        if "JP" not in Dterm1:
            UnRhole = "TL" + str(TLIndex)
            UnRouted.append([Dterm1, UnRhole])
        if "JP" not in Dterm2:
            UnRhole = "BL" + str(TLIndex)
            UnRouted.append([Dterm2, UnRhole])
        #
        D_Line = Dname + " " #
        D_Line = D_Line + "TL" + str(TLIndex) + " " + "BL" + str(TLIndex) + " "
        X_Line = "X" + str(XIndex) + " " + Dterm1 + " " + "TL" + str(TLIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        X_Line = "X" + str(XIndex) + " " + Dterm2 + " " + "BL" + str(TLIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        TLIndex = TLIndex + 1
        BLIndex = BLIndex + 1
        #
        D_Line = D_Line + DValue + "\n" 
        BOMtext.insert(END, D_Line)
    # add resistors to Power / Gnd
    TLIndex = max(TLIndex, BLIndex)
    BLIndex = max(TLIndex, BLIndex)
    for R in range (0, len(RL_OneList), 1):
        Rterm = RL_OneList[R]
        Rname  = Rterm[0]
        Rterm1 = Rterm[1]
        Rterm2 = Rterm[2]
        RValue = Rterm[3]
        #
        R_Line = Rname + " "
        if Rterm1 == "0":
            if "BL" in Rterm2:
                R_Line = R_Line + "GND " + Rterm2 + " "
            else:
                R_Line = R_Line + "GND " + "BL" + str(BLIndex) + " " #
                if "JP" not in Rterm2:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Rterm2, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Rterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BLIndex = BLIndex + 1
        elif "VDD" in Rterm1:
            if "TL" in Rterm2:
                R_Line = R_Line + "VDD " + Rterm2 + " "
            else:
                R_Line = R_Line + "VDD " + "TL" + str(TLIndex) + " "
                if "JP" not in Rterm2:
                    UnRhole = "TL" + str(TLIndex)
                    UnRouted.append([Rterm2, UnRhole])
            X_Line = "XTL" + str(TLIndex) + " " + Rterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            TLIndex = TLIndex + 1
        elif "VEE" in Rterm1:
            if "BL" in Rterm2:
                R_Line = R_Line + "VDD " + Rterm2 + " "
            else:
                R_Line = R_Line + "VEE " + "BL" + str(BLIndex) + " "
                if "JP" not in Rterm2:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Rterm2, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Rterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BLIndex = BLIndex + 1
        #
        elif Rterm2 == "0":
            if "BL" in Rterm1:
                R_Line = R_Line + "GND " + Rterm1 + " "
            else:
                R_Line = R_Line + "GND " + "BL" + str(BLIndex) + " "
                if "JP" not in Rterm1:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Rterm1, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Rterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BLIndex = BLIndex + 1
        elif "VDD" in Rterm2:
            if "TL" in Rterm1:
                R_Line = R_Line + "VDD " + Rterm1 + " "
            else:
                R_Line = R_Line + "VDD " + "TL" + str(TLIndex) + " "
                if "JP" not in Rterm1:
                    UnRhole = "TL" + str(TLIndex)
                    UnRouted.append([Rterm1, UnRhole])
            X_Line = "XTL" + str(TLIndex) + " " + Rterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            TLIndex = TLIndex + 1
        elif "VEE" in Rterm2:
            if "BL" in Rterm1:
                R_Line = R_Line + "VEE " + Rterm1 + " "
            else:
                R_Line = R_Line + "VEE " + "BL" + str(BLIndex) + " "
                if "JP" not in Rterm1:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Rterm1, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Rterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BLIndex = BLIndex + 1
        #
        R_Line = R_Line + RValue + "\n" 
        BOMtext.insert(END, R_Line)
    ## add capacitors / inductors to Power / Gnd
    # TLIndex = max(TLIndex, BLIndex)
    # BLIndex = max(TLIndex, BLIndex)
    for C in range (0, len(CL_OneList), 1):
        Cterm = CL_OneList[C]
        Cname  = Cterm[0]
        Cterm1 = Cterm[1]
        Cterm2 = Cterm[2]
        CValue = Cterm[3]
        #
        C_Line = Cname + " " # 
        if Cterm1 == "0":
            if "BL" in Cterm2:
                C_Line = C_Line + "GND " + Cterm2 + " "
            else:
                C_Line = C_Line + "GND " + "BL" + str(BLIndex) + " "
                if "JP" not in Cterm2:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Cterm2, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Cterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BLIndex = BLIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VDD" in Cterm1:
            if "TL" in Cterm2:
                C_Line = C_Line + "VDD " + Cterm2 + " "
            else:
                C_Line = C_Line + "VDD " + "TL" + str(TLIndex) + " "
                if "JP" not in Cterm2:
                    UnRhole = "TL" + str(TLIndex)
                    UnRouted.append([Cterm2, UnRhole])
            X_Line = "XTL" + str(TLIndex) + " " + Cterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            TLIndex = TLIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VEE" in Cterm1:
            if "BL" in Cterm2:
                C_Line = C_Line + "GND " + Cterm2 + " "
            else:
                C_Line = C_Line + "VEE " + "BL" + str(BLIndex) + " "
                if "JP" not in Cterm2:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Cterm2, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Cterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BLIndex = BLIndex + 1
            BOMtext.insert(END, X_Line)
        elif Cterm2 == "0":
            if "BL" in Cterm1:
                C_Line = C_Line + "GND " + Cterm1 + " "
            else:
                C_Line = C_Line + "GND " + "BL" + str(BLIndex) + " "
                if "JP" not in Cterm1:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Cterm1, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Cterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BLIndex = BLIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VDD" in Cterm2:
            if "TL" in Cterm1:
                C_Line = C_Line + "VDD " + Cterm2 + " "
            else:
                C_Line = C_Line + "VDD " + "TL" + str(TLIndex) + " "
                if "JP" not in Cterm1:
                    UnRhole = "TL" + str(TLIndex)
                    UnRouted.append([Cterm1, UnRhole])
            X_Line = "XTL" + str(TLIndex) + " " + Cterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            TLIndex = TLIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VEE" in Cterm2:
            if "BL" in Cterm1:
                C_Line = C_Line + "GND " + Cterm1 + " "
            else:
                C_Line = C_Line + "VEE " + "BL" + str(BLIndex) + " "
                if "JP" not in Cterm1:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Cterm1, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Cterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BLIndex = BLIndex + 1
            BOMtext.insert(END, X_Line)
        #
        C_Line = C_Line + CValue + "\n" 
        BOMtext.insert(END, C_Line)
    # List Diodes on Left side
    for D in range (0, len(DL_OneList), 1):
        Dterm = DL_OneList[D]
        Dname  = Dterm[0]
        Dterm1 = Dterm[1]
        Dterm2 = Dterm[2]
        DValue = Dterm[3]
        #
        D_Line = Dname + " " # 
        if Dterm1 == "0":
            if "BL" in Dterm2:
                D_Line = D_Line + "GND " + Dterm1 + " "
            else:
                D_Line = D_Line + "GND " + "BL" + str(BLIndex) + " "
                if "JP" not in Dterm2:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Dterm2, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Dterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BLIndex = BLIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VDD" in Dterm1:
            if "TL" in Dterm2:
                D_Line = D_Line + "VDD " + Dterm1 + " "
            else:
                D_Line = D_Line + "VDD " + "TL" + str(TLIndex) + " "
                if "JP" not in Dterm2:
                    UnRhole = "TL" + str(TLIndex)
                    UnRouted.append([Dterm2, UnRhole])
            X_Line = "XTL" + str(TLIndex) + " " + Dterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            TLIndex = TLIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VEE" in Dterm1:
            if "BL" in Dterm2:
                D_Line = D_Line + "GND " + Dterm1 + " "
            else:
                D_Line = D_Line + "VEE " + "BL" + str(BLIndex) + " "
                if "JP" not in Dterm2:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Dterm2, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Dterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BLIndex = BLIndex + 1
            BOMtext.insert(END, X_Line)
        elif Dterm2 == "0":
            if "BL" in Dterm1:
                D_Line = D_Line + "GND " + Dterm1 + " "
            else:
                D_Line = D_Line + "BL" + str(BLIndex) + " GND "
                if "JP" not in Dterm1:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Dterm1, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Dterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BLIndex = BLIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VDD" in Dterm2:
            if "TL" in Dterm1:
                D_Line = D_Line + "VDD " + Dterm1 + " "
            else:
                D_Line = D_Line + "TL" + str(TLIndex) + " VDD "
                if "JP" not in Dterm1:
                    UnRhole = "TL" + str(TLIndex)
                    UnRouted.append([Dterm1, UnRhole])
            X_Line = "XTL" + str(TLIndex) + " " + Dterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            TLIndex = TLIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VEE" in Dterm2:
            if "BL" in Dterm1:
                D_Line = D_Line + "GND " + Dterm1 + " "
            else:
                D_Line = D_Line + "BL" + str(BLIndex) + " VEE "
                if "JP" not in Dterm1:
                    UnRhole = "BL" + str(BLIndex)
                    UnRouted.append([Dterm1, UnRhole])
            X_Line = "XBL" + str(BLIndex) + " " + Dterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BLIndex = BLIndex + 1
        #
        D_Line = D_Line + DValue + "\n" 
        BOMtext.insert(END, D_Line)
    # List Q transistors on Left side
    for Q in range (0, len(QL_List), 1):
        Qterm = QL_List[Q]
        Qname = Qterm[0]
        Qterm1 = Qterm[1]
        Qterm2 = Qterm[2]
        Qterm3 = Qterm[3]
        Qterm4 = Qterm[4]
        QValue = Qterm[5]
        #
        Q_Line = Qname + " "
        #
        if "VDD" in Qterm:
            TopQL = 0
        elif "VEE" in Qterm:
            TopQL = 1
        if "TL" in Qterm1 or "TL" in Qterm2 or "TL" in Qterm3:
            TopQL = 0
        elif "BL" in Qterm1 or "BL" in Qterm2 or "BL" in Qterm3:
            TopQL = 1
        # Do three terminals
        for T in range(1, 4, 1):
            if TopQL == 0:
                QIndex = TLIndex
                if "TL" in Qterm[T]:
                    Q_Line = Q_Line + " " + Qterm[T] + " "
                else:
                    Q_Line = Q_Line + "TL" + str(QIndex) + " "
                    TLIndex = TLIndex + 1
                if Qterm[T] == "0":
                    QN1 = "GND"
                    X_Line = "XTL" + str(QIndex) + " 0 " + QN1 + " cross_point\n"
                elif "VDD" in Qterm[T]:
                    QN1 = "VDD"
                    X_Line = "XTL" + str(QIndex) + " " + QN1 + " NC cross_point\n"
                elif "JP" not in Qterm[T]:
                    if "TL" in Qterm[T]:
                        donothing()
                    else:
                        UnRhole = "TL" + str(QIndex)
                        UnRouted.append([Qterm[T], UnRhole])
                else:
                    QN1 = Qterm[T]
                    X_Line = "X" + str(XIndex) + " " + QN1 + " " + "TL" + str(QIndex) + " cross_point\n"
                    XIndex = XIndex + 1
                #
            else:
                QIndex = BLIndex
                if "BL" in Qterm[T]:
                    Q_Line = Q_Line + " " + Qterm[T] + " "
                else:
                    Q_Line = Q_Line + "BL" + str(QIndex) + " "
                    BLIndex = BLIndex + 1
                if Qterm[T] == "0":
                    QN1 = "GND"
                    X_Line = "XBL" + str(QIndex) + " 0 " + QN1 + " cross_point\n"
                elif "VEE" in Qterm1:
                    QN1 = "VEE"
                    X_Line = "XBL" + str(QIndex) + " " + QN1 + " NC cross_point\n"
                elif "JP" not in Qterm[T]:
                    if "BL" in Qterm[T]:
                        donothing()
                    else:
                        UnRhole = "BL" + str(QIndex)
                        UnRouted.append([Qterm[T], UnRhole])
                else:
                    QN1 = Qterm[T]
                    X_Line = "X" + str(XIndex) + " " + QN1 + " " + "BL" + str(QIndex) + " cross_point\n"
                    XIndex = XIndex + 1
                #
            BOMtext.insert(END, X_Line)
        #
        Q_Line = Q_Line + Qterm4 + " " + QValue + "\n" 
        BOMtext.insert(END, Q_Line)
        if TopQL == 0: # Toggle between top and bottom
            TopQL = 1
        else:
            TopQL = 0
## Right Side BB for jumpers 9-16
    # List two BB pin resistors on Left side
    for R in range (0, len(RR_TwoList), 1):
        Rterm = RR_TwoList[R]
        Rname  = Rterm[0]
        Rterm1 = Rterm[1]
        Rterm2 = Rterm[2]
        RValue = Rterm[3]
        if "JP" not in Rterm1:
            UnRhole = "TR" + str(TRIndex)
            UnRouted.append([Rterm1, UnRhole])
        if "JP" not in Rterm2:
            UnRhole = "BR" + str(TRIndex)
            UnRouted.append([Rterm2, UnRhole])
        #
        R_Line = Rname + " " 
        R_Line = R_Line + "TR" + str(TRIndex) + " " + "BR" + str(TRIndex) + " "
        X_Line = "X" + str(XIndex) + " " + Rterm1 + " " + "TR" + str(TRIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        X_Line = "X" + str(XIndex) + " " + Rterm2 + " " + "BR" + str(TRIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        TRIndex = TRIndex + 1
        BRIndex = BRIndex + 1
        #
        R_Line = R_Line + RValue + "\n" 
        BOMtext.insert(END, R_Line)
    # List two BB capacitors Right side
    for C in range (0, len(CR_TwoList), 1):
        Cterm = CR_TwoList[C]
        Cname  = Cterm[0]
        Cterm1 = Cterm[1]
        Cterm2 = Cterm[2]
        CValue = Cterm[3]
        if "JP" not in Cterm1:
            UnRhole = "TR" + str(TRIndex)
            UnRouted.append([Cterm1, UnRhole])
        if "JP" not in Rterm2:
            UnRhole = "BR" + str(TRIndex)
            UnRouted.append([Cterm2, UnRhole])
        #
        C_Line = Cname + " " # 
        C_Line = C_Line + "TR" + str(TRIndex) + " " + "BR" + str(TRIndex) + " "
        X_Line = "X" + str(XIndex) + " " + Cterm1 + " " + "TR" + str(TRIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        X_Line = "X" + str(XIndex) + " " + Cterm2 + " " + "BR" + str(TRIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        TRIndex = TRIndex + 1
        BRIndex = BRIndex + 1
        #
        C_Line = C_Line + CValue + "\n" 
        BOMtext.insert(END, C_Line)
    # Add two BB pin Diodes 
    for D in range ( 0, len(DR_TwoList), 1):
        Dterm = DR_TwoList[D]
        Dname  = Dterm[0]
        Dterm1 = Dterm[1]
        Dterm2 = Dterm[2]
        DValue = Dterm[3]
        if "JP" not in Dterm1:
            UnRhole = "TR" + str(TRIndex)
            UnRouted.append([Dterm1, UnRhole])
        if "JP" not in Rterm2:
            UnRhole = "BR" + str(TRIndex)
            UnRouted.append([Dterm2, UnRhole])
        #
        D_Line = Dname + " "
        D_Line = D_Line + "TR" + str(TLIndex) + " " + "BR" + str(TRIndex) + " "
        X_Line = "X" + str(XIndex) + " " + Dterm1 + " " + "TR" + str(TRIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        X_Line = "X" + str(XIndex) + " " + Dterm2 + " " + "BR" + str(TRIndex) + " cross_point\n"
        XIndex = XIndex + 1
        BOMtext.insert(END, X_Line)
        TRIndex = TRIndex + 1
        BRIndex = BRIndex + 1
        #
        D_Line = D_Line + DValue + "\n" 
        BOMtext.insert(END, D_Line)
    # add resistors to Power / Gnd
    # TRIndex = max(TRIndex, BRIndex)
    # BRIndex = max(TRIndex, BRIndex)
    for R in range (0, len(RR_OneList), 1):
        Rterm = RR_OneList[R]
        Rname  = Rterm[0]
        Rterm1 = Rterm[1]
        Rterm2 = Rterm[2]
        RValue = Rterm[3]
        #
        R_Line = Rname + " " 
        if Rterm1 == "0":
            if "BR" in Rterm2:
                R_Line = R_Line + "GND " + Rterm2 + " "
            else:
                R_Line = R_Line + "GND " + "BR" + str(BRIndex) + " "
                if "JP" not in Rterm2:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Rterm2, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Rterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BRIndex = BRIndex + 1
        elif "VDD" in Rterm1:
            if "TR" in Rterm2:
                R_Line = R_Line + "VDD " + Rterm2 + " "
            else:
                R_Line = R_Line + "VDD " + "TR" + str(TRIndex) + " "
                if "JP" not in Rterm2:
                    UnRhole = "TR" + str(TRIndex)
                    UnRouted.append([Rterm2, UnRhole])
            X_Line = "XTR" + str(TRIndex) + " " + Rterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            TRIndex = TRIndex + 1
        elif "VEE" in Rterm1:
            if "BR" in Rterm2:
                R_Line = R_Line + "GND " + Rterm2 + " "
            else:
                R_Line = R_Line + "VEE " + "BR" + str(BRIndex) + " "
                if "JP" not in Rterm2:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Rterm2, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Rterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BRIndex = BRIndex + 1
        elif Rterm2 == "0":
            if "BR" in Rterm1:
                R_Line = R_Line + "GND " + Rterm1 + " "
            else:
                R_Line = R_Line + "GND " + "BR" + str(BRIndex) + " "
                if "JP" not in Rterm1:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Rterm1, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Rterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BRIndex = BRIndex + 1
        elif "VDD" in Rterm2:
            if "TR" in Rterm1:
                R_Line = R_Line + "VDD " + Rterm1 + " "
            else:
                R_Line = R_Line + "VDD " + "TR" + str(TRIndex) + " "
                if "JP" not in Rterm1:
                    UnRhole = "TR" + str(TRIndex)
                    UnRouted.append([Rterm1, UnRhole])
            X_Line = "XTR" + str(TRIndex) + " " + Rterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            TRIndex = TRIndex + 1
        elif "VEE" in Rterm2:
            if "BR" in Rterm1:
                R_Line = R_Line + "GND " + Rterm1 + " "
            else:
                R_Line = R_Line + "VEE " + "BR" + str(BRIndex) + " "
                if "JP" not in Rterm1:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Rterm1, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Rterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BRIndex = BRIndex + 1
        #
        R_Line = R_Line + RValue + "\n" 
        BOMtext.insert(END, R_Line)
    ## add capacitors to Power / Gnd
    # TRIndex = max(TRIndex, BRIndex)
    # BRIndex = max(TRIndex, BRIndex)
    for C in range (0, len(CR_OneList), 1):
        Cterm = CR_OneList[C]
        Cname  = Cterm[0]
        Cterm1 = Cterm[1]
        Cterm2 = Cterm[2]
        CValue = Cterm[3]
        #
        C_Line = Cname + " " # 
        if Cterm1 == "0":
            if "BR" in Cterm2:
                C_Line = C_Line + "GND " + Cterm2 + " "
            else:
                C_Line = C_Line + "GND " + "BR" + str(BRIndex) + " "
                if "JP" not in Cterm2:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Cterm2, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Cterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BRIndex = BRIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VDD" in Cterm1:
            if "TR" in Cterm2:
                C_Line = C_Line + "VDD " + Cterm2 + " "
            else:
                C_Line = C_Line + "VDD " + "TR" + str(TRIndex) + " "
                if "JP" not in Cterm2:
                    UnRhole = "TR" + str(TRIndex)
                    UnRouted.append([Cterm2, UnRhole])
            X_Line = "XTR" + str(TRIndex) + " " + Cterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            TRIndex = TRIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VEE" in Cterm1:
            if "BR" in Cterm2:
                C_Line = C_Line + "GND " + Cterm2 + " "
            else:
                C_Line = C_Line + "VEE " + "BR" + str(BRIndex) + " "
                if "JP" not in Cterm2:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Cterm2, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Cterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BRIndex = BRIndex + 1
            BOMtext.insert(END, X_Line)
        elif Cterm2 == "0":
            if "BR" in Cterm1:
                C_Line = C_Line + "GND " + Cterm1 + " "
            else:
                C_Line = C_Line + "GND " + "BR" + str(BRIndex) + " "
                if "JP" not in Cterm1:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Cterm1, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Cterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BRIndex = BRIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VDD" in Cterm2:
            if "TR" in Cterm1:
                C_Line = C_Line + "VDD " + Cterm1 + " "
            else:
                C_Line = C_Line + "VDD " + "TR" + str(TRIndex) + " "
                if "JP" not in Cterm1:
                    UnRhole = "TR" + str(TRIndex)
                    UnRouted.append([Cterm1, UnRhole])
            X_Line = "XTL" + str(TRIndex) + " " + Cterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            TRIndex = TRIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VEE" in Cterm2:
            if "BR" in Cterm1:
                C_Line = C_Line + "GND " + Cterm1 + " "
            else:
                C_Line = C_Line + "VEE " + "BR" + str(BRIndex) + " "
                if "JP" not in Cterm1:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Cterm1, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Cterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BOMtext.insert(END, X_Line)
            BRIndex = BRIndex + 1
        #
        C_Line = C_Line + CValue + "\n" 
        BOMtext.insert(END, C_Line)
    # List Diodes on Right side
    # TRIndex = max(TRIndex, BRIndex)
    # BRIndex = max(TRIndex, BRIndex)
    for D in range (0, len(DR_OneList), 1):
        Dterm = DR_OneList[D]
        Dname  = Dterm[0]
        Dterm1 = Dterm[1]
        Dterm2 = Dterm[2]
        DValue = Dterm[3]
        #
        D_Line = Dname + " " # 
        if Dterm1 == "0":
            if "BR" in Dterm2:
                D_Line = D_Line + "GND " + Dterm2 + " "
            else:
                D_Line = D_Line + "GND " + "BR" + str(BRIndex) + " "
                if "JP" not in Dterm2:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Dterm2, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Dterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BRIndex = BRIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VDD" in Dterm1:
            if "TR" in Dterm2:
                D_Line = D_Line + "VDD " + Dterm2 + " "
            else:
                D_Line = D_Line + "VDD " + "TR" + str(TRIndex) + " "
                if "JP" not in Dterm2:
                    UnRhole = "TR" + str(TRIndex)
                    UnRouted.append([Dterm2, UnRhole])
            X_Line = "XTR" + str(TRIndex) + " " + Dterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            TRIndex = TRIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VEE" in Dterm1:
            if "BR" in Dterm2:
                D_Line = D_Line + "GND " + Dterm2 + " "
            else:
                D_Line = D_Line + "VEE " + "BR" + str(BRIndex) + " "
                if "JP" not in Dterm2:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Dterm2, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Dterm2 + " NC cross_point\n"
            XIndex = XIndex + 1
            BRIndex = BRIndex + 1
            BOMtext.insert(END, X_Line)
        elif Dterm2 == "0":
            if "BR" in Dterm1:
                D_Line = D_Line + "GND " + Dterm1 + " "
            else:
                D_Line = D_Line + "BR" + str(BRIndex) + " GND "
                if "JP" not in Dterm1:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Dterm1, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Dterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BRIndex = BRIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VDD" in Dterm2:
            if "TR" in Dterm1:
                D_Line = D_Line + "GND " + Dterm1 + " "
            else:
                D_Line = D_Line + "TR" + str(TRIndex) + " VDD "
                if "JP" not in Dterm1:
                    UnRhole = "TR" + str(TRIndex)
                    UnRouted.append([Dterm1, UnRhole])
            X_Line = "XTR" + str(TRIndex) + " " + Dterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            TRIndex = TRIndex + 1
            BOMtext.insert(END, X_Line)
        elif "VEE" in Dterm2:
            if "BR" in Dterm1:
                D_Line = D_Line + "GND " + Dterm1 + " "
            else:
                D_Line = D_Line + "BR" + str(Index) + " VEE "
                if "JP" not in Dterm1:
                    UnRhole = "BR" + str(BRIndex)
                    UnRouted.append([Dterm1, UnRhole])
            X_Line = "XBR" + str(BRIndex) + " " + Dterm1 + " NC cross_point\n"
            XIndex = XIndex + 1
            BRIndex = BRIndex + 1
            BOMtext.insert(END, X_Line)
        #
        D_Line = D_Line + DValue + "\n" 
        BOMtext.insert(END, D_Line)
    # List Q transistors on Right side
    for Q in range ( 0, len(QR_List), 1):
        Qterm = QR_List[Q]
        Qname = Qterm[0]
        Qterm1 = Qterm[1]
        Qterm2 = Qterm[2]
        Qterm3 = Qterm[3]
        Qterm4 = Qterm[4]
        QValue = Qterm[5]
        #
        Q_Line = Qname + " "
        #
        if "VDD" in Qterm:
            TopQR = 0
        elif "VEE" in Qterm:
            TopQR = 1
        if "TR" in Qterm1 or "TR" in Qterm2 or "TR" in Qterm3:
            TopQR = 0
        elif "BR" in Qterm1 or "BR" in Qterm2 or "BR" in Qterm3:
            TopQR = 1
        # Do three terminals
        for T in range(1, 4, 1):
            if TopQR == 0:
                QIndex = TRIndex
                if "TR" in Qterm[T]:
                    Q_Line = Q_Line + " " + Qterm[T] + " "
                else:
                    Q_Line = Q_Line + "TR" + str(QIndex) + " "
                    TRIndex = TRIndex + 1
                if Qterm[T] == "0":
                    QN1 = "GND"
                    X_Line = "XTR" + str(QIndex) + " 0 " + QN1 + " cross_point\n"
                elif "VDD" in Qterm[T]:
                    QN1 = "VDD"
                    X_Line = "XTR" + str(QIndex) + " " + QN1 + " NC cross_point\n"
                elif "JP" not in Qterm[T]:
                    if "TR" in Qterm[T]:
                        donothing()
                    else:
                        UnRhole = "TR" + str(QIndex)
                        UnRouted.append([Qterm[T], UnRhole])
                else:
                    QN1 = Qterm[T]
                    X_Line = "X" + str(XIndex) + " " + QN1 + " " + "TR" + str(QIndex) + " cross_point\n"
                    XIndex = XIndex + 1
                #
            else:
                QIndex = BRIndex
                if "BR" in Qterm[T]:
                    Q_Line = Q_Line + " " + Qterm[T] + " "
                else:
                    Q_Line = Q_Line + "BR" + str(QIndex) + " "
                    BRIndex = BRIndex + 1
                if Qterm[T] == "0":
                    QN1 = "GND"
                    X_Line = "XBR" + str(QIndex) + " 0 " + QN1 + " cross_point\n"
                elif "VEE" in Qterm1:
                    QN1 = "VEE"
                    X_Line = "XBR" + str(QIndex) + " " + QN1 + " NC cross_point\n"
                elif "JP" not in Qterm[T]:
                    if "BR" in Qterm[T]:
                        donothing()
                    else:
                        UnRhole = "BR" + str(QIndex)
                        UnRouted.append([Qterm[T], UnRhole])
                else:
                    QN1 = Qterm[T]
                    X_Line = "X" + str(XIndex) + " " + QN1 + " " + "BR" + str(QIndex) + " cross_point\n"
                    XIndex = XIndex + 1
                #
            BOMtext.insert(END, X_Line)
        #
        Q_Line = Q_Line + Qterm4 + " " + QValue + "\n" 
        BOMtext.insert(END, Q_Line)
        if TopQR == 0: # Toggle between top and bottom
            TopQR = 1
        else:
            TopQR = 0
    # List U ICs
    for U in range ( 0, len(UL_List), 1):
        CmpName = UL_List[U][0]
        CmpName = CmpName.replace("X","")
        CmpName = CmpName.replace(chr(167),"")# remove §
        U_Line = CmpName + " "
        for UPins in range(1, len(UL_List[U]), 1):
            CompPin = UL_List[U][UPins]
            U_Line = U_Line + CompPin + " "
        U_Line = U_Line + "\n"
        BOMtext.insert(END, U_Line)
    # Add back cross points to scope and Awg channels if any
    for X in range  ( 0, len(XCPList), 1):
        CP_Line = XCPList[X]
        SplitLine = []
        SplitLine = CP_Line.split()
        xpin1 = SplitLine[0]
        # xpin1 = xpin1.replace("X","") # remove X
        xpin1 = xpin1.replace(chr(167),"") # remove §
        X_Line = xpin1 + " " + SplitLine[1] + " " + SplitLine[2] +" cross_point\n"
        BOMtext.insert(END, X_Line)
    # Add Power / Ground
    # print(VPower)
    for PWR in range ( 0, len(VPower), 1):
        VPowerConnections[PWR].append(VPower[PWR])
        # print( "Found ", VPower[PWR], " connected to ", Vpin)
        V_Line = "V" + str(VIndex) + " " + VPower[PWR] + " GND 5\n"
        VIndex = VIndex + 1
        BOMtext.insert(END, V_Line)
    # print(UnRouted)
def ScanBBpins():
    """
    Scans all pins in each region of a breadboard by connecting AINH
    through jumpers and measuring the voltage measured on each BB pin.
    Logs pins that seem to have "resistor" to one of the power rails.
    """
    global ser, CompString, JumperString, OnOffString, NumConn
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA
    global AwgAOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    #
    ser.write(b'x\n') # Reset all cross point switches to open
    ## Clear all text in Editor
    BOMtext.delete("1.0", END)
    # Configure AWG channel A DC 4.0 V
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(1) # set awg wave to sine
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, 0.0)
    AWGAOffsetEntry.delete(0,END)
    AWGAOffsetEntry.insert(0,1.0)
    AWGAFreqEntry.delete(0,END)
    AWGAFreqEntry.insert(4, 500)
    ## Send waveform
    MakeAWGwaves()
    # Select just Scope Channel A
    ShowC1_V.set(1)
    ShowC2_V.set(0)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 1
    #
    VOLTAGE_MIN = -4.25
    VOLTAGE_MAX = 4.25
    #
    UsedPins = []
    regions = ["TL", "BL", "TR", "BR"]
    for region in regions:
        upper_range = 17 if region[0] == "T" else 16
        if region[1] == "L":
            adc_jumper = "JP1"
            dac_jumper = "JP2"
        else:
            adc_jumper = "JP16"
            dac_jumper = "JP15"
        # Set up ADC connection
        set_connection(adc_jumper, "AINH", 1)
        time.sleep(0.01)
        #
        for i in range(1, upper_range + 1):
            pin = region + str(i)
            # Connect test BB pin to ADC
            set_connection(adc_jumper, pin, 1)
            # get data
            Get_Data()
            VDC = numpy.mean(VBuffA)
            #
            if VDC > VOLTAGE_MAX:
                R_Line = "Pin " + pin + " has resistor to VDD\n"
                BOMtext.insert(END, R_Line)
                UsedPins.append(pin)
            elif VDC < VOLTAGE_MIN:
                R_Line = "Pin " + pin + " has resistor to VEE\n"
                BOMtext.insert(END, R_Line)
                UsedPins.append(pin)
            elif VDC > -0.25 and VDC < 0.25:
                R_Line = "Pin " + pin + " has resistor to GND\n"
                BOMtext.insert(END, R_Line)
                UsedPins.append(pin)
            else:
                pass
                #print("{:.2f} V - Pin {} likely open".format(VDC, pin))
            # Disconnect test pin
            set_connection(adc_jumper, pin, 0)
            #
            root.update()
    set_connection(adc_jumper, "AINH", 0)
    # print(UsedPins)
    # Test remaing "open" pins two at a time top to bottom for components?
    adc_jumper = "JP1"
    dac_jumper = "JP2"
    set_connection(adc_jumper, "AINH", 1)
    set_connection(dac_jumper, "AWG1", 1)
    for i in range(1, 17): # Left side BB
        pin1 = "TL" + str(i)
        pin2 = "BL" + str(i)
        if pin1 in UsedPins or pin2 in UsedPins:
            pass
        else:
            # Connect test BB pin to ADC and DAC
            set_connection(dac_jumper, pin1, 1)
            set_connection(adc_jumper, pin2, 1)
            time.sleep(0.01)
            # get data
            Get_Data()
            VDC = numpy.mean(VBuffA)
            VMax = numpy.max(VBuffA)
            VMin = numpy.min(VBuffA)
            Vpp = VMax - VMin
            #
            if Vpp < 1.1 and Vpp > 0.9:
                if VDC > 0.45 and VDC < 0.65:
                    R_Line = "Pin " + pin1 + " has resistor to " + pin2 + "\n"
                else:
                    R_Line = "Pin " + pin1 + " has capacitor to " + pin2 + "\n"
                BOMtext.insert(END, R_Line)
        # Disconnect test pin
        set_connection(dac_jumper, pin1, 0)
        set_connection(adc_jumper, pin2, 0)
        root.update()
    # Test remaing "open" pins two at a time top to bottom for components?
    adc_jumper = "JP16"
    dac_jumper = "JP15"
    set_connection(adc_jumper, "AINH", 1)
    set_connection(dac_jumper, "AWG1", 1)
    for i in range(1, 16): # Right side BB
        pin1 = "TR" + str(i)
        pin2 = "BR" + str(i)
        if pin1 in UsedPins or pin2 in UsedPins:
            pass
        else:
            # Connect test BB pin to ADC and DAC
            set_connection(dac_jumper, pin1, 1)
            set_connection(adc_jumper, pin2, 1)
            time.sleep(0.01)
            # get data
            Get_Data()
            VDC = numpy.mean(VBuffA)
            VMax = numpy.max(VBuffA)
            VMin = numpy.min(VBuffA)
            Vpp = VMax - VMin
            #
            if Vpp < 1.1 and Vpp > 0.9:
                if VDC > 0.45 and VDC < 0.65:
                    R_Line = "Pin " + pin1 + " has resistor to " + pin2 + "\n"
                else:
                    R_Line = "Pin " + pin1 + " has capacitor to " + pin2 + "\n"
                BOMtext.insert(END, R_Line)
        # Disconnect test pin
        set_connection(dac_jumper, pin1, 0)
        set_connection(adc_jumper, pin2, 0)
        root.update()
    ####   
    ser.write(b'x\n') # Reset all cross point switches to open
    ####
#
def ScanDev2(List_Dev):
    global ComponentList, BOMtext, FWRevOne
    global BBwidth, BBheight, BBGridSize, BL1XY

    # Calculate Xstep and YStep size for 50 X 40 0.1" grid, 11 pixels per grid point?
    XStep = BBwidth/BBGridSize
    MidY = (BL1XY[1] - 1) * XStep
    # List 2 terminal Devices
    for R in range (0, len(List_Dev), 1):
        Xh1 = Yh1 = Xh2 = Yh2 = GrNum = 0
        Terms = List_Dev[R]
        Name = Terms[0]
        Term1 = Terms[1]
        Term2 = Terms[2]
        ValString = Terms[3]
        try:
            Value = UnitConvert(ValString)
        except:
            Value = 0.0
        # print(Term1, " " , Term2, " " , Value) #
        xpin1 = Term1
        xpin2 = Term2
        # Translate node name if necessary
        for xp in range (0, len(ComponentList), 1 ):
            if ("TR" in Term1) or ("BR" in Term1) or ("TL" in Term1) or ("BL" in Term1):
                xpin1 = Term1
            elif "V" in Term1:
                xpin1 = Term1
            elif Term1 in ComponentList[xp]:
                CompPins = ComponentList[xp]
                xpin1 = CompPins[0]
                xpin1 = xpin1.replace("X","")
                xpin1 = xpin1.replace(chr(167),"")# remove §
            if ("TR" in Term2 ) or ("BR" in Term2) or ("TL" in Term2) or ("BL" in Term2):
                xpin2 = Term2
            elif "V" in Term2:
                xpin2 = Term2
            elif Term2 in ComponentList[xp]:
                CompPins = ComponentList[xp]
                xpin2 = CompPins[0]
                xpin2 = xpin2.replace("X","")
                xpin2 = xpin2.replace(chr(167),"")# remove §
        # print(xpin1, " ", xpin2)
        # find comp pin locations on BB graphic
        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
        Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
        if "V" in xpin1:
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
        if "0" == xpin1 or "COM" == xpin1 or "GND" == xpin1:
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
        if "V" in xpin2:
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
        if "0" == xpin2 or "COM" == xpin2 or "GND" == xpin2:
            Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
        #
        Meas = DMeas = ResOn = CapOn = 0
        if FWRevOne == "Red3": # Use Red 3 Hardware test resistors
            if "R" in Name:
                if Value < 1000: # if measuring a low value resistor use 470
                    Meas = VerifyRes2(xpin1, xpin2, "470")
                else: # Use default test res
                    Meas = VerifyRes2(xpin1,xpin2)
            elif "C" in Name:
                if Value > 0.0000002: # if measuring a high value capacitor use 470
                    Meas = VerifyCap2(xpin1,xpin2, "470")
                else: # Use default test res
                    Meas = VerifyCap2(xpin1,xpin2, "24k")
            elif "D" in Name:
                DMeas = VerifyDiode2(xpin1,xpin2)
            if "0" == xpin1:
                xpin1 = "GND"
            if "0" == xpin2:
                xpin2 = "GND"
            # convert results to string with engineering notation
            if Meas < 1 and "C" in Name: # Probably a cap
                Vtext = Meas * 1E6
                Ftxt = '{0:.3f} '.format(Vtext) + "uF"
                if Vtext < 0.001:
                    Vtext = Vtext * 1E6
                    Ftxt = '{0:.1f} '.format(Vtext) + "pF"
                else:
                    Vtext = Vtext * 1E3
                    Ftxt = '{0:.3f} '.format(Vtext) + "nF"
            if "R" in Name:
                Vtext = Meas
                if Vtext > 1000:
                    Vtext = Vtext / 1E3
                    Ftxt = '{0:.2f} '.format(Vtext) + "k"
                else:
                    Ftxt = '{0:.3f} '.format(Vtext) # + "nF"
            if (Meas > 0.9*Value) and (Meas < 1.1*Value):
                R_Line = Name + " Verified at " + xpin1 + " " + xpin2
                DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Name)
            elif DMeas == 1 and "D" in Name:
                R_Line = Name + " Verified at " + xpin1 + " " + xpin2
                DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Name)
            elif DMeas == -1 and "D" in Name:
                R_Line = Name + " Verified at " + xpin1 + " " + xpin2
                DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Name)
            elif DMeas == 0 and "D" in Name:
                R_Line = Name + " Found Open, Expected " + ValString
            else:
                R_Line = Name + " = " + Ftxt + " Expected " + ValString
        else: # Use Red 2 limited device checks
            if ("R" in Name) or ("C" in Name):
                if "V" in xpin1 or "V" in xpin2:
                    ResOn = CheckRes1(xpin1,xpin2)
                elif "0" == xpin1 or "COM" == xpin1 or "GND" == xpin1:
                    ResOn = CheckRes1(xpin1,xpin2)
                elif "0" == xpin2 or "COM" == xpin2 or "GND" == xpin2:
                    ResOn = CheckRes1(xpin1,xpin2)
                else:
                    ResOn, CapOn = CheckResCap2(xpin1,xpin2)
            elif "D" in Name:
                DMeas = CheckDiode2(xpin1,xpin2)
            #
            if "0" == xpin1:
                xpin1 = "GND"
            if "0" == xpin2:
                xpin2 = "GND"
            if ResOn == 1 or CapOn == 1:
                R_Line = Name + " Confirmed at " + xpin1 + " " + xpin2
                DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Name)
            elif DMeas == 1 and "D" in Name:
                R_Line = Name + " Confirmed at " + xpin1 + " " + xpin2
                DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Name)
            elif DMeas == -1 and "D" in Name:
                R_Line = Name + " Confirmed at " + xpin1 + " " + xpin2
                DrawCompOval(XStep, Xh1, Yh1, Xh2, Yh2, Name)
            elif DMeas == 0 and "D" in Name:
                R_Line = Name + " Found Open, Expected " + ValString
            else:
                R_Line = Name + " = Open, Expected " + ValString
        R_Line = R_Line + "\n"
        BOMtext.insert(END, R_Line)
        root.update()
##
#
def ScanTrans3(List_T):
    global ComponentList, BOMtext, FWRevOne
    global BBwidth, BBheight, BBGridSize, BL1XY

    # Calculate Xstep and YStep size for 50 X 40 0.1" grid, 11 pixels per grid point?
    XStep = BBwidth/BBGridSize
    MidY = (BL1XY[1] - 1) * XStep
    #
    for T in range (0, len(List_T), 1):
        Xh1 = Yh1 = Xh2 = Yh2 = Xh3 = Yh3 = GrNum = 0
        Tterm = List_T[T]
        Tname = Tterm[0]
        Tterm1 = Tterm[1]
        Tterm2 = Tterm[2]
        Tterm3 = Tterm[3]
        TVString = Tterm[5]
        # print(Rterm1, " " , Rterm2, " " , RValue)
        #
        xpin1 = Tterm1
        xpin2 = Tterm2
        xpin3 = Tterm3
        QBeta = QOff = QOn = 0
        MOn = MOff = 0
        BJT = "XXX"
        MOS = "XXXX"
        for xp in range (0, len(ComponentList), 1 ):
            if ("TR" in Tterm1) or ("BR" in Tterm1) or ("TL" in Tterm1) or ("BL" in Tterm1):
                xpin1 = Tterm1
            elif Tterm1 in ComponentList[xp]:
                CompPins = ComponentList[xp]
                xpin1 = CompPins[0]
                xpin1 = xpin1.replace("X","")
                xpin1 = xpin1.replace(chr(167),"")# remove §
            if ("TR" in Tterm2) or ("BR" in Tterm2) or ("TL" in Tterm2) or ("BL" in Tterm2):
                xpin2 = Tterm2
            elif Tterm2 in ComponentList[xp]:
                CompPins = ComponentList[xp]
                xpin2 = CompPins[0]
                xpin2 = xpin2.replace("X","")
                xpin2 = xpin2.replace(chr(167),"")# remove §
            if ("TR" in Tterm3) or ("BR" in Tterm3) or ("TL" in Tterm3) or ("BL" in Tterm3):
                xpin3 = Tterm3
            elif Tterm3 in ComponentList[xp]:
                CompPins = ComponentList[xp]
                xpin3 = CompPins[0]
                xpin3 = xpin3.replace("X","")
                xpin3 = xpin3.replace(chr(167),"")# remove §
            #
        # find comp pin locations on BB graphic
        Xh1, Yh1, GrNum = FindBBPin(xpin1, XStep)
        Xh2, Yh2, GrNum = FindBBPin(xpin2, XStep)
        Xh3, Yh3, GrNum = FindBBPin(xpin3, XStep)
        if "V" in xpin1:
            Xh1 = Xh2 - XStep
            Yh1 = Yh2 # + XStep
        if "V" in xpin3:
            Xh3 = Xh2 + XStep
            Yh3 = Yh2 # + XStep
        if "0" == xpin1 or "COM" == xpin1 or "GND" == xpin1:
            Xh1 = Xh2 - XStep
            Yh1 = Yh2 # + XStep
        if "0" == xpin3 or "COM" == xpin3 or "GND" == xpin3:
            Xh3 = Xh2 - XStep
            Yh3 = Yh2 # + XStep
        Xm = max([Xh1, Xh2, Xh3])
        Ym = max([Yh1, Yh2, Yh3])
        Xn = min([Xh1, Xh2, Xh3])
        Yn = min([Yh1, Yh2, Yh3])
        #
        if FWRevOne == "Red3": # Use Red 3 Hardware test resistors
            # Check if BJT or MOS
            if "Q" in Tname:
                # Check if NPN or PNP by B-E diode direction
                Polr = VerifyDiode2(xpin2, xpin3)
                if Polr == -1: # Found NPN
                    BJT = "NPN"
                elif Polr == 1: # Found PNP
                    BJT = "PNP"
                else:
                    BJT = "XXX"
                QBeta, QOff = VerifyBJT(xpin1, xpin2, xpin3, BJT)
            elif "M" in Tname:
                # Check if NMOS or PMOS by S-D diode direction
                Polr = VerifyDiode2(xpin1, xpin3)
                if Polr == 1: # Found NMOS
                    MOS = "NMOS"
                elif Polr == -1: # Found PMOS
                    MOS = "PMOS"
                else:
                    MOS = "XXXX"
                MOn, MOff = VerifyMOS(xpin1, xpin2, xpin3, MOS)
            #
            if "0" == xpin1:
                xpin1 = "GND"
            if "0" == xpin2:
                xpin2 = "GND"
            if "0" == xpin3:
                xpin3 = "GND"
            if QBeta > 10:
                R_Line = Tname + " " + BJT + " Verified at " + xpin1 + " " + xpin2 + " " + xpin3
                DrawCompOval(XStep, Xm, Ym, Xn, Yn, Tname)
            elif MOn == 1 and MOff == 1:
                R_Line = Tname + " " + MOS + " Verified at " + xpin1 + " " + xpin2 + " " + xpin3
                DrawCompOval(XStep, Xm, Ym, Xn, Yn, Tname)
            elif BJT == "XXX" and MOS == "XXXX":
                R_Line = Tname + " No Transistor Found at " + xpin1 + " " + xpin2 + " " + xpin3
            else:
                R_Line = Tname + " Found Open, Expected " + TVString
        else: # Use Red 2 limited device checks
            # Check if BJT or MOS FWRevOne = "Red2"
            if "Q" in Tname:
                # Check if NPN or PNP by E-B diode direction
                Polr = CheckDiode2(xpin2, xpin3)
                if Polr == 1: # Found NPN
                    BJT = "PNP"
                elif Polr == -1: # Found PNP
                    BJT = "NPN"
                else:
                    Polr = CheckDiode2(xpin3, xpin2)
                    if Polr == 1: # Found NPN
                        BJT = "NPN"
                    elif Polr == -1: # Found PNP
                        BJT = "PNP"
                    else:
                        BJT = "XXX"
                QOn, QOff = CheckBJT(xpin1, xpin2, xpin3, BJT)
            elif "M" in Tname:
                # Check if NMOS or PMOS by S-D diode direction
                Polr = CheckDiode2(xpin1, xpin3)
                if Polr == 1: # Found NMOS
                    MOS = "NMOS"
                elif Polr == -1: # Found PMOS
                    MOS = "PMOS"
                else:
                    MOS = "XXXX"
                MOn, MOff = CheckMOS(xpin1, xpin2, xpin3, MOS)
            #
            if "0" == xpin1:
                xpin1 = "GND"
            if "0" == xpin2:
                xpin2 = "GND"
            if "0" == xpin3:
                xpin3 = "GND"
            if QOn == 1 and QOff == 1:
                R_Line = Tname + " " + BJT + " Confirmed at " + xpin1 + " " + xpin2 + " " + xpin3
                DrawCompOval(XStep, Xm, Ym, Xn, Yn, Tname)
            elif MOn == 1 and MOff == 1:
                R_Line = Tname + " " + MOS + " Confirmed at " + xpin1 + " " + xpin2 + " " + xpin3
                DrawCompOval(XStep, Xm, Ym, Xn, Yn, Tname)
            elif BJT == "XXX" and MOS == "XXXX":
                R_Line = Tname + " No Transistor Found at " + xpin1 + " " + xpin2 + " " + xpin3
            else:
                R_Line = Tname + " Found Open, Expected " + TVString
        R_Line = R_Line + "\n"
        BOMtext.insert(END, R_Line)
        root.update()
#print(len(ComponentList))
def ScanPwrGnd():
    global ComponentList, VPower, VPowerConnections, VPlus, VMinus
    global BBwidth, BBheight, BBGridSize, BL1XY, BBblack
    
# look for power and GND wire connections
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(0)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 1
    # Show Power / GND wires if any
    XStep = YStep = BBwidth/BBGridSize
    HStep = int(XStep/2)
    PinW = int(0.3 * XStep)
    Xd = 6 * XStep
    Yd = 33 * XStep
    VPower_id = []
    WireColor = BBblack
    MidY = (BL1XY[1] - 1) * XStep
    #
    ser.write(b'x\n') # Reset all cross point switches to open
    # connect AINH input to measurement jumpers
    set_connection("JP16", "AINH", 1) #
    set_connection("JP1", "AINH", 1) #
    for xp in range (0, len(ComponentList), 1 ):
        CompPins = ComponentList[xp]
    # check if this cross point is connected to one of the possible Power rails
        for PWR in range ( 0, len(VPower), 1):
            Xh1 = Yh1 = Xh2 = Yh2 = WireFound = 0
            if VPower[PWR] in CompPins:
                Vpin = CompPins[0]
                Vpin = Vpin.replace("X","")
                Vpin = Vpin.replace(chr(167),"")# remove §
                VPowerConnections[PWR].append(Vpin)
                if Vpin != "BR17": # Can't test unused BB pin BR17
                    # print("Found ", VPower[PWR], " connected to ", Vpin)
                    Xh1, Yh1, GrNum = FindBBPin(Vpin, XStep)
                    if ("TR" in Vpin) or ("BR" in Vpin): # Rigth side BB
                        set_connection("JP16", Vpin, 1) # CH A input to BB pin
                    else:
                        set_connection("JP1", Vpin, 1) # CH A input to BB pin
                    time.sleep(0.01)
                    # get data
                    Get_Data()
                    VDCA = numpy.mean(VBuffA) # calculate average voltage
                    if "VDD" == VPower[PWR]:
                        Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
                        if Yh1 < MidY:
                            WireColor = "red"
                        else:
                            WireColor = "blue"
                        if VDCA > 4.3:
                            VPlus = VDCA
                            R_Line = "VDD Verified at " + Vpin
                            WireFound = 1
                            # print( "VPlus = ", VPlus)
                        else:
                            R_Line = Vpin + " Voltage =  " + str(VDCA) + " Expected VDD"
                            WireFound = 0
                    elif "0" == VPower[PWR] or "GND" == VPower[PWR]:
                        Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 1)
                        WireColor = BBblack
                        if VDCA > -0.1 and VDCA < 0.1:
                            R_Line = "GND Verified at " + Vpin
                            WireFound = 1
                        else:
                            R_Line = Vpin + " Voltage =  " + str(VDCA) + " Expected GND"
                            WireFound = 0
                    elif "VEE" == VPower[PWR]:
                        Xh1, Xh2, Yh1, Yh2 = FindPowerRail(Xh1, Xh2, Yh1, Yh2, MidY, GrNum, XStep, 0)
                        if Yh1 < MidY:
                            WireColor = "red"
                        else:
                            WireColor = "blue"
                        if VDCA < -4.3:
                            VMinus = VDCA
                            R_Line = "VEE Verified at " + Vpin
                            WireFound = 1
                            # print( "VMinus = ", VMinus)
                        else:
                            R_Line = Vpin + " Voltage =  " + str(VDCA) + " Expected VEE"
                            WireFound = 0
                    else:
                        R_Line = Vpin + " Found Open, Expected " + VPower[PWR]
                        WireFound = 0
                    R_Line = R_Line + "\n"
                    BOMtext.insert(END, R_Line)
                    if WireFound > 0:
                        MidLineX = abs(Xh1 + Xh2)/2
                        MidLineY = abs(Yh1 + Yh2)/2
                        PWRLine = [Xh1, Yh1, MidLineX+XStep, MidLineY, Xh2, Yh2]
                        Power_id = breadboard_canvas.create_line(PWRLine, smooth=TRUE, fill=WireColor, width=4)
                        VPower_id.append(Power_id)
                        Power_id = breadboard_canvas.create_oval(Xh1-2, Yh1-2, Xh1+2, Yh1+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                        VPower_id.append(Power_id)
                        Power_id = breadboard_canvas.create_oval(Xh2-2, Yh2-2, Xh2+2, Yh2+2, outline="#a0a0a0", fill="#a0a0a0", width=1)
                        VPower_id.append(Power_id)
                    if ("TR" in Vpin) or ("BR" in Vpin): # Rigth side BB
                        set_connection("JP16", Vpin, 0) # CH A input from BB pin
                    else:
                        set_connection("JP1", Vpin, 0) # CH A input from BB pin
                    root.update()
                else:
                    R_Line = "Can not check open BB pin BR17.\n"
                    BOMtext.insert(END, R_Line)
                    root.update()
    #
    ser.write(b'x\n') # Reset all cross point switches to open
#
def MeasVOpenCircuit():
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA, VBuffB
    global AWGBShape, AWGBAmplEntry, AWGBOffsetEntry, TRACESread
    global AwgAOnOffBt, AwgBOnOffBt, VOpenCircuit

    # Measure the open circuit voltage reading of Scope Channel(s)
    ser.write(b'x\n') # Reset all cross point switches to open
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 2
    time.sleep(0.01)
    # get data
    Get_Data()
    VOpenCircuit = numpy.mean(VBuffA) # calculate average voltage
    # print("Measured Scope Open Circuit Voltage = ", VOpenCircuit)
#
def VerifyComps():
    global VPower, UnRouted, RL_OneList, RR_OneList, RL_TwoList, RR_TwoList, CL_OneList
    global CR_OneList, CL_TwoList, CR_TwoList, DL_OneList, DR_OneList, DL_TwoList
    global DR_TwoList, QL_List, QR_List, UL_List, UR_List, PassFailSvBB
    global U_Connections, XCPList, ComponentList, VPowerConnections, SVB
    global BOMtext, BOMStatus, root, FWRevOne, VOpenCircuit, TMsb

    if BOMStatus.get() == 0:
        MakeBOMScreen()
    # Set time bas / sample rate
    TMsb.delete(0,"end")
    TMsb.insert(0,"1.0ms")
    BTime()
    PassFailSvBB.config(font="Arial 14 bold", foreground="green", text = "Running")
    MeasVOpenCircuit() # Measure the open circuit voltage reading of Scope Channel(s)
    ser.write(b'x\n') # Reset all cross point switches to open
    ser.write(b'? 1 0 0 0\n') # Disable test resistors
    # Clear text window
    BOMtext.delete("1.0", END)
    SVB = 1
    #
    #ParseNetlist2() # list of all subcircuit instances found
    # Check Power and GND wired BB connections
    ScanPwrGnd()
    # List Resistors
    ScanDev2(RL_TwoList)
    ScanDev2(RR_TwoList)
    # if FWRevOne == "Red3":
    ScanDev2(RL_OneList)
    ScanDev2(RR_OneList)
    # List Capacitors
    ScanDev2(CL_TwoList)
    ScanDev2(CR_TwoList)
    if FWRevOne == "Red3":
        ScanDev2(CL_OneList)
        ScanDev2(CR_OneList)
    # List Diodes
    ScanDev2(DL_TwoList)
    ScanDev2(DR_TwoList)
    #if FWRevOne == "Red3":
    ScanDev2(DL_OneList)
    ScanDev2(DR_OneList)
    # List Transistors
    ScanTrans3(QL_List)
    ScanTrans3(QR_List)
    #
    PassFailSvBB.config(font="Arial 14 bold", foreground="green", text = "Finished!")
    SVB = 0
#       
def VerifyRes2(Pin1, Pin2, TestR = "33k"):
    global ser, CompString, JumperString, OnOffString, NumConn, Vsys, VPlus
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA, VBuffB
    global AWGBShape, AWGBAmplEntry, AWGBOffsetEntry, TRACESread, VOpenCircuit
    global AwgAOnOffBt, AwgBOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open
    Rbot = "JP12"
    if TestR == "33k" or TestR == "24k":
        ser.write(b'? 0 0 0 0\n') # Enable test resistors
        if TestR == "33k":
            Rbot = "JP12" # JP12 for 33k JP10 for 24k
        else:
            Rbot = "JP10" # JP12 for 33k JP10 for 24k
    elif TestR == "3.9k" or TestR == "470":
        ser.write(b'? 0 1 1 1\n') # Enable test resistors
        if TestR == "3.9k":
            Rbot = "JP10" # JP10 for 3.9k JP12 for 470
        else:
            Rbot = "JP12" # JP10 for 3.9k JP12 for 470
    else:
        ser.write(b'? 0 0 0 0\n') # Enable test resistors
    TestValue = UnitConvert(TestR)
    TestValue = TestValue + 96 # add in switch resistance
    # Configure AWG channel A DC 4.0 V
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(0) # set awg wave to DC
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, 0.0)
    if "VDD" == Pin1 or "VDD" == Pin2 or "VEE" == Pin1 or "VEE" == Pin2:
        # for testing resistors not connected to GND
        AWGAOffsetEntry.delete(0,END)
        AWGAOffsetEntry.insert(0,0.0)
    else:
        AWGAOffsetEntry.delete(0,END)
        AWGAOffsetEntry.insert(0,4.0)
    # Configure AWG channel B DC 0.0 V
    AwgBOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgB_Ampl(255)
    AWGBShape.set(0) # set awg wave to DC
    AWGBAmplEntry.delete(0,END)
    AWGBAmplEntry.insert(0, 0.0)
    AWGBOffsetEntry.delete(0,END)
    AWGBOffsetEntry.insert(0,0.0)
    ## Send waveform
    MakeAWGwaves()
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 2
    #
    # Connect test BB pins to ADC and DAC
    if TestR == "33k" or TestR == "470":
        set_connection("JP14", "AINH", 1) # CH A input to top of test res
        set_connection("JP14", "AWG1", 1) # Awg 1 output to top of test res
    if TestR == "24k" or TestR == "3.9k":
        set_connection("JP13", "AINH", 1) # CH A input to top of test res
        set_connection("JP13", "AWG1", 1) # Awg 1 output to top of test res
    if ("TR" in Pin1) or ("BR" in Pin1) or ("TR" in Pin2) or ("BR" in Pin2): # Rigth side BB
        set_connection("JP16", Rbot, 1)
        set_connection("JP16", "BINH", 1)
        if "0" == Pin1 or "VDD" == Pin1 or "VEE" == Pin1 or "GND" == Pin1:
            set_connection("JP16", Pin2, 1) # top of Unknown to bottom of test res
        elif "0" == Pin2 or "VDD" == Pin2 or "VEE" == Pin2 or "GND" == Pin2:
            set_connection("JP16", Pin1, 1) # top of Unknown to bottom of test res
        else:
            set_connection("JP15", "AWG2", 1) # AWG 2 output to bottom of unknown
            set_connection("JP16", Pin1, 1) # top of Unknown to bottom of test res
            set_connection("JP15", Pin2, 1) # bottom of Unknown to bottom of test res
    else: # Left side BB
        set_connection("JP1", Rbot, 1)
        set_connection("JP1", "BINH", 1)
        if "0" == Pin1 or "VDD" == Pin1 or "VEE" == Pin1 or "GND" == Pin1:
            set_connection("JP1", Pin2, 1) # top of Unknown to bottom of test res
        elif "0" == Pin2 or "VDD" == Pin2 or "VEE" == Pin2 or "GND" == Pin2:
            set_connection("JP1", Pin1, 1) # top of Unknown to bottom of test res
        else:
            set_connection("JP2", "AWG2", 1) # AWG 2 output to bottom of unknown
            set_connection("JP1", Pin1, 1) # top of Unknown to bottom of test res
            set_connection("JP2", Pin2, 1) # bottom of Unknown to bottom of test res
    #
    time.sleep(0.05)
    # get data
    # print("Test Res = ", TestValue)
    if VPlus == 0:
        VPlus = Vsys + 0.25
    Get_Data()
    VDCA = numpy.mean(VBuffA) # calculate average voltage
    VDCB = numpy.mean(VBuffB) # calculate average voltage
    # Calculate Resistor Value
    if "VDD" == Pin1 or "VDD" == Pin2: # for testing resistors not connected to GND
        IDC = (VDCB-VDCA)/(TestValue) # Using test resisistor
        RMeas = ((VPlus-VDCB)/IDC)-48
    elif "VEE" == Pin1 or "VEE" == Pin2:
        IDC = (VDCB-VDCA)/(TestValue) # Using test resisistor
        RMeas = ((-5.2-VDCB)/IDC)-48
    elif "0" == Pin1 or "0" == Pin2 or "GND" == Pin1 or "GND" == Pin2:
        IDC = (VDCA-VDCB)/(TestValue) # Using test resisistor
        RMeas = (VDCB/IDC)-50
    else:
        IDC = (VDCA-VDCB)/(TestValue) # Using test resisistor
        RMeas = (VDCB/IDC)-158 # subtract aprox switch resistance
    # Disconnect test pins
    ResetMatrix(1) # Reset all cross point switches to open
    #ser.write(b'? 1 0 0 0\n') # Disable test resistors
    #
    return(RMeas)
## print(VerifyCap2("TR11", "BR11"))
def VerifyCap2(Pin1, Pin2, TestR = "24k", TestF = 500):
    global ser, CompString, JumperString, OnOffString, NumConn
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA, VBuffB
    global AWGBShape, AWGBAmplEntry, AWGBOffsetEntry, AWGAFreqEntry, DCV1, DCV2
    global AwgAOnOffBt, AwgBOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open
    Rbot = "JP12"
    if TestR == "33k" or TestR == "24k":
        ser.write(b'? 0 0 0 0\n') # Enable test resistors
        if TestR == "33k":
            Rbot = "JP12" # JP12 for 33k JP10 for 24k
        else:
            Rbot = "JP10" # JP12 for 33k JP10 for 24k
    elif TestR == "3.9k" or TestR == "470":
        ser.write(b'? 0 1 1 1\n') # Enable test resistors
        if TestR == "3.9k":
            Rbot = "JP10" # JP10 for 3.9k JP12 for 470
        else:
            Rbot = "JP12" # JP10 for 3.9k JP12 for 470
    else:
        ser.write(b'? 0 0 0 0\n') # Enable test resistors
    TestValue = UnitConvert(TestR)
    # Configure AWG channel A Sine 4.0 V P-P
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(1) # set awg wave to Sine
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, -2.0)
    AWGAOffsetEntry.delete(0, END)
    AWGAOffsetEntry.insert(0, 2.0)
    AWGAFreqEntry.delete(0,END)
    AWGAFreqEntry.insert(4, TestF) # Set test Freq to 500 Hz
    # Configure AWG channel B DC 0.0 V
    AwgBOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgB_Ampl(255)
    AWGBShape.set(0) # set awg wave to DC
    AWGBAmplEntry.delete(0,END)
    AWGBAmplEntry.insert(0, 0.0)
    AWGBOffsetEntry.delete(0,END)
    AWGBOffsetEntry.insert(0,0.0)
    ## Send waveform
    MakeAWGwaves()
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 2
    ## Connect test BB pins to ADC and DAC
    # JP14 for 33k JP13 for 24k
    if TestR == "33k" or TestR == "470":
        set_connection("JP14", "AINH", 1) # CH A input to top of test res
        set_connection("JP14", "AWG1", 1) # Awg 1 output to top of test res
    if TestR == "24k" or TestR == "3.9k":
        set_connection("JP13", "AINH", 1) # CH A input to top of test res
        set_connection("JP13", "AWG1", 1) # Awg 1 output to top of test res
    if ("TR" in Pin1) or ("BR" in Pin1) or ("TR" in Pin2) or ("BR" in Pin2): # Rigth side BB
        set_connection("JP16", Rbot, 1)
        set_connection("JP16", "BINH", 1)
        if "0" == Pin1 or "VDD" == Pin1 or "VEE" == Pin1:
            set_connection("JP16", Pin2, 1) # top of Unknown to bottom of test res
        elif "0" == Pin2 or "VDD" == Pin2 or "VEE" == Pin2:
            set_connection("JP16", Pin1, 1) # top of Unknown to bottom of test res
        else:
            set_connection("JP15", "AWG2", 1) # AWG 2 output to bottom of unknown
            set_connection("JP16", Pin1, 1) # top of Unknown to bottom of test res
            set_connection("JP15", Pin2, 1) # bottom of Unknown to bottom of test res
    else: # Left side BB
        set_connection("JP1", Rbot, 1)
        set_connection("JP1", "BINH", 1)
        if "0" == Pin1 or "VDD" == Pin1 or "VEE" == Pin1:
            set_connection("JP1", Pin2, 1) # top of Unknown to bottom of test res
        elif "0" == Pin2 or "VDD" == Pin2 or "VEE" == Pin2:
            set_connection("JP1", Pin1, 1) # top of Unknown to bottom of test res
        else:
            set_connection("JP2", "AWG2", 1) # AWG 2 output to bottom of unknown
            set_connection("JP1", Pin1, 1) # top of Unknown to bottom of test res
            set_connection("JP2", Pin2, 1) # bottom of Unknown to bottom of test res
    #
    if TestValue == 470:
        time.sleep(0.2)
    else:
        time.sleep(0.1)
    # get data
    Get_Data()
    # print("TestValue = ", TestValue)
    # print("TestF = ", TestF)
    DCV1 = numpy.mean(VBuffA) # calculate average voltage
    DCV2 = numpy.mean(VBuffB) # calculate average voltage
    VrmsAB = numpy.sqrt(numpy.mean(numpy.square(VBuffA-VBuffB)))
    VrmsB = numpy.sqrt(numpy.mean(numpy.square(VBuffB-DCV2)))
    # PhaseAB = Sine_Phase()
    if "VDD" == Pin1 or "VDD" == Pin2: # for testing resistors not connected to GND
        RSw = 48
    elif "VEE" == Pin1 or "VEE" == Pin2:
        RSw = 48
    elif "0" == Pin1 or "0" == Pin2 or "GND" == Pin1 or "GND" == Pin2:
        RSw = 50
    else:
        if TestValue == 470:
            RSw = 100
        else:
            RSw = 96
    # Calculate Capacitor Value
    # print("TestValue = ", TestValue)
    IAC = (VrmsAB)/(TestValue+96) # Using 33k test resisistor
    RMeas = (VrmsB/IAC)-RSw
    #print("VrmsAB = ", VrmsAB) print("VrmsB = ", VrmsB) print("IAC = ", IAC) print("RMeas = ", RMeas)
    try:
        CMeas = 1 / ( 2 * math.pi * TestF * RMeas ) # in farads
    except:
        CMeas = 0
    # print("CMeas = ", CMeas)
    CMeas = CMeas - 1.5e-10 # subtract paracitic cap?
    # Disconnect test pins
    ResetMatrix(1)# Reset all cross point switches to open
    ser.write(b'? 1 0 0 0\n') # Disable test resistors
    #
    return(CMeas)
#
## print(VerifyDiode2("TR10", "VDD"))
def VerifyDiode2(Pin1, Pin2, TestR = "3.9k", TestF = 500):
    global ser, CompString, JumperString, OnOffString, NumConn
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA, VBuffB
    global AWGBShape, AWGBAmplEntry, AWGBOffsetEntry, AWGAFreqEntry, DCV1, DCV2
    global AwgAOnOffBt, AwgBOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open
    Rbot = "JP12"
    if TestR == "33k" or TestR == "24k":
        ser.write(b'? 0 0 0 0\n') # Enable test resistors
        if TestR == "33k":
            Rbot = "JP12" # JP12 for 33k JP10 for 24k
        else:
            Rbot = "JP10" # JP12 for 33k JP10 for 24k
    elif TestR == "3.9k" or TestR == "470":
        ser.write(b'? 0 1 1 1\n') # Enable test resistors
        if TestR == "3.9k":
            Rbot = "JP10" # JP10 for 3.9k JP12 for 470
        else:
            Rbot = "JP12" # JP10 for 3.9k JP12 for 470
    else:
        ser.write(b'? 0 0 0 0\n') # Enable test resistors
    TestValue = UnitConvert(TestR)
    # Configure AWG channel A Sine 4.0 V P-P
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(1) # set awg wave to Sine
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, -2.0)
    AWGAOffsetEntry.delete(0,END)
    AWGAOffsetEntry.insert(0,2.0)
    AWGAFreqEntry.delete(0,END)
    AWGAFreqEntry.insert(4, TestF) # Set test Freq to 500 Hz
    # Configure AWG channel B DC 0.0 V
    AwgBOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgB_Ampl(255)
    AWGBShape.set(0) # set awg wave to DC
    AWGBAmplEntry.delete(0,END)
    AWGBAmplEntry.insert(0, 0.0)
    AWGBOffsetEntry.delete(0,END)
    AWGBOffsetEntry.insert(0,0.0)
    ## Send waveform
    MakeAWGwaves()
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 2
    #
    # Connect test BB pins to ADC and DAC
    # JP14 for 33k JP13 for 24k
    set_connection("JP13", "AINH", 1) # CH A input to top of test res
    set_connection("JP13", "AWG1", 1) # Awg 1 output to top of test res

    if ("TR" in Pin1) or ("BR" in Pin1) or ("TR" in Pin2) or ("BR" in Pin2): # Rigth side BB
        set_connection("JP16", Rbot, 1)
        set_connection("JP16", "BINH", 1)
        if "0" == Pin1 or "VDD" == Pin1 or "VEE" == Pin1:
            set_connection("JP16", Pin2, 1) # top of Unknown to bottom of test res
        elif "0" == Pin2 or "VDD" == Pin2 or "VEE" == Pin2:
            set_connection("JP16", Pin1, 1) # top of Unknown to bottom of test res
        else:
            set_connection("JP15", "AWG2", 1) # AWG 2 output to bottom of unknown
            set_connection("JP16", Pin1, 1) # top of Unknown to bottom of test res
            set_connection("JP15", Pin2, 1) # bottom of Unknown to bottom of test res
    else: # Left side BB
        set_connection("JP1", Rbot, 1)
        set_connection("JP1", "BINH", 1)
        if "0" == Pin1 or "VDD" == Pin1 or "VEE" == Pin1:
            set_connection("JP1", Pin2, 1) # top of Unknown to bottom of test res
        elif "0" == Pin2 or "VDD" == Pin2 or "VEE" == Pin2:
            set_connection("JP1", Pin1, 1) # top of Unknown to bottom of test res
        else:
            set_connection("JP2", "AWG2", 1) # AWG 2 output to bottom of unknown
            set_connection("JP1", Pin1, 1) # top of Unknown to bottom of test res
            set_connection("JP2", Pin2, 1) # bottom of Unknown to bottom of test res
    #
    time.sleep(0.1)
    # get data
    Get_Data()
##    VDCA = numpy.mean(VBuffA)
##    VMaxA = numpy.max(VBuffA)
##    VMinA = numpy.min(VBuffA)
##    VppA = VMaxA - VMinA
    VDCB = numpy.mean(VBuffB)
    VMaxB = numpy.max(VBuffB)
    VMinB = numpy.min(VBuffB)
    VppB = VMaxB - VMinB
##    print("DC B = ", VDCB)
##    print("Max B = ", VMaxB)
##    print("Min B = ", VMinB)
##    print("P-P B = ", VppB)
    #
    DiodeAK = 0
    if VMaxB > 1.5 and VMinB > -0.8:
        DiodeAK = 1
    elif VMaxB < 0.8 and VMinB < -1.5:
        DiodeAK = -1
    else:
        DiodeAK = 0
    # Disconnect test pins
    ResetMatrix(1) # Reset all cross point switches to open
    ser.write(b'? 1 0 0 0\n') # Disable test resistors
    #
    return(DiodeAK)
# print(VerifyBJT( "BR2", "BR3", "BR4", "NPN" ))
# print(VerifyBJT( "TL10", "TL11", "TL12", "PNP" ))
def VerifyBJT( Col, Base, Emit, BJT ):
    global ser, CompString, JumperString, OnOffString, NumConn, VOpenCircuit
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA, VBuffB
    global AWGBShape, AWGBAmplEntry, AWGBOffsetEntry, AWGAFreqEntry, DCV1, DCV2
    global AwgAOnOffBt, AwgBOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open
    if BJT == "NPN":
        Emit_V = 0.00
        Base_V = 3.0
        Col_V = 3.5
        ser.write(b'? 0 0 1 0\n') # Enable test resistors Col Res to + 5
    elif BJT == "PNP":
        Emit_V = 4.0
        Base_V = 1.0
        Col_V = 1.1
        ser.write(b'? 0 0 0 0\n') # Enable test resistors Col Res to GND
    else:
        return( -1, -1 )
    EmitRes = 100
    # connect collector, base, emitter to jumpers
    if "TL" in Col or "BL" in Col:
        ColJp = "JP1"
    else:
        ColJp = "JP11"
    #
    if "TL" in Base or "BL" in Base:
        BaseJp = "JP2"
    else:
        BaseJp = "JP12"
    #
    if "TL" in Emit or "BL" in Emit:
        EmitJp = "JP3"
        EmitRes = 108
    else:
        EmitJp = "JP16"
        EmitRes = 100
    set_connection(ColJp, Col, 1)
    set_connection(BaseJp, Base, 1)
    set_connection(EmitJp, Emit, 1)
    # Set AWG1 to DC Emitter voltage
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(0) # set awg wave to DC
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, 0.0)
    AWGAOffsetEntry.delete(0,END)
    AWGAOffsetEntry.insert(0, Emit_V)
    # Set AWG2 to DC Base voltage
    AwgBOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgB_Ampl(255)
    AWGBShape.set(0) # set awg wave to DC
    AWGBAmplEntry.delete(0,END)
    AWGBAmplEntry.insert(0, 0.0)
    AWGBOffsetEntry.delete(0,END)
    AWGBOffsetEntry.insert(0, Base_V)
    ## Send waveform
    MakeAWGwaves()
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(1)
    SelectChannels()
    # print(ColJp, BaseJp, EmitJp)
    # Connect Scope Channel A to Base jumper
    set_connection("JP2", "JP12", 1)
    # set_connection("JP2", BaseJp, 1)
    set_connection("JP2", "AINH", 1)
    # Connect Scope Channel B to collector jumper
    set_connection("JP1", "JP11", 1)
    # set_connection("JP1", ColJp, 1)
    set_connection("JP1", "BINH", 1)
    # Connect Scope AWG1 to Emitter jumper
    set_connection(EmitJp, "AWG1", 1)
    if EmitJp == "JP3":
        set_connection("JP4", "CINH", 1)
        set_connection("JP4", Emit, 1)
    else:
        set_connection("JP15", "CINH", 1)
        set_connection("JP15", Emit, 1)
    # Connect Scope AWG2 to Base resistor jumper
    set_connection("JP14", "AWG2", 1)
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VBase = numpy.mean(VBuffA)
    VCol = numpy.mean(VBuffB)
    VEmit = numpy.mean(VBuffC)
    VBE = VBase - VEmit
    BJTOn = 0
    BJTOff = 0
    # print("Base = ", VBase, "Col = ", VCol, "Emit = ", VEmit, "VBE = ", VBE)
    if BJT == "NPN":
        IC = VEmit / EmitRes # IE ~= IC
        IB = (3.0 - VBase) / 33100
        Beta = int(IC/IB)
        if VBE > 0.55 and VCol < Col_V:
            BJTOn = Beta
        else:
            BJTOn = 0
    else:
        IC = VCol / 270 #
        IB = (VBase - 1.0) / 33100
        Beta = int(IC/IB)
        if VBE < -0.55 and VCol > Col_V:
            BJTOn = Beta
        else:
            BJTOn = 0
##    else:
##        if VBase < Base_V and VCol > Col_V:
##            BJTOn = 1
##        else:
##            BJTOn = 0
    # Connect Open to Base
    set_connection(BaseJp, Base, 0)
    if EmitJp == "JP3":
        set_connection("JP3", Base, 1) # Connect Base to Emitter for Off
    else:
        set_connection("JP15", Base, 1) # Connect Base to Emitter for Off
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VBase = numpy.mean(VBuffA)
    VCol = numpy.mean(VBuffB)
    VEmit = numpy.mean(VBuffC)
    VBE = VBase - VEmit
    # print("Base = ", VBase, "Collector = ", VCol, "Emitter = ", VEmit)
    if BJT == "NPN":
        if VBase > VOpenCircuit and VCol > 4.0:
            BJTOff = 1
        else:
            BJTOff = 0
    else:
        if VBase > VOpenCircuit and VCol < 1.0:
            BJTOff = 1
        else:
            BJTOff = 0
    #
    ResetMatrix(1) # Reset all cross point switches to open
    ser.write(b'? 1 0 0 0\n') # Disable test resistors
    #
    return(BJTOn, BJTOff)
# print(VerifyMOS("BR2", "BR3", "BR4", "NMOS"))
def VerifyMOS( Drain, Gate, Source, MOS ):
    global ser, CompString, JumperString, OnOffString, NumConn
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA, VBuffB
    global AWGBShape, AWGBAmplEntry, AWGBOffsetEntry, AWGAFreqEntry, DCV1, DCV2
    global AwgAOnOffBt, AwgBOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open
    if MOS == "NMOS":
        Sour_V = 0.00
        Gate_V = 3.5
        Drain_V = 3.0
        ser.write(b'? 0 0 1 0\n') # Enable test resistors Drain Res to + 5
    elif MOS == "PMOS":
        Sour_V = 4.0
        Gate_V = -0.5
        Drain_V = 1.0
        ser.write(b'? 0 0 0 0\n') # Enable test resistors Drain Res to GND
    else:
        return( -1, -1 )
    SourRes = 100
    # connect Drain, Gate, Source to jumpers
    if "TL" in Drain or "BL" in Drain:
        DrnJp = "JP1"
    else:
        DrnJp = "JP11"
    #
    if "TL" in Gate or "BL" in Gate:
        GateJp = "JP2"
    else:
        GateJp = "JP12"
    #
    if "TL" in Source or "BL" in Source:
        SourJp = "JP3"
        SourRes = 108
    else:
        SourJp = "JP16"
        SourRes = 100
    set_connection(DrnJp, Drain, 1)
    set_connection(GateJp, Gate, 1)
    set_connection(SourJp, Source, 1)
    # Set AWG1 to DC Emitter voltage
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(0) # set awg wave to DC
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, 0.0)
    AWGAOffsetEntry.delete(0,END)
    AWGAOffsetEntry.insert(0, Sour_V)
    # Set AWG2 to DC Base voltage
    AwgBOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgB_Ampl(255)
    AWGBShape.set(0) # set awg wave to DC
    AWGBAmplEntry.delete(0,END)
    AWGBAmplEntry.insert(0, 0.0)
    AWGBOffsetEntry.delete(0,END)
    AWGBOffsetEntry.insert(0, Gate_V)
    ## Send waveform
    MakeAWGwaves()
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(1)
    SelectChannels()
    
    # print(DrnJp, GateJp, SourJp)
    # Connect Scope Channel A to Base jumper
    set_connection("JP2", "JP12", 1)
    # set_connection("JP2", GateJp, 1)
    set_connection("JP2", "AINH", 1)
    # Connect Scope Channel B to collector jumper
    set_connection("JP1", "JP11", 1)
    # set_connection("JP1", DrnJp, 1)
    set_connection("JP1", "BINH", 1)
    # Connect Scope AWG1 to Emitter jumper
    set_connection(SourJp, "AWG1", 1)
    if SourJp == "JP3":
        set_connection("JP4", "CINH", 1)
        set_connection("JP4", Source, 1)
    else:
        set_connection("JP15", "CINH", 1)
        set_connection("JP15", Source, 1)
    # Connect Scope AWG2 to Base resistor jumper
    set_connection("JP14", "AWG2", 1)
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VGate = numpy.mean(VBuffA)
    VDrain = numpy.mean(VBuffB)
    VSource = numpy.mean(VBuffC)
    MOSOn = 0
    MOSOff = 0
    # print("Gate = ", VGate, "Drain = ", VDrain, "Source = ", VSource)
    if MOS == "NMOS":
        if VDrain < Drain_V:
            MOSOn = 1
        else:
            MOSOn = 0
    else:
        if VDrain > Drain_V:
            MOSOn = 1
        else:
            MOSOn = 0
    # Connect Open to Base
    set_connection(GateJp, Gate, 0)
    if SourJp == "JP3":
        set_connection("JP3", Gate, 1) # Connect Gate to Source for Off
    else:
        set_connection("JP15", Gate, 1) # Connect Gate to Source for Off
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VGate = numpy.mean(VBuffA)
    VDrain = numpy.mean(VBuffB)
    VSource = numpy.mean(VBuffC)
    # print("Gate = ", VGate, "Drain = ", VDrain, "Source = ", VSource)
    if MOS == "NMOS":
        if VDrain > 4.0:
            MOSOff = 1
        else:
            MOSOff = 0
    else:
        if VDrain < 1.0:
            MOSOff = 1
        else:
            MOSOff = 0
    #
    ResetMatrix(1) # Reset all cross point switches to open
    ser.write(b'? 1 0 0 0\n') # Disable test resistors
    #
    return(MOSOn, MOSOff)
# print(CheckBJT("BL10", "BL11", "BL12", "NPN"))
# FWRevOne = "Red2"
def CheckBJT( Col, Base, Emit, BJT ):
    global ser, CompString, JumperString, OnOffString, NumConn
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA
    global AwgAOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open
    # connect collector, base, emitter to jumpers
    if "TL" in Col or "BL" in Col:
        ColJp = "JP1"
    else:
        ColJp = "JP16"
    #
    if "TL" in Base or "BL" in Base:
        BaseJp = "JP2"
    else:
        BaseJp = "JP15"
    #
    if "TL" in Emit or "BL" in Emit:
        EmitJp = "JP3"
    else:
        EmitJp = "JP14"
    set_connection(ColJp, Col, 1)
    set_connection(BaseJp, Base, 1)
    set_connection(EmitJp, Emit, 1)
    if BJT == "NPN":
        Emit_V = "0.0"
        Base_V = 0.5
        Col_V = 0.1
    else:
        Emit_V = "4.0"
        Base_V = 3.6
        Col_V = 3.9
    # Set AWG1 to DC 0 V
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(0) # set awg wave to DC
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, 0.0)
    AWGAOffsetEntry.delete(0,END)
    AWGAOffsetEntry.insert(0, Emit_V)
    ## Send waveform
    MakeAWGwaves()
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(0)
    SelectChannels()
    # Connect Scope Channel A and C to drive Base jumper
    set_connection(BaseJp, "AINH", 1)
    set_connection(BaseJp, "CINH", 1)
    # Connect Scope Channel B to collector jumper
    set_connection(ColJp, "BINH", 1)
    # Connect Scope AWG1 to Emitter jumper
    set_connection(EmitJp, "AWG1", 1)
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VBase = numpy.mean(VBuffA)
    VCol = numpy.mean(VBuffB)
    #print("VBase = ", VBase)
    #print("VCol = ", VCol)
    BJTOn = 0
    BJTOff = 0
    if BJT == "NPN":
        if VBase > Base_V and VCol < Col_V:
            BJTOn = 1
        else:
            BJTOn = 0
    else:
        if VBase < Base_V and VCol > Col_V:
            BJTOn = 1
        else:
            BJTOn = 0
    # Connect Open to Base
    set_connection(BaseJp, "AINH", 0)
    # Connect Base to Emitter
    set_connection(EmitJp, Base, 1)
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VBase = numpy.mean(VBuffA)
    VCol = numpy.mean(VBuffB)
    #print("VBase = ", VBase)
    #print("VCol = ", VCol)
    if VBase > (VOpenCircuit-0.1) and VCol > (VOpenCircuit-0.1) and VBase < (VOpenCircuit+0.2) and VCol < (VOpenCircuit+0.2):
        BJTOff = 1
    else:
        BJTOff = 0
    #
    ResetMatrix(1) # Reset all cross point switches to open
    #
    return(BJTOn, BJTOff)
# print(CheckMOS("BR2", "BR3", "BR4", "NMOS"))
def CheckMOS( Drain, Gate, Source, MOS ):
    global ser, CompString, JumperString, OnOffString, NumConn, VOpenCircuit
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA, VBuffB
    global AWGBShape, AWGBAmplEntry, AWGBOffsetEntry, AWGAFreqEntry, DCV1, DCV2
    global AwgAOnOffBt, AwgBOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open
    # connect drain, gate, source to jumpers
    if "TL" in Drain or "BL" in Drain:
        DrnJp = "JP1"
    else:
        DrnJp = "JP16"
    #
    if "TL" in Gate or "BL" in Gate:
        GateJp = "JP2"
    else:
        GateJp = "JP15"
    #
    if "TL" in Source or "BL" in Source:
        SourJp = "JP3"
    else:
        SourJp = "JP14"
    set_connection(DrnJp, Drain, 1)
    set_connection(GateJp, Gate, 1)
    set_connection(SourJp, Source, 1)
    if MOS == "NMOS":
        Sour_V = 0.00
        Gate_V = 4.0
        Drain_V = 0.5
    elif MOS == "PMOS":
        Sour_V = 4.0
        Gate_V = 0.0
        Drain_V = 3.5
    else:
        return( -1, -1 )
    SourRes = 100
    # Set AWG1 to DC Source voltage
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(0) # set awg wave to DC
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, 0.0)
    AWGAOffsetEntry.delete(0,END)
    AWGAOffsetEntry.insert(0, Sour_V)
    # Set AWG2 to DC Gate voltage
    AwgBOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgB_Ampl(255)
    AWGBShape.set(0) # set awg wave to DC
    AWGBAmplEntry.delete(0,END)
    AWGBAmplEntry.insert(0, 0.0)
    AWGBOffsetEntry.delete(0,END)
    AWGBOffsetEntry.insert(0, Gate_V)
    ## Send waveform
    MakeAWGwaves()
    # Select Scope Channel A and B
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    ShowC3_V.set(0)
    SelectChannels()
    # Connect Scope Channel A to Base jumper
    set_connection(GateJp, "AINH", 1)
    # Connect Scope Channel B to collector jumper
    set_connection(DrnJp, "BINH", 1)
    # Connect AWG1 to Source jumper
    set_connection(SourJp, "AWG1", 1)
    # Connect Scope AWG2 to Gate jumper
    set_connection(GateJp, "AWG2", 1)
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VGate = numpy.mean(VBuffA)
    VDrain = numpy.mean(VBuffB)
    #print("VGate = ", VGate)
    #print("VDrain = ", VDrain)
    MosOn = 0
    MosOff = 0
    if MOS == "NMOS":
        if VDrain < Drain_V:
            MosOn = 1
        else:
            MosOn = 0
    else:
        if VDrain > Drain_V:
            MosOn = 1
        else:
            MosOn = 0
    # Connect Open to Gate
    set_connection(GateJp, "AWG2", 0)
    # Short Gate to source
    set_connection(SourJp, Gate, 1)
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VGate = numpy.mean(VBuffA)
    VDrain = numpy.mean(VBuffB)
    #print("VGate = ", VGate)
    #print("VDrain = ", VDrain)
    if VDrain > (VOpenCircuit-0.1) and VDrain < (VOpenCircuit+0.2):
        MosOff = 1
    else:
        MosOff = 0
    #
    ResetMatrix(1) # Reset all cross point switches to open
    #
    return(MosOn, MosOff)
#
def CheckRes1( Pin1, Pin2): # Check devices with one pin connected to a power rail
    global ser, CompString, JumperString, OnOffString, NumConn
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA
    global AwgAOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open
    ResOn = 0
    if ("TR" in Pin1) or ("BR" in Pin1): # Rigth side BB
        set_connection("JP16", Pin1, 1) # CH A input to BB pin
        set_connection("JP16", "AINH", 1)
    elif ("TL" in Pin1) or ("BL" in Pin1): # Left side BB
        set_connection("JP1", Pin1, 1) # CH A input to BB pin
        set_connection("JP1", "AINH", 1)
    if ("TR" in Pin2) or ("BR" in Pin2): # Rigth side BB
        set_connection("JP16", Pin2, 1) # CH A input to BB pin
        set_connection("JP16", "AINH", 1)
    elif ("TL" in Pin2) or ("BL" in Pin2): # Left side BB
        set_connection("JP1", Pin2, 1) # CH A input to BB pin
        set_connection("JP1", "AINH", 1)
    time.sleep(0.01)
    # get data
    Get_Data()
    VDCA = numpy.mean(VBuffA) # calculate average voltage
    if "VDD" in Pin1 or "VDD" in Pin2:
        if VDCA > 2.6:
            ResOn = 1
    if "VEE" in Pin1 or "VEE" in Pin2:
        if VDCA < -2.6:
            ResOn = 1
    if "0" in Pin1 or "0" in Pin2 or "GND" in Pin1 or "GND" in Pin2:
        if VDCA < 2.3 and VDCA > -2.3:
            ResOn = 1
    # Disconnect test pins
    ResetMatrix(1) # Reset all cross point switches to open
    #
    return(ResOn)
#    
def CheckResCap2( Pin1, Pin2 ):
    global ser, CompString, JumperString, OnOffString, NumConn
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA
    global AwgAOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open        
    # Configure AWG channel A DC 4.0 V
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(1) # set awg wave to sine
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, 0.0)
    AWGAOffsetEntry.delete(0,END)
    AWGAOffsetEntry.insert(0,1.0)
    AWGAFreqEntry.delete(0,END)
    AWGAFreqEntry.insert(4, 500)
    ## Send waveform
    MakeAWGwaves()
    # Select just Scope Channel A
    ShowC1_V.set(1)
    ShowC2_V.set(0)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 1
    #
    # connect two pins to jumpers
    if "TL" in Pin1 or "BL" in Pin1 or "TL" in Pin2 or "BL" in Pin2:
        adc_jumper = "JP1"
        dac_jumper = "JP2"
    else:
        adc_jumper = "JP16"
        dac_jumper = "JP15"
    #
    # Connect test BB pin to ADC and DAC
    set_connection(adc_jumper, "AINH", 1)
    set_connection(dac_jumper, "AWG1", 1)
    set_connection(adc_jumper, Pin1, 1)
    set_connection(dac_jumper, Pin2, 1)
    #
    time.sleep(0.01)
    # get data
    Get_Data()
    VDC = numpy.mean(VBuffA)
    VMax = numpy.max(VBuffA)
    VMin = numpy.min(VBuffA)
    Vpp = VMax - VMin
    #
    ResOn = 0
    CapOn = 0
    if Vpp < 1.1 and Vpp > 0.9:
        if VDC > 0.45 and VDC < 0.65:
            ResOn = 1
            CapOn = 0
        else:
            ResOn = 0
            CapOn = 1
    # Disconnect test pins
    ResetMatrix(1) # Reset all cross point switches to open
    #
    return(ResOn, CapOn)
# print(CheckDiode2("BL11","BL12"))
def CheckDiode2( Pin1, Pin2 ):
    global ser, CompString, JumperString, OnOffString, NumConn, VOpenCircuit
    global AWGAShape, AWGAAmplEntry, AWGAOffsetEntry, root, VBuffA
    global AwgAOnOffBt, FailedPins, ShowC1_V, ShowC2_V, ShowC3_V

    ResetMatrix(1) # Reset all cross point switches to open        
    # Configure AWG channel A DC 4.0 V
    AwgAOnOffBt.config(text='ON', style="Run.TButton")
    SetAwgA_Ampl(255)
    AWGAShape.set(1) # set awg wave to sine
    AWGAAmplEntry.delete(0,END)
    AWGAAmplEntry.insert(0, 1.5)
    AWGAOffsetEntry.delete(0,END)
    AWGAOffsetEntry.insert(0,3.5)
    AWGAFreqEntry.delete(0,END)
    AWGAFreqEntry.insert(4, 500)
    ## Send waveform
    MakeAWGwaves()
    # Select just Scope Channel A
    ShowC1_V.set(1)
    ShowC2_V.set(0)
    ShowC3_V.set(0)
    SelectChannels()
    TRACESread = 1
    DiodeAK = 0
    #
    if "VDD" in Pin1 or "VDD" in Pin2: # One end of diode connected to VDD
        set_connection("JP1", "AINH", 1) # Use input divider as 1 Meg load
        set_connection("JP1", "BINH", 1) # Use input divider as 1 Meg load
        set_connection("JP1", "CINH", 1) # Use input divider as 1 Meg load
        if "VDD" in Pin1:
            set_connection("JP1", Pin2, 1) # Use to Measure voltage on diode
        else:
            set_connection("JP1", Pin1, 1) # Use to Measure voltage on diode
        time.sleep(0.01)
        # get data
        Get_Data()
        VDC = numpy.mean(VBuffA)
        if VDC > VOpenCircuit:
            DiodeAK = 1
        #
    elif "VEE" in Pin1 or "VEE" in Pin2 or "0" in Pin1 or "0" in Pin2: # One end of diode connected to VDD
        set_connection("JP1", "AINH", 1) # Use input divider as 1 Meg load
        set_connection("JP1", "BINH", 1) # Use input divider as 1 Meg load
        set_connection("JP1", "CINH", 1) # Use input divider as 1 Meg load
        if "VEE" in Pin1 or "0" in Pin1:
            set_connection("JP1", Pin2, 1) # Use to Measure voltage on diode
        else:
            set_connection("JP1", Pin1, 1) # Use to Measure voltage on diode
        time.sleep(0.01)
        # get data
        Get_Data()
        VDC = numpy.mean(VBuffA)
        if VDC < VOpenCircuit-0.1:
            DiodeAK = -1
        #
    else: # connect two pins to jumpers
        if "TL" in Pin1 or "BL" in Pin1 or "TL" in Pin2 or "BL" in Pin2:
            adc_jumper = "JP1"
            dac_jumper = "JP2"
        else:
            adc_jumper = "JP16"
            dac_jumper = "JP15"
        #
        # Connect test BB pin to ADC and DAC
        set_connection(adc_jumper, "AINH", 1) # Use input divider as load
        set_connection(adc_jumper, "CINH", 1) # Use input divider as load
        set_connection(dac_jumper, "AWG1", 1)
        set_connection(adc_jumper, Pin1, 1)
        set_connection(dac_jumper, Pin2, 1)
        #
        time.sleep(0.01)
        # get data
        Get_Data()
        VDC = numpy.mean(VBuffA)
        VMax = numpy.max(VBuffA)
        VMin = numpy.min(VBuffA)
        Vpp = VMax - VMin
        # print("VDC = ",VDC)
        # print("VMax = ",VMax)
        # print("VMin = ",VMin)
        # print("Vpp = ",Vpp)
        if Vpp < 1.1 and Vpp > 0.35:
            if VMax > (VOpenCircuit+0.4) and VMin < (VOpenCircuit+0.1):
                DiodeAK = 1
            elif VMax > (VOpenCircuit+0.1) and VMin < (VOpenCircuit-0.2):
                DiodeAK = -1
            else:
                DiodeAK = 0
    # Disconnect test pins
    ResetMatrix(1) # Reset all cross point switches to open
    #
    return(DiodeAK)
# print(CheckDiode2( "TL13" , "BL13" ))    
def MakeTestResWindow():
    global SWRev, RevDate, TestResStatus, TestResDisp, SW1, SW2, SW3, COLORblack, COLORwhite
    global ResSch, FrameBG, BorderSize, TestResOff, CPRevDate
    global TestResSW1, TestResSW2, TestResSW3, testreswindow, RDY0T, RDX0L
    global RoundGrnBtn, RoundRedBtn
    
    if TestResStatus.get() == 0: #
        TestResStatus.set(1)
        TestResDisp.set(1)
        testreswindow = Toplevel()
        testreswindow.title("Test Resistor Controls " + SWRev + CPRevDate)
        testreswindow.resizable(FALSE,FALSE)
        testreswindow.protocol("WM_DELETE_WINDOW", DestroyTestResScreen)
        testreswindow.geometry("530x310")
        testreswindow.configure(background=FrameBG, borderwidth=BorderSize)
# from here down we build GUI
        Font_tuple = ("Comic Sans MS", 10, "bold")
        TRGRW = 530 - ( RDX0L + 200 ) # Width of the Res Div Schem
        TRGRH = 300 - ( 2 * RDY0T )   # Height of the Res Div Schem
        SW1 = SW2 = SW3 = 0
        #
        display = Label(testreswindow, text="Test Resistor Switches", foreground= "Blue",font = Font_tuple)
        display.place(x = RDX0L, y = RDY0T)

        Disablebutton = Button(testreswindow, image=RoundRedBtn, command=TestResDisable)
        Disablebutton.place(x = RDX0L, y = RDY0T+30)
        Disablelable = Label(testreswindow, text="Disable Switches", foreground= "Blue",font = Font_tuple)
        Disablelable.place(x = RDX0L+40, y = RDY0T+30)
        Enablebutton = Button(testreswindow, image = RoundGrnBtn, command=TestResEnable)
        Enablebutton.place(x = RDX0L, y = RDY0T+70)
        Enablelable = Label(testreswindow, text="Enable Switches", foreground= "Blue",font = Font_tuple)
        Enablelable.place(x = RDX0L+40, y = RDY0T+70)
        
        TestResdismissbutton = Button(testreswindow, text="Dismiss", command=DestroyTestResScreen)
        TestResdismissbutton.place(x = RDX0L, y = 260)
        
        ResSch = Canvas(testreswindow, width=TRGRW, height=TRGRH, background=COLORwhite)
        ResSch.place(x = 200, y = RDY0T) #
        ResSch.bind('<1>', onResSchClick)
        ResSch.bind('<3>', onResSchClick)
        #
        TestResOff = 0
        # Draw Schematic
        #
        Ypt = 20
        ResSch.create_rectangle(18, Ypt-10, 54, Ypt+10, width=3) # JP9
        ResSch.create_text(36, Ypt, text = "JP9", fill=COLORblack, font=("arial", FontSize+2 ))
        DrawRes(120, Ypt, 10, ResSch, 1)
        ResSch.create_text(215, Ypt, text = "24k", fill=COLORblack, font=("arial", FontSize))
        Ypt = Ypt + 32
        #
        ResSch.create_rectangle(18, Ypt-10, 54, Ypt+10, width=3) # JP9
        ResSch.create_text(36, Ypt, text = "JP10", fill=COLORblack, font=("arial", FontSize+2 ))
        DrawRes(120, Ypt, 10, ResSch, 1)
        ResSch.create_text(215, Ypt, text = "3.948k", fill=COLORblack, font=("arial", FontSize))
        ResSch.create_oval(85, Ypt-9, 95, Ypt-19, outline="#a0a0a0", fill="#a0a0a0", width=2)
        ResSch.create_oval(115, Ypt-27, 125, Ypt-37, outline="#a0a0a0", fill="#a0a0a0", width=2)
        ResSch.create_oval(115, Ypt-5, 125, Ypt+5, outline="#a0a0a0", fill="#a0a0a0", width=2)
        ResSch.create_line(54, Ypt, 72, Ypt, fill=COLORblack, width=3)
        ResSch.create_line(72, Ypt-14, 90, Ypt-14, fill=COLORblack, width=3)
        ResSch.create_line(72, Ypt, 72, Ypt-14, fill=COLORblack, width=3)
        ResSch.create_line(198, Ypt, 198, Ypt-30, fill=COLORblack, width=3)
        ResSch.create_line(198, Ypt-16, 250, Ypt-16, fill=COLORblack, width=3)
        TestResSW1 = ResSch.create_line(90, Ypt-14, 120, Ypt-32, fill=COLORwhite, arrow="last", width=3)
        Ypt = Ypt + 32
        #
        ResSch.create_rectangle(18, Ypt-10, 54, Ypt+10, width=3) # JP9
        ResSch.create_text(36, Ypt, text = "JP11", fill=COLORblack, font=("arial", FontSize+2))
        DrawRes(64, Ypt, 10, ResSch, 1)
        ResSch.create_text(80, Ypt-16, text = "267", fill=COLORblack, font=("arial", FontSize))
        ResSch.create_line(54, Ypt, 64, Ypt, fill=COLORblack, width=3)
        ResSch.create_line(175, Ypt-16, 195, Ypt-16, fill=COLORblack, width=3)
        ResSch.create_text(210, Ypt-16, text = "+5V", fill=COLORblack, font=("arial", FontSize))
        ResSch.create_line(175, Ypt+16, 195, Ypt+16, fill=COLORblack, width=3)
        ResSch.create_text(210, Ypt+16, text = "0V", fill=COLORblack, font=("arial", FontSize))
        ResSch.create_oval(140, Ypt+5, 150, Ypt-5, outline="#a0a0a0", fill="#a0a0a0", width=2)
        ResSch.create_oval(170, Ypt+11, 180, Ypt+21, outline="#a0a0a0", fill="#a0a0a0", width=2)
        ResSch.create_oval(170, Ypt-11, 180, Ypt-21, outline="#a0a0a0", fill="#a0a0a0", width=2)
        TestResSW2 = ResSch.create_line(145, Ypt, 175, Ypt+16, fill=COLORwhite, arrow="last", width=3)
        Ypt = Ypt + 32
        #
        ResSch.create_rectangle(18, Ypt-10, 54, Ypt+10, width=3) # JP9
        ResSch.create_text(36, Ypt, text = "JP12", fill=COLORblack, font=("arial", FontSize+2))
        ResSch.create_line(54, Ypt, 230, Ypt, fill=COLORblack, width=3)
        TopY = 2.5 * 32
        ResSch.create_line(230, Ypt, 230, Ypt+TopY, fill=COLORblack, width=3)
        ResSch.create_line(181, Ypt+TopY, 230, Ypt+TopY, fill=COLORblack, width=3)
        Ypt = Ypt + 32
        #
        ResSch.create_rectangle(18, Ypt-10, 54, Ypt+10, width=3) # JP9
        ResSch.create_text(36, Ypt, text = "JP13", fill=COLORblack, font=("arial", FontSize+2))
        ResSch.create_line(54, Ypt, 250, Ypt, fill=COLORblack, width=3)
        TopY = 3.5 * 32
        ResSch.create_line(250, Ypt, 250, Ypt-TopY, fill=COLORblack, width=3)
        Ypt = Ypt + 32
        #
        ResSch.create_rectangle(18, Ypt-10, 54, Ypt+10, width=3) # JP9
        ResSch.create_text(36, Ypt, text = "JP14", fill=COLORblack, font=("arial", FontSize+2))
        DrawRes(70, Ypt, 10, ResSch, 1)
        ResSch.create_text(75, Ypt-10, text = "33k", fill=COLORblack, font=("arial", FontSize))
        ResSch.create_oval(146, Ypt+5, 156, Ypt-5, outline="#a0a0a0", fill="#a0a0a0", width=2)
        ResSch.create_oval(175, Ypt+11, 185, Ypt+21, outline="#a0a0a0", fill="#a0a0a0", width=2)
        ResSch.create_line(54, Ypt, 70, Ypt, fill=COLORblack, width=3)
        TestResSW3 = ResSch.create_line(181, Ypt+16, 151, Ypt, fill=COLORwhite, arrow="last", width=3)
        Ypt = Ypt + 32
        #
        ResSch.create_rectangle(18, Ypt-10, 54, Ypt+10, width=3) # JP9
        ResSch.create_text(36, Ypt, text = "JP15", fill=COLORblack, font=("arial", FontSize+2 ))
        DrawRes(70, Ypt, 10, ResSch, 1)
        ResSch.create_text(75, Ypt+10, text = "518", fill=COLORblack, font=("arial", FontSize))
        ResSch.create_oval(146, Ypt+5, 156, Ypt-5, outline="#a0a0a0", fill="#a0a0a0", width=2)
        ResSch.create_line(70, Ypt, 70, Ypt-32, fill=COLORblack, width=3)
        Ypt = Ypt + 32
        ResSch.create_rectangle(18, Ypt-10, 54, Ypt+10, width=3) # JP9
        ResSch.create_text(36, Ypt, text = "JP16", fill=COLORblack, font=("arial", FontSize+2 ))
        # Ypt = Ypt + 28
##
def DestroyTestResScreen():
    global ser, testreswindow, TestResStatus, TestResDisp, TestResOff
    
    TestResOff = 0
    ser.write(b'? 1 0 0 0\n') # Res switches to open
    TestResStatus.set(0)
    TestResDisp.set(0)
    testreswindow.destroy()
#
def TestResDisable():
    global ser, SW1, SW2, SW3, ResSch, TestResSW1, TestResSW2, TestResSW3, TestResOff

    # Disconnect test Resistors
    ResSch.delete(TestResSW1)
    ResSch.delete(TestResSW2)
    ResSch.delete(TestResSW3)
    SW1 = SW2 = SW3 = TestResOff = 0
    ser.write(b'? 1 0 0 0\n') # Res switches to open
#
def TestResEnable():
    global ser, SW1, SW2, SW3, ResSch, TestResSW1, TestResSW2, TestResSW3, TestResOff

    # Connect test Resistors
    ser.write(b'? 0 0 0 0\n') # Res switches to closed
    TestResOff = 1
    ResSch.delete(TestResSW1)
    ResSch.delete(TestResSW2)
    ResSch.delete(TestResSW3)
    if SW1 == 0 :
        TestResSW1 = ResSch.create_line(90, 38, 120, 20, fill=COLORblack, arrow="last", width=3)
    else:
        TestResSW1 = ResSch.create_line(90, 38, 120, 52, fill=COLORblack, arrow="last", width=3)
    if SW2 == 0:
        TestResSW2 = ResSch.create_line(145, 84, 175, 100, fill=COLORblack, arrow="last", width=3)
    else:
        TestResSW2 = ResSch.create_line(145, 84, 175, 68, fill=COLORblack, arrow="last", width=3)
    if SW3 == 0:
        TestResSW3 = ResSch.create_line(181, 196, 151, 180, fill=COLORblack, arrow="last", width=3)
    else:
        TestResSW3 = ResSch.create_line(181, 196, 151, 212, fill=COLORblack, arrow="last", width=3) 
#    
def onResSchClick(event):
    global TestResSW1, TestResSW2, TestResSW3, ser, ResSch, SW1, SW2, SW3, TestResOff
#
    CursorX = event.x
    CursorY = event.y
    if TestResOff == 0:
        return
    # Find which switch was clicked on 90, 52-14, 120, 52-32
    if CursorX > 90 and CursorX < 120 and CursorY > 20 and CursorY < 52:
        ResSch.delete(TestResSW1)
        if SW1 == 0:
            SW1 = 1
            TestResSW1 = ResSch.create_line(90, 38, 120, 52, fill=COLORblack, arrow="last", width=3)
        else:
            SW1 = 0
            TestResSW1 = ResSch.create_line(90, 38, 120, 20, fill=COLORblack, arrow="last", width=3)
    elif CursorX > 145 and CursorX < 175 and CursorY > 68 and CursorY < 100:
        ResSch.delete(TestResSW2)
        if SW2 == 0:
            SW2 = 1
            TestResSW2 = ResSch.create_line(145, 84, 175, 68, fill=COLORblack, arrow="last", width=3)
        else:
            SW2 = 0
            TestResSW2 = ResSch.create_line(145, 84, 175, 100, fill=COLORblack, arrow="last", width=3)
    elif CursorX > 151 and CursorX < 181 and CursorY > 180 and CursorY < 212: # 181, Ypt+16, 151, Ypt
        ResSch.delete(TestResSW3)
        if SW3 == 0:
            SW3 = 1
            TestResSW3 = ResSch.create_line(181, 196, 151, 212, fill=COLORblack, arrow="last", width=3)
        else:
            SW3 = 0
            TestResSW3 = ResSch.create_line(181, 196, 151, 180, fill=COLORblack, arrow="last", width=3)    
    #
    SendStr = '? 0 ' + str(SW3) + ' ' + str(SW2) + ' ' + str(SW1) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
#

# create an AI prompt box
def handle_user_prompt(event):
    global PromptBox, ChatHistory
    user_input = PromptBox.get().strip()
    
def handle_user_prompt(event):
    global PromptBox, ChatHistory, GeminiModel
    user_input = PromptBox.get().strip()
    
    if not user_input:
        return

    # 1. Clear input immediately
    PromptBox.delete(0, END)

    # 2. Enable box for appending
    ChatHistory.config(state=NORMAL)
    
    # 3. Add User Prompt with Tag
    ChatHistory.insert(END, "\nYou: ", "user_tag")
    ChatHistory.insert(END, f"{user_input}\n", "text_tag")
    
    # 4. "Thinking" Indicator
    ChatHistory.insert(END, "AI: Thinking...\n", "status_tag")
    ChatHistory.see(END)
    ChatHistory.update()

    # 5. Get Gemini Response
    try:
        response = GeminiModel.generate_content(user_input)
        reply = response.text
    except Exception as e:
        reply = f"Error: {str(e)}"

    # 6. Replace "Thinking..." with the actual response
    ChatHistory.delete("end-2l", "end-1c") 
    ChatHistory.insert(END, "AI: ", "ai_tag")
    ChatHistory.insert(END, f"{reply}\n", "text_tag")

    # 7. Finalize view
    ChatHistory.see(END)
    ChatHistory.config(state=DISABLED)
    
    # ENSURE CURSOR STAYS IN BOX
    PromptBox.focus_set()
