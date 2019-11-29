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

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

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

##################################
# For E/gamma correction and VID #
##################################
from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
setupEgammaPostRecoSeq(process,applyEnergyCorrections=False,
                       applyVIDOnCorrectedEgamma=False,
                       isMiniAOD=True)


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
process.recoTree.SmearedElectron = cms.untracked.InputTag("slimmedElectrons")
process.recoTree.SmearedPhoton = cms.untracked.InputTag("slimmedPhotons")
#process.recoTree.SmearedElectron = cms.untracked.InputTag("calibratedPatElectrons") # -- Smeared Electron
#process.recoTree.SmearedPhoton = cms.untracked.InputTag("calibratedPatPhotons") # -- Smeared Photon
#process.recoTree.Jet = cms.untracked.InputTag("slimmedJets") # -- miniAOD -- #
#process.recoTree.MET = cms.untracked.InputTag("slimmedMETs") # -- miniAOD -- #
process.recoTree.GenParticle = cms.untracked.InputTag("prunedGenParticles") # -- miniAOD -- #

# -- for electrons -- # chaged to 2017 ID Map
process.recoTree.rho = cms.untracked.InputTag("fixedGridRhoFastjetAll")
process.recoTree.conversionsInputTag = cms.untracked.InputTag("reducedEgamma:reducedConversions") # -- miniAOD -- #

# -- for photons -- #
process.recoTree.effAreaChHadFile = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfChargedHadrons_90percentBased_TrueVtx.txt")
process.recoTree.effAreaNeuHadFile= cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfNeutralHadrons_90percentBased_TrueVtx.txt")
process.recoTree.effAreaPhoFile   = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfPhotons_90percentBased_TrueVtx.txt")




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
runMetCorAndUncFromMiniAOD(process, isData= not isMC, electronColl=cms.InputTag('slimmedElectrons'), jetCollUnskimmed=cms.InputTag('slimmedJets'))
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
  #process.calibratedPatElectrons *
  #process.calibratedPatPhotons *  
  #process.selectedElectrons *
  #process.selectedPhotons *
  #process.egmPhotonIDSequence *
  #process.egmGsfElectronIDSequence *
  #process.electronIDValueMapProducer *
  #process.fullPatMetSequence *  #This is the phi corrections part
  process.recoTree
)
