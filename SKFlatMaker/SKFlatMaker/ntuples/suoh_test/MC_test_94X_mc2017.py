import FWCore.ParameterSet.Config as cms

#####################
# -- set by hand -- #
#####################
isMC = True
isSignalMC = False
applyCorrection = False

#GT_MC = '94X_mc2017_realistic_v12' # -- 2017 Nov MC
GT_MC = '94X_mc2017_realistic_v10'
#GT_DATA = '90X_dataRun2_Prompt_v1' # -- 2017 prompt reco v1

# TESTFILE_MC = 'file:/u/user/kplee/scratch/ROOTFiles_Test/80X/ExampleMiniAODv2_ZMuMuPowheg_M120to200_Moriond17.root' # -- no signal -- #
#TESTFILE_MC = 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/RECOSIMstep_94X_mc2017_realistic_v10-v1/00000/0293A280-B5F3-E711-8303-3417EBE33927.root' # -- a root file of DYJetsToLL_M-50, MG
TESTFILE_MC = 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAOD/ZToEE_NNPDF31_13TeV-powheg_M_3500_4500/MINIAODSIM/94X_mc2017_realistic_v10-v2/00000/201990FB-B306-E811-9A19-782BCB678094.root' # -- a root file of /ZToEE_NNPDF31_13TeV-powheg_M_3500_4500/RunIIFall17MiniAOD-94X_mc2017_realistic_v10-v2/MINIAODSIM
TESTFILE_DATA = 'file:/afs/cern.ch/work/s/suoh/entuple_making/KPLee_code/CMSSW_9_4_2/src/Phys/SKFlatMaker/ntuples/suoh_test/17Nov17_Rereco/DoubleMuon/00FB06B4-0DDF-E711-9291-02163E012A3F.root'

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
#process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

# -- Global Tags -- #
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")

if isMC == True:
  process.GlobalTag.globaltag = cms.string(GT_MC)
else:
  process.GlobalTag.globaltag = cms.string(GT_DATA) #prompt-reco global tag


process.TFileService = cms.Service("TFileService",
  fileName = cms.string('ntuple_skim_corrected.root')
)

# -- FastFilters -- //
process.goodOfflinePrimaryVertices = cms.EDFilter("VertexSelector",
   # src = cms.InputTag("offlinePrimaryVertices"),
   src = cms.InputTag("offlineSlimmedPrimaryVertices"), # -- miniAOD -- #
   cut = cms.string("!isFake && ndof > 4 && abs(z) < 24 && position.Rho < 2"), # tracksSize() > 3 for the older cut
   filter = cms.bool(True),   # otherwise it won't filter the events, just produce an empty vertex collection.
)

process.FastFilters = cms.Sequence( process.goodOfflinePrimaryVertices )

#For E/gamma correction and VID
from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
setupEgammaPostRecoSeq(process,applyEnergyCorrections=False,
                       applyVIDOnCorrectedEgamma=False,
                       isMiniAOD=True)

#########################
# -- EGM Correction -- ##
#########################
process.load('Configuration.StandardSequences.Services_cff')
process.load('EgammaAnalysis.ElectronTools.calibratedPatElectronsRun2_cfi')
process.RandomNumberGeneratorService.calibratedPatElectrons = cms.PSet(
  initialSeed = cms.untracked.uint32(81),
  engineName = cms.untracked.string('TRandom3')
)
process.calibratedPatElectrons.isMC = isMC

process.load('EgammaAnalysis.ElectronTools.calibratedPatPhotonsRun2_cfi')
process.RandomNumberGeneratorService.calibratedPatPhotons = cms.PSet(
  initialSeed = cms.untracked.uint32(81),
  engineName = cms.untracked.string('TRandom3')
)
process.calibratedPatPhotons.isMC = isMC

################################
# -- for electron/photon ID -- #
################################
from PhysicsTools.SelectorUtils.tools.vid_id_tools import *

# turn on VID producer, indicate data format  to be
# DataFormat.AOD or DataFormat.MiniAOD, as appropriate 
dataFormat = DataFormat.MiniAOD
# -- switchOnVIDElectronIdProducer: load RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cff <- makes egmGsfElectronIDSequence
# -- egmGsfElectronIDSequence = cms.Sequence( electronMVAValueMapProducer * egmGsfElectronIDs * electronRegressionValueMapProducer) -- #
switchOnVIDElectronIdProducer(process, dataFormat)
switchOnVIDPhotonIdProducer(process, dataFormat)

