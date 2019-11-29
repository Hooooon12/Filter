import FWCore.ParameterSet.Config as cms

#####################
# -- set by hand -- #
#####################
isMC = False
isSignalMC = False

GT_MC = '94X_mc2017_realistic_v12' # -- 2017 Nov MC
GT_DATA = '90X_dataRun2_Prompt_v1' # -- 2017 prompt reco v1

# TESTFILE_MC = 'file:/u/user/kplee/scratch/ROOTFiles_Test/80X/ExampleMiniAODv2_ZMuMuPowheg_M120to200_Moriond17.root' # -- no signal -- #
TESTFILE_MC = 'file:/u/user/kplee/scratch/ROOTFiles_Test/80X/MINIAOD_DYLL_M50toInf_Morind17.root' # -- signal -- #
TESTFILE_DATA = 'root://cms-xrd-global.cern.ch//store/data/Run2017F/DoubleMuon/MINIAOD/PromptReco-v1/000/305/040/00000/3804E121-34B2-E711-8E67-02163E01A599.root' # -- a root file of DoubleMuon data set, period F, 2017 prompt reco

####################################################################################################################

if not isMC: isSignalMC = False
 
process = cms.Process("NTUPLE")

## MessageLogger
process.load("FWCore.MessageLogger.MessageLogger_cfi")

## Options and Output Report
process.options   = cms.untracked.PSet( 
  SkipEvent = cms.untracked.vstring('ProductNotFound'),
  wantSummary = cms.untracked.bool(True) 
)
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

## Source
FileName = TESTFILE_DATA
if isMC: FileName = TESTFILE_MC

process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring( FileName )
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

# -- Geometry and Detector Conditions (needed for a few patTuple production steps) -- #
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

# -- Global Tags -- #
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
if isMC == True:
  process.GlobalTag.globaltag = cms.string(GT_MC)
else:
  process.GlobalTag.globaltag = cms.string(GT_DATA) #prompt-reco global tag


process.TFileService = cms.Service("TFileService",
  fileName = cms.string('ntuple_skim.root')
)

# -- FastFilters -- //
process.goodOfflinePrimaryVertices = cms.EDFilter("VertexSelector",
   # src = cms.InputTag("offlinePrimaryVertices"),
   src = cms.InputTag("offlineSlimmedPrimaryVertices"), # -- miniAOD -- #
   cut = cms.string("!isFake && ndof > 4 && abs(z) < 24 && position.Rho < 2"), # tracksSize() > 3 for the older cut
   filter = cms.bool(True),   # otherwise it won't filter the events, just produce an empty vertex collection.
)

process.FastFilters = cms.Sequence( process.goodOfflinePrimaryVertices )

########################
# -- EGM Correction: -- #
########################
# -- EGM 80X regression: https://twiki.cern.ch/twiki/bin/viewauth/CMS/EGMRegression -- #
#from EgammaAnalysis.ElectronTools.regressionWeights_cfi import regressionWeights
#process = regressionWeights(process)
#process.load('EgammaAnalysis.ElectronTools.regressionApplication_cff')

# -- EGM 80X scale and smearing correction -- #
#process.load('Configuration.StandardSequences.Services_cff')
#process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
#                  calibratedPatElectrons  = cms.PSet( initialSeed = cms.untracked.uint32(8675389),
#                                                      engineName = cms.untracked.string('TRandom3'),
#                                                      ),
#                  calibratedPatPhotons    = cms.PSet( initialSeed = cms.untracked.uint32(8675389),
#                                                      engineName = cms.untracked.string('TRandom3'),
#                                                      ),
#)

#process.load('EgammaAnalysis.ElectronTools.calibratedPatElectronsRun2_cfi')
#process.load('EgammaAnalysis.ElectronTools.calibratedPatPhotonsRun2_cfi')

#process.calibratedPatElectrons.isMC = cms.bool(isMC)
#process.calibratedPatPhotons.isMC = cms.bool(isMC)

