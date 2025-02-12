#!/usr/bin/python
# Configurable Analog Meter Interface
# For Python versions 2.7 and 3.X

import __future__
import math
import time
import sys
try:
    import numpy
    numpy_found = True
except:
    numpy_found = False
#
if sys.version_info[0] == 2:
    print("Python 2.x")
    import urllib2
    import tkFont
    from Tkinter import *
    from ttk import *
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfilename
    from tkSimpleDialog import askstring
    from tkMessageBox import *
if sys.version_info[0] == 3:
    print ("Python 3.x")    
    import urllib.request, urllib.error, urllib.parse
    import tkinter
    from tkinter.font import *
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename
    from tkinter.simpledialog import askstring
    from tkinter.messagebox import *
    from tkinter.colorchooser import askcolor
    from PIL import Image, ImageTk
#
# from operator import add
import math
import time
#
# check which operating system
import platform
#
# Check to see if user passed init file name on command line
if len(sys.argv) > 1:
    InitFileName = str(sys.argv[1])
    print( 'Init file name: ' + InitFileName )
else:
    InitFileName = 'alice_init.ini'
#
root = Tk()
RevDate = "(4 Feb 2025)"
SWRev = "1.0 "
# small bit map of ADI logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root.title("Analog Meter " + SWRev + RevDate + ": Cross Point")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
print("Windowing System is " + str(root.tk.call('tk', 'windowingsystem')))
#
InitFileName = "analog_meter_init.ini"
#
CHANNELS = 3            # Number of Channel traces 1 to 4
MouseFocus = 1
#
ConfigFileName = "analog-meter-config.cfg"
COLORcanvas = "#000000"   # 100% black
COLORgrid = "#808080"     # 50% Gray
COLORtrace1 = "#00ff00"   # 100% green
COLORtrace2 = "#ff8000"   # 100% orange
COLORtrace3 = "#00ffff"   # 100% cyan
COLORtrace4 = "#ffff00"   # 100% yellow
COLORtrace5 = "#ff00ff"   # 100% magenta
COLORtrace6 = "#C80000"   # 90% red
COLORtrace7 = "#8080ff"   # 100% purple
COLORtrace8 = "#C8C8C8"   # 75% Gray
COLORtext = "#ffffff"     # 100% white
COLORdial = "#404040"     # 25% Gray
ButtonGreen = "#00ff00"   # 100% green
ButtonRed = "#ff0000" # 100% red
GUITheme = "Light"
ColorMode = IntVar()
ColorMode.set(0)
# # Can be Light or Dark or Blue or LtBlue or Custom where:
FrameBG = "#d7d7d7" # Background color for frame
ButtonText = "#000000" # Button Text color
# Widget relief can be RAISED, GROOVE, RIDGE, and FLAT
ButRelief = RAISED
LabRelief = FLAT
FrameRefief = RIDGE
LocalLanguage = "English"
FontSize = 8
BorderSize = 1
GridWidth = IntVar()
GridWidth.set(2)
TRACEwidth = IntVar()
TRACEwidth.set(3)
MAScreenStatus = IntVar()
MAScreenStatus.set(0)
RUNstatus = IntVar()
RUNstatus.set(0)
Tdiv = IntVar()
Tdiv.set(10)
AWG_Amp_Mode = IntVar()
AWG_Amp_Mode.set(0)
IA_Mode = IntVar()
EnableInterpFilter = IntVar()
EnableInterpFilter.set(1)
# Analog Meter Variables
MGRW = 400                 # Width of the Analog Meter face 400 default
MGRH = 400                 # Height of the Analog Meter face 400 default
MXcenter = int(MGRW/2.0)   # Meter Center
MYcenter = int(MGRH/2.0)
MRadius = MXcenter - 50    # Meter Radius
Mmin = 0.0                 # Meter Scale Min Value
Mmax = 5.0                 # Meter Scale Max Value
MajorDiv = 10              # Meter Scale number of div
MinorDiv = 5
DialSpan = 270             # Number of degrees for analog meter dial
MeterLabelText = "Volts"
InOffA = 0.0
InGainA = 1.0
InOffB = 0.0
InGainB = 1.0
InOffC = 0.0
InGainC = 1.0
InOffD = 0.0
InGainD = 1.0
TimeDiv = 0.0002
# Digital flags
D0_is_on = False
D1_is_on = False
D2_is_on = False
D3_is_on = False
D4_is_on = False
D5_is_on = False
D6_is_on = False
D7_is_on = False
PWM1_is_on = False
PWM2_is_on = False
# Digital waveform buffers
DBuff0 = []
DBuff1 = []
DBuff2 = []
DBuff3 = []
DBuff4 = []
DBuff5 = []
DBuff6 = []
DBuff7 = []
#
Interp8Filter = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]
Interp4Filter = [0.25, 0.25, 0.25, 0.25]
Interp3Filter = [0.333, 0.334, 0.333]
Interp2Filter = [0.5, 0.5]
#('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
# 'aqua' built-in native Mac OS X only; Native Mac OS X
windowingsystem = root.tk.call('tk', 'windowingsystem')
ScreenWidth = root.winfo_screenwidth()
ScreenHeight = root.winfo_screenheight()
# print(str(ScreenWidth) + "X" + str(ScreenHeight))
if (root.tk.call('tk', 'windowingsystem')=='aqua'):
    Style_String = 'aqua'
    # On Macs, allow the dock icon to deiconify.
    root.createcommand('::tk::mac::ReopenApplication', root.deiconify)
    root.createcommand('::tk::mac::Quit', root.destroy)# Bcloseexit)
    # On Macs, set up menu bar to be minimal.
    root.option_add('*tearOff', False)
    if sys.version_info[0] == 2:
        menubar = tKinter.Menu(root)
        appmenu = tKinter.Menu(menubar, name='apple')
    else:
        menubar = tkinter.Menu(root)
        appmenu = tkinter.Menu(menubar, name='apple')
    # menubar = tk.Menu(root)
    # appmenu = tk.Menu(menubar, name='apple')
    menubar.add_cascade(menu=appmenu)
    # appmenu.add_command(label='Exit', command=Bcloseexit)
    root['menu'] = menubar
else:
    Style_String = 'alt'
