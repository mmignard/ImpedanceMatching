# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 10:00:16 2023

@author: MarcMignard
ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρσςτυφχψωάέήϊίόύϋώΆΈΉΊΌΎΏ±≥≤ΪΫ÷≈°√ⁿ²ˑ
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
length = 0.5    #length in units of rise time
nX = 50         #number of simulation steps in distance dimension
nT = 100        #number of simulation steps in time dimension. Generally this needs to be > nX
endT = 20       #simulation end time in units of propagation delay along total length
maxV = 1        #maximum drive voltage
zTrace = 100    #characteristic impedance of transmission line
zSrc = 100      #source impedance
zTerm = 1e6     #load termination impedance
sRise = np.linspace(0,endT/2,int(nT/2))
#srcDrv contains both a rising edge and a falling edge
srcDrv = np.clip(np.concatenate((maxV*sRise,maxV*(1-sRise))),0,maxV)
t = np.linspace(0,endT,nT)

#show what the source drive waveform looks like
plt.figure()
plt.plot(t,srcDrv)
plt.show()

##########################################################################
###  Subplots of voltage versus time
###     
##########################################################################
params = [[221,0.25,100],[222,0.5,100],[223,0.25,20],[224,0.5,20]] #[subplot,length,zSrc]
plt.figure(figsize=(8,8),dpi=150)
plt.suptitle(f'Voltage versus time of several stub lengths and source impedances, zTrace={zTrace}')

for i in range(len(params)):
    length = params[i][1]     #length in units of rise time
    zSrc = params[i][2]       #source impedance
    totalWave = MakeWaves(srcDrv,zSrc,zTrace,zTerm,length,nX,endT)
    Vovershoot = maxV*2/(1+zSrc/zTrace)   
    Vundershoot = maxV*2/(1+zSrc/zTrace)*(1+(zSrc-zTrace)/(zSrc+zTrace))
    plt.subplot(params[i][0])
    plt.title(f'length={length}, zSrc={zSrc}')
    plt.plot(t,totalWave[:,-1],'--',label='load')
    plt.plot(t,totalWave[:,int(nX/4)],label='mid 1/4')
    plt.plot(t,totalWave[:,0],':',label='source')
    plt.plot([0,t[-1]],[Vovershoot,Vovershoot],'k:')
    plt.plot([0,t[-1]],[Vundershoot,Vundershoot],'k:')
    plt.xlim([-0.1,t[-1]+0.1])
    plt.ylim([-0.8,maxV*1.8])
    plt.grid(True)
    plt.legend()
    if i==0 or i==2:
        plt.ylabel('voltage')
    if i==2 or i==3:
        plt.xlabel('time (units of rise time)')
plt.savefig('./media/reflections.svg', bbox_inches='tight')
plt.show()

##########################################################################
###   Animation plot of voltage versus position
###     
##########################################################################
zSrc=20
zTrace=100
xOne = np.linspace(0,1,nX)
waveOne = MakeWaves(srcDrv,zSrc,zTrace,zTerm,1,nX,endT)
xHalf = np.linspace(0,0.5,nX)
waveHalf = MakeWaves(srcDrv,zSrc,zTrace,zTerm,0.5,nX,endT)
xThird = np.linspace(0,0.33,nX)
waveThird = MakeWaves(srcDrv,zSrc,zTrace,zTerm,0.33,nX,endT)
xQuarter = np.linspace(0,0.25,nX)
waveQuarter = MakeWaves(srcDrv,zSrc,zTrace,zTerm,0.25,nX,endT)

def updateline(num, waveOne, axOne, waveHalf, axHalf, waveThird, axThird, waveQuarter, axQuarter):
    axOne.set_data(xOne,waveOne[num,:])
    axHalf.set_data(xHalf,waveHalf[num,:]+1)
    axThird.set_data(xThird,waveThird[num,:]+2)
    axQuarter.set_data(xQuarter,waveQuarter[num,:]+3)
    #time_text.set_text("Points: %.0f" % int(num))
    return axOne,axHalf, axThird, axQuarter

fig, ax = plt.subplots(figsize=(4,4),dpi=150)
plt.grid(True)
plt.title(f'Voltage versus position of several stub lengths,\nzSrc={zSrc}, zTrace={zTrace}')
#plt.title(f'zSrc={zSrc}, zTrace={zTrace}')
plt.xlabel('position (units of tRise*vPropagation)')
plt.ylabel('voltage')

ax.set_ylim(-0.8, 4.2)
ax.set_xlim(0, 1)
axOne = ax.plot([], [], 'r-', label="One")[0]
axHalf = ax.plot([], [], 'g-', label="Half")[0]
axThird = ax.plot([], [], 'b-', label="Third")[0]
axQuarter = ax.plot([], [], 'k-', label="Quarter")[0]

#For animations to work in Spyder IDE, have to run '%matplotlib qt5', switch back with '%matplotlib inline'
#Change to interval=10 to save video. Real time animation runs slower, so use interval=5
anim = animation.FuncAnimation(fig, updateline, frames=waveHalf.shape[0], interval=5, blit=True, fargs=(waveOne, axOne, waveHalf, axHalf, waveThird, axThird, waveQuarter, axQuarter))

#Steps required to create html5 videos:
#  1) pip install ffmpeg-python
#  2) download and install ffmpeg from https://www.ffmpeg.org/download.html
#  3) add path to ffmpgeg.exe using "edit ENV"
#  4) in new cmd window, type "ffmpeg -version" to make sure it works
#printing to file takes a long time
#ffmpeg is not required just to view the files
# with open(f"./media/StubsVideoSrc{zSrc}.html", "w") as f:
#     print(anim.to_html5_video(), file=f)

# To save the animation using Pillow as a gif (pip install Pillow)
writer = animation.PillowWriter(fps=60,
                                metadata=dict(artist='Me'),
                                bitrate=1800)
anim.save(f"./media/StubsVideoSrc{zSrc}.gif", writer=writer)

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
    