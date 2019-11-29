from CRABClient.UserUtilities import config, getUsernameFromSiteDB

config = config()

config.General.requestName = 'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8' ## EDIT
config.General.workArea = 'crab_projects'
config.General.transferLogs = False
config.General.transferOutputs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'RunSKFlatMaker.py'
config.JobType.sendExternalFolder = True
config.JobType.pyCfgParams = [] ## EDIT
#config.JobType.numCores = 8
#config.JobType.maxMemoryMB = 4000

config.Data.inputDataset = '/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAOD-94X_mc2017_realistic_v10-v2/MINIAODSIM' ## EDIT

config.Data.splitting = 'FileBased' ## EDIT
config.Data.unitsPerJob = 1
config.Data.outLFNDirBase = '/store/user/%s/SKFlat/' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'SKFlatMaker_2017_v1'

config.Site.storageSite = 'T3_KR_KISTI'
