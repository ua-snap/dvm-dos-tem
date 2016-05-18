##########################################################################
#
# Configure different suites here
#
##########################################################################

# A suite is an assemblage of variables to plot in one or more sub-plots
# along with some configuration and meta-data about the variables (i.e.
# which variables to group in which sub-plots and what units/labels to use.

# Sample suite with comments:
#  'standard' : {
#    'desc': "some help text about this suite",  # Notes
#    'rows': 1,        # rows of subplots to create
#    'cols': 1,        # columns of subplots to create NOTE: must be 1 for now!!
#    'traces': [
#      {
#        'jsontag': 'GPPAll',  # The variable name in json file
#        'axesnum': 0,         # Which subplot axes to draw on
#        'units': 'gC/m^2',    # Label for y axis?
#        'pft': '',            # Empty tag indicating this is a pft variable
#                              # Omit for non-pft variables!
#
#        'pftpart': 'Leaf'     # Leaf, Stem, or Root. Only if 'pft' key is present!
#      },
#    ]
#  }

configured_suites = {
  'Environment': {
    'desc': "Environmental variables plot (precip, temps, light, water)",
    'rows': 5,
    'cols': 1,
    'traces': [
      { 'jsontag': 'TShlw', 'axesnum': 0, },
      { 'jsontag': 'TDeep', 'axesnum': 0, },
      { 'jsontag': 'TMineA', 'axesnum': 0, },
      { 'jsontag': 'TMineB', 'axesnum': 0, },
      { 'jsontag': 'TMineC', 'axesnum': 0},
      { 'jsontag': 'TAir', 'axesnum': 0, },

      { 'jsontag': 'Snowfall', 'axesnum': 1, },
      { 'jsontag': 'Rainfall', 'axesnum': 1, },
      { 'jsontag': 'EET', 'axesnum': 1, },
      { 'jsontag': 'PET', 'axesnum': 1, },
      { 'jsontag': 'VPD', 'axesnum': 1, },

      { 'jsontag': 'WaterTable', 'axesnum': 2, },
      { 'jsontag': 'ActiveLayerDepth', 'axesnum': 2, },

      { 'jsontag': 'VWCShlw', 'axesnum': 3, },
      { 'jsontag': 'VWCDeep', 'axesnum': 3, },
      { 'jsontag': 'VWCMineA', 'axesnum': 3, },
      { 'jsontag': 'VWCMineB', 'axesnum': 3, },
      { 'jsontag': 'VWCMineC', 'axesnum': 3, },

      { 'jsontag': 'PARAbsorb', 'axesnum': 4, },
      { 'jsontag': 'PAR', 'axesnum': 4, },
    ]
  },
  'Soil': {
    'desc': "A set of carbon soil variables.",
    'rows': 6,
    'cols': 1,
    'traces': [
      { 'jsontag': 'LitterfallNitrogenPFT', 'axesnum': 0, 'units': 'gN/m^2', 'pft': '', },
      { 'jsontag': 'TotNitrogenUptake', 'axesnum': 0, 'units': 'gN/m^2', 'pft': '', },

      { 'jsontag': 'CarbonShallow', 'axesnum': 1, 'units': 'gC/m^2', },
      { 'jsontag': 'CarbonDeep', 'axesnum': 1, 'units': 'gC/m^2', },
      { 'jsontag': 'DeadMossCarbon', 'axesnum': 1, 'units': 'gC/m^2', },

      { 'jsontag': 'CarbonMineralSum', 'axesnum': 2, 'units': 'gC/m^2', },

      { 'jsontag': 'OrganicNitrogenSum', 'axesnum':3, 'units': 'gN/m^2', },

      { 'jsontag': 'AvailableNitrogenSum', 'axesnum':4, 'units': 'gN/m^2', },
      { 'jsontag': 'DeadMossNitrogen', 'axesnum': 4, 'units': 'gN/m^2', },
      { 'jsontag': 'StNitrogenUptakeAll', 'axesnum': 4, 'units': 'gN/m^2', },
      { 'jsontag': 'InNitrogenUptakeAll', 'axesnum': 4, 'units': 'gN/m^2', },

      { 'jsontag': 'RH', 'axesnum': 5, 'units': 'gC/m^2',},
      { 'jsontag': 'RHraw', 'axesnum': 5, 'units': 'gC/m^2',},
      { 'jsontag': 'RHsoma', 'axesnum': 5, 'units': 'gC/m^2',},
      { 'jsontag': 'RHsomcr', 'axesnum': 5, 'units': 'gC/m^2',},
      { 'jsontag': 'RHsompr', 'axesnum': 5, 'units': 'gC/m^2',}, 
    ]
  },
  'Vegetation':{
    'desc': "The standard targetted vegetation outputs",
    'rows': 5,
    'cols': 1,
    'traces': [
      { 'jsontag': 'GPPAllIgnoringNitrogen', 'units': 'gC/m^2', 'axesnum': 0, 'pft': '', },
      { 'jsontag': 'NPPAllIgnoringNitrogen', 'units': 'gC/m^2', 'axesnum': 0, 'pft': '', },

      { 'jsontag': 'GPPAll', 'axesnum': 1, 'units': 'gC/m^2', 'pft': '', },
      { 'jsontag': 'NPPAll', 'axesnum': 1, 'units': 'gC/m^2', 'pft': '', },

      { 'jsontag': 'VegCarbon', 'axesnum': 2, 'pft': '', 'pftpart': 'Leaf'},
      { 'jsontag': 'VegCarbon', 'axesnum': 2, 'pft': '', 'pftpart': 'Stem'},
      { 'jsontag': 'VegCarbon', 'axesnum': 2, 'pft': '', 'pftpart': 'Root'},
      { 'jsontag': 'LitterfallCarbonAll', 'axesnum': 2, 'units': 'gC/m^2', 'pft': '', },

      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 3, 'pft': '', 'pftpart': 'Leaf'},
      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 3, 'pft': '', 'pftpart': 'Stem'},
      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 3, 'pft': '', 'pftpart': 'Root'},

      { 'jsontag': 'LitterfallNitrogenPFT', 'axesnum': 4, 'units': 'gC/m^2', 'pft': '', },
      { 'jsontag': 'TotNitrogenUptake', 'axesnum': 4, 'units': 'gC/m^2', 'pft': '', }
    ] 
  },
  'VegSoil':{
    'desc': "The standard targetted vegetation and soil outputs",
    'rows': 9,
    'cols': 1,
    'traces': [
      { 'jsontag': 'GPPAllIgnoringNitrogen', 'units': 'gC/m^2', 'axesnum': 0, 'pft': '', },
      { 'jsontag': 'NPPAllIgnoringNitrogen', 'units': 'gC/m^2', 'axesnum': 0, 'pft': '', },

      { 'jsontag': 'GPPAll', 'axesnum': 0, 'units': 'gC/m^2', 'pft': '', },
      { 'jsontag': 'NPPAll', 'axesnum': 0, 'units': 'gC/m^2', 'pft': '', },

      { 'jsontag': 'VegCarbon', 'axesnum': 1, 'units': 'gC/m^2', 'pft': '', 'pftpart': 'Leaf'},
      { 'jsontag': 'VegCarbon', 'axesnum': 1, 'units': 'gC/m^2', 'pft': '', 'pftpart': 'Stem'},
      { 'jsontag': 'VegCarbon', 'axesnum': 1, 'units': 'gC/m^2', 'pft': '', 'pftpart': 'Root'},
      { 'jsontag': 'LitterfallCarbonAll', 'axesnum': 1, 'units': 'gC/m^2', 'pft': '', },

      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 2, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Leaf'},
      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 2, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Stem'},
      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 2, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Root'},

      { 'jsontag': 'LitterfallNitrogenPFT', 'axesnum': 3, 'units': 'gN/m^2', 'pft': '', },
      { 'jsontag': 'TotNitrogenUptake', 'axesnum': 3, 'units': 'gN/m^2', 'pft': '', },

      { 'jsontag': 'CarbonShallow', 'axesnum': 4, 'units': 'gC/m^2', },
      { 'jsontag': 'CarbonDeep', 'axesnum': 4, 'units': 'gC/m^2', },
      { 'jsontag': 'DeadMossCarbon', 'axesnum': 4, 'units': 'gC/m^2', },

      { 'jsontag': 'CarbonMineralSum', 'axesnum': 5, 'units': 'gC/m^2', },

      { 'jsontag': 'OrganicNitrogenSum', 'axesnum':6, 'units': 'gN/m^2', },

      { 'jsontag': 'AvailableNitrogenSum', 'axesnum':7, 'units': 'gN/m^2', },
      { 'jsontag': 'StNitrogenUptakeAll', 'axesnum': 7, 'units': 'gN/m^2', },
      { 'jsontag': 'InNitrogenUptakeAll', 'axesnum': 7, 'units': 'gN/m^2', },

      { 'jsontag': 'MossdeathCarbon', 'axesnum': 8, 'units': 'gC/m^2', },
      { 'jsontag': 'MossdeathNitrogen', 'axesnum': 8, 'units': 'gC/m^2', },
    ]
  },
  'NCycle':{
    'desc': "Viewing annual N cycle outputs",
    'rows': 7,
    'cols': 1,
    'traces': [
      { 'jsontag': 'NetNMin', 'axesnum':0, 'units': 'gN/m^2', },
      { 'jsontag': 'NetNImmob', 'axesnum':0, 'units': 'gN/m^2', },


      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 1, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Leaf'},
      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 1, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Stem'},
      { 'jsontag': 'VegStructuralNitrogen', 'axesnum': 1, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Root'},
      { 'jsontag': 'VegLabileNitrogen', 'axesnum': 1, 'units': 'gN/m^2', 'pft': '', },

      { 'jsontag': 'LitterfallNitrogenPFT', 'axesnum': 2, 'units': 'gN/m^2', 'pft': '', },
      { 'jsontag': 'TotNitrogenUptake', 'axesnum': 2, 'units': 'gN/m^2', 'pft':'', },
      { 'jsontag': 'StNitrogenUptake', 'axesnum': 2, 'units': 'gN/m^2', 'pft': '', },
      { 'jsontag': 'LuxNitrogenUptake', 'axesnum': 2, 'units': 'gN/m^2', 'pft': '', },

      { 'jsontag': 'LitterfallNitrogen', 'axesnum': 3, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Leaf'},
      { 'jsontag': 'LitterfallNitrogen', 'axesnum': 3, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Stem'},
      { 'jsontag': 'LitterfallNitrogen', 'axesnum': 3, 'units': 'gN/m^2', 'pft': '', 'pftpart': 'Root'},

      { 'jsontag': 'OrganicNitrogenSum', 'axesnum':4, 'units': 'gN/m^2', },

      { 'jsontag': 'AvailableNitrogenSum', 'axesnum':5, 'units': 'gN/m^2', },
      { 'jsontag': 'StNitrogenUptakeAll', 'axesnum': 5, 'units': 'gN/m^2', },
      { 'jsontag': 'InNitrogenUptakeAll', 'axesnum': 5, 'units': 'gN/m^2', },

      { 'jsontag': 'DeadMossNitrogen', 'axesnum': 6, 'units': 'gN/m^2', },
      { 'jsontag': 'AvlNInput', 'axesnum': 6, 'units': 'gN/m^2', },
      { 'jsontag': 'AvlNLost', 'axesnum': 6, 'units': 'gN/m^2', },

    ] 
  },
  'Fire':{
    'desc': "Visualizing fire disturbance of soil and vegetation",
    'rows': 5,
    'cols': 1,
    'traces': [
      { 'jsontag': 'Burnthick', 'units': 'cm', 'axesnum': 0, },
   
      { 'jsontag': 'BurnVeg2AirC', 'axesnum': 1, 'units': 'gC/m^2',},
      { 'jsontag': 'BurnVeg2SoiAbvVegC', 'axesnum': 1, 'units': 'gC/m^2',},
      { 'jsontag': 'BurnVeg2SoiBlwVegC', 'axesnum': 1, 'units': 'gC/m^2',},

      { 'jsontag': 'BurnVeg2AirN', 'axesnum': 2, 'units': 'gN/m^2',},
      { 'jsontag': 'BurnVeg2SoiAbvVegN', 'axesnum': 2, 'units': 'gN/m^2',},
      { 'jsontag': 'BurnVeg2SoiBlwVegN', 'axesnum': 2, 'units': 'gN/m^2',},
      
      { 'jsontag': 'BurnSoi2AirC', 'axesnum': 3, 'units': 'gC/m^2',},

      { 'jsontag': 'BurnSoi2AirN', 'axesnum': 4, 'units': 'gC/m^2',},      

    ] 
  },
}
