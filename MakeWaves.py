# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 10:00:16 2023

@author: MarcMignard
ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρσςτυφχψωάέήϊίόύϋώΆΈΉΊΌΎΏ±≥≤ΪΫ÷≈°√ⁿ²ˑ∂
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
#For animations to work in Spyder IDE, have to run '%matplotlib qt5', switch back with '%matplotlib inline'

##########################################################################
###   This code implements the d'Alembert solution to the 1-dimensional lossless wave equation
###   wave equation: https://en.wikipedia.org/wiki/Wave_equation and https://en.wikipedia.org/wiki/Telegrapher%27s_equations
###   d'Alembert solution: https://en.wikipedia.org/wiki/D%27Alembert%27s_formula
##########################################################################

def MakeWaves(srcDrv,zSrc,zTrace,zTerm,length,nX,endT):
    rightWave = np.zeros(nX+2)    #wave going in direction from source to load
    leftWave = np.zeros(nX+2)     #wave going in direction from load to source
    nT = srcDrv.size              #number of time steps
    totalWave = np.zeros((nT,nX)) #array to return
    x = np.linspace(-1/(nX-1),1+1/(nX-1),nX+2)*length
    #The points on the left and right of x are one simulation time step away from the physical line
    #This allows simple linear interpolation to update the simulation step
    velocity = 1 #by definition
    x[0] = -velocity*endT/nT
    x[-1] = length + velocity*endT/nT
    
    #for all the time steps in the simulation
    for tIdx in np.arange(nT):
        temp = rightWave[-1] #need to save this before updating rightWave
        #at the beginning is both the source (through the zSrc/zTrace voltage divider), and the reflection from the left-going wave
        rightWave[0] = srcDrv[tIdx]/(1+zSrc/zTrace) + leftWave[0]*(zSrc-zTrace)/(zSrc+zTrace) 
        rightWave = np.interp(x-endT/nT,x,rightWave)
        #at the end is the reflection from the right-going wave
        leftWave[-1] = temp*(zTerm-zTrace)/(zTerm+zTrace)
        leftWave =  np.interp(x+endT/nT,x,leftWave)
        totalWave[tIdx,:] = rightWave[1:-1] + leftWave[1:-1]
    return totalWave

#rise time and velocity are one unit by definition
zSrc = 100      #source impedance
zTrace = 100    #characteristic impedance of transmission line
zTerm = 1e6     #load termination impedance
length = 0.5    #length in units of rise time
nX = 1000       #number of simulation steps in distance dimension
nT = 2000       #number of simulation steps in time dimension. Generally this needs to be > nX
endT = 20       #simulation end time in units of propagation delay along total length
maxV = 1        #maximum drive voltage
sRise = np.linspace(0,endT/2,int(nT/2))
#srcDrv contains both a rising edge and a falling edge
srcDrv = np.clip(np.concatenate((maxV*sRise,maxV*(1-sRise))),0,maxV)
t = np.linspace(0,endT,nT)

#show what the source drive waveform looks like
# plt.figure()
# plt.plot(t,srcDrv)
# plt.show()

##########################################################################
###  Subplots of voltage versus time
###     
##########################################################################
params = [[321,0.25,20,'fine everywhere'],[322,0.25,100,'fine everywhere'],
          [323,0.5,20,'undershoot bad'],[324,0.5,100,'fine everywhere'],
          [325,1,20,'undershoot bad'],[326,1,100,'load ok, problem near source']] #[subplot,length,zSrc]
plt.figure(figsize=(8,8),dpi=150)
plt.suptitle(f'Voltage versus time of several stub lengths and source impedances, zTrace={zTrace}', y=0.92)