## Check if there is an analog_meter_init.ini file to read in
try:
    InitFile = open(InitFileName) # "analog_meter_init.ini"
    for line in InitFile:
        try:
            exec( line.rstrip() )
        except:
            print("Skiping " + line.rstrip()) 
    InitFile.close()
except:
    print( "No Init File Read. " + InitFileName + " Not Found")
#
root.style = Style()
try:
    root.style.theme_use(Style_String)
except:
    root.style.theme_use('default')
if MouseFocus == 1:
    root.tk_focusFollowsMouse()
#
DevID = "m1k"
#
if sys.version_info[0] == 2:
    default_font = tkFont.nametofont("TkDefaultFont")
if sys.version_info[0] == 3:
    default_font = tkinter.font.nametofont("TkDefaultFont")
try:
    default_font.config(size=FontSize) # or .configure ?
except:
    print("Warning! Default Font Size was not set")
#
# Import Hardware Specific control I/O functions:
#
if DeBugMode == 2:
    exec( open(HardwareFile).read() )
else:
    try:
        exec( open(HardwareFile).read() )
    except:
        root.update()
        showwarning("WARNING","Trouble Reading Hardware Specific File!")
        HardwareFile = askopenfilename(defaultextension = ".py", filetypes=[("Hardware File:", "*.py")])
        if HardwareFile == None:
            root.destroy()
            exit()
        else:
            try:
                exec( open(HardwareFile).read() )
            except:
                root.update()
                showwarning("WARNING","Trouble Reading Hardware Specific File!")
                root.destroy()
                exit()
#
# Converts a numeric string with "M" e6 or "k" e3 or "m" e-3 or "u" e-6
# to floating point number so calculations can be done on the user inputs
def UnitConvert(Value):
    
    Value = str.strip(Value,'V')
    Value = str.strip(Value,'s')
    if 'K' in Value:
        Value = str.strip(Value,'K') #
        Value = float(Value) * math.pow(10,3)
    elif 'k' in Value:
        Value = str.strip(Value,'k') #
        Value = float(Value) * math.pow(10,3)
    elif 'm' in Value:
        Value = str.strip(Value,'m') #
        Value = float(Value) * math.pow(10,-3)
    elif 'M' in Value:
        Value = str.strip(Value,'M') #
        Value = float(Value) * math.pow(10,6)
    elif 'u' in Value:
        Value = str.strip(Value,'u') #
        Value = float(Value) * math.pow(10,-6)
    elif 'n' in Value:
        Value = str.strip(Value,'n') #
        Value = float(Value) * math.pow(10,-9)
    else:
        Value = float(Value)
    return Value
# Take just integer part of digits
def UnitIntConvert(Value):
    
    Value = str.strip(Value,'V')
    Value = str.strip(Value,'s')
    if 'K' in Value:
        Value = str.strip(Value,'K') #
        Value = int(Value) * 1000
    elif 'k' in Value:
        Value = str.strip(Value,'k') #
        Value = int(Value) * 1000
    elif 'm' in Value:
        Value = str.strip(Value,'m') #
        Value = int(Value) * 0.001
    elif 'M' in Value:
        Value = str.strip(Value,'M') #
        Value = int(Value) * 1000000
    elif 'u' in Value:
        Value = str.strip(Value,'u') #
        Value = int(Value) * 0.000001
    elif 'n' in Value:
        Value = str.strip(Value,'n') #
        Value = int(Value) * 0.000000001
    else:
        Value = int(Value)
    return Value
#
# Draw analog meter face
#
def Build_meter():
    global MXcenter, MYcenter, MRadius, MGRW, MGRH, MAScreenStatus, MeterMaxEntry
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6, COLORtrace7
    global COLORtext, TRACEwidth, GridWidth, FontSize
    global COLORcanvas, COLORgrid, COLORdial, SWRev, RevDate, MAca, mawindow
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel
    global IndicatorA, IndicatorB, IndicatorC, IndicatorD
    global IndicatorM, IndicatorMX, IndicatorMY
    global ValueDisA, ValueDisB, ValueDisC, ValueDisD, DialSpan, CHANNELS
    global ValueDisM, ValueDisMX, ValueDisMY

    if MAScreenStatus.get() == 0:
        MAScreenStatus.set(1)
        mawindow = Toplevel()
        mawindow.title("Analog Meter " + SWRev + RevDate)
        mawindow.protocol("WM_DELETE_WINDOW", DestroyMAScreen)
    
        MAca = Canvas(mawindow, width=MGRW, height=MGRH, background=COLORcanvas)
        MAca.bind("<Configure>", MACaresize)
        MAca.pack(side=TOP, expand=YES, fill=BOTH)