print "switchOnVIDElectronIDProducer -> len(process.egmGsfElectronIDs.physicsObjectIDs) : " + str(len(process.egmGsfElectronIDs.physicsObjectIDs))
print "switchOnVIDPhotonIdProducer -> len(process.egmPhotonIDs.physicsObjectIDs) : " + str(len(process.egmPhotonIDs.physicsObjectIDs))


# define which electron IDs we want to produce 
my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V1_cff', # -- 94X cut based electron ID
                 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V1_cff', # -- 94X MVA based electron ID, noIso
                 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V1_cff', # -- 94X MVA based electron ID, iso
                 'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff']# -- HEEP V70 electron ID

#add e_id modules to the VID producer
for idmod in my_id_modules:
  setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)

# define which photon IDs we want to produce
my_phoid_modules = ['RecoEgamma.PhotonIdentification.Identification.cutBasedPhotonID_Fall17_94X_V1_TrueVtx_cff', # -- 94X cut based photon ID 
                    'RecoEgamma.PhotonIdentification.Identification.mvaPhotonID_Fall17_94X_V1_cff'] # -- 94X MVA based photon ID

#add phoid modules to the VID producer
for idmod in my_phoid_modules:
  setupAllVIDIdsInModule(process,idmod,setupVIDPhotonSelection)


process.load("RecoEgamma.PhotonIdentification.PhotonIDValueMapProducer_cfi")
process.load("RecoEgamma.ElectronIdentification.ElectronIDValueMapProducer_cfi")

process.selectedElectrons = cms.EDFilter("PATElectronSelector",
    src = cms.InputTag("calibratedPatElectrons"),
    cut = cms.string("pt>5 && abs(eta)")
)
process.selectedPhotons = cms.EDFilter("PATPhotonSelector",
    src = cms.InputTag("calibratedPatPhotons"),
    cut = cms.string("pt>5 && abs(eta)")
)

process.egmGsfElectronIDs.physicsObjectSrc = cms.InputTag('selectedElectrons')
print len(process.egmGsfElectronIDs.physicsObjectIDs)
for psets in process.egmGsfElectronIDs.physicsObjectIDs:
  print "---------------------"
  print psets
#print process.egmGsfElectronIDs.physicsObjectIDs[0]
process.electronIDValueMapProducer.srcMiniAOD = cms.InputTag('selectedElectrons')
process.electronRegressionValueMapProducer.srcMiniAOD = cms.InputTag('selectedElectrons')
process.electronMVAValueMapProducer.srcMiniAOD = cms.InputTag('selectedElectrons')

process.egmPhotonIDs.physicsObjectSrc = cms.InputTag('selectedPhotons')
print len(process.egmPhotonIDs.physicsObjectIDs)
for psets in process.egmPhotonIDs.physicsObjectIDs:
  print"---------------------"
  print psets
process.egmPhotonIsolation.srcToIsolate = cms.InputTag('selectedPhotons')
process.photonIDValueMapProducer.srcMiniAOD = cms.InputTag('selectedPhotons')
process.photonRegressionValueMapProducer.srcMiniAOD = cms.InputTag('selectedPhotons')
process.photonMVAValueMapProducer.srcMiniAOD = cms.InputTag('selectedPhotons')

######################
# MET Phi Correction #
######################
#from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
#runMetCorAndUncFromMiniAOD(process, isData=True )  #For MC isData=False

#################
# -- DY Tree -- #
#################
from SKFlatMaker.SKFlatMaker.SKFlatMaker_cfi import *
from SKFlatMaker.SKFlatMaker.PUreweight2012_cff import *

process.recoTree = SKFlatMaker.clone()
process.recoTree.isMC = isMC