for i in range(len(params)):
    length = params[i][1]     #length in units of rise time
    zSrc = params[i][2]       #source impedance
    totalWave = MakeWaves(srcDrv,zSrc,zTrace,zTerm,length,nX,endT)
    Vovershoot = maxV*2/(1+zSrc/zTrace)   
    Vundershoot = maxV*2/(1+zSrc/zTrace)*(1+(zSrc-zTrace)/(zSrc+zTrace))
    plt.subplot(params[i][0])
    #plt.title(f'length={length}, zSrc={zSrc}')
    plt.plot(t,totalWave[:,-1],'--',label='load')
    plt.plot(t,totalWave[:,int(nX/2)],label='middle')
    plt.plot(t,totalWave[:,0],':',label='source')
    plt.xlim([-0.1,t[-1]+0.1])
    plt.ylim([-0.8,maxV*1.8])
    plt.grid(True)
    plt.legend(loc='upper right')
    plt.text(0.1,-0.7,f'length={length}, zSrc={zSrc}')
    plt.text(0.1,-0.4,params[i][3])
    if i==2:
        plt.annotate('', xy=(2.5,Vundershoot), xytext=(2,-0.2), arrowprops=dict(facecolor='black', width=1, headwidth=5, headlength=8))
    if i==4:
        plt.annotate('', xy=(4,Vundershoot), xytext=(2.5,-0.2), arrowprops=dict(facecolor='black', width=1, headwidth=5, headlength=8))
    if i==5:
        plt.annotate('', xy=(2,0.5), xytext=(4,-0.2), arrowprops=dict(facecolor='black', width=1, headwidth=5, headlength=8))
    if i%2==0:
        plt.ylabel('voltage')
        #plt.plot([0,t[-1]],[Vovershoot,Vovershoot],'k:')
        #plt.plot([0,t[-1]],[Vundershoot,Vundershoot],'k:')
    if i==4 or i==5:
        plt.xlabel('time (units of rise time)')
plt.savefig('./media/reflections.svg', bbox_inches='tight')
plt.show()

##########################################################################
###   Animation plot of voltage versus position
###     
##########################################################################
'''
Need large nX=1000,nT=2000 for simulation of voltage vs time to match LTSpice.
But want small nX=50,nT=100 to make reasonable sized animated GIFs of voltage vs position.
'''
zSrc = 100      #source impedance
zTrace = 100    #characteristic impedance of transmission line
zTerm = 1e6     #load termination impedance
nX = 50         #number of simulation steps in distance dimension
nT = 100        #number of simulation steps in time dimension. Generally this needs to be > nX
endT = 20       #simulation end time in units of propagation delay along total length
maxV = 1        #maximum drive voltage
sRise = np.linspace(0,endT/2,int(nT/2))
#srcDrv contains both a rising edge and a falling edge
srcDrv = np.clip(np.concatenate((maxV*sRise,maxV*(1-sRise))),0,maxV)
t = np.linspace(0,endT,nT)

xOne = np.linspace(0,1,nX)
waveOne20 = MakeWaves(srcDrv,20,zTrace,zTerm,1,nX,endT)
waveOne100 = MakeWaves(srcDrv,100,zTrace,zTerm,1,nX,endT)
xHalf = np.linspace(0,0.5,nX)
waveHalf20 = MakeWaves(srcDrv,20,zTrace,zTerm,0.5,nX,endT)
waveHalf100 = MakeWaves(srcDrv,100,zTrace,zTerm,0.5,nX,endT)
xQuarter = np.linspace(0,0.25,nX)
waveQuarter20 = MakeWaves(srcDrv,20,zTrace,zTerm,0.25,nX,endT)
waveQuarter100 = MakeWaves(srcDrv,100,zTrace,zTerm,0.25,nX,endT)

def updateline(num, axOne20, axHalf20, axQuarter20, waveOne20, waveHalf20, waveQuarter20, 
               axOne100, axHalf100, axQuarter100, waveOne100, waveHalf100, waveQuarter100):
    axOne20.set_data(xOne,waveOne20[num,:])
    axHalf20.set_data(xHalf,waveHalf20[num,:]+1)
    axQuarter20.set_data(xQuarter,waveQuarter20[num,:]+2)
    axOne100.set_data(xOne,waveOne100[num,:])
    axHalf100.set_data(xHalf,waveHalf100[num,:]+1)
    axQuarter100.set_data(xQuarter,waveQuarter100[num,:]+2)
    #time_text.set_text("Points: %.0f" % int(num))
    return axOne20,axHalf20,axQuarter20,axOne100,axHalf100,axQuarter100