#########################
# -- for electron ID -- #
#########################


from PhysicsTools.SelectorUtils.tools.vid_id_tools import *

# turn on VID producer, indicate data format  to be
# DataFormat.AOD or DataFormat.MiniAOD, as appropriate 
dataFormat = DataFormat.MiniAOD
# -- switchOnVIDElectronIdProducer: load RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cff <- makes egmGsfElectronIDSequence
# -- egmGsfElectronIDSequence = cms.Sequence( electronMVAValueMapProducer * egmGsfElectronIDs * electronRegressionValueMapProducer) -- #
switchOnVIDElectronIdProducer(process, dataFormat)
switchOnVIDPhotonIdProducer(process, dataFormat)

# define which electron IDs we want to produce
my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V1_cff', # -- 94X cut based electron ID
                 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V1_cff', # -- 94X MVA based electron ID, noIso
                 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V1_cff', # -- 94X MVA based electron ID, iso
                 'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff']# -- HEEP V70 electron ID

#add e_id modules to the VID producer
for idmod in my_id_modules:
    setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)

# define which photon IDs we want to produce
my_phoid_modules = ['RecoEgamma.PhotonIdentification.Identification.cutBasedPhotonID_Fall17_94X_V1_cff', # -- 92X cut based photon ID 
                    'RecoEgamma.PhotonIdentification.Identification.mvaPhotonID_Fall17_94X_V1_cff'] # -- 94X MVA based photon ID


process.load("RecoEgamma.ElectronIdentification.ElectronIDValueMapProducer_cfi")
# process.electronIDValueMapProducer.srcMiniAOD = cms.InputTag('slimmedElectrons')
# process.electronMVAValueMapProducer.srcMiniAOD = cms.InputTag('slimmedElectrons')

#add phoid modules to the VID producer
for idmod in my_phoid_modules:
    setupAllVIDIdsInModule(process,idmod,setupVIDPhotonSelection)


#process.selectedElectrons = cms.EDFilter("PATElectronSelector",
#    #src = cms.InputTag("calibratedPatElectrons"),
#    src = cms.InputTag("slimmedElectrons"),                                    
#    cut = cms.string("pt>5 && abs(eta)")
#)


######################
# MET Phi Correction #
######################
#from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
#runMetCorAndUncFromMiniAOD(process, isData=True )  #For MC isData=False

#################
# -- DY Tree -- #
#################
from Phys.SKFlatMaker.SKFlatMaker_cfi import *
from Phys.SKFlatMaker.PUreweight2012_cff import *

process.recoTree = SKFlatMaker.clone()
process.recoTree.isMC = isMC

# -- Objects -- #
process.recoTree.Muon = cms.untracked.InputTag("slimmedMuons") # -- miniAOD -- #
process.recoTree.Electron = cms.untracked.InputTag("slimmedElectrons") # -- miniAOD -- #
process.recoTree.UnCorrElectron = cms.untracked.InputTag("slimmedElectrons") # -- miniAOD: before applying energy scale correction -- #
process.recoTree.Photon = cms.untracked.InputTag("slimmedPhotons") # -- miniAOD -- #
process.recoTree.Jet = cms.untracked.InputTag("slimmedJets") # -- miniAOD -- #
process.recoTree.MET = cms.untracked.InputTag("slimmedMETs") # -- miniAOD -- #
process.recoTree.GenParticle = cms.untracked.InputTag("prunedGenParticles") # -- miniAOD -- #