# MAca.bind("<Return>", DoNothing)
        MAca.bind("<space>", onCanvasSpaceBar)
        if DialSpan > 359:
            DialSpan = 355
        DialStart = 360 - ((DialSpan-180)/2)
        DialCenter = 0.15 * MRadius
        MAca.create_arc(MXcenter-MRadius, MYcenter+MRadius, MXcenter+MRadius, MYcenter-MRadius, start=DialStart, extent=DialSpan, outline=COLORgrid, fill=COLORdial, width=GridWidth.get())
        MAca.create_arc(MXcenter-DialCenter, MYcenter+DialCenter, MXcenter+DialCenter, MYcenter-DialCenter, start=DialStart, extent=DialSpan, outline="blue", fill="blue", width=GridWidth.get())
        if Mmin >= Mmax:
            Mmax = Mmin + 0.1
            MeterMaxEntry.delete(0,END)
            MeterMaxEntry.insert(0, Mmax)
        MScale = Mmax - Mmin
        DialStart = 90 + (DialSpan/2)
        for tick in range(MajorDiv+1):
            TIradius = 1.1 * MRadius
            TOradius = 1.2 * MRadius
            Angle = DialStart - ((DialSpan*tick)/MajorDiv)
            NextAngle = DialStart - ((DialSpan*(tick+1))/MajorDiv)
            MinorTickStep = (Angle - NextAngle)/5.0
            RAngle = math.radians(Angle)
            y = MRadius*math.sin(RAngle)
            x = MRadius*math.cos(RAngle)
            yi = TIradius*math.sin(RAngle)
            xi = TIradius*math.cos(RAngle) 
            yt = TOradius*math.sin(RAngle)
            xt = TOradius*math.cos(RAngle)
            if Angle > 270:
                y = 0 - y
                yi = 0 - yi
                yt = 0 - yt
            #Draw Major Tick
            MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
            # Add Text Label
            Increment = MajorDiv/MScale
            axis_value = float((tick/Increment)+Mmin)
            # axis_label = '{0:.2f}'.format(axis_value)
            axis_label = str(round(axis_value,2 ))
            # axis_label = str(axis_value)
            MAca.create_text(MXcenter+xt, MYcenter-yt, text = axis_label, fill=COLORtext, font=("arial", FontSize ))
            # Add minor Ticks
            TIradius = 1.05 * MRadius
            if tick < MajorDiv:
                for minor in range(MinorDiv-1):
                    MinorAngle = Angle-((minor+1)*MinorTickStep)
                    RAngle = math.radians(MinorAngle)
                    y = MRadius*math.sin(RAngle)
                    x = MRadius*math.cos(RAngle)
                    yi = TIradius*math.sin(RAngle)
                    xi = TIradius*math.cos(RAngle)
                    if MinorAngle > 270:
                        y = 0 - y
                        yi = 0 - yi
                    #Draw Minor Tick
                    MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())

        MeterLabel = MAca.create_text(MXcenter-MRadius/2,MYcenter+MRadius/2, text = MeterLabelText, fill=COLORtext, font=("arial", FontSize+4 ))
        
        IndicatorA = MAca.create_line(MXcenter, MYcenter, MXcenter+x, MYcenter-y, fill=COLORtrace1, arrow="last", width=TRACEwidth.get())
        IndicatorB = IndicatorC = IndicatorD = IndicatorM = IndicatorMX = IndicatorMY = IndicatorA
        VString = ' {0:.4f} '.format(0.0) # format with 4 decimal places
        TextX = MXcenter - MRadius
        TextY = MYcenter + MRadius
        if CHANNELS >= 1:
            ValueDisA = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace1, font=("arial", FontSize+4 ))
        if CHANNELS >= 2:
            TextY = TextY + FontSize + 5
            ValueDisB = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace2, font=("arial", FontSize+4 ))
        if CHANNELS >= 3:
            TextY = TextY + FontSize + 5
            ValueDisC = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace3, font=("arial", FontSize+4 ))
        if CHANNELS >= 4:
            TextY = TextY + FontSize + 5
            ValueDisD = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace4, font=("arial", FontSize+4 ))
        TextX = TextX + 7 * FontSize
        TextY = MYcenter + MRadius
        ValueDisM = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace5, font=("arial", FontSize+4 ))
        TextY = TextY + FontSize + 5
        ValueDisMX = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace6, font=("arial", FontSize+4 ))
        TextY = TextY + FontSize + 5
        ValueDisMXY = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace7, font=("arial", FontSize+4 ))
#
def DestroyMAScreen():
    global mawindow, MAScreenStatus #, MAca, MADisp

    MAScreenStatus.set(0)
    mawindow.destroy()
#
#
def Update_Analog_Meter(ValueA, ValueB, ValueC, ValueD, ValueM):
    global MXcenter, MYcenter, MRadius, MAca, MGRW, MGRH
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V, CHANNELS
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, TRACEwidth, GridWidth, FontSize
    global Mmin, Mmax, MajorDiv, DialSpan, MeterMaxEntry
    global IndicatorA, IndicatorB, ValueDisA, ValueDisB
    global IndicatorC, IndicatorD, ValueDisC, ValueDisD
    global IndicatorM, IndicatorMX, IndicatorMY
    global ValueDisM, ValueDisMX, ValueDisMY
    global MathTrace, Show_MathX, Show_MathY
    
    if Mmin >= Mmax:
        Mmax = Mmin + 0.1
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    MScale = Mmax - Mmin
    DialStart = 90 + (DialSpan/2)
    Tradius = 1.0 * MRadius
    try:
        MAca.delete(IndicatorA) # remove old lines
        MAca.delete(ValueDisA)# remove old text
    except:
        pass
    try:
        MAca.delete(IndicatorB)
        MAca.delete(ValueDisB)
    except:
        pass
    try:
        MAca.delete(IndicatorC)
        MAca.delete(ValueDisC)
    except:
        pass
    try:
        MAca.delete(IndicatorD)
        MAca.delete(ValueDisD)
    except:
        pass
    try:
        MAca.delete(IndicatorM)
        MAca.delete(ValueDisM)
    except:
        pass
    try:
        MAca.delete(IndicatorMX)
        MAca.delete(ValueDisMX)
    except:
        pass
    try:
        MAca.delete(IndicatorMY)
        MAca.delete(ValueDisMY)
    except:
        pass
    TextX = MXcenter - MRadius
    TextY = MYcenter + MRadius
    if ShowC1_V.get() > 0 and CHANNELS >= 1:
        Angle = DialStart - ((DialSpan*(ValueA-Mmin))/MScale) # calculate angle of CHA indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        ya = Tradius*math.sin(RAngle) # convert angle to x y position
        xa = Tradius*math.cos(RAngle)
        if Angle > 270:
            ya = 0 - ya
        IndicatorA = MAca.create_line(MXcenter, MYcenter, MXcenter+xa, MYcenter-ya, fill=COLORtrace1, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueA) # format with 4 decimal places
        ValueDisA = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace1, font=("arial", FontSize+4 ))
    if ShowC2_V.get() > 0 and CHANNELS >= 2:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueB-Mmin))/MScale) # calculate angle of CHB indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yb = Tradius*math.sin(RAngle) # convert angle to x y position
        xb = Tradius*math.cos(RAngle)
        if Angle > 270:
            yb = 0 - yb
        IndicatorB = MAca.create_line(MXcenter, MYcenter, MXcenter+xb, MYcenter-yb, fill=COLORtrace2, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueB) # format with 4 decimal places
        ValueDisB = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace2, font=("arial", FontSize+4 ))
    if ShowC3_V.get() > 0 and CHANNELS >= 3:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueC-Mmin))/MScale) # calculate angle of CHC indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yc = Tradius*math.sin(RAngle) # convert angle to x y position
        xc = Tradius*math.cos(RAngle)
        if Angle > 270:
            yc = 0 - yc
        IndicatorC = MAca.create_line(MXcenter, MYcenter, MXcenter+xc, MYcenter-yc, fill=COLORtrace3, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueC) # format with 4 decimal places
        ValueDisC = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace3, font=("arial", FontSize+4 ))
    if ShowC4_V.get() > 0 and CHANNELS >= 4:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueD-Mmin))/MScale) # calculate angle of CHD indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yd = Tradius*math.sin(RAngle) # convert angle to x y position
        xd = Tradius*math.cos(RAngle)
        if Angle > 270:
            yd = 0 - yd
        IndicatorD = MAca.create_line(MXcenter, MYcenter, MXcenter+xd, MYcenter-yd, fill=COLORtrace4, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueD) # format with 4 decimal places
        ValueDisD = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace4, font=("arial", FontSize+4 ))
    TextX = TextX + 7 * FontSize
    TextY = MYcenter + MRadius
    if MathTrace.get() > 0:
        Angle = DialStart - ((DialSpan*(ValueM-Mmin))/MScale) # calculate angle of Math indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yd = Tradius*math.sin(RAngle) # convert angle to x y position
        xd = Tradius*math.cos(RAngle)
        if Angle > 270:
            yd = 0 - yd
        IndicatorM = MAca.create_line(MXcenter, MYcenter, MXcenter+xd, MYcenter-yd, fill=COLORtrace5, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueM) # format with 4 decimal places
        ValueDisM = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace5, font=("arial", FontSize+4 ))
    if Show_MathX.get() > 0:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueMX-Mmin))/MScale) # calculate angle of Math indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yd = Tradius*math.sin(RAngle) # convert angle to x y position
        xd = Tradius*math.cos(RAngle)
        if Angle > 270:
            yd = 0 - yd
        IndicatorMX = MAca.create_line(MXcenter, MYcenter, MXcenter+xd, MYcenter-yd, fill=COLORtrace6, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueMX) # format with 4 decimal places
        ValueDisMX = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace6, font=("arial", FontSize+4 ))
    if Show_MathY.get() > 0:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueMY-Mmin))/MScale) # calculate angle of Math indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yd = Tradius*math.sin(RAngle) # convert angle to x y position
        xd = Tradius*math.cos(RAngle)
        if Angle > 270:
            yd = 0 - yd
        IndicatorMY = MAca.create_line(MXcenter, MYcenter, MXcenter+xd, MYcenter-yd, fill=COLORtrace7, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueMY) # format with 4 decimal places
        ValueDisMY = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace7, font=("arial", FontSize+4 ))
