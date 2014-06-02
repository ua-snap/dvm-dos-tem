#!/usr/bin/env python

# could add code here to load up calibration_targets variable from the
# contents of an excel file...? or just plain csv?

calibration_targets = {
  ## WARNING: JUNK, PLACEHOLDER VALUES! USE AT YOUR OWN RISK!
  "deciduous": {
    'cmtnumber': 3,
                                 #    pft0     pft1      pft2      pft3     pft4     pft5     pft6     pft7     pft8    pft9   
                                 #  Spruce    Salix    Decid.   E.green   Sedges    Forbs  Grasses  Lichens  Feather.   Misc.
    'GPPAllIgnoringNitrogen':    [  468.74,   81.73,    27.51,    22.23,   29.85,   28.44,   11.29,    7.75,   42.18,   0.00 ], # ingpp     (gC/m2/year)   GPP without N limitation
    'NPPAllIgnoringNitrogen':    [  200.39,   61.30,    25.73,    20.79,   27.91,   26.59,   10.56,    7.25,   39.44,   0.00 ], # innpp     (gC/m2/year)   NPP without N limitation 
    'NPPAll':                    [  133.59,   40.87,    13.76,    11.12,   14.92,   14.22,    5.65,    3.87,   21.09,   0.00 ], # npp       (gC/m2/year)   NPP with N limitation
    'Nuptake':                   [    0.67,    0.42,     0.17,     0.17,    0.22,    0.21,    0.08,    0.01,    0.24,   0.00 ], # nuptake   (gN/m2/year)
    'VegCarbon': {
      'Leaf':                    [  121.92,   13.17,     8.85,     6.03,    5.60,    5.33,    2.12,   35.22,  100.35,   0.00 ], # vegcl     (gC/m2)
      'Stem':                    [ 1519.45,  129.81,    76.07,    13.10,    0.00,    0.00,    0.00,    0.00,    0.00,   0.00 ], # vegcw     (gC/m2)
      'Root':                    [  410.34,    4.00,     4.20,     1.17,    9.33,    8.89,    3.53,    0.00,    0.00,   0.00 ], # vegcr     (gC/m2)
    },
    'VegStructuralNitrogen': {
      'Leaf':                    [    1.05,    0.53,     0.38,     0.15,    0.26,    0.25,    0.09,    0.99,    2.31,   0.00 ], # vegnl     (gN/m2)
      'Stem':                    [    2.74,    3.05,     3.10,     0.23,    0.00,    0.00,    0.00,    0.00,    0.00,   0.00 ], # vegnw     (gN/m2)
      'Root':                    [    3.52,    0.06,     0.06,     0.01,    0.19,    0.17,    0.07,    0.00,    0.00,   0.00 ], # vegnr     (gN/m2)
    },
    'MossDeathC':              178.00,    #  dmossc
    'CarbonShallow':          1783.00,    #  shlwc
    'CarbonDeep':             5021.00,    #  deepc
    'CarbonMineralSum':       9000.00,    #  minec
    'OrganicNitrogenSum':      363.00,    #  soln
    'AvailableNitrogenSum':      0.76,    #  avln
  },
  ## WARNING: JUNK, PLACEHOLDER VALUES! USE AT YOUR OWN RISK!
  "black spruce": {
    'cmtnumber': 0,
                                 #    pft0     pft1      pft2      pft3     pft4     pft5     pft6     pft7     pft8    pft9   
                                 #  Spruce    Salix    Decid.   E.green   Sedges    Forbs  Grasses  Lichens  Feather.   Misc.
    'GPPAllIgnoringNitrogen':    [  468.74,   81.73,    27.51,    22.23,   29.85,   28.44,   11.29,    7.75,   42.18,   0.00 ], # ingpp     (gC/m2/year)   GPP without N limitation
    'NPPAllIgnoringNitrogen':    [  200.39,   61.30,    25.73,    20.79,   27.91,   26.59,   10.56,    7.25,   39.44,   0.00 ], # innpp     (gC/m2/year)   NPP without N limitation 
    'NPPAll':                    [  133.59,   40.87,    13.76,    11.12,   14.92,   14.22,    5.65,    3.87,   21.09,   0.00 ], # npp       (gC/m2/year)   NPP with N limitation
    'Nuptake':                   [    0.67,    0.42,     0.17,     0.17,    0.22,    0.21,    0.08,    0.01,    0.24,   0.00 ], # nuptake   (gN/m2/year)
    'VegCarbon': {
      'Leaf':                    [  121.92,   13.17,     8.85,     6.03,    5.60,    5.33,    2.12,   35.22,  100.35,   0.00 ], # vegcl     (gC/m2)
      'Stem':                    [ 1519.45,  129.81,    76.07,    13.10,    0.00,    0.00,    0.00,    0.00,    0.00,   0.00 ], # vegcw     (gC/m2)
      'Root':                    [  410.34,    4.00,     4.20,     1.17,    9.33,    8.89,    3.53,    0.00,    0.00,   0.00 ], # vegcr     (gC/m2)
    },
    'VegStructuralNitrogen': {
      'Leaf':                    [    1.05,    0.53,     0.38,     0.15,    0.26,    0.25,    0.09,    0.99,    2.31,   0.00 ], # vegnl     (gN/m2)
      'Stem':                    [    2.74,    3.05,     3.10,     0.23,    0.00,    0.00,    0.00,    0.00,    0.00,   0.00 ], # vegnw     (gN/m2)
      'Root':                    [    3.52,    0.06,     0.06,     0.01,    0.19,    0.17,    0.07,    0.00,    0.00,   0.00 ], # vegnr     (gN/m2)
    },
    'MossDeathC':              178.00,    #  dmossc
    'CarbonShallow':          1783.00,    #  shlwc
    'CarbonDeep':             5021.00,    #  deepc
    'CarbonMineralSum':       9000.00,    #  minec
    'OrganicNitrogenSum':      363.00,    #  soln
    'AvailableNitrogenSum':      0.76,    #  avln
  },
}