fig, (ax20, ax100) = plt.subplots(1,2,figsize=(7,4),dpi=150)
plt.suptitle(f'Voltage versus position, zTrace={zTrace}') #, y=0.92)
plt.subplot(121)
plt.title(f'zSrc=20')
plt.grid(True)
plt.xlabel('position (units of tRiseˑvelocity)')
plt.ylabel('voltage')

plt.subplot(122)
plt.title(f'zSrc=100')
plt.grid(True)
plt.xlabel('position (units of tRiseˑvelocity)')

ax20.set_ylim(-0.8, 3.5)
ax20.set_xlim(0, 1)
ax100.set_ylim(-0.8, 3.5)
ax100.set_xlim(0, 1)
axOne20 = ax20.plot([], [], 'r-', label="One")[0]
axHalf20 = ax20.plot([], [], 'b-', label="Half")[0]
axQuarter20 = ax20.plot([], [], 'k-', label="Quarter")[0]
axOne100 = ax100.plot([], [], 'r-', label="One")[0]
axHalf100 = ax100.plot([], [], 'b-', label="Half")[0]
axQuarter100 = ax100.plot([], [], 'k-', label="Quarter")[0]

#For animations to work in Spyder IDE, have to run '%matplotlib qt5', switch back with '%matplotlib inline'
#Change to interval=10 to save video. Real time animation runs slower, so use interval=5
anim = animation.FuncAnimation(fig, updateline, frames=waveHalf20.shape[0], interval=10, blit=True, fargs=(axOne20, axHalf20, axQuarter20, waveOne20, waveHalf20, waveQuarter20, 
               axOne100, axHalf100, axQuarter100, waveOne100, waveHalf100, waveQuarter100))

#Steps required to create html5 videos:
#  1) pip install ffmpeg-python
#  2) download and install ffmpeg from https://www.ffmpeg.org/download.html
#  3) add path to ffmpgeg.exe using "edit ENV"
#  4) in new cmd window, type "ffmpeg -version" to make sure it works
# printing to file takes a long time
# ffmpeg is not required just to view the files
# with open(f"./media/StubsVideo.html", "w") as f:
#     print(anim.to_html5_video(), file=f)

# To save the animation using Pillow as a gif (pip install Pillow)
# writer = animation.PillowWriter(fps=60,
#                                 metadata=dict(artist='Me'),
#                                 bitrate=1800)
# anim.save(f"./media/StubsVideo.gif", writer=writer)

plt.show()

##########################################################################
###   Drawings to explain code and equations
###     
##########################################################################

#pip install schemdraw, pip install schemdraw[svgmath]
import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing():
    Rleft = elm.Resistor().label('Rleft')
    #elm.Line().up()
    #elm.Line().right()
    #elm.Tag().label('Vmid')
    Rright = elm.Resistor().label('Rright')
    elm.SourceV().down().label('Vright')
    elm.Line().left()
    elm.Line().left()
    elm.Ground()
    elm.SourceV().up().label('Vleft')
    #elm.Tag().at(Rright).label('Vmid')
    #elm.Tag().at(Rright).label('Vmid').left()
    
with schemdraw.Drawing():
    elm.SourceV().up().label('Vsrc')
    elm.Resistor().label('Rsrc')
    #elm.Line().up()
    #elm.Line().right()
    #elm.Tag().label('Vmid')
    Rright = elm.Resistor().label('Rright')
    elm.SourceV().down().label('Vright')
    elm.Line().left()
    elm.Line().left()
    elm.Ground()
    elm.SourceV().up().label('Vleft')
    #elm.Tag().at(Rright).label('Vmid')
    