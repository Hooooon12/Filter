import FWCore.ParameterSet.Config as cms

SKFlatMaker = cms.EDAnalyzer("SKFlatMaker",

  DataYear = cms.untracked.int32(-1),
  processName = cms.untracked.string("HLT"),
  DebugLevel = cms.untracked.int32(0),

  # -- Object Tags -- #
  Muon = cms.untracked.InputTag("slimmedMuons"),
  Electron = cms.untracked.InputTag("slimmedElectrons"),
  Photon = cms.untracked.InputTag("slimmedPhotons"),
  Jet = cms.untracked.InputTag("slimmedJets"),
  GenJet = cms.untracked.InputTag("slimmedGenJets"),
  FatJet = cms.untracked.InputTag("slimmedJetsAK8"),
  GenFatJet = cms.untracked.InputTag("slimmedGenJetsAK8"),
  MET = cms.InputTag("slimmedMETs"),
  LHEEventProduct = cms.untracked.InputTag("externalLHEProducer"),
  LHERunInfoProduct = cms.untracked.InputTag("externalLHEProducer"),
  GenParticle = cms.untracked.InputTag("genParticles"),

  #### MiniIso
  pfCandsForMiniIso = cms.untracked.InputTag("packedPFCandidates"),
  ## Muon
  ## https://github.com/cms-sw/cmssw/blob/f493624b3018543865bbf04bb8a48c5dae44bc82/RecoMuon/MuonIsolation/python/muonPFIsolationValues_cff.py
  miniIsoParams  = cms.vdouble(0.05, 0.2, 10.0, 0.5, 0.0001, 0.01, 0.01, 0.01, 0.0),
  ## Electron
  ## https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/RecoParticleFlow/PFProducer/python/electronPFIsolationValues_cff.py
  miniIsoParamsE = cms.vdouble(0.05, 0.2, 10.0, 0.0, 0.015, 0.015, 0.08, 0.0, 0.0),
  miniIsoParamsB = cms.vdouble(0.05, 0.2, 10.0, 0.0, 0.000, 0.000, 0.00, 0.0, 0.0),

  # -- electron information -- #
  rho = cms.untracked.InputTag("fixedGridRhoFastjetAll"),
  conversionsInputTag = cms.untracked.InputTag("allConversions"),
  GsfTrack = cms.untracked.InputTag("electronGsfTracks"),
  electron_EA_NHandPh_file = cms.untracked.FileInPath("RecoEgamma/ElectronIdentification/data/Fall17/effAreaElectrons_cone03_pfNeuHadronsAndPhotons_94X.txt"),
  electron_IDtoSave = cms.untracked.vstring(
"cutBasedElectronID-Fall17-94X-V2-veto",
"cutBasedElectronID-Fall17-94X-V2-loose",
"cutBasedElectronID-Fall17-94X-V2-medium",
"cutBasedElectronID-Fall17-94X-V2-tight",
'mvaEleID-Fall17-iso-V2-wp80' ,
'mvaEleID-Fall17-iso-V2-wp90' ,
'mvaEleID-Fall17-iso-V2-wpHZZ' ,
'mvaEleID-Fall17-iso-V2-wpLoose',
'mvaEleID-Fall17-noIso-V2-wp80' ,
'mvaEleID-Fall17-noIso-V2-wp90' ,
'mvaEleID-Fall17-noIso-V2-wpLoose',
"heepElectronID-HEEPV70",
  ),

  #### Rochestor
  roccorPath = cms.string('SKFlatMaker/SKFlatMaker/data/roccor.Run2.v2/RoccoR2017.txt'),

  # -- photon information -- #
  photon_EA_CH_file = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfChargedHadrons_90percentBased_TrueVtx.txt"),
  photon_EA_HN_file = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfNeutralHadrons_90percentBased_TrueVtx.txt"),
  photon_EA_Ph_file = cms.untracked.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfPhotons_90percentBased_TrueVtx.txt"),

  # -- Jet information -- #
  AK4Jet_payloadName = cms.string('AK4PFchs'),
  AK8Jet_payloadName = cms.string('AK8PFPuppi'),
  AK4Jet_JER_PtRes_filepath = cms.string('SKFlatMaker/SKFlatMaker/data/JRDatabase/textFiles/Summer16_25nsV1_MC/Summer16_25nsV1_MC_PtResolution_AK4PFchs.txt'),
  AK4Jet_JER_SF_filepath = cms.string('SKFlatMaker/SKFlatMaker/data/JRDatabase/textFiles/Summer16_25nsV1_MC/Summer16_25nsV1_MC_SF_AK4PFchs.txt'),
  AK8Jet_JER_PtRes_filepath = cms.string('SKFlatMaker/SKFlatMaker/data/JRDatabase/textFiles/Summer16_25nsV1_MC/Summer16_25nsV1_MC_PtResolution_AK8PFPuppi.txt'),
  AK8Jet_JER_SF_filepath = cms.string('SKFlatMaker/SKFlatMaker/data/JRDatabase/textFiles/Summer16_25nsV1_MC/Summer16_25nsV1_MC_SF_AK8PFPuppi.txt'),

  # -- MET information -- #
  METFilterResults_PAT = cms.InputTag("TriggerResults", "", "PAT"),
  METFilterResults_RECO = cms.InputTag("TriggerResults", "", "RECO"),
  pfMET = cms.untracked.InputTag("pfMet"),
     
  # -- Trigger -- #
  TriggerResults = cms.untracked.InputTag("TriggerResults", "", "HLT"),
  TriggerResultsPAT = cms.untracked.InputTag("TriggerResults", "", "PAT"),
  ##TriggerObject = cms.untracked.InputTag("selectedPatTrigger"),
  TriggerObject = cms.untracked.InputTag("slimmedPatTrigger"),     
 
  # -- Else -- #
  GenEventInfo = cms.untracked.InputTag("generator"),
  BeamSpot = cms.untracked.InputTag("offlineBeamSpot"),
  PrimaryVertex = cms.untracked.InputTag("offlinePrimaryVerticesWithBS"),
  Track = cms.untracked.InputTag("generalTracks"),
  PileUpInfo = cms.untracked.InputTag("addPileupInfo"),

  # -- Store Flags -- #
  StoreMuonFlag = cms.untracked.bool(True),
  StoreElectronFlag = cms.untracked.bool(True),
  StoreCalibElectronFlag = cms.untracked.bool(True),
  StorePhotonFlag = cms.untracked.bool(True),
  StoreJetFlag = cms.untracked.bool(True),
  StoreFatJetFlag = cms.untracked.bool(True),
  StoreMETFlag = cms.untracked.bool(True),
  StoreLHEFlag = cms.untracked.bool(True),
  StoreGENFlag = cms.untracked.bool(True),
  KeepAllGen = cms.untracked.bool(True),   
  StorePriVtxFlag = cms.untracked.bool(True),
  StoreHLTReportFlag = cms.untracked.bool(True),
  StoreHLTObjectFlag = cms.untracked.bool(False),
  StoreL1PrefireFlag = cms.untracked.bool(False),

  # -- Filters -- #
  ApplyFilter = cms.untracked.bool(False),
  FilterType = cms.untracked.int32(0),

  #### PDF ID's to be save
  ScaleIDRange = cms.untracked.vint32(-999,-999),
  PDFErrorIDRange = cms.untracked.vint32(-999,-999),
  PDFAlphaSIDRange = cms.untracked.vint32(-999,-999),
  PDFAlphaSScaleValue = cms.untracked.vdouble(-999.,-999.),

)