# -- Objects without Corrections -- # 
process.recoTree.Muon = cms.untracked.InputTag("slimmedMuons") # -- miniAOD -- #
process.recoTree.Electron = cms.untracked.InputTag("slimmedElectrons") # -- miniAOD -- # before smearing
process.recoTree.Photon = cms.untracked.InputTag("slimmedPhotons") # -- miniAOD -- #
#process.recoTree.SmearedElectron = "calibratedPatElectrons" # -- Smeared Electron
#process.recoTree.SmearedPhoton = "calibratedPatPhotons" # -- Smeared Photon
process.recoTree.SmearedElectron = cms.untracked.InputTag("selectedElectrons")
process.recoTree.SmearedPhoton = cms.untracked.InputTag("selectedPhotons")
#process.recoTree.SmearedElectron = cms.untracked.InputTag("calibratedPatElectrons") # -- Smeared Electron
#process.recoTree.SmearedPhoton = cms.untracked.InputTag("calibratedPatPhotons") # -- Smeared Photon
#process.recoTree.Jet = cms.untracked.InputTag("slimmedJets") # -- miniAOD -- #
#process.recoTree.MET = cms.untracked.InputTag("slimmedMETs") # -- miniAOD -- #
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
process.recoTree.effAreaChHadFile = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfChargedHadrons_90percentBased_TrueVtx.txt")
process.recoTree.effAreaNeuHadFile= cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfNeutralHadrons_90percentBased_TrueVtx.txt")
process.recoTree.effAreaPhoFile   = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfPhotons_90percentBased_TrueVtx.txt")
#------------------------------------------- Photon IDs for 2017 analysis
process.recoTree.phoLooseIdMap = cms.untracked.InputTag("egmPhotonIDs:cutBasedPhotonID-Fall17-94X-V1-loose")
process.recoTree.phoMediumIdMap = cms.untracked.InputTag("egmPhotonIDs:cutBasedPhotonID-Fall17-94X-V1-medium")
process.recoTree.phoTightIdMap = cms.untracked.InputTag("egmPhotonIDs:cutBasedPhotonID-Fall17-94X-V1-tight")
process.recoTree.phoMVAIDWP90Map = cms.untracked.InputTag("egmPhotonIDs:mvaPhoID-RunIIFall17-v1-wp90")
process.recoTree.phoMVAIDWP80Map = cms.untracked.InputTag("egmPhotonIDs:mvaPhoID-RunIIFall17-v1-wp80")

# -- Corrections -- #

# -- JEC
JEC_files = ('Fall17_17Nov2017BCDEF_V6_DATA', 'Fall17_17Nov2017_V6_MC')
if isMC:
  jecFile = JEC_files[1]
else:
  jecFile = JEC_files[0]

from CondCore.CondDB.CondDB_cfi import CondDB
if hasattr(CondDB, 'connect'): delattr(CondDB, 'connect')
process.jec = cms.ESSource("PoolDBESSource",CondDB,
    connect = cms.string('sqlite_fip:SKFlatMaker/SKFlatMaker/data/JEC/db/%s.db'%jecFile),            
    toGet = cms.VPSet(
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_%s_AK4PF"%jecFile),
            label= cms.untracked.string("AK4PF")),
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_%s_AK4PFchs"%jecFile),
            label= cms.untracked.string("AK4PFchs")),
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_%s_AK4PFPuppi"%jecFile),
            label= cms.untracked.string("AK4PFPuppi")),
    )
)
process.es_prefer_jec = cms.ESPrefer("PoolDBESSource","jec")
print "JEC based on", process.jec.connect
process.load("PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff")
from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
if isMC:
  updateJetCollection(
    process,
    jetSource = cms.InputTag('slimmedJets'),
    jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute']), 'None'),
    )
else :
  updateJetCollection(
    process,
    jetSource = cms.InputTag('slimmedJets'),
    jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']), 'None'),
    )

process.recoTree.Jet = cms.untracked.InputTag("slimmedJets") # -- miniAOD -- #
process.recoTree.FatJet = cms.untracked.InputTag("slimmedJetsAK8")

# -- MET Correction
from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
runMetCorAndUncFromMiniAOD(process, isData= not isMC, electronColl=cms.InputTag('selectedElectrons'), jetCollUnskimmed=cms.InputTag('slimmedJets'))
process.recoTree.MET = cms.InputTag("slimmedMETs","","PAT")

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
process.recoTree.KeepAllGen = isMC
process.recoTree.StoreLHEFlag = isSignalMC

####################
# -- Let it run -- #
####################
process.p = cms.Path(
  process.FastFilters *
  process.egammaPostRecoSeq *
  process.calibratedPatElectrons *
  process.calibratedPatPhotons *  
  process.selectedElectrons *
  process.selectedPhotons *
  process.egmPhotonIDSequence *
  process.egmGsfElectronIDSequence *
  #process.electronIDValueMapProducer *
  #process.fullPatMetSequence *  #This is the phi corrections part
  process.recoTree
)
