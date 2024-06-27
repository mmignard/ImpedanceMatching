# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 08:36:00 2023

@author: MarcMignard
ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρσςτυφχψωάέήϊίόύϋώΆΈΉΊΌΎΏ±≥≤ΪΫ÷≈°√ⁿ²ˑ
"""

import numpy as np
import matplotlib.pyplot as plt
from PyLTSpice import RawRead
from PyLTSpice import SimCommander
#have to run 'pip install pyltspice' to use these
#documentation is at https://pyltspice.readthedocs.io/en/latest/
#more info and source code is at https://github.com/nunobrum/PyLTSpice

##########################################################################
###  point-to-point transmission line
###  
##########################################################################

fn = '.\\LTSpice\\singleTrace'
tRise = 1               #rise time in nS
fracToMid = 1/4         #fraction of total length until signal is sampled (using two Tlines so can see voltage at this point)
tdT1 = fracToMid*tRise  #propagation delay of first transmission line
tdT2 = tRise - tdT1     #propagation delay of second transmission line
tStart = 10             #little delay at beginning of simulation, probably not necessary
tEnd = tStart+10*tRise  #length of simulation
zSource = 20            #impedance of source
zTrace = 100            #impedance of transmission lines
zTermination = 1e6      #impedance of termination

def RunSim(fn,tdT1,tdT2,zSource=20,zTrace=100,zTerm=1e6):
    LTC = SimCommander(fn+'.asc')
    LTC.set_component_value('RS', f'{zSource}')
    LTC.set_component_value('RL', f'{zTermination}')
    LTC.set_element_model('T1', f'Td={tdT1}n Z0={zTrace}')
    LTC.set_element_model('T2', f'Td={tdT2}n Z0={zTrace}')
    LTC.set_element_model('V1', f'PULSE(0 1 {tStart}n {tRise}n {tRise}n 380n 800n 10)')
    LTC.add_instructions(f'.tran {tEnd}n')
    LTC.run()
    LTC.wait_completion()
    
def PlotTraces(fn):    
    LTR = RawRead(fn+'_1.raw')
    VVL = LTR.get_trace('V(vl)')
    VVS = LTR.get_trace('V(vs)')
    VVM = LTR.get_trace('V(vm)')
    x = LTR.get_trace('time')  # Gets the time axis
    steps = LTR.get_steps()
    for step in range(len(steps)):
        plt.plot((x.get_time_axis(step)*1e9-tStart)/tRise, VVS.get_wave(step),':', label='source')
    for step in range(len(steps)):
        plt.plot((x.get_time_axis(step)*1e9-tStart)/tRise, VVM.get_wave(step), label='middle')
    for step in range(len(steps)):
        plt.plot((x.get_time_axis(step)*1e9-tStart)/tRise, VVL.get_wave(step),'--', label='load')

plt.figure(figsize=(5,8),dpi=150)
if zTermination > 1000:
    plt.suptitle(f'impedance mismatch reflections\nzSrc={zSource}Ω, zTrace={zTrace}Ω, zTerm=open')
else:    
    plt.suptitle(f'impedance mismatch reflections\nzSrc={zSource}Ω, zTrace={zTrace}Ω, zTerm={zTermination}Ω')

lengths = np.asarray([1,0.5,0.33,0.25])
for L in np.arange(lengths.size):
    plt.subplot(lengths.size,1,L+1)
    lenTotal = lengths[L] #total transmission line length as a fraction of rise time
    RunSim(fn,lenTotal*tdT1,lenTotal*tdT2,zSource,zTrace)
    PlotTraces(fn)
    plt.grid(True)
    if 0==L:
        plt.ylabel('voltage (source=1V)')
    plt.xlim(0,10)
    plt.ylim(0,1.75)
    plt.text(1.8,0.1,f'length = {lenTotal}*rise')

plt.legend()
plt.xlabel('time (scaled by rise time)')
#plt.savefig('singleTrace.svg', bbox_inches='tight')
#plt.savefig('singleTrace.jpg', bbox_inches='tight')
plt.show()

##########################################################################
###  max under/overshoot
###  
##########################################################################

plt.figure(figsize=(5,4),dpi=150)
plt.suptitle(f'worst case under/overshoot\nzTrace={zTrace}Ω, zTerm=open')

zSrc = np.asarray([100,20])
for z in np.arange(zSrc.size):
    plt.subplot(zSrc.size,1,z+1)
    lenTotal = 0.5 #total transmission line length as a fraction of rise time
    zSource = zSrc[z]
    RunSim(fn,lenTotal*tdT1,lenTotal*tdT2,zSource,zTrace)
    LTR = RawRead(fn+'_1.raw')    
    VVL = LTR.get_trace('V(vl)')
    x = LTR.get_trace('time')  # Gets the time axis
    steps = LTR.get_steps()
    for step in range(len(steps)):
        plt.plot((x.get_time_axis(step)*1e9-tStart)/tRise, VVL.get_wave(step))
    plt.grid(True)
    plt.xlim(0,10)
    plt.ylim(0,1.75)
    plt.text(1.8,0.1,f'length = {lenTotal}*rise, zSrc={zSource}Ω')
    if 0==z:
        plt.ylabel('voltage (source=1V)')
    if zSource<zTrace:
        overshoot = 2/(1+zSource/zTrace)
        undershoot = 2/(1+zSource/zTrace)*(1+(zSource-zTrace)/(zSource+zTrace))
        plt.plot([1.5,4],[overshoot,overshoot],'k:')    
        plt.plot([2.5,4],[undershoot,undershoot],'k:')    
        plt.text(4,overshoot-0.05,f'{overshoot:.2f}')
        plt.text(4,undershoot-0.05,f'{undershoot:.2f}')

#plt.legend()
plt.xlabel('time (scaled by rise time)')
#plt.savefig('overshoot.svg', bbox_inches='tight')
#plt.savefig('overshoot.jpg', bbox_inches='tight')
plt.show()

##########################################################################
###  point-to-point transmission line, source series RC termination
###  
##########################################################################

fn = 'singleTrace_RCsrc'
tRise = 1               #rise time in nS
fracToMid = 1/4         #fraction of total length until signal is sampled (using two Tlines so can see voltage at this point)
tdT1 = fracToMid*tRise  #propagation delay of first transmission line
tdT2 = tRise - tdT1     #propagation delay of second transmission line
tStart = 10             #little delay at beginning of simulation, probably not necessary
tEnd = tStart+50*tRise  #length of simulation
zSource =100            #impedance of source
zTrace = 100            #impedance of transmission lines
zTermination = 1e6      #impedance of termination

def RunSim(fn,tdT1,tdT2,zSource=20,zTrace=100,zTerm=1e6,CS=10):
    LTC = SimCommander(fn+'.asc')
    LTC.set_component_value('RS', f'{zSource}')
    LTC.set_component_value('CS', f'{CS}p')
    LTC.set_component_value('RL', f'{zTermination}')
    LTC.set_element_model('T1', f'Td={tdT1}n Z0={zTrace}')
    LTC.set_element_model('T2', f'Td={tdT2}n Z0={zTrace}')
    LTC.set_element_model('V1', f'PULSE(0 1 {tStart}n {tRise}n {tRise}n 380n 800n 10)')
    LTC.add_instructions(f'.tran {tEnd}n')
    LTC.run()
    LTC.wait_completion()
    
plt.figure(figsize=(5,8),dpi=150)
if zTermination > 1000:
    plt.suptitle(f'Source series RC termination\nzSrc={zSource}Ω, zTrace={zTrace}Ω, zTerm=open')
else:    
    plt.suptitle(f'Source series RC termination\nzSrc={zSource}Ω, zTrace={zTrace}Ω, zTerm={zTermination}Ω')

CSs = np.asarray([1,10,50,100])
for cs in np.arange(CSs.size):
    plt.subplot(CSs.size,1,cs+1)
    lenTotal = 2 #total transmission line length as a fraction of rise time
    RunSim(fn,lenTotal*tdT1,lenTotal*tdT2,zSource,zTrace,1e6,CSs[cs])
    PlotTraces(fn)
    plt.grid(True)
    if 0==cs:
        plt.ylabel('voltage (source=1V)')
        plt.annotate('Worrisome transition', xy=(3.5,0.5), xytext=(7.5,0.75), arrowprops=dict(facecolor='black', width=1, headwidth=5, headlength=8))
    plt.xlim(0,20)
    plt.ylim(0,1.25)
    plt.text(5,0.1,f'CS = {CSs[cs]}pF')

plt.legend()
plt.xlabel('time (scaled by rise time)')
#plt.savefig('sourceRCterm.svg', bbox_inches='tight')
#plt.savefig('sourceRCterm.jpg', bbox_inches='tight')
plt.show()

##########################################################################
###  mistune source series resistor
###  
##########################################################################


fn = 'singleTrace'
tRise = 1               #rise time in nS
fracToMid = 1/4         #fraction of total length until signal is sampled (using two Tlines so can see voltage at this point)
tdT1 = fracToMid*tRise  #propagation delay of first transmission line
tdT2 = tRise - tdT1     #propagation delay of second transmission line
tStart = 10             #little delay at beginning of simulation, probably not necessary
tEnd = tStart+50*tRise  #length of simulation
zSource =100            #impedance of source
zTrace = 100            #impedance of transmission lines
zTermination = 1e6      #impedance of termination

def RunSim(fn,tdT1,tdT2,zSource=20,zTrace=100,zTerm=1e6):
    LTC = SimCommander(fn+'.asc')
    LTC.set_component_value('RS', f'{zSource}')
    LTC.set_component_value('RL', f'{zTermination}')
    LTC.set_element_model('T1', f'Td={tdT1}n Z0={zTrace}')
    LTC.set_element_model('T2', f'Td={tdT2}n Z0={zTrace}')
    LTC.set_element_model('V1', f'PULSE(0 1 {tStart}n {tRise}n {tRise}n 380n 800n 10)')
    LTC.add_instructions(f'.tran {tEnd}n')
    LTC.run()
    LTC.wait_completion()
    
plt.figure(figsize=(5,8),dpi=150)
if zTermination > 1000:
    plt.suptitle(f'Detune source term to avoid invalid\ndigital voltage, zTrace={zTrace}Ω, zTerm=open')
else:    
    plt.suptitle(f'Source series RC termination\nzSrc={zSource}Ω, zTrace={zTrace}Ω, zTerm={zTermination}Ω')

zSrc = np.asarray([100,40,30,20])
for z in np.arange(zSrc.size):
    plt.subplot(zSrc.size,1,z+1)
    lenTotal = 2 #total transmission line length as a fraction of rise time
    zSource = zSrc[z]
    RunSim(fn,lenTotal*tdT1,lenTotal*tdT2,zSource,zTrace,1e6)
    PlotTraces(fn)
    plt.plot([0,11],[0.8,0.8],'k:')   
    plt.text(11,0.7,'0.8')
    plt.grid(True)
    if 0==z:
        plt.ylabel('voltage (source=1V)')        
        #plt.annotate('Worrisome transition', xy=(3.5,0.5), xytext=(7.5,0.75), arrowprops=dict(facecolor='black', width=1, headwidth=5, headlength=8))
    plt.xlim(0,20)
    plt.ylim(0,1.75)
    plt.text(5,0.1,f'zSrc = {zSource}Ω')

plt.legend()
plt.xlabel('time (scaled by rise time)')
#plt.savefig('srcTermDetune.svg', bbox_inches='tight')
#plt.savefig('srcTermDetune.jpg', bbox_inches='tight')
plt.show()


##########################################################################
###  load R termination
###  
##########################################################################


fn = 'singleTrace'
tRise = 1               #rise time in nS
fracToMid = 1/4         #fraction of total length until signal is sampled (using two Tlines so can see voltage at this point)
tdT1 = fracToMid*tRise  #propagation delay of first transmission line
tdT2 = tRise - tdT1     #propagation delay of second transmission line
tStart = 10             #little delay at beginning of simulation, probably not necessary
tEnd = tStart+20*tRise  #length of simulation
zSource = 20            #impedance of source
zTrace = 100            #impedance of transmission lines
zTermination = 1e6      #impedance of termination
    
plt.figure(figsize=(5,8),dpi=150)
plt.suptitle(f'Parallel load termination\nzSrc={zSource}Ω, zTrace={zTrace}Ω')

zTerm = np.asarray([1000,500,200,100])
for z in np.arange(zSrc.size):
    plt.subplot(zSrc.size,1,z+1)
    lenTotal = 2 #total transmission line length as a fraction of rise time
    zTermination = zTerm[z]
    RunSim(fn,lenTotal*tdT1,lenTotal*tdT2,zSource,zTrace,zTermination)
    PlotTraces(fn)
    plt.plot([0,11],[0.8,0.8],'k:')   
    plt.text(11,0.7,'0.8')
    plt.grid(True)
    if 0==z:
        plt.ylabel('voltage (source=1V)')        
        #plt.annotate('Worrisome transition', xy=(3.5,0.5), xytext=(7.5,0.75), arrowprops=dict(facecolor='black', width=1, headwidth=5, headlength=8))
    plt.xlim(0,20)
    plt.ylim(0,1.75)
    plt.text(5,0.1,f'zTerm = {zTermination}Ω')

plt.legend(loc='lower right')
plt.xlabel('time (scaled by rise time)')
#plt.savefig('parLoadTerm.svg', bbox_inches='tight')
#plt.savefig('parLoadTerm.jpg', bbox_inches='tight')
plt.show()

##########################################################################
###  load RC termination
###  
##########################################################################

fn = 'singleTrace_loadRC'
tRise = 1               #rise time in nS
fracToMid = 1/4         #fraction of total length until signal is sampled (using two Tlines so can see voltage at this point)
tdT1 = fracToMid*tRise  #propagation delay of first transmission line
tdT2 = tRise - tdT1     #propagation delay of second transmission line
tStart = 10             #little delay at beginning of simulation, probably not necessary
tEnd = tStart+50*tRise  #length of simulation
zSource =20             #impedance of source
zTrace = 100            #impedance of transmission lines
zTermination = 100      #impedance of termination

def RunSim(fn,tdT1,tdT2,zSource=20,zTrace=100,zTerm=1e6,CL=10):
    LTC = SimCommander(fn+'.asc')
    LTC.set_component_value('RS', f'{zSource}')
    LTC.set_component_value('CL', f'{CL}p')
    LTC.set_component_value('RL', f'{zTermination}')
    LTC.set_element_model('T1', f'Td={tdT1}n Z0={zTrace}')
    LTC.set_element_model('T2', f'Td={tdT2}n Z0={zTrace}')
    LTC.set_element_model('V1', f'PULSE(0 1 {tStart}n {tRise}n {tRise}n 380n 800n 10)')
    LTC.add_instructions(f'.tran {tEnd}n')
    LTC.run()
    LTC.wait_completion()
    
plt.figure(figsize=(5,8),dpi=150)
if zTermination > 1000:
    plt.suptitle(f'Parallel load RC termination\nzSrc={zSource}Ω, zTrace={zTrace}Ω, zTerm=open')
else:    
    plt.suptitle(f'Parallel load RC termination\nzSrc={zSource}Ω, zTrace={zTrace}Ω, zTerm={zTermination}Ω')

CLs = np.asarray([1,10,50,100])
for cl in np.arange(CLs.size):
    plt.subplot(CLs.size,1,cl+1)
    lenTotal = 2 #total transmission line length as a fraction of rise time
    RunSim(fn,lenTotal*tdT1,lenTotal*tdT2,zSource,zTrace,1e6,CLs[cl])
    PlotTraces(fn)
    plt.plot([0,11],[0.8,0.8],'k:')   
    plt.text(11,0.7,'0.8')
    plt.grid(True)
    if 0==cl:
        plt.ylabel('voltage (source=1V)')
        #plt.annotate('Worrisome transition', xy=(3.5,0.5), xytext=(7.5,0.75), arrowprops=dict(facecolor='black', width=1, headwidth=5, headlength=8))
    if (CLs.size-1)==cl:
        plt.annotate('Worrisome transition', xy=(2,0.85), xytext=(4,1.3), arrowprops=dict(facecolor='black', width=1, headwidth=5, headlength=8))
    plt.xlim(0,20)
    plt.ylim(0,1.75)
    plt.text(5,0.1,f'CL = {CLs[cl]}pF')

plt.legend()
plt.xlabel('time (scaled by rise time)')
#plt.savefig('parLoadRCterm.svg', bbox_inches='tight')
#plt.savefig('parLoadRCterm.jpg', bbox_inches='tight')
plt.show()

##########################################################################
###  stubs
###  
##########################################################################