#
# Resize Analog Meter window
def MACaresize(event):
    global MAca, MGRW, MGRH, CANVASwidthMA, CANVASheightMA, FontSize
    global MXcenter, MYcenter, MRadius, COLORdial, MeterMinEntry, MeterMaxEntry
    global IndicatorA, IndicatorB, COLORtrace1, COLORtrace2, COLORtext, TRACEwidth, GridWidth
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel 
     
    CANVASwidthMA = event.width - 4
    CANVASheightMA = event.height - 4
    MGRW = CANVASwidthMA # 170 new grid width
    MGRH = CANVASheightMA  # 10 new grid height
    MXcenter = int(MGRW/2.0)   # Meter Center
    MYcenter = int(MGRH/2.0)
    MRadius = MXcenter - 50    # Meter Radius
    MakeMeterDial()
#
#
def MakeMeterDial():
    global MAca, MGRW, MGRH, CANVASwidthMA, CANVASheightMA, FontSize
    global MXcenter, MYcenter, MRadius, COLORdial, MeterMinEntry, MeterMaxEntry
    global IndicatorA, IndicatorB, COLORtrace1, COLORtrace2, COLORtext, TRACEwidth, GridWidth
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel, DialSpan
    
    # Re make meter dial
    MAca.delete(ALL) # remove all items
    if DialSpan > 359:
        DialSpan = 355
    DialStart = 360 - ((DialSpan-180)/2)
    DialCenter = 0.15 * MRadius
    MAca.create_arc(MXcenter-MRadius, MYcenter+MRadius, MXcenter+MRadius, MYcenter-MRadius, start=DialStart, extent=DialSpan, outline=COLORgrid, fill=COLORdial, width=GridWidth.get())
    MAca.create_arc(MXcenter-DialCenter, MYcenter+DialCenter, MXcenter+DialCenter, MYcenter-DialCenter, start=DialStart, extent=DialSpan, outline="blue", fill="blue", width=GridWidth.get())
#
    try:
        Mmin = float(eval(MeterMinEntry.get()))
    except:
        MeterMinEntry.delete(0,END)
        MeterMinEntry.insert(0, Mmin)
    try:
        Mmax = float(eval(MeterMaxEntry.get()))
    except:
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    if Mmin >= Mmax:
        Mmax = Mmin + 0.1
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    MScale = Mmax - Mmin
    DialStart = 90.0 + (DialSpan/2.0)
    for tick in range(MajorDiv+1):
        TIradius = 1.1 * MRadius
        TOradius = 1.2 * MRadius
        Angle = DialStart - ((DialSpan*tick)/MajorDiv)
        NextAngle = DialStart - ((DialSpan*(tick+1))/MajorDiv)
        MinorTickStep = (Angle - NextAngle)/5.0
        RAngle = math.radians(Angle)
        y = MRadius*math.sin(RAngle)
        x = MRadius*math.cos(RAngle)
        yi = TIradius*math.sin(RAngle)
        xi = TIradius*math.cos(RAngle) 
        yt = TOradius*math.sin(RAngle)
        xt = TOradius*math.cos(RAngle)
        if Angle > 270:
            y = 0 - y
            yi = 0 - yi
            yt = 0 - yt
        #Draw Major Tick
        MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
        # Add Text Label
        Increment = MajorDiv/MScale
        axis_value = float((tick/Increment)+Mmin)
        axis_label = str(round(axis_value,2 ))
        # axis_label = str(axis_value)
        MAca.create_text(MXcenter+xt, MYcenter-yt, text = axis_label, fill=COLORtext, font=("arial", FontSize ))
        # Add minor Ticks
        TIradius = 1.05 * MRadius
        if tick < MajorDiv:
            for minor in range(MinorDiv-1):
                MinorAngle = Angle-((minor+1)*MinorTickStep)
                RAngle = math.radians(MinorAngle)
                y = MRadius*math.sin(RAngle)
                x = MRadius*math.cos(RAngle)
                yi = TIradius*math.sin(RAngle)
                xi = TIradius*math.cos(RAngle)
                if MinorAngle > 270:
                    y = 0 - y
                    yi = 0 - yi
                #Draw Minor Tick
                MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
        MeterLabel = MAca.create_text(MXcenter, MYcenter+MRadius/2, text = MeterLabelText, fill=COLORtext, font=("arial", FontSize+4 ))
