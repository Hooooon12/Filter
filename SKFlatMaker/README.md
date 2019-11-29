# SKFlatMaker

## For 2016 and 2017

### Environment
```bash
# Setup for >= CMSSW_9_4_10
export SCRAM_ARCH=slc6_amd64_gcc630

# For machines with CVMFS
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

# Make CMSSW directory

#### 1) For a test job or developement 
cmsrel CMSSW_9_4_10
cd CMSSW_9_4_10/src

#### 2) For production, let's not use the working directory but use new and clean directory
#### Also, I recommend using lxplus
scram p -n Run2Legacy_v3__CMSSW_9_4_10 CMSSW CMSSW_9_4_10
cd Run2Legacy_v3__CMSSW_9_4_10/src

#### Then,
cmsenv
git cms-init

######################
#### EGamma smearing
#### https://twiki.cern.ch/twiki/bin/view/CMS/EgammaMiniAODV2#2017_MiniAOD_V2
######################

git cms-merge-topic cms-egamma:EgammaPostRecoTools #just adds in an extra file to have a setup function to make things easier
scram b

#############
#### v2 VID
#### https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_formats
#### The Fall17_94X_V2 ID modules are included by default for CMSSW_10_2_X and higher, for CMSSW_9_4_X you can obtain them through following git cms-merge-topic: 
#### Both CutBased and MVA
#############

git cms-merge-topic cms-egamma:EgammaID_949
scram b

##########################
#### MET EE Noise filter
#### https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1865.html
#### https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETUncertaintyPrescription#Instructions_for_9_4_X_X_9_for_2
##########################

git cms-merge-topic cms-met:METFixEE2017_949_v2
scram b

###############################
#### Rerun ecalBadCalibfilter
#### https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2#How_to_run_ecal_BadCalibReducedM
###############################

git cms-addpkg RecoMET/METFilters
scram b

#########################
#### L1Prefire reweight
#### https://twiki.cern.ch/twiki/bin/view/CMS/L1ECALPrefiringWeightRecipe
#########################

#git cms-merge-topic lathomas:L1Prefiring_9_4_9
git cms-merge-topic jedori0228:L1Prefiring_9_4_9__UseFileFileInPath
#### Do not compile here, we need SKFlatMaker cloned

######################
#### Now SKFlatMaker
######################

# Copy this code
git clone git@github.com:CMSSNU/SKFlatMaker.git
cd SKFlatMaker

#### 1) For a test job or development 
git checkout master
git checkout -b <testbranch>

#### 2) For production
git checkout Run2Legacy_v3 #### use the tag

cd $CMSSW_BASE/src

# Compile
scram b -j4

# Setup
cd $CMSSW_BASE/src/SKFlatMaker
source setup.sh

# Now, submitting crab jobs.
cd $CMSSW_BASE/src/SKFlatMaker/SKFlatMaker/script/CRAB3
# txtfilename = "<txtfile which has list of samples you want to run>"
# e.g., if txtfilename = "2017_DATA.txt"
python MakeCrab.py <txtfilename>
# then it will print crab submission commands
# copy them somewhere
cd $SKFlatTag/2017/crab_submission_DATA/
# now, run the submission commands
```

## For 2018

### Environment
```bash
# Setup for >= CMSSW_10_2_5
export SCRAM_ARCH=slc6_amd64_gcc700

# For machines with CVMFS
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

# Make CMSSW directory

#### 1) For a test job or developement
cmsrel CMSSW_10_4_0_patch1
cd CMSSW_10_4_0_patch1/src

#### 2) For production, let's not use the working directory but use new and clean directory
#### Also, I recommend using lxplus
scram p -n Run2Legacy_v3__CMSSW_10_4_0_patch1 CMSSW CMSSW_10_4_0_patch1
cd Run2Legacy_v3__CMSSW_10_4_0_patch1/src

#### Then,
cmsenv
git cms-init

######################
#### EGamma smearing
#### https://twiki.cern.ch/twiki/bin/view/CMS/EgammaMiniAODV2#2018_MiniAOD
#### https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaPostRecoRecipes#2018_Preliminary_Energy_Correcti
######################

git cms-merge-topic cms-egamma:EgammaPostRecoTools #just adds in an extra file to have a setup function to make things easier
scram b -j 8

git clone git@github.com:cms-egamma/EgammaAnalysis-ElectronTools.git EgammaAnalysis/ElectronTools/data
cd EgammaAnalysis/ElectronTools/data
git checkout ScalesSmearing2018_Dev
cd -
git cms-merge-topic cms-egamma:EgammaPostRecoTools_dev
scram b -j 8

###############################
#### Rerun ecalBadCalibfilter
#### https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2#How_to_run_ecal_BadCalibReducedM
###############################

git cms-addpkg RecoMET/METFilters

######################
#### Now SKFlatMaker
######################

# Copy this code
git clone git@github.com:CMSSNU/SKFlatMaker.git
cd SKFlatMaker

#### 1) For a test job or development 
git checkout master
git checkout -b <testbranch>

#### 2) For production
git checkout Run2Legacy_v3 #### use the tag

cd $CMSSW_BASE/src

# Compile
scram b -j 8

# Setup
cd $CMSSW_BASE/src/SKFlatMaker
source setup.sh

# Now, submitting crab jobs.
cd $CMSSW_BASE/src/SKFlatMaker/SKFlatMaker/script/CRAB3
# edit MakeCrab.py
# txtfilename = "<txtfile which has list of samples you want to run>"
# e.g., if txtfilename = "2018_DATA.txt"
python MakeCrab.py
# then it will print crab submission commands
# copy them somewhere
cd $SKFlatTag/2018/crab_submission_DATA/
# now, run the submission commands
```

# test runs
```bash
cd $CMSSW_BASE/src/SKFlatMaker/SKFlatMaker/test/
cmsRun RunSKFlatMaker.py year=2016 sampletype=DATA maxEvents=1000 ## Run 2016 DATA
cmsRun RunSKFlatMaker.py year=2016 sampletype=MC maxEvents=1000 ## Run 2016 MC
cmsRun RunSKFlatMaker.py year=2017 sampletype=DATA maxEvents=1000 ## Run 2017 DATA
cmsRun RunSKFlatMaker.py year=2017 sampletype=MC maxEvents=1000 ## Run 2017 MC
cmsRun RunSKFlatMaker.py year=2018 sampletype=DATA maxEvents=1000 ## Run 2018 DATA
cmsRun RunSKFlatMaker.py year=2018 sampletype=MC maxEvents=1000 ## Run 2018 MC
```
