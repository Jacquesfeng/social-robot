#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 13:23:32 2017

@author: fengjacques
"""

import math
import matplotlib.pyplot as plt
import numpy as np

from firebase import firebase

def readfromfirebase():

    Cx=[];Cy=[];Cz=[];Calpha=[];Cbeta=[]; Cgamma=[];Ctime=[]        
    for data in result:
        Cx.append(data['x'])
        Cy.append(data['y'])
        Cz.append(data['z'])
        Calpha.append(data['alpha'])
        Cbeta.append(data['beta'])
        Cgamma.append(data['gamma'])
        Ctime.append(result.index(data)*0.2+0.2)
    
    return Cx,Cy,Cz,Calpha,Cbeta,Cgamma,Ctime

def reduceaccnoise(sample,still=0):
    #still is the mean average of the sample, or when the phone is still & flat
    noisefreedata = []
    threshold = np.var(sample)
    for i in range(len(sample)):
        if math.fabs(sample[i])< threshold:
            noisefreedata.append(0)
        else:
            noisefreedata.append(sample[i])
            
    return noisefreedata

def comparesign(a,b):
    if a>=0 and b >=0:
        return True
    elif a<0 and b<0:
        return True
    else:
        return False
    

def findangPeaks(vals,delta,error = 45,mw = 5):
    #mw, minimum width, the amount of time allowed for orientation change, set at 1 second, 5 * 200ms as average person
    # these numbers are currently arbitrary, is machine learned over a period of time to better define these values
    noisefreeang=[]
    for i in range(mw-1):
        noisefreeang.append(0)
    
    # 1 represents upperhand motion, 0 is other, -1 is lowerhand motion
    for i in range(mw-1,len(vals)):
        prevVal = vals[i-mw]
        currVal = vals[i]   
        if math.fabs(currVal- prevVal - delta)< error and comparesign(currVal-prevVal,delta) == True:
            noisefreeang.append(1)
        elif math.fabs(currVal- prevVal + delta)< error and comparesign(currVal-prevVal,delta) == False:
            noisefreeang.append(-1)
        else:
            noisefreeang.append(0)
        
    return noisefreeang

def findaccPeaks(vals, threshold = 0.5):
    peaks = []
    for i in range(1,len(vals)-1):
        prevVal = vals[i-1]
        currVal = vals[i]
        nextVal = vals[i+1]
        
        # Check if the current value is a PEAK above a certain threshold value
        if currVal > prevVal and currVal > nextVal and math.fabs(currVal) > threshold:
            peaks.append(1)
        # Check if the current value is a VALLEY above a certain threshold value
        elif currVal < prevVal and currVal < nextVal and math.fabs(currVal) > threshold:
            peaks.append(-1)
        else:
            peaks.append(0)

    return peaks

def cleandata(Cx,Cy,Cz,Calpha,Cbeta,Cgamma, Ctime):
    x = reduceaccnoise(Cx,0)
    y = reduceaccnoise(Cy,0)
    z = reduceaccnoise(Cz,0)  
    time = Ctime
    alpha=findangPeaks(Calpha,225)
    beta=findangPeaks(Cbeta,200)
    gamma=findangPeaks(Cgamma,-160)
    
    return x,y,z,alpha,beta,gamma,time

def countaccPeaks(x,y,z,time):
    accVal = []
    for i in range(len(time)):
        a = math.sqrt(x[i]**2 + y[i]**2 + z[i]**2)
        accVal.append(a)
    extremeties = findaccPeaks(accVal)
    Peaks = sum(extremeties)/2
             #this should tell number of peaks , as -1 and a immediate following 1 cancels, devides by two one motion for up one for down
    return Peaks,accVal

def countangPeaks(alpha,beta,gamma,time):
    totalang =[]
    for i in range(len(time)):
        totalang.append(alpha[i]+beta[i]+gamma[i])
    
    angpeaks = [0]
    for i in range(1,len(totalang)):
        if totalang[i]-totalang[i-1]>0 and totalang[i]==3:
            angpeaks.append(1)
        elif totalang[i]-totalang[i-1] < 0 and totalang[i] == -3:
            angpeaks.append(-1)
        else:
            angpeaks.append(0)

    return totalang,angpeaks
        

if __name__ == "__main__":
    firebase = firebase.FirebaseApplication('https://social-robot-b24fb.firebaseio.com/', None)
    result = firebase.get('/', None)
    
    Cx,Cy,Cz,Calpha,Cbeta,Cgamma,Ctime = readfromfirebase()             #C stands for crude data
    x,y,z,alpha,beta,gamma,time = cleandata(Cx,Cy,Cz,Calpha,Cbeta,Cgamma,Ctime)
    accPeaks,accVal = countaccPeaks(x,y,z,time)
    totalang,angPeaks = countangPeaks(alpha,beta,gamma,time)
    
    numberaccPeaks = round(accPeaks)
    numberangPeaks = angPeaks.count(1)
    
    print("\n accelerometers indicates", numberaccPeaks, " gestures that could be smoking")    
    print("\n orientation sensors indicates", numberangPeaks, " gestures that could be smoking")
    
    numberofPeaks = min(numberaccPeaks,numberangPeaks)
    print("\n \n taking the minimum value we have", numberofPeaks, " gestures that could be smoking")
    fig1 = plt.figure("acceleration")
    plt.plot(time, x,'b-')
    plt.plot(time, y,'g-')
    plt.plot(time, z,'r-')
    plt.plot(time, accVal,'m-')
    plt.ylabel('m/sec^2')
    plt.xlabel('time')
    plt.legend(['x', 'y', 'z'])
    
    
    fig2 = plt.figure("seperate")
    plt.subplot(4,1,1)
    plt.plot(time, x,'b-')
    plt.ylabel('m/sec^2')
    plt.xlabel('time')
    plt.legend(['x'])    
    plt.subplot(4,1,2)
    plt.plot(time, y,'g-')
    plt.ylabel('m/sec^2')
    plt.xlabel('time')
    plt.legend(['y']) 
    plt.subplot(4,1,3)
    plt.plot(time, z,'r-')
    plt.ylabel('m/sec^2')
    plt.xlabel('time')
    plt.legend(['z'])   
    plt.subplot(4,1,4)
    plt.plot(time, accVal,'4-')
    plt.ylabel('m/sec^2')
    plt.xlabel('time')
    plt.legend(['comparison']) 
    
    fig3 = plt.figure("orientation")
    plt.plot(time, Calpha,'b-')
    plt.plot(time, Cbeta,'g-')
    plt.plot(time, Cgamma,'r-')
    plt.ylabel('degree')
    plt.xlabel('time')
    plt.legend(['Calpha', 'Cbeta', 'Cgamma'])

"""      
    fig4 = plt.figure("cleanorientation")
    plt.plot(time, alpha,'b-')
    plt.plot(time, beta,'g-')
    plt.plot(time, gamma,'r-')
    plt.plot(time, totalang,'m-')
    plt.ylabel('value')
    plt.xlabel('time')
    plt.legend(['alpha', 'beta', 'gamma','totalang'])  
"""    