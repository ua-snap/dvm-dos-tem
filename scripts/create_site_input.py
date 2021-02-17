#!/usr/bin/env python

import sys

import subprocess
import glob
import shutil

import multiprocessing as mp
import itertools

from contextlib import contextmanager

import configobj
import argparse
import textwrap
import os
import csv

import netCDF4

import datetime as dt
import numpy as np


# Paths to input files from
BASE_AR5_RCP85_CONFIG = textwrap.dedent('''\
  veg src = 'land_cover/v_0_4/iem_vegetation_model_input_v0_4.tif'

  drainage src = 'drainage/Lowland_1km.tif'

  soil clay src = 'BLISS_IEM/mu_claytotal_r_pct_0_25mineral_2_AK_CAN.img'
  soil sand src = 'BLISS_IEM/mu_sandtotal_r_pct_0_25mineral_2_AK_CAN.img'
  soil silt src = 'BLISS_IEM/mu_silttotal_r_pct_0_25mineral_2_AK_CAN.img'

  topo slope src = 'slope/iem_prism_slope_1km.tif'
  topo aspect src = 'aspect/iem_prism_aspect_1km.tif'
  topo elev src = 'elevation/iem_prism_dem_1km.tif'

  h clim first yr = 1901
  h clim last yr = 2015
  h clim orig inst = 'CRU'
  h clim ver = 'TS40'
  h clim tair src = 'tas_mean_C_iem_cru_TS40_1901_2015/tas/tas_mean_C_CRU_TS40_historical_'
  h clim prec src = 'pr_total_mm_iem_cru_TS40_1901_2015/pr_total_mm_CRU_TS40_historical_'
  h clim rsds src = 'rsds_mean_MJ-m2-d1_iem_CRU-TS40_historical_1901_2015_fix/rsds/rsds_mean_MJ-m2-d1_iem_CRU-TS40_historical_'
  h clim vapo src = 'vap_mean_hPa_iem_CRU-TS40_historical_1901_2015_fix/vap/vap_mean_hPa_iem_CRU-TS40_historical_'

  fire fri src = 'iem_ancillary_data/Fire/FRI.tif'
  ''')

MRI_CGCM3_AR5_RCP85_CONFIG = textwrap.dedent('''\
  p clim first yr = 2006
  p clim last yr = 2100
  p clim ver = 'rcp85'

  p clim orig inst = 'MRI-CGCM3'
  p clim tair src = 'tas_mean_C_ar5_MRI-CGCM3_rcp85_2006_2100/tas/tas_mean_C_iem_ar5_MRI-CGCM3_rcp85_'
  p clim prec src = 'pr_total_mm_ar5_MRI-CGCM3_rcp85_2006_2100/pr/pr_total_mm_iem_ar5_MRI-CGCM3_rcp85_'
  p clim rsds src = 'rsds_mean_MJ-m2-d1_ar5_MRI-CGCM3_rcp85_2006_2100_fix/rsds/rsds_mean_MJ-m2-d1_iem_ar5_MRI-CGCM3_rcp85_'
  p clim vapo src = 'vap_mean_hPa_ar5_MRI-CGCM3_rcp85_2006_2100_fix/vap/vap_mean_hPa_iem_ar5_MRI-CGCM3_rcp85_'
  ''')

NCAR_CCSM4_AR5_RCP85_CONFIG = textwrap.dedent('''\
  p clim first yr = 2006
  p clim last yr = 2100
  p clim ver = 'rcp85'

  p clim orig inst = 'NCAR-CCSM4'
  p clim tair src = 'tas_mean_C_ar5_NCAR-CCSM4_rcp85_2006_2100/tas/tas_mean_C_iem_ar5_NCAR-CCSM4_rcp85_'
  p clim prec src = 'pr_total_mm_ar5_NCAR-CCSM4_rcp85_2006_2100/pr/pr_total_mm_iem_ar5_NCAR-CCSM4_rcp85_'
  p clim rsds src = 'rsds_mean_MJ-m2-d1_ar5_NCAR-CCSM4_rcp85_2006_2100_fix/rsds/rsds_mean_MJ-m2-d1_iem_ar5_NCAR-CCSM4_rcp85_'
  p clim vapo src = 'vap_mean_hPa_ar5_NCAR-CCSM4_rcp85_2006_2100_fix/vap/vap_mean_hPa_iem_ar5_NCAR-CCSM4_rcp85_'
  ''')