#
#
def Analog_In():
    global CHAVOffsetEntry, CHAVGainEntry, CHBVOffsetEntry, CHBVGainEntry
    global CHCVOffsetEntry, CHCVGainEntry, CHDVOffsetEntry, CHDVGainEntry
    global VBuffA, VBuffB, VBuffC, VBuffD, CHANNELS
    global InOffA, InGainA, InOffB, InGainB
    global InOffC, InGainC, InOffD, InGainD

    # Main loop
    while (True):       
        if (RUNstatus.get() == 1):
            # Do input divider Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
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
                    InOffB = float(eval(CHBVOffsetEntry.get()))
                except:
                    CHBVOffsetEntry.delete(0,END)
                    CHBVOffsetEntry.insert(0, InOffB)
                try:
                    InGainB = float(eval(CHBVGainEntry.get()))
                except:
                    CHBVGainEntry.delete(0,END)
                    CHBVGainEntry.insert(0, InGainB)
            if CHANNELS >= 3:
                try:
                    InOffC = float(eval(CHCVOffsetEntry.get()))
                except:
                    CHCVOffsetEntry.delete(0,END)
                    CHCVOffsetEntry.insert(0, InOffC)
                try:
                    InGainC = float(eval(CHCVGainEntry.get()))
                except:
                    CHCVGainEntry.delete(0,END)
                    CHCVGainEntry.insert(0, InGainC)
            if CHANNELS >= 4:
                try:
                    InOffD = float(eval(CHDVOffsetEntry.get()))
                except:
                    CHDVOffsetEntry.delete(0,END)
                    CHDVOffsetEntry.insert(0, InOffD)
                try:
                    InGainD = float(eval(CHDVGainEntry.get()))
                except:
                    CHDVGainEntry.delete(0,END)
                    CHDVGainEntry.insert(0, InGainD)
                
            DCVA0 = 0.0 # initalize measurment variable
            DCVB0 = 0.0
            DCVC0 = 0.0
            DCVD0 = 0.0
            DCVM0 = 0.0
            Get_Data()
            #
            DCVA0 = numpy.mean(VBuffA) # calculate average
            DCVB0 = numpy.mean(VBuffB) # calculate average
            DCVC0 = numpy.mean(VBuffC) # calculate average
            DCVD0 = numpy.mean(VBuffD) # calculate average
            DCVM0 = DCVA0 - DCVB0
            # DCVA = (DCVA - InOffA) * InGainA
            VString = ' {0:.4f} '.format(DCVA0) # format with 4 decimal places
            # print VString
            VString = VString + ' {0:.4f} '.format(DCVB0) # format with 4 decimal places
            # print VString
            label.config(text = VString) # change displayed values
            #
            Update_Analog_Meter(DCVA0, DCVB0, DCVC0, DCVD0, DCVM0)
            # time.sleep(0.1)
            
    # Update tasks and screens by TKinter
        root.update_idletasks()
        root.update()            
#
# Use mouse wheel to scroll entry values
def onTextScroll(event):   
    button = event.widget
    cursor_position = button.index(INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    NewVal = OldValfl
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    # respond to Linux or Windows wheel event
    if event.num == 5 or event.delta == -120:
        NewVal = OldValfl - Step
    if event.num == 4 or event.delta == 120:
        NewVal = OldValfl + Step
    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor
#
# Use Arrow keys to inc dec entry values
def onTextKey(event):
    button = event.widget
    cursor_position = button.index(INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    if platform.system() == "Windows":
        if event.keycode == 38: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 40: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Linux":
        if event.keycode == 111: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 116: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Darwin":
        if event.keycode == 0x7D: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 0x7E: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    else:
        return
#
    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor
#
def onMeterMinMax(event):
    onTextScroll(event)
    MakeMeterDial()
#
def onKeyMinMax(event):
    onTextKey(event)
    MakeMeterDial()
#
# Pause / start on space bar
def onCanvasSpaceBar(event):
    global RUNstatus, MAca

    if event.widget == MAca:
        if RUNstatus.get() == 0:
            RUNstatus.set(1)
        elif RUNstatus.get() > 0:
            RUNstatus.set(0)
#
def ReSetAGO():
    global CHAVGainEntry, CHAVOffsetEntry

    CHAVGainEntry.delete(0,"end")
    CHAVGainEntry.insert(0,1.0)
    CHAVOffsetEntry.delete(0,"end")
    CHAVOffsetEntry.insert(0,0.0)
#
def ReSetBGO():
    global CHBVGainEntry, CHBVOffsetEntry

    CHBVGainEntry.delete(0,"end")
    CHBVGainEntry.insert(0,1.0)
    CHBVOffsetEntry.delete(0,"end")
    CHBVOffsetEntry.insert(0,0.0)
#
def ReSetCGO():
    global CHCVGainEntry, CHCVOffsetEntry

    CHCVGainEntry.delete(0,"end")
    CHCVGainEntry.insert(0,1.0)
    CHCVOffsetEntry.delete(0,"end")
    CHCVOffsetEntry.insert(0,0.0)
## Nop
def donothing():
    global RUNstatus
## Another Nop
def DoNothing(event):
    global RUNstatus
## Save current configureation to file
#
def BSaveConfig(filename):
    global root, win1, win2, CHANNELS
    global MeterMinEntry, MeterMaxEntry, CHAVGainEntry, CHAVOffsetEntry
    global CHBVGainEntry, CHBVOffsetEntry, CHCVGainEntry, CHCVOffsetEntry
    global CHDVGainEntry, CHDVOffsetEntry
    global ScreenWidth, ScreenHeight
    global COLORtext, COLORcanvas, COLORtrigger, COLORsignalband, COLORframes, COLORgrid, COLORzeroline
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2, COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4
    global COLORtrace5, COLORtraceR5, COLORtrace6, COLORtraceR6, COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8

    # open Config file for Write?
    try:
        ConfgFile = open(filename, "w")
    except: # didn't work? then just return
        return
    # Save Window placements
    ConfgFile.write("root.geometry('+" + str(root.winfo_x()) + '+' + str(root.winfo_y()) + "')\n")
    
    ConfgFile.write('ColorMode.set(' + str(ColorMode.get()) + ')\n')
    # Windows configuration
    
    # Save Color Def
    ConfgFile.write('COLORtext = "' + COLORtext + '"\n')
    ConfgFile.write('COLORcanvas = "' + COLORcanvas + '"\n')
    ConfgFile.write('COLORtrigger = "' + COLORtrigger + '"\n')
    ConfgFile.write('COLORsignalband = "' + COLORsignalband + '"\n')
    ConfgFile.write('COLORframes = "' + COLORframes + '"\n')
    ConfgFile.write('COLORgrid = "' + COLORgrid + '"\n')
    ConfgFile.write('COLORtrace1 = "' + COLORtrace1 + '"\n')
    ConfgFile.write('COLORtraceR1 = "' + COLORtraceR1 + '"\n')
    ConfgFile.write('COLORtrace2 = "' + COLORtrace2 + '"\n')
    ConfgFile.write('COLORtraceR2 = "' + COLORtraceR2 + '"\n')
    ConfgFile.write('COLORtrace3 = "' + COLORtrace3 + '"\n')
    ConfgFile.write('COLORtraceR3 = "' + COLORtraceR3 + '"\n')
    ConfgFile.write('COLORtrace4 = "' + COLORtrace4 + '"\n')
    ConfgFile.write('COLORtraceR4 = "' + COLORtraceR4 + '"\n')
    ConfgFile.write('COLORtrace5 = "' + COLORtrace5 + '"\n')
    ConfgFile.write('COLORtraceR5 = "' + COLORtraceR5 + '"\n')
    ConfgFile.write('COLORtrace6 = "' + COLORtrace6 + '"\n')
    ConfgFile.write('COLORtraceR6 = "' + COLORtraceR6 + '"\n')
    ConfgFile.write('COLORtrace7 = "' + COLORtrace7 + '"\n')
    ConfgFile.write('COLORtraceR7 = "' + COLORtraceR7 + '"\n')
    ConfgFile.write('COLORtrace8 = "' + COLORtrace8 + '"\n')
    ConfgFile.write('COLORtraceR8 = "' + COLORtraceR8 + '"\n')
    #
    #
    ConfgFile.write('ShowC1_V.set(' + str(ShowC1_V.get()) + ')\n')
    ConfgFile.write('ShowC2_V.set(' + str(ShowC2_V.get()) + ')\n')
    ConfgFile.write('ShowC3_V.set(' + str(ShowC3_V.get()) + ')\n')
    ConfgFile.write('ShowC4_V.set(' + str(ShowC4_V.get()) + ')\n')

    ConfgFile.write('MeterMinEntry.delete(0,END)\n')
    ConfgFile.write('MeterMinEntry.insert(4, ' + MeterMinEntry.get() + ')\n')
    ConfgFile.write('MeterMaxEntry.delete(0,END)\n')
    ConfgFile.write('MeterMaxEntry.insert(0, "' + MeterMaxEntry.get() + '")\n')
    if CHANNELS >= 1:
        ConfgFile.write('CHAVGainEntry.delete(0,END)\n')
        ConfgFile.write('CHAVGainEntry.insert(4, ' + CHAVGainEntry.get() + ')\n')
        ConfgFile.write('CHAVOffsetEntry.delete(0,END)\n')
        ConfgFile.write('CHAVOffsetEntry.insert(4, ' + CHAVOffsetEntry.get() + ')\n')
    if CHANNELS >= 2:
        ConfgFile.write('CHBVGainEntry.delete(0,END)\n')
        ConfgFile.write('CHBVGainEntry.insert(4, ' + CHBVGainEntry.get() + ')\n')
        ConfgFile.write('CHBVOffsetEntry.delete(0,END)\n')
        ConfgFile.write('CHBVOffsetEntry.insert(4, ' + CHBVOffsetEntry.get() + ')\n')
    if CHANNELS >= 3:
        ConfgFile.write('CHCVGainEntry.delete(0,END)\n')
        ConfgFile.write('CHCVGainEntry.insert(4, ' + CHCVGainEntry.get() + ')\n')
        ConfgFile.write('CHCVOffsetEntry.delete(0,END)\n')
        ConfgFile.write('CHCVOffsetEntry.insert(4, ' + CHCVOffsetEntry.get() + ')\n')
    if CHANNELS >= 4:
        ConfgFile.write('CHDVGainEntry.delete(0,END)\n')
        ConfgFile.write('CHDVGainEntry.insert(4, ' + CHDVGainEntry.get() + ')\n')
        ConfgFile.write('CHDVOffsetEntry.delete(0,END)\n')
        ConfgFile.write('CHDVOffsetEntry.insert(4, ' + CHDVOffsetEntry.get() + ')\n')
    #
    ConfgFile.close()
## Load configuration from a file    
def BLoadConfig(filename):
    global root, win1, win2, CHANNELS
    global MeterMinEntry, MeterMaxEntry, CHAVGainEntry, CHAVOffsetEntry
    global CHBVGainEntry, CHBVOffsetEntry, CHCVGainEntry, CHCVOffsetEntry
    global CHDVGainEntry, CHDVOffsetEntry
    global ScreenWidth, ScreenHeight
    global COLORtext, COLORcanvas, COLORtrigger, COLORsignalband, COLORframes, COLORgrid, COLORzeroline
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2, COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4
    global COLORtrace5, COLORtraceR5, COLORtrace6, COLORtraceR6, COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8

    # Read configuration values from file
    try:
        ConfgFile = open(filename)
        for line in ConfgFile:
            try:
                exec( line.rstrip(), globals(), globals())
                #exec( line.rstrip() )
            except:
                print( "Skipping " + line.rstrip())
        ConfgFile.close()
    except:
        print( "Config File Not Found.")
    if ScreenWidth < root.winfo_x() or ScreenHeight < root.winfo_y(): # check if main window will be placed off screen?
        root.geometry('+0+0')
    
    try:
        if ScreenWidth < win1.winfo_x() or ScreenHeight < win1.winfo_y(): # check if DAC1 window will be placed off screen?
            win1.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < win2.winfo_x() or ScreenHeight < win2.winfo_y(): # check if DAC2 window will be placed off screen?
            win2.geometry('+0+0')
    except:
        donothing()
    # ca.config(background=COLORcanvas)
    # Needs to reload from waveform files
    # Regenerate waveform from formula
    #if AWGAShape.get()==10:
    #    AWGAConfigMath()
    
#
    time.sleep(0.05)
    # turn off unused channels
    if CHANNELS < 2:
        ShowC2_V.set(0)
    if CHANNELS < 3:
        ShowC3_V.set(0)
    if CHANNELS < 4:
        ShowC4_V.set(0)
#
# setup main window 
#
# Show channels variables
ShowC1_V = IntVar()   # curves to display variables
ShowC2_V = IntVar()
ShowC3_V = IntVar()   # curves to display variables
ShowC4_V = IntVar()
ShowRA_V = IntVar()
ShowRB_V = IntVar()
ShowRC_V = IntVar()
ShowRD_V = IntVar()
ShowMath = IntVar()
MathTrace = IntVar()
Show_MathX = IntVar()
Show_MathY = IntVar()
# , YsignalMX, YsignalMY
ShowC1_V.set(1)
ShowC2_V.set(1)
ShowC3_V.set(1)
ShowMath.set(0)
MathTrace.set(0)
Show_MathX.set(0)
Show_MathY.set(0)
if GUITheme == "Light": # Can be Light or Dark or Blue or LtBlue
    FrameBG = "#d7d7d7"
    ButtonText = "#000000"
elif GUITheme == "Dark":
    FrameBG = "#484848"
    ButtonText = "#ffffff"
elif GUITheme == "Blue":
    FrameBG = "#242468"
    ButtonText = "#d0d0ff"
elif GUITheme == "LtBlue":
    FrameBG = "#c0e8ff"
    ButtonText = "#000040"
EntryText = "#000000"
BoxColor = "#0000ff" # 100% blue
#
root.geometry('+300+0')
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
#
root.style.configure("TFrame", background=FrameBG, borderwidth=BorderSize)
root.style.configure("TLabelframe", background=FrameBG)
root.style.configure("TLabel", foreground=ButtonText, background=FrameBG, relief=LabRelief)
root.style.configure("TEntry", foreground=EntryText, background=FrameBG, relief=ButRelief) #cursor='sb_v_double_arrow'
root.style.configure("TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=FrameBG)
root.style.configure("TRadiobutton", foreground=ButtonText, background=FrameBG, indicatorcolor=FrameBG)
root.style.configure("TButton", foreground=ButtonText, background=FrameBG, highlightcolor=FrameBG, relief=ButRelief)
# define custom buttons
root.style.configure("TSpinbox", arrowsize=13) # only changes things in Python 3
root.style.configure("W3.TButton", width=3, relief=ButRelief)
root.style.configure("W4.TButton", width=4, relief=ButRelief)
root.style.configure("W5.TButton", width=5, relief=ButRelief)
root.style.configure("W6.TButton", width=6, relief=ButRelief)
root.style.configure("W7.TButton", width=7, relief=ButRelief)
root.style.configure("W8.TButton", width=8, relief=ButRelief)
root.style.configure("W9.TButton", width=9, relief=ButRelief)
root.style.configure("W10.TButton", width=10, relief=ButRelief)
root.style.configure("W11.TButton", width=11, relief=ButRelief)
root.style.configure("W16.TButton", width=16, relief=ButRelief)
root.style.configure("W17.TButton", width=17, relief=ButRelief)
root.style.configure("Stop.TButton", background=ButtonRed, foreground="#000000", width=4, relief=ButRelief)
root.style.configure("Run.TButton", background=ButtonGreen, foreground="#000000", width=4, relief=ButRelief)
root.style.configure("Pwr.TButton", background=ButtonGreen, foreground="#000000", width=8, relief=ButRelief)
root.style.configure("PwrOff.TButton", background=ButtonRed, foreground="#000000", width=8, relief=ButRelief)
root.style.configure("RConn.TButton", background=ButtonRed, foreground="#000000", width=5, relief=ButRelief)
root.style.configure("GConn.TButton", background=ButtonGreen, foreground="#000000", width=5, relief=ButRelief)
root.style.configure("Rtrace1.TButton", background=COLORtrace1, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace1.TButton", background=COLORtrace1, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("Ctrace1.TButton", background=COLORtrace1, foreground="#000000", relief=ButRelief)
root.style.configure("Rtrace2.TButton", background=COLORtrace2, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace2.TButton", background=COLORtrace2, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("Ctrace2.TButton", background=COLORtrace2, foreground="#000000", relief=ButRelief)
root.style.configure("Ctrace3.TButton", background=COLORtrace3, foreground="#000000", relief=ButRelief)
root.style.configure("Ctrace4.TButton", background=COLORtrace4, foreground="#000000", relief=ButRelief)

root.style.configure("A10B.TLabel", foreground=ButtonText, font="Arial 10 bold") # Black text
root.style.configure("A10R.TLabel", foreground=ButtonRed, font="Arial 10 bold") # Red text
root.style.configure("A10G.TLabel", foreground=ButtonGreen, font="Arial 10 bold") # Red text
root.style.configure("A12B.TLabel", foreground=ButtonText, font="Arial 12 bold") # Black text
root.style.configure("A16B.TLabel", foreground=ButtonText, font="Arial 16 bold") # Black text
root.style.configure("Stop.TRadiobutton", background=ButtonRed, indicatorcolor=FrameBG)
root.style.configure("Run.TRadiobutton", background=ButtonGreen, indicatorcolor=FrameBG)
root.style.configure("Disab.TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=ButtonRed)
root.style.configure("Enab.TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=ButtonGreen)
root.style.configure("Strace1.TCheckbutton", background=COLORtrace1, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("Strace2.TCheckbutton", background=COLORtrace2, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("WPhase.TRadiobutton", width=5, foreground="#000000", background="white", indicatorcolor=("red", "green"))
root.style.configure("GPhase.TRadiobutton", width=5, foreground="#000000", background="gray", indicatorcolor=("red", "green"))
#
label = Label(root, font = "Arial 16 bold")
label.grid(row=1, columnspan=3, sticky=W)
label.config(text = " ")
frame0 = Frame( root )
frame0.grid(row=2, column=0, sticky=W)
rb1 = Radiobutton(frame0, text="Stop", style="Stop.TRadiobutton", variable=RUNstatus, value=0 )
rb1.pack(side=LEFT)#.grid(row=2, column=0, sticky=W)
rb2 = Radiobutton(frame0, text="Run", style="Run.TRadiobutton", variable=RUNstatus, value=1 )
rb2.pack(side=LEFT)#.grid(row=2, column=1, sticky=W)
# Entry inputs for Meter Min and Max
frame1 = Frame( root )
frame1.grid(row=3, column=0, sticky=W)
MeterMinEntry = Entry(frame1, width=5, cursor='double_arrow')
#MeterMinEntry.bind("<Return>", BOffsetA)
MeterMinEntry.bind('<MouseWheel>', onMeterMinMax)# with Windows OS
MeterMinEntry.bind("<Button-4>", onMeterMinMax)# with Linux OS
MeterMinEntry.bind("<Button-5>", onMeterMinMax)
MeterMinEntry.bind('<Key>', onKeyMinMax)
MeterMinEntry.pack(side=LEFT)
MeterMinEntry.delete(0,"end")
MeterMinEntry.insert(0,Mmin)
MeterMinlab = Button(frame1, text="Meter Min", style="W9.TButton", command=donothing)# SetVAPoss)
MeterMinlab.pack(side=LEFT)
#
frame2 = Frame( root )
frame2.grid(row=4, column=0, sticky=W)
MeterMaxEntry = Entry(frame1, width=5, cursor='double_arrow')
#MeterMaxEntry.bind("<Return>", BOffsetA)
MeterMaxEntry.bind('<MouseWheel>', onMeterMinMax)# with Windows OS
MeterMaxEntry.bind("<Button-4>", onMeterMinMax)# with Linux OS
MeterMaxEntry.bind("<Button-5>", onMeterMinMax)
MeterMaxEntry.bind('<Key>', onKeyMinMax)
MeterMaxEntry.pack(side=LEFT)
MeterMaxEntry.delete(0,"end")
MeterMaxEntry.insert(0,Mmax)
MeterMaxlab = Button(frame1, text="Meter Max", style="W9.TButton", command=donothing)# SetVAPoss)
MeterMaxlab.pack(side=LEFT)
# input probe wigets
prlab = Label(root, text="Adjust Gain / Offset")
prlab.grid(row=5, column=0, sticky=W)
# Input Probes sub frame 
ProbeA = Frame( root )
ProbeA.grid(row=6, column=0, sticky=W)
gain1lab = Button(ProbeA, text="CA-V", width=4, style="Ctrace1.TButton", command=ReSetAGO) 
gain1lab.pack(side=LEFT,fill=X)
CHAVGainEntry = Entry(ProbeA, width=5, cursor='double_arrow')
CHAVGainEntry.bind('<Return>', onTextKey)
CHAVGainEntry.bind('<MouseWheel>', onTextScroll)
CHAVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVGainEntry.bind("<Button-5>", onTextScroll)
CHAVGainEntry.bind('<Key>', onTextKey)
CHAVGainEntry.pack(side=LEFT)
CHAVGainEntry.delete(0,"end")
CHAVGainEntry.insert(0,InGainA)
CHAVOffsetEntry = Entry(ProbeA, width=5, cursor='double_arrow')
CHAVOffsetEntry.bind('<Return>', onTextKey)
CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVOffsetEntry.bind("<Button-5>", onTextScroll)
CHAVOffsetEntry.bind('<Key>', onTextKey)
CHAVOffsetEntry.pack(side=LEFT)
CHAVOffsetEntry.delete(0,"end")
CHAVOffsetEntry.insert(0,InOffA)
#
ProbeB = Frame( root )
ProbeB.grid(row=7, column=0, sticky=W)
gain2lab = Button(ProbeB, text="CB-V", width=4, style="Ctrace2.TButton", command=ReSetBGO) 
gain2lab.pack(side=LEFT,fill=X)
CHBVGainEntry = Entry(ProbeB, width=5, cursor='double_arrow')
CHBVGainEntry.bind('<Return>', onTextKey)
CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
CHBVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVGainEntry.bind("<Button-5>", onTextScroll)
CHBVGainEntry.bind('<Key>', onTextKey)
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,InGainB)
CHBVOffsetEntry = Entry(ProbeB, width=5, cursor='double_arrow')
CHBVOffsetEntry.bind('<Return>', onTextKey)
CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVOffsetEntry.bind("<Button-5>", onTextScroll)
CHBVOffsetEntry.bind('<Key>', onTextKey)
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,InOffB)
#
ProbeC = Frame( root )
ProbeC.grid(row=8, column=0, sticky=W)
gain3lab = Button(ProbeC, text="CC-V", width=4, style="Ctrace3.TButton", command=ReSetCGO) 
gain3lab.pack(side=LEFT,fill=X)
CHCVGainEntry = Entry(ProbeC, width=5, cursor='double_arrow')
CHCVGainEntry.bind('<Return>', onTextKey)
CHCVGainEntry.bind('<MouseWheel>', onTextScroll)
CHCVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHCVGainEntry.bind("<Button-5>", onTextScroll)
CHCVGainEntry.bind('<Key>', onTextKey)
CHCVGainEntry.pack(side=LEFT)
CHCVGainEntry.delete(0,"end")
CHCVGainEntry.insert(0,InGainC)
CHCVOffsetEntry = Entry(ProbeC, width=5, cursor='double_arrow')
CHCVOffsetEntry.bind('<Return>', onTextKey)
CHCVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHCVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHCVOffsetEntry.bind("<Button-5>", onTextScroll)
CHCVOffsetEntry.bind('<Key>', onTextKey)
CHCVOffsetEntry.pack(side=LEFT)
CHCVOffsetEntry.delete(0,"end")
CHCVOffsetEntry.insert(0,InOffC)
#
# Define Analog Meter display for two indicators
Build_meter()
#
# Try to connect to hardware

Sucess = ConnectDevice()
#print("Channels = ", CHANNELS)
ConfigFileName = "analog-meter-config.cfg"
BLoadConfig(ConfigFileName) # load configuration from last session
#print("Channels = ", CHANNELS)
if Sucess:
    root.update()
    # Start sampling
    Analog_In()
#
else:
    root.update()
    showwarning("WARNING","Could Not Connect!")
    root.destroy()
    exit()