def cmtnames():
  '''returns a list of community names'''
  return [key for key in calibration_targets.keys()]

def cmtnumbers():
  '''returns the cmt number for each known commnunity'''
  return [data['cmtnumber'] for k, data in calibration_targets.iteritems()]

def caltargets2prettystring():
  '''returns a formatted string with one cmt name/number pair per line'''
  s = ''
  for key, value in calibration_targets.iteritems():
    s += "{1:02d} {0:}\n".format(key, value['cmtnumber'])
  s = s[0:-1] # trim the last new line
  return s

def toxl():
  ''' A total hack attempt at writing out an excel workbook from the values
  that are hardcoded above in the calibraiton_targets dict. Actually kinda 
  works though...'''

  import xlwt

  font0 = xlwt.Font()
  font0.name = 'Times New Roman'
  font0.colour_index = 2
  font0.bold = True

  style0 = xlwt.XFStyle()
  style0.font = font0

  wb = xlwt.Workbook()

  nzr = 5
  nzc = 5


  for community, cmtdata in calibration_targets.iteritems():
    ws = wb.add_sheet(community)

    #        r  c
    ws.write(0, 0, 'community number:', style0)
    ws.write(0, 1, cmtdata['cmtnumber'])

    r = nzr
    for key, data in cmtdata.iteritems():
      print "OPERATING ON: %s" % key
      if key == 'cmtnumber':
        pass
      else:
        ws.write(r, 1, key) # col 1, the main key
        print "row: %s col: %s key: %s" % (r, 1, key)
        if type(data) == list:
          for col, pftvalue in enumerate(data):
            ws.write(r, col + nzc, pftvalue)
            print "row: %s col: %s pftvalue: %s" % (r, col + nzc, pftvalue)

          r = r + 1
            
        elif type(data) == dict:
          for compartment, pftvals in data.iteritems():
            ws.write(r, 2, compartment)
            print "row: %s col: %s compartment: %s" % (r, 2, compartment)

            for col, pftvalue in enumerate(pftvals):
              ws.write(r, col + nzc, pftvalue)
              print "row: %s col: %s pftvalue: %s" % (r, col + nzc, pftvalue)

            r = r + 1
        elif type(data) == int or type(data) == float:
          print "WTF"
          ws.write(r, nzc, data)
          print "row: %s col: %s data: %s" % (r, nzc, data)
          r = r + 1



  wb.save('example.xls')




def frmxl():
  print "NOT IMPLEMENTED"

if __name__ == '__main__':
  print "Nothing happening here yet..."

  # for testing:
  toxl()






