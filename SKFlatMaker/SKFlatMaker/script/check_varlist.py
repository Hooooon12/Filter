import os

def InFile(line_files, words):

  for fline in line_files:

    ThisWordsOkay = True

    for word in words:
      if word not in fline:
        ThisWordsOkay = False

    if ThisWordsOkay:
      return True

  return False
  

objects = [
"Electron",
"FatJet",
"GEN",
"Jet",
"LHE",
"MET",
"Muon",
"Photon",
"Trigger",
]

BashColor_Red = '\033[0;31m'
BashColor_Green = '\033[0;32m'
BashColor_NC = '\033[0m'

lines_header = open('../interface/SKFlatMaker.h').readlines()
lines_src = open('../src/SKFlatMaker.cc').readlines()

for obj in objects:

  HasMissingVariable = False

  print "######################################"
  print "#### Checking ["+obj+"] variables ####"
  print "######################################"
  print ""

  lines = open('varlist_'+obj+'.txt').readlines()

  # 0 = header
  # 1 = src, initilize
  # 2 = src, Branch
  # 3 = src, fill value

  for WhatToPrint in range(0,4):

    if WhatToPrint==0:
      print "#### interface/SKFlatMaker.h ####"
      print ""
    if WhatToPrint==1:
      print "#### src/SKFlatMaker.cc, SKFlatMaker::analyze() ####"
      print ""
    if WhatToPrint==2:
      print "#### src/SKFlatMaker.cc, SKFlatMaker::beginJob() ####"
      print ""
    if WhatToPrint==3:
      print "#### src/SKFlatMaker.cc, SKFlatMaker::analyze() ####"
      print ""

    for line in lines:
      words = line.strip('\n').split('\t')

      vartype = words[0]
      varname = words[1]
      isvector = words[2]

      if isvector=="1":
        if WhatToPrint==0:

          words = ["vector", vartype, varname]
          if not InFile(lines_header, words):
            HasMissingVariable = True
            print '  vector<'+vartype+'> '+varname+';'

        elif WhatToPrint==1:

          words = [varname, 'clear']
          if not InFile(lines_src, words):
            HasMissingVariable = True
            print '  '+varname+'.clear();'

        elif WhatToPrint==2:

          words = ['DYTree', 'Branch', varname, 'vector', vartype, '&', varname]
          if not InFile(lines_src, words):
            HasMissingVariable = True
            print '    DYTree->Branch("'+varname+'", "vector<'+vartype+'>", &'+varname+');'

        elif WhatToPrint==3:

          words = [varname, "push_back"]
          if not InFile(lines_src, words):
            HasMissingVariable = True
            #print '    '+varname+'.push_back( );'
            print varname+' : not filled'

      else:
        if WhatToPrint==0:

          words = [vartype, varname]
          if not InFile(lines_header, words):
            HasMissingVariable = True
            print '  '+vartype+' '+varname+';'

        elif WhatToPrint==1:

          words = [varname, '=']
          if not InFile(lines_src, words):
            HasMissingVariable = True
            print '  '+varname+' = -999;'

        elif WhatToPrint==2:

          vartypechar = ""
          if vartype=="double":
            vartypechar = "D"
          elif vartype=="int":
            vartypechar = "I"
          elif vartype=="unsigned int":
            vartypechar = "i"
          elif vartype=="bool":
            vartypechar = "O"

          words = ['DYTree', 'Branch', varname, '&', varname, vartypechar]
          if not InFile(lines_src, words):
            HasMissingVariable = True
            print '    DYTree->Branch("'+varname+'",&'+varname+',"'+varname+'/'+vartypechar+'");'

    if not HasMissingVariable:
      print "====> "+BashColor_Green+"All okay"+BashColor_NC
    else:
      print "====> "+BashColor_Red+"Missing "+BashColor_NC

    print ""
