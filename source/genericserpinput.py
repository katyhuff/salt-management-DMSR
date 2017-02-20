
# sorry about the implicit imports
from RefuelCore import *

class genericInput(SerpentInputFile):

    """ 
 this file contains an object for non-DMSR serpent input files.
 this came afterwards because originally this was only intended
 to work with DMSRs. Then I realized maybe other people could
 (hopefully) use this code.

 This object is identical to the other SerpentInputFile, but
 the __init__ method doesn't run the DMSR core writer.

    """

    def __init__(self,num_nodes=None,PPN=None,pmem=None,queue=None,direc='.'):
        """Initialization. Returns a SerpentInputFile object.

        Arguments:
            None

        Keyword args:
            num_nodes -- number of nodes to run the input file on. integer.
            PPN -- processors per node. integer.
            pmem -- requested memory per processor.
           queue -- torque queue to run on. string. e.g. "gen5" or "super"
        """

        #initially no extra burnup is assigned to the file, or burnup settings
        self.RefuelRate=None
        self.AbsorberAdditionRate=None
        self.OffGasRate=None
        self.BurnTime=[]
        self.maxdamageflux=None
        self.PowerNormalization=''
        self.directory=direc #default directory to run and store data in
        #initially there is no reprocessing
        self.volumetricflows=[]  #the variable "flows" holds all mass flow info.
        self.ratioflows=[]
        self.includefiles=[]
        self.otheropts = []
        
        #this is a variable that tells if an attempt has been made to submit the job
        self.submitted_once=False
        
        #output variables
        self.kefflist=[]
        self.convratiolist=[]
        self.betalist=[]
        self.convratio=None
        self.betaEff=None

        self.includefiles = []

        self.xslibfiles='''set acelib "sss_endfb7u.xsdata"
        set nfylib "sss_endfb7.nfy"
        set declib "sss_endfb7.dec"\n\n'''
        #assign default qsub settings if none were specified. else assign the specified settings.
        if num_nodes!=None:
            self.num_nodes=num_nodes
        else:
            #num_nodes refers to the function argument. self.num_nodes is the instance variable being assigned.
            self.num_nodes=SerpentInputFile.default_num_nodes
            print "using default number of nodes for qsub script, {0} nodes".format(SerpentInputFile.default_num_nodes)
        if PPN!=None:
            self.PPN=PPN
        else:
            self.PPN=SerpentInputFile.default_PPN
            print "using the default number of PPN for qsub, {0} PPN".format(SerpentInputFile.default_PPN)
        if pmem!=None:
            self.pmem=pmem
        else:
            self.pmem=SerpentInputFile.default_pmem
            print "using default requested amount of memory, {0} ".format(SerpentInputFile.default_pmem)
        if queue!=None:
            self.queue=queue
        else:
            self.queue=SerpentInputFile.default_queue
            print "using default queue, {0}".format(SerpentInputFile.default_queue)


        #The name of the input file being used should be, by default, 'MSRs2'. This should be able to be changed if necessary.
        self.inputfilename='MSRs2'
        
        #There should be a default temperature of the molten salt. By default it will be 900 K.
        self.tempK=tempK

        #The serpent input file has to be run eventually. There will be a boolean attached to this object that shows whether the serpent job
        #has finished running on the cluster yet.
        self.job_done=False

        #now initialize the list of materials that are present in the input file. This is a list of objects of the SerpentMaterial class.
        self.materials=[]

        #Find the volume of fuel in the core for this input file. 
        self.fuelvolume=None
        for mat in self.materials:
            if mat.materialname=='fuel':
                self.fuelvolume=mat.volume
        if self.fuelvolume==None:
            raise Exception("There was an error in reading in the volume of the fuel material from the corewriter output.")

        #default to use TMP for temperature XS interpolation
        self.tmp_or_tms='tmp'

    def GetMaxDamageFlux(self):
        """ I need to override this so that people don't accidentally
        get wrong readings for MaxDamgeFlux in graphite. This only works if
        you know where the max fast flux happens, which is generically only
        determined for our DMSR core writer. """

        raise Exception(' sorry, this only works with the DMSR core writer ')

    def WriteJob(self, directory='.',usebumodethree=False):
        """ partially overrides RefuelCore.SerpentInputFile.SubmitJob """
        SerpentInputFile.WriteJob(self,directory='.',usebumodethree=usebumodethree)

        # now need to append other serpent options
        serpinp = open(self.inputfilename, 'a') #append mode

        for opt in self.otheropts:
            serpinp.write(opt)

        for f in self.includefiles:
            if f not in os.listdir('.'):
                raise Exception("include file '.' not found in wdir".format(f))
        
        serpinp.close()

