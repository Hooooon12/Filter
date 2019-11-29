import os
from shutil import copyfile
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'Suon_Test_v1'
config.General.workArea = 'Test_v1'

config.JobType.pluginName = 'Analysis'
#config.JobType.psetName = '../withEGMcorrection/DATA_cfg_ReReco.py'
config.JobType.psetName = '../withEGMcorrection/DATA_cfg_test_2017promptReco.py'

#config.Data.inputDataset = ''
config.Data.userInputFiles = ['/store/data/Run2017D/DoubleMuon/MINIAOD/PromptReco-v1/000/302/031/00000/0E8F2B04-388F-E711-B66B-02163E0141EA.root']

config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
#config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 40
config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())
config.Data.publication = False

config.Site.storageSite = 'T3_KR_KISTI'

GoldenJSON = './Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'

version = '_v1'
from CRABAPI.RawCommand import crabCommand

config.General.requestName = 'Data_2017_test'+version
#config.Data.inputDataset = '/SingleMuon/Run2016B-03Feb2017_ver2-v2/MINIAOD'
config.Data.lumiMask = GoldenJSON

crabCommand('submit', config = config)
