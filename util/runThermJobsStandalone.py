#!/usr/bin/env python
# Runs jobs in a directory

import argparse
import os
import pickle as pk
import RefuelCore
import genericserpinput

days = []
flist = os.listdir('.')
inputfiles = [fname for fname in flist if fname.startswith("input")]
for fname in inputfiles:
    day = [char for char in fname if char.isdigit()]
    if day == []:
        raise Exception('{} unexpectedly found in inputfileslog.'.format(fname))
    dayInt = int( "".join(day) )
    days.append(dayInt)
days.sort()

for day in days:    
    print("Processing day {}".format(day))
    with open('inputday{}.dat'.format(day)) as fh:
        core = pk.load(fh)
    core.num_nodes = 1
    core.PPN = 40
    core.queue = "local"
    core.num_particles = 10000
#   core.pmem = "3600MB"
    core.BurnTime = []
    core.volumetricflows = []
    core.ratioflows = []
    jobdir = "job_day{}".format(day)
    os.mkdir(jobdir)
    core.WriteJob(jobdir)
    core.SubmitJob('local')
    
    