# -- for electrons -- # chaged to 2017 ID Map
process.recoTree.rho = cms.untracked.InputTag("fixedGridRhoFastjetAll")
process.recoTree.conversionsInputTag = cms.untracked.InputTag("reducedEgamma:reducedConversions") # -- miniAOD -- #
process.recoTree.eleVetoIdMap = cms.untracked.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-veto")
process.recoTree.eleLooseIdMap = cms.untracked.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-loose")
process.recoTree.eleMediumIdMap = cms.untracked.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-medium")
process.recoTree.eleTightIdMap = cms.untracked.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-tight")
#process.recoTree.eleHEEPIdMap = cms.untracked.InputTag("RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff")
process.recoTree.eleMVAIdnoIsoWP80Map = cms.untracked.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V1-wp80")
process.recoTree.eleMVAIdnoIsoWP90Map = cms.untracked.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V1-wp90")
process.recoTree.eleMVAIdisoWP80Map = cms.untracked.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V1-wp80")
process.recoTree.eleMVAIdisoWP90Map = cms.untracked.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V1-wp90")

# -- for photons -- #
process.recoTree.full5x5SigmaIEtaIEtaMap   = cms.untracked.InputTag("photonIDValueMapProducer:phoFull5x5SigmaIEtaIEta")
process.recoTree.phoChargedIsolation = cms.untracked.InputTag("photonIDValueMapProducer:phoChargedIsolation")
process.recoTree.phoNeutralHadronIsolation = cms.untracked.InputTag("photonIDValueMapProducer:phoNeutralHadronIsolation")
process.recoTree.phoPhotonIsolation = cms.untracked.InputTag("photonIDValueMapProducer:phoPhotonIsolation")
process.recoTree.effAreaChHadFile = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/PHYS14/effAreaPhotons_cone03_pfChargedHadrons_V2.txt")
process.recoTree.effAreaNeuHadFile= cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/PHYS14/effAreaPhotons_cone03_pfNeutralHadrons_V2.txt")
process.recoTree.effAreaPhoFile   = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/PHYS14/effAreaPhotons_cone03_pfPhotons_V2.txt")
#------------------------------------------- Photon IDs for 2017 analysis
process.recoTree.phoLooseIdMap = cms.untracked.InputTag("egmPhotonIDs:cutBasedPhotonID-Fall17-94X-V1-loose")
process.recoTree.phoMediumIdMap = cms.untracked.InputTag("egmPhotonIDs:cutBasedPhotonID-Fall17-94X-V1-medium")
process.recoTree.phoTightIdMap = cms.untracked.InputTag("egmPhotonIDs:cutBasedPhotonID-Fall17-94X-V1-tight")
process.recoTree.phoMVAIDWP90Map = cms.untracked.InputTag("egmPhotonIDs:mvaPhoID-RunIIFall17-v1-wp90")
process.recoTree.phoMVAIDWP80Map = cms.untracked.InputTag("egmPhotonIDs:mvaPhoID-RunIIFall17-v1-wp80")


# -- for Track & Vertex -- #
process.recoTree.PrimaryVertex = cms.untracked.InputTag("offlineSlimmedPrimaryVertices") # -- miniAOD -- #

# -- Else -- #
process.recoTree.PileUpInfo = cms.untracked.InputTag("slimmedAddPileupInfo")

# -- Filters -- #
process.recoTree.ApplyFilter = False

# -- Store Flags -- #
process.recoTree.StoreMuonFlag = True
process.recoTree.StoreElectronFlag = True
process.recoTree.StorePhotonFlag = True # -- photon part should be updated! later when it is necessary -- #
process.recoTree.StoreJetFlag = True
process.recoTree.StoreMETFlag = True
#process.recoTree.StoreGENFlag = False
process.recoTree.StoreGENFlag = isMC
process.recoTree.StoreLHEFlag = isSignalMC

####################
# -- Let it run -- #
####################
process.p = cms.Path(
  process.FastFilters *
  #process.regressionApplication *
  #process.calibratedPatElectrons *
  #process.selectedElectrons *
  process.egmPhotonIDSequence *
  process.egmGsfElectronIDSequence *
  #process.fullPatMetSequence *  #This is the phi corrections part
  process.recoTree
)