# variable specification, units, datatype, etc
# more or less the same as defining with netcdf CDL I guess..?
VARSPEC = {
  'vegetation.nc': {
    'veg_class': {'dims':'Y,X', 'dtype': 'i4'}
  },
  'soil_texture.nc': {
    'pct_sand': {'dims':'Y,X', 'dtype': 'f4'},
    'pct_silt': {'dims':'Y,X', 'dtype': 'f4'},
    'pct_clay': {'dims':'Y,X', 'dtype': 'f4'},
  },
  'drainage.nc': {
    'drainage_class': {'dims':'Y,X', 'dtype': 'i4'},
  },
  'co2.nc': {
    'co2': {'dtype':'f4'},
  },
  'topo.nc': {
    'slope': {'dims':'Y,X', 'dtype':'f4'},
    'aspect': {'dims':'Y,X', 'dtype':'f4'},
    'elevation': {'dims':'Y,X', 'dtype':'f4'}
  },
  'fri-fire.nc': {
    'fri': {'dtype':'i4'},
    'fri_severity': {'dtype':'i4'},
    'fri_jday_of_burn': {'dtype':'i4'},
    'fri_area_of_burn': {'dtype':'i4'}
  },
  'projected-explicit-fire.nc': {
    'time': {'dtype':'f4', 'units':'REPLACE ME', 'long_name':'time','calendar':'365_day'},
    'exp_burn_mask': {'dtype':'i4'},
    'exp_area_of_burn': {'dtype':'i4'},
    'exp_fire_severirty': {'dtype':'i4'},
    'exp_jday_of_burn': {'dtype':'i4'},
  },       
  'historic-explicit-fire.nc': {
    'time': {'dtype':'f4', 'units':'REPLACE ME', 'long_name':'time','calendar':'365_day'},
    'exp_burn_mask': {'dtype':'i4'},
    'exp_area_of_burn': {'dtype':'i4'},
    'exp_fire_severirty': {'dtype':'i4'},
    'exp_jday_of_burn': {'dtype':'i4'},
  },       
  'projected-climate.nc': {
    'time': {'dims':'time', 'dtype':'f4', 'units':'REPLACE ME', 'long_name':'time','calendar':'365_day'},
    'tair': {'dims':'time,Y,X', 'dtype':'f4', 'units':'celsius', 'standard_name':'air_temperature'},
    'nirr': {'dims':'time,Y,X', 'dtype':'f4', 'units':'W m-2', 'standard_name':'downwelling_shortwave_flux_in_air'},
    'precip': {'dims':'time,Y,X', 'dtype':'f4', 'units':'mm month-1', 'standard_name':'precipitation_amount'},
    'vapor_press': {'dims':'time,Y,X', 'dtype':'f4', 'units':'hPa', 'standard_name':'water_vapor_pressure'},
  },   
  'historic-climate.nc': {
    'time': {'dims':'time','dtype':'f4', 'units':'REPLACE ME', 'long_name':'time','calendar':'365_day'},
    'tair': {'dims':'time,Y,X','dtype':'f4', 'units':'celsius', 'standard_name':'air_temperature'},
    'nirr': {'dims':'time,Y,X','dtype':'f4', 'units':'W m-2', 'standard_name':'downwelling_shortwave_flux_in_air'},
    'precip': {'dims':'time,Y,X','dtype':'f4', 'units':'mm month-1', 'standard_name':'precipitation_amount'},
    'vapor_press': {'dims':'time,Y,X','dtype':'f4', 'units':'', 'standard_name':'water_vapor_pressure'},
  },
}

