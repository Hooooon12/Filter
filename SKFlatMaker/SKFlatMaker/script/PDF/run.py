import os

#filename = 'samplelist_2016.txt'
#filename = 'samplelist_2017.txt'
filename = 'samplelist_2018.txt'
#filename = 'samplelist_Private.txt'

IsPrivate = ("Private" in filename)

lines = open(filename).readlines()
Year = "2016"
if "2017" in filename:
  Year = "2017"
elif "2018" in filename:
  Year = "2018"

hostname = os.environ['HOSTNAME']
SKFlatWD = os.environ['SKFlatWD']

os.system('mkdir -p logs_'+Year)

for line in lines:

  if "#" in line:
    continue

  line = line.strip('\n')
  samplePDs = line.split("/")

  sample = samplePDs[1]

  dascmd = '/cvmfs/cms.cern.ch/common/dasgoclient --limit=1 --query="file dataset='+line+'"'
  if IsPrivate:
    dascmd = '/cvmfs/cms.cern.ch/common/dasgoclient --limit=1 --query="file dataset='+line+' instance=prod/phys03"'
  print dascmd

  os.system(dascmd+' > tmp.txt')

  filepaths = open('tmp.txt').readlines()

  if len(filepaths)==0:
    print "No file for : "+sample
    break

  filepath = filepaths[0].replace('/xrootd','').strip('\n')

  #if 'lxplus' not in hostname:
  filepath = 'root://cms-xrd-global.cern.ch/'+filepath

  cmd = 'cmsRun '+SKFlatWD+'/SKFlatMaker/test/RunSKFlatMaker.py maxEvents=1 inputFiles='+filepath

  InShiftTxt = False

  ## I think it is better to save non-shifted info in the spreadsheet

  HasFile = os.path.isfile(SKFlatWD+'/SKFlatMaker/script/MCPDFInfo/'+Year+'/'+sample+'.txt')

  '''
  if HasFile:

    MCInfoLines = open(SKFlatWD+'/SKFlatMaker/script/MCPDFInfo/'+Year+'/'+sample+'.txt').readlines()
    words = MCInfoLines[0].split()
    # 1001,1009 gaussian  2001,2100 2101,2102 1.5,1.5
    ScaleIDRange = words[0]
    PDFErrorType = words[1]
    PDFErrorIDRange = words[2]
    PDFAlphaSIDRange = words[3]
    PDFAlphaSScaleValue = words[4]

    cmd += ' PDFErrorType='+PDFErrorType
    cmd += ' ScaleIDRange='+ScaleIDRange
    cmd += ' PDFErrorIDRange='+PDFErrorIDRange
    cmd += ' PDFAlphaSIDRange='+PDFAlphaSIDRange
    cmd += ' PDFAlphaSScaleValue='+PDFAlphaSScaleValue

  else:
    ### to avoid exit()
    cmd += ' PDFErrorType=hessian'
  '''

  if IsPrivate:
    cmd = cmd+' sampletype=PrivateMC'
  else:
    cmd = cmd+' sampletype=MC'

  cmd = cmd+' year='+Year

  final_cmd = cmd+' > logs_'+Year+'/'+sample+'.log'
  print final_cmd
  os.system(final_cmd)

os.system('rm tmp.txt')
