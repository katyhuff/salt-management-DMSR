# This script will check thermal reactivity coefficients of both
# the fuel and the graphite. TMP method for doppler broadening is
# used by default.
from RefuelCore import *
import copy
from scipy.optimize import curve_fit
import time
import os

def linear(x, m, b):
    """ the most complicated equation known to man."""
    return m*x + b

def stabileCheck(inputfile, queue='gen5', ppn=8, verb=False):
    """ Checks the stability of a SerpentInputFile object.
        The input file is re-written using the perl core writer.
        Reactivity is checked at 50 deg C increments away from 900.
    Input:
        SerpentInputFile to assess rho coefficients
    Output:
        Float. Best fit temp coeff of reactivity"""

    # parameters for the analysis
    tmp_or_tms='tmp'
    perlcase=3 #case param for perl script. this one assumes graphite
                # to be 50 K above the salt temperature

    # copy core data for core writer
    coresize=inputfile.core_size
    coresalt=inputfile.salt_type #doesn't actually matter
    sf=inputfile.salt_fraction
    p=inputfile.pitch
    name = inputfile.inputfilename

    # get 900 K case rho
    k900=inputfile.ReadKeff()
    rho900 = (k900-1.0)/k900

    #construct new inputfiles
    testT=[800.0,850.0,950.0,1000.0,1100.0]
    inplist=range(len(testT)) #initialize

    # each new input file must get a copy of the right fuel isotopics.
    fuelmat=None
    for mat in inputfile.materials:
        if mat.materialname =='fuel':
            fuelmat=mat #save reference to fuelmat
            break
    if fuelmat==None:
        raise Exception("fuel material not found in inputfile")

    for i,T in enumerate(testT):
        dirname=name+'stability'+str(int(T))
        os.mkdir(dirname)
        os.chdir(dirname)
        inplist[i]=SerpentInputFile(core_size=coresize,salt_type=coresalt,
                                case=perlcase,salt_fraction=sf,
                                initial_enrichment=0.0,num_nodes=1,
                                pitch=p,tempK=T,queue=queue, PPN=ppn)
        # change inputfile name
        inplist[i].SetInputFileName(name+str(int(testT[i])))
        #set directory
        inplist[i].directory=dirname

        # copy isotopics from requested core
        for j,mat in enumerate(inplist[i].materials):
            if mat.materialname=='fuel':
                # change material composition
                delindex=j
                break
        del inplist[i].materials[delindex]
        inplist[i].materials.append(copy.copy(fuelmat))
        # and now the fuel must have the correct test temperature
        inplist[i].materials[-1].SetTemp(testT[i])

        #annnddd submit!
        inplist[i].SubmitJob()

        os.chdir('..')

    #wait
    time.sleep(1)
    while not(all([inp.IsDone() for inp in inplist])):
        time.sleep(3)

    #read reactivity
    rhos=[(inp.ReadKeff()-1.0)/inp.ReadKeff() for inp in inplist]

    #append old data @ 900 K
    rhos.append(rho900)
    testT.append(900.0)

    #fit linear
    param=curve_fit(linear, testT, rhos)
    param=param[0] #ignore covariance data

    if verb:
        print "temperatures attempted"
        print testT
        print "reactivities"
        print rhos

    return param[0] #return slope