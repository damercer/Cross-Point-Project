# Cross Point Project
Software-Configured Breadboard Hardware Targeting Circuit Wiring Error Reduction in ECE Labs.
#
Abstract:
#
The hardware project aims to examine the effectiveness of software-configured wiring compared to traditional manual wiring of breadboards. While both methods use actual hardware, the software-configured approach automates the connections between components, thereby minimizing wiring errors and setup time. The intent is to investigate the impact of each approach on student comprehension, engagement, and error rates. By comparing these two approaches, the project seeks to determine which method better supports student engagement, educational outcomes and reduces frustration associated with complex circuit construction.
#
Introduction:
#
Hands-on experiential learning is a cornerstone of ECE education, typically relying on manual wiring of circuits on solderless breadboards. Using a traditional solderless breadboard as the means for building electronic circuit lab experiments requires the student, in addition to placing components, to manually insert wires to connect together the component pins according to a schematic diagram. These manual translation steps from schematic to hardware can lead to wiring errors in the experimental setup that can obscure circuit principles. While this manual wiring method offers valuable experience in physical component handling and troubleshooting, the extra time needed for debugging and correcting these errors leads to frustration and loss of precious lab time to investigate the circuit concept in question.

The goal is to evaluate the educational benefits and potential drawbacks of these software-configured hardware systems compared to traditional manual wiring. By doing so, it addresses the need for balancing hands-on skills with error minimization and conceptual understanding in electrical engineering education.
#
Analog switch matrix cross point experiment breadboard.
#
![Screenshot Prototype PCB](/Red1-Board-final.jpg)
Prototype PCB (Red version)
 
The idea is to computerize the wiring of the breadboard in an effort to reduce student frustration when building complex experiments. Using four analog 16X8 cross point switches wired together into two 32X8 cross points with a fifth switch matrix interconnecting the two smaller arrays into effectively a single 64X16 array.

This breadboard makes real, hardware connections between the 64 breadboard component pins on the board to the16 “jumper” nodes on the board via software commands, instead of needing to manually install jumper wires. The prototype PCB is shown, figure 1, which incorporates two mini 170 pin solderless breadboards, one for each of the 32X8 cross point arrays. There are a combined 68 total component pin locations across both mini breadboards with power distribution strips top and bottom. The two mini breadboards connect to the PCB through pogo pins and so they can be easily removed. It would then be possible to bolt on custom daughter PCBs with whatever components are needed for a given course already installed. Such as CMOS transistor arrays (CD4007) with even some pre-wired sub-circuits like current sources and OTAs.

The combined 64X16 cross point matrix board uses a total of 5 CH446DS 16X8 analog cross point ICs (from China) programed via a RP-2040 micro controller breakout board (Pi Pico or equivalent). Materials cost per board, in quantities of 10 or more, is less than $30 not including the assembly labor.

The board is powered from the Pi Pico USB connection. For powering the experiment circuits, male Pin Jumpers can be set for 0 and +3.3V, 0 and +5V or -5V and +5V power (or 0 and +10V) using an on board isolated 5V DC-DC generator.

LTspice is used to enter the schematic for the experiment. In addition to the standard library symbols a number of supporting schematic library files have been created. Schematic symbols for TO-92 transistors and resistors of various lead spacing are available in the LTspice files. 