def gli_wrapper(srcfile, lon, lat, dtype=None):
  '''gdallocationinfo wrapper'''
  s = "gdallocationinfo -wgs84 -valonly {} {} {}".format(srcfile, lon, lat)
  result = subprocess.run(s.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  # Should handle errors here....not sure what to do with them yet...
  data = result.stdout.decode('utf-8').strip()
  return data

def create_empty_file(fpath, fname):

  ncfile = netCDF4.Dataset(os.path.join(fpath,fname), mode='w', format='NETCDF4')

  Y = ncfile.createDimension('Y', 1)
  X = ncfile.createDimension('X', 1)
  
  if 'time' in VARSPEC[fname]:
    ncfile.createDimension('time', None) # append along time axis

  lat = ncfile.createVariable('lat', np.float32, ('Y', 'X',))
  lon = ncfile.createVariable('lon', np.float32, ('Y', 'X',))
  print(fname)
  print(VARSPEC[fname])
  for varname, spec in VARSPEC[fname].items():
    v = ncfile.createVariable(varname, spec['dtype'], spec['dims'].split(','))
    for attribute, attribute_value in spec.items():
      if attribute == 'dtype' or attribute == 'dims':
        pass
      else:
        v.setncattr(attribute, attribute_value)

  ncfile.close()

def fill_file_A(fpath, fname, var=None, data=None):
  '''Assumes that data passed in is the correct shape. No precautions taken here.'''
  if var not in VARSPEC[fname]:
    raise RuntimeError("Can't find var: {} in VARSPEC!".format(var))
  ncfile = netCDF4.Dataset(os.path.join(fpath, fname), mode='a')
  ncfile.variables[var][:] = data
  ncfile.close()

def fill_file_B(fpath, fname, var=None, data=None, start=None, end=None):
  '''Not tested, don't think this is the way to go...prefer A'''
  if var not in VARSPEC[fname]:
    raise RuntimeError("Can't find var: {} in VARSPEC!".format(var))
  if start is None and end is None:
    print("Start and end are both None, assume this file does not have a time axis to worry about.")
    # Assumptions: 
    #  - file has dims Y,X each size 1
    #  - file has dims lat,lon each in terms of (Y,X)
    #  - file has one or more data variables, each in terms of (Y,X)
    ncfile = netCDF4.Dataset(os.path.join(fpath, fname), mode='a')
    ncfile.variables[var][:] = data
    ncfile.close()
  else: 
    print("Start or end is set, so we have to assume file has time axis.")
    # Assumptions: 
    #  - file has dims time,Y,X; time dimension is unlimited, Y and X are both size=1
    #  - file has coordinate variable named time, interms of (time)
    #  - file has variables lat,lon each in terms of (Y,X)
    #  - file has one of more variables in terms of (time,Y,X)
    #  - file 
    print("STUB - not doing anything yet...")

def get_SNAP_climate_data(var, lon, lat, which=None, config=None, start=None, end='all'):
  '''Extract climate data from SNAP source files.
  This function is specific to the SNAP tif files so don't try to generalize it.'''
  if start is None:
    raise RuntimeError("Must set start date: 'YYYY-MM-DD'")

  # Map here from SNAP variable names (as in config dict) to 
  # our desired names (as expressed in VARSPEC)

  if which == 'historic':
    src_path = os.path.join(args.src_climate, config['h clim {} src'.format(var)])
  elif which == 'projected':
    src_path = os.path.join(args.src_climate, config['p clim {} src'.format(var)])
  else:
    src_path = '' # probably gonna crash later

  src_files = glob.glob(src_path + "*.tif")
  
  def date_key(x):
    '''Function that helps sort files by date. 
    Takes something like: 
        /some/long/path/mean_C_CRU_TS40_historical_11_1902.tif
    and returns a datetime object created from end of the file name.
    '''
    fdate = dt.datetime(
      year=int(os.path.splitext(os.path.basename(x))[0].split('_')[-1]), 
      month=int(os.path.splitext(os.path.basename(x))[0].split('_')[-2]),
      day=1)
    return fdate

  src_files = sorted(src_files, key=date_key)

  # filter src_files here based on start and end...

  # basic, non-parallel approach:
  #data = [gli_wrapper(i, lon, lat) for i in src_files]

  # Or parallel approach
  # make the args (list of tuples) that get passed to gli_wrapper
  arg_list = zip(src_files, itertools.repeat(lon), itertools.repeat(lat))
  with mp.Pool(processes=6) as pool:
    data = pool.starmap(gli_wrapper, arg_list)

  #from IPython import embed; embed()
  # Handle issues for each variable...
  if var == 'rsds':
    # Coerce data into expected type. Note variable names are different - 
    # in the SNAP files (config dict) it is rsds, in our files (VARSPEC) it is nirr
    data = np.array(data, dtype=VARSPEC['{}-climate.nc'.format(which)]['nirr']['dtype'])
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("%% NOTE! Converting rsds (nirr) from MJ/m^2/day to W/m^2!")
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    data[:] = (1000000 / (60*60*24)) * data[:]

  assert len(data) == len(src_files), "data array does not match number of source files!"


  # Build out the time coordinate variable info...
  def time_offset(dt_obj, start_point):
    '''Takes a datetime object and a starting point (also datetime object)
    and returns the netcdf time offset, i.e. "days since YYYY-MM-DD".
    '''
    tm_offset = netCDF4.date2num(
        dt_obj, 
        units="days since {}".format(start_point), 
        calendar='365_day'
    )
    return tm_offset

  start_point = date_key(src_files[0]).strftime('%Y-%m-%d')
  timecoord = [time_offset(date_key(i), start_point) for i in src_files]

  return data, timecoord




def src_climate_validator(arg_src_climate):
  '''Make sure that the directory exists and has files...'''
  try:
    files = os.listdir(arg_src_climate)
  except OSError as e:
    msg = "Invalid folder for source climate data! {}".format(e)
    raise argparse.ArgumentTypeError(msg)
  return arg_src_climate

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
 
      description=textwrap.dedent('''help'''),
      epilog=textwrap.dedent('''epilog'''),
  )
  parser.add_argument('--src-climate', type=src_climate_validator,  help='path to source climate files')
  parser.add_argument('--src-ancillary', help='path to source ancillary files')
  parser.add_argument('--src-config', default='mri-cgcm3', choices=['mri-cgcm3','ncar-ccsm4'],
    help='choose config that maps how the source input files should be laid out (directories, file names, etc)')

  parser.add_argument('--outdir', default='input-staging-area', 
    help='path to directory where new folder of files should be written')
  parser.add_argument('--tag', default='cru-ts40_ar5_rcp85_')

  args = parser.parse_args()
  print("Command line args: {}".format(args))

  print("Reading config file...")
  config = configobj.ConfigObj(BASE_AR5_RCP85_CONFIG.split("\n"))

  # Pick up the user's config option for which projected climate to use 
  # overwrite the section in the config object.
  cmdline_config = configobj.ConfigObj()
  if 'ncar-ccsm4' in args.src_config:
    cmdline_config = configobj.ConfigObj(NCAR_CCSM4_AR5_RCP85_CONFIG.split("\n"))
  elif 'mri-cgcm3' in args.src_config:
    cmdline_config = configobj.ConfigObj(MRI_CGCM3_AR5_RCP85_CONFIG.split("\n"))
  config.merge(cmdline_config)
  #print("\n".join(config.write()))


  lon, lat = (-164.823923, 65.161991)


  base_outdir = os.path.join( args.outdir, 'SITE_{}_{}'.format(args.tag, config['p clim orig inst']) )
  print("Will be (over)writing files to:    ", base_outdir)
  if not os.path.exists(base_outdir):
    os.makedirs(base_outdir)

  create_empty_file(base_outdir, 'drainage.nc')
  drainage_class = gli_wrapper(os.path.join(args.src_ancillary, config['drainage src']), lon, lat)
  # Need to threshold drainage data before writing...
  fill_file_A(base_outdir, 'drainage.nc', var='drainage_class', data=drainage_class)

  create_empty_file(base_outdir, 'topo.nc')
  slope = gli_wrapper(os.path.join(args.src_ancillary, config['topo slope src']), lon, lat)
  aspect = gli_wrapper(os.path.join(args.src_ancillary, config['topo aspect src']), lon, lat)
  elevation = gli_wrapper(os.path.join(args.src_ancillary, config['topo elev src']), lon, lat)
  fill_file_A(base_outdir, 'topo.nc', var="slope", data=slope)
  fill_file_A(base_outdir, 'topo.nc', var="aspect", data=aspect)
  fill_file_A(base_outdir, 'topo.nc', var="elevation", data=elevation)


  create_empty_file(base_outdir, 'vegetation.nc')
  veg_class = gli_wrapper(os.path.join(args.src_ancillary, config['veg src']), lon, lat)
  fill_file_A(base_outdir, 'vegetation.nc', var='veg_class', data=veg_class)

  create_empty_file(base_outdir, 'soil_texture.nc')
  pct_sand = gli_wrapper(os.path.join(args.src_ancillary, config['soil sand src']), lon, lat)
  pct_silt = gli_wrapper(os.path.join(args.src_ancillary, config['soil silt src']), lon, lat)
  pct_clay = gli_wrapper(os.path.join(args.src_ancillary, config['soil clay src']), lon, lat)
  fill_file_A(base_outdir, 'soil_texture.nc', var='pct_sand', data=pct_sand)
  fill_file_A(base_outdir, 'soil_texture.nc', var='pct_silt', data=pct_silt)
  fill_file_A(base_outdir, 'soil_texture.nc', var='pct_clay', data=pct_clay)

  create_empty_file(base_outdir, 'historic-climate.nc')
  tair_data, _ = get_SNAP_climate_data('tair', lon, lat, which='historic', config=config, start='1901-01-01', end='all')
  nirr_data, _ = get_SNAP_climate_data('rsds', lon, lat, which='historic', config=config, start='1901-01-01', end='all')
  vapo_data, _ = get_SNAP_climate_data('vapo', lon, lat, which='historic',config=config, start='1901-01-01', end='all')
  precip_data, time_coord = get_SNAP_climate_data('prec', lon, lat, which='historic', config=config, start='1901-01-01', end='all')
  fill_file_A(base_outdir, 'historic-climate.nc', var='tair', data=tair_data)
  fill_file_A(base_outdir, 'historic-climate.nc', var='nirr', data=nirr_data)
  fill_file_A(base_outdir, 'historic-climate.nc', var='vapor_press', data=vapo_data)
  fill_file_A(base_outdir, 'historic-climate.nc', var='precip', data=precip_data)

  create_empty_file(base_outdir, 'projected-climate.nc')
  tair_data, _ = get_SNAP_climate_data('tair', lon, lat, which='projected', config=config, start='2016-01-01', end='all')
  nirr_data, _ = get_SNAP_climate_data('rsds', lon, lat, which='projected', config=config, start='2016-01-01', end='all')
  vapo_data, _ = get_SNAP_climate_data('vapo', lon, lat, which='projected',config=config, start='2016-01-01', end='all')
  precip_data, time_coord = get_SNAP_climate_data('prec', lon, lat, which='projected', config=config, start='2016-01-01', end='all')
  fill_file_A(base_outdir, 'projected-climate.nc', var='tair', data=tair_data)
  fill_file_A(base_outdir, 'projected-climate.nc', var='nirr', data=nirr_data)
  fill_file_A(base_outdir, 'projected-climate.nc', var='vapor_press', data=vapo_data)
  fill_file_A(base_outdir, 'projected-climate.nc', var='precip', data=precip_data)



  from IPython import embed; embed()





    # import datetime as dt

    # startdt = dt.datetime.strptime(start, "%Y-%m-%d")
    # if end == 'all':
    #   print("Not implemented yet...")
    #   exit(-1)
    # else:
    #   enddt = dt.datetime.strptime(end, '%Y-%m-%d')

    #for year in 


    # Does not work, loses time over time...
    # for month in range(0,25):
    #   mid_month = (startdt + dt.timedelta(days=15))
    #   mid_month = mid_month + dt.timedelta(days=(30*month))
    #   print(mid_month.strftime("%Y-%m"))






    #pass #src_path = 


  # s = "gdallocationinfo -wgs84 -valonly {} {} {}".format(os.path.join(args.src_ancillary, config['veg src']), lon, lat)
  # result = subprocess.run(s.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
  # veg_class = result.stdout.decode('utf-8')



  #result.check_returncode()
  
  

#./create_site_input.py --wgs84 --xy -164.823923 65.161991 --tag koug_hill --which all --overwrite 