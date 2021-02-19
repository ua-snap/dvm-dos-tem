#!/usr/bin/env python

import os
import errno
import glob
import netCDF4 as nc
import numpy as np

import argparse
import textwrap

import subprocess

def mkdir_p(path):
  '''Emulates the shell's `mkdir -p`.'''
  try:
    os.makedirs(path)
  except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise


'''
Utility functions for working with dvmdostem inputs.
'''

#################################################################
# Define custom errors that are relevant for this application
#################################################################
class BadInputFilesValueError(ValueError):
  '''Raise when there is a problem with the input files.'''

class MissingInputFilesValueError(ValueError):
  '''Raise when not enough files are present.'''


def verify_input_files(in_folder):
  '''
  Raises various exceptions if there are problems with the files in the in_folder.

  Parameters
  ----------
  in_folder : str
    A path to a folder of dvmdostem inputs.

  Throws
  ------  
  BadInputFilesValueError, 

  Returns
  -------
  None
  '''
  required_files = set(['co2.nc', 'drainage.nc', 'fri-fire.nc', 
      'historic-climate.nc', 'historic-explicit-fire.nc',
      'projected-climate.nc', 'projected-explicit-fire.nc', 'run-mask.nc',
      'soil-texture.nc', 'topo.nc', 'vegetation.nc'])

  files = set([f for f in os.listdir(in_folder) if os.path.isfile(os.path.join(in_folder, f))])
  dirs = [d for d in os.listdir(in_folder) if os.path.isdir(os.path.join(in_folder, d))]

  # any 
  #print "Symetric difference: ", files.symmetric_difference(required_files)
  
  if len(files.difference(required_files)) > 0:
    print("WARNING: extra files present: ", files.difference(required_files))

  if len(required_files.difference(files)):
    msg = "Missing files: {}".format(required_files.difference(files))
    raise MissingInputFilesValueError(msg)

  if 'output' not in dirs:
    raise MissingInputFilesValueError("'output/' directory not present!")


def crop_attr_string(ys='', xs='', yo='', xo='', msg=''):
  '''
  Returns a string to be included as a netCDF global attribute named "crop".

  The string will start with the filename and function name responsible for
  creating the (new) input file, and if provided, will include values for size
  and offset. The size attributes are relatively self-explanatory (by looking
  at the size of the resulting file), and so can generally be ignored. The
  offset arguments are much more important to include.

  Parameters
  ----------
  ys, xs : str
    Strings denoting the spatial size of the domain.
  yo, xo : str
    Strings denoting the pixel offsets used to crop the data from the input dataset
  msg : str
    An additional message string to be included.

  Returns
  -------
  s : str
    A string something like:
    "./scripts/input_util.py::crop_file --ysize 3 --xsize 4 --yx 0 0
  '''
  import inspect
  cf = inspect.currentframe().f_back # <-- gotta look up one frame.

  # Start with the file name and function name
  s = "{}::{}".format(cf.f_code.co_filename, cf.f_code.co_name,)

  # add other info if present.
  for t, val in zip(['--ysize','--xsize','--yx',''],[ys,xs,' '.join([str(yo), str(xo)]), msg]):
    if val != '':
      s += " {} {}".format(t, val)

  return s


def crop_file(infile, outfile, y, x, ysize, xsize):
  '''
  Creates a new `outfile` and copies data from the `infile` to the new `outfile`
  according to `y`, `x`, and respective size parameters. Copys all attributes
  and adds a new attribute describing this crop step.
  '''

  with nc.Dataset(infile, 'r') as src, nc.Dataset(outfile, 'w') as dst:

    # copy global attributes all at once
    dst.setncatts(src.__dict__)

    # add the crop attribute string
    dst.crop = crop_attr_string(yo=y, xo=x, ys=ysize, xs=xsize)

    # next, create dimensions in the new file, mirroring the old dims
    for name, dimension in list(src.dimensions.items()):
      if name == 'X':
        dst.createDimension(name, xsize)
      elif name == 'Y':
        dst.createDimension(name, ysize)
      else:
        dst.createDimension(name, (len(dimension) if not dimension.isunlimited() else None))

    for name, var in list(src.variables.items()):
      print("  copying variable {} with dimensions {}".format(name, var.dimensions))
      newvar = dst.createVariable(name, var.datatype, var.dimensions)

      # Copy all attributes for the variable over
      newvar.setncatts(var.__dict__)

      # Now work on copying data...
      if var.dimensions == ('Y','X'):
        newvar[:] = var[y:y+ysize,x:x+xsize]
      elif var.dimensions == ('time','Y','X'):
        newvar[:] = var[:,y:y+ysize,x:x+xsize]
      elif 'Y' in var.dimensions and len(var.dimensions) == 1:
        newvar[:] = var[y:y+ysize]
      elif 'X' in var.dimensions and len(var.dimensions) == 1:
        newvar[:] = var[x:x+xsize]
      elif 'time' in var.dimensions and len(var.dimensions) == 1:
        newvar[:] = var[:]
      elif 'year' in var.dimensions and len(var.dimensions) == 1:
        newvar[:] = var[:]
      else:
        print("NOT SURE WHAT TO DO WITH VARIABLE: {} HAVING DIMS: {}".format(name, var.dimensions))


def cropper(xo,yo,xs,ys,input_file="",output_file="/tmp/smaller.nc", write_lonlat=True):
  '''
  Very thin wrapper around gdal_translate.

  Advantage: it will update the geo referencing info
  Disadvantage: this may not create a valid 1x1 dataset
  '''
  if input_file == "":
    raise RuntimeError("Must provide an input_file path to cropper(...) function!")

  if xs <= 1 or ys == 1:
    print("Probably not supported by GDAL!")

  if write_lonlat:
    write_ll='WRITE_LONLAT=YES' 
  else:
    write_ll='WRITE_LONLAT=NO'

  print("Cropping...")
  subprocess.call([
    'gdal_translate','-of','netcdf',
    '-co', write_ll,
    '-srcwin',str(xo),str(yo),str(xs),str(ys),
    input_file,
    output_file
  ])

def crop_wrapper(args):
  '''
  Parses input folder name to find tag, and creates appropriately named
  output directory alongside the input directory. Calls the crop_file
  function for each netcdf file found in the input directory.
  '''
  infolder = args.input_folder

  filelist = glob.glob(os.path.join(infolder, "*.nc"))

  # Assume infolder is of the form: some/long/path/<tag>_<Ysize>x<Xsize>
  # Then grab the last element of the path, split it on underscores and 
  # take the first element to get the tag:
  tag = os.path.split(infolder)[-1].split('_')[0:-1]
  tag = '_'.join(os.path.basename(os.path.normpath(infolder)).split('_')[0:-1])
  outfolder = os.path.join(os.path.dirname(os.path.normpath(infolder)), "{}_{}x{}".format(tag, args.ysize, args.xsize))

  print("Creating output folder: ", outfolder)
  mkdir_p(outfolder)

  for srcfile in filelist:
    infile = srcfile
    outfile = os.path.join(outfolder, os.path.basename(srcfile))
    print("input file: {}  -->  output file: {}".format(infile, outfile))
    y, x = args.yx
    crop_file(infile, outfile, y, x, args.ysize, args.xsize)

def climate_gap_count_plot(args):
  '''
  Creates plots showing how many missing datapoints exist for each pixel.

  Creates 2 figures: first from the historic file and then from the projected
  file.

  Each variable is shown in a different sub-plot. There are some idiosyncracies
  surrouding the labeling of the colorbar, so use with caution! But this should
  give a rough idea where there are bad pixels and how bad they are.
  ''' 

  # Keep imports of graphic stuff here so that the rest of the script
  # is usable even w/o matplotlib installed.
  import numpy as np
  import matplotlib.pyplot as plt
  import matplotlib.gridspec as gridspec

  CLIMATE_FILES = ['historic-climate.nc', 'projected-climate.nc']
  VARS = ['tair', 'precip', 'nirr', 'vapor_press']

  ROWS = 2
  COLS = 2

  gs = gridspec.GridSpec(ROWS, COLS)

  for cf in CLIMATE_FILES:
    axtair = plt.subplot(gs[0,0])
    axprecip = plt.subplot(gs[0,1])
    axnirr = plt.subplot(gs[1,0])
    axvapo = plt.subplot(gs[1,1])

    for i, (ax, v) in enumerate(zip([axtair, axprecip, axnirr, axvapo], VARS)):
      with nc.Dataset(os.path.join(args.input_folder, cf)) as hds:

        dataset = hds.variables[v][:] # Should be a 3D numpy array (time, y, x)
        if type(dataset) != np.ma.core.MaskedArray:
          dataset = np.ma.core.MaskedArray(dataset, np.zeros(dataset.shape, dtype = bool))
        #from IPython import embed; embed()
        #if dataset.mask == False:
        if not (np.ma.is_masked(dataset)):
          # No bad data, set mask to shape of first slice of dataset
          dataset.mask = np.zeros(dataset.shape[1:], dtype=bool)
        img = ax.imshow(
            np.ma.masked_greater_equal(
                np.apply_along_axis(np.count_nonzero, 0, dataset.mask),
                len(dataset)),
            interpolation='none',
            vmin=0,
            vmax=len(dataset),
            cmap='gray_r',
            origin='lower',

        )
      ax.set_title(v)
      plt.colorbar(img, ax=ax)

    plt.suptitle(os.path.join(args.input_folder, cf))
    plt.tight_layout()
    plt.show(block=True)



def climate_ts_plot(args):
  '''
  Make time series plots of the 4 climate driver variables.

  There are 2 modes controlled by the value of `args.type`. In `raw` mode, 2 
  figures are generated, one for historic and one for projected data (with the
  `args.stitch` argument, the data is concatenated along the temporal 
  dimension and only one figure is shown). Each figure has 4 subplots, one for 
  each variable. The data on each plot is shown directly from the input files,
  so it is monthly resolution. The plot is generally too dense to read without
  zooming in, but ALL the data is shown, un-adultered.

  In `spatial-temporal-summary` mode, one figure is created (the data is
  automatically stitched along the temporal dimension) with one subplot for each
  variable. The data that is shown is also averaged over the spatial dimensions
  of the input files AND resampled to an annual resolution along the time
  dimension.
  '''

  # Keep imports of graphic stuff here so that the rest of the script
  # is usable even w/o matplotlib installed.
  import matplotlib.pyplot as plt
  import matplotlib.gridspec as gridspec
  import matplotlib.ticker as ticker
  import pandas as pd

  CLIMATE_FILES = ['historic-climate.nc', 'projected-climate.nc']
  VARS = ['tair', 'precip', 'nirr', 'vapor_press']
  ROWS = 4
  COLS = 1

  y, x = args.yx

  gs = gridspec.GridSpec(ROWS, COLS)

  if args.type == 'spatial-temporal-summary':

    if args.stitch:
      print("Warning: Ignoring command line argument --stitch")
    hds = nc.Dataset(os.path.join(args.input_folder, CLIMATE_FILES[0]))
    pds = nc.Dataset(os.path.join(args.input_folder, CLIMATE_FILES[1]))

    end_hist = nc.num2date(hds.variables['time'][-1], hds.variables['time'].units, hds.variables['time'].calendar)

    htcV = hds.variables['time']
    ptcV = pds.variables['time']

    hidx = pd.DatetimeIndex(pd.date_range(
        start=nc.num2date(htcV[0], htcV.units, htcV.calendar).strftime(),
        end=nc.num2date(htcV[-1], htcV.units, htcV.calendar).strftime(),
        freq='MS') # <-- month starts)
    )
    pidx = pd.DatetimeIndex(pd.date_range(
        start=nc.num2date(ptcV[0], ptcV.units, ptcV.calendar).strftime(),
        end=nc.num2date(ptcV[-1], ptcV.units, ptcV.calendar).strftime(),
        freq='MS') # <-- month starts
    )

    full_index = pd.DatetimeIndex(pd.date_range(
        start=nc.num2date(htcV[0], htcV.units, htcV.calendar).strftime(),
        end=nc.num2date(ptcV[-1], ptcV.units, ptcV.calendar).strftime(),
        freq='MS') # <-- month starts
    )

    df = pd.DataFrame({}, index=full_index)
    for var in VARS:
      hS = pd.Series(hds.variables[var][:,y,x], index=hidx).reindex(full_index)
      pS = pd.Series(pds.variables[var][:,y,x], index=pidx).reindex(full_index)
      hckey = 'historic {}'.format(var)
      pckey = 'projected {}'.format(var)
      df[hckey] = hS
      df[pckey] = pS


    # Take means across spatial dimensions. Results in one timeseries for each
    # variable 
    for v in VARS:
      '''
      >>> time,Y,X = (4,2,2)
      >>> np.arange(time*Y*X).reshape((time,Y,X))
      array([[[ 0,  1],
              [ 2,  3]],

             [[ 4,  5],
              [ 6,  7]],

             [[ 8,  9],
              [10, 11]],

             [[12, 13],
              [14, 15]]])
      >>> a.reshape((-1, Y*X))
      array([[ 0,  1,  2,  3],
             [ 4,  5,  6,  7],
             [ 8,  9, 10, 11],
             [12, 13, 14, 15]])
      >>> np.average(a.reshape((-1, Y*X)), axis=1)
      array([ 1.5,  5.5,  9.5, 13.5])
      '''

      hncV = hds.variables[v]
      pncV = pds.variables[v]

      spatial_flat_hncV = hncV[:].reshape( (-1, len(hds.variables['Y']) * len(hds.variables['X'])) )
      spatial_flat_pncV = pncV[:].reshape( (-1, len(pds.variables['Y']) * len(pds.variables['X'])) )

      avh = np.mean(spatial_flat_hncV, axis=1)
      avp = np.mean(spatial_flat_pncV, axis=1)

      hS = pd.Series(avh, index=hidx).reindex(full_index)
      pS = pd.Series(avp, index=pidx).reindex(full_index)

      hckey = 'h sp mean {}'.format(v)
      pckey = 'p sp mean {}'.format(v)

      df[hckey] = hS
      df[pckey] = pS

    # Get annual stats
    rsmpl_mean = df.resample('A').mean()
    rsmpl_std = df.resample('A').std()
    rsmpl_sum = df.resample('A').sum()

    fig = plt.figure(figsize=(11,8.5))
    plt_title = "\n".join(("Annual Averages", args.input_folder, ",".join(CLIMATE_FILES)))
    fig.suptitle(plt_title) 

    axes = []
    for i, var in enumerate(VARS):
      if i > 0:
        ax = plt.subplot(gs[i,0], sharex=axes[0])
        axes.append(ax)
      else:
        ax = plt.subplot(gs[i,0])
        axes.append(ax)

      hckey = 'historic {}'.format(var)
      pckey = 'projected {}'.format(var)

      ax.set_title(var)
      ax.set_ylabel(hds.variables[var].units)

      if var == 'precip' or var == 'nirr':
        ax.plot(rsmpl_sum.index, rsmpl_sum[hckey])
        ax.plot(rsmpl_sum.index, rsmpl_sum[pckey])
        ax.set_ylabel(hds.variables[var].units.replace('month', 'year'))

      else:
        ax.plot(rsmpl_mean.index, rsmpl_mean[hckey])
        ax.plot(rsmpl_mean.index, rsmpl_mean[pckey])

      #ax.plot(rsmpl_mean.index, rsmpl_mean['h sp mean {}'.format(var)], color='red', linewidth=.5)
      #ax.fill_between(rsmpl_std.index, rsmpl_std['h sp mean'], 

    for i, ax in enumerate(axes):
      if ax != axes[-1]:
        plt.setp(ax.get_xticklabels(), visible=False)

    plt.show(block=True)

  elif args.type == 'raw':

    if args.stitch:

      hds = nc.Dataset(os.path.join(args.input_folder, CLIMATE_FILES[0]))
      pds = nc.Dataset(os.path.join(args.input_folder, CLIMATE_FILES[1]))

      axes = []
      for i, v in enumerate(VARS):
        full_ds = np.concatenate((hds.variables[v][:,y,x], pds.variables[v][:,y,x]), axis=0)
        if i > 0:
          ax = plt.subplot(gs[i,0], sharex=axes[0])
          axes.append(ax)
        else:
          ax = plt.subplot(gs[i,0])
          axes.append(ax)
        ax.plot(full_ds[:], marker='o')
        ax.set_title(v)

      # Modify all axes to add annual grid...
      try:
        _ = (a for a in axes) # just check that axes is a list.
        for ax in axes:
          ax.xaxis.set_major_locator(ticker.MultipleLocator(12))
          ax.grid()
      except TypeError:
        print(axes, 'is not iterable; setting grid on single axes instance')
        axes.xaxis.set_major_locator(ticker.MultipleLocator(12))
        axes.grid()

      plt.suptitle("{}: {},{}".format(args.input_folder, CLIMATE_FILES[0], CLIMATE_FILES[1]))
      plt.show(block=True)

      hds.close()
      pds.close()

    else:
      for i, v in enumerate(VARS):
        ax = plt.subplot(gs[i,0])
        with nc.Dataset(os.path.join(args.input_folder, CLIMATE_FILES[0])) as hds:
          ax.plot(hds.variables[v][:,y, x])
          ax.set_title(v)
      plt.suptitle(os.path.join(args.input_folder, CLIMATE_FILES[0]))
      plt.show(block=True)

      plt.title(CLIMATE_FILES[1])
      for i, v in enumerate(VARS):
        ax = plt.subplot(gs[i,0])
        with nc.Dataset(os.path.join(args.input_folder, CLIMATE_FILES[1])) as hds:
          ax.plot(hds.variables[v][:,y, x])
          ax.set_title(v)
      plt.suptitle(os.path.join(args.input_folder, CLIMATE_FILES[1]))
      plt.show(block=True)

  else:
    print("Cmd line arg should be checked such that you can't arrive here.")


def tunnel_fast(latvar,lonvar,lat0,lon0):
  '''
  Find closest pair in a set of (lat,lon) pairs to specified query point.
  latvar - 2D latitude data, usually from reading a netCDF dataset
  lonvar - 2D longitude data, usually from reading a netCDF dataset
  lat0,lon0 - query point
  Returns iy,ix such that the square of the tunnel distance
  between (latval[it,ix],lonval[iy,ix]) and (lat0,lon0)
  is minimum.
  Code from Unidata's Python Workshop:
  https://github.com/Unidata/unidata-python-workshop
  '''

  # convert to radians
  #from IPython import embed; embed()
  rad_factor = np.pi/180.0 # for trignometry, need angles in radians
  latvals = latvar * rad_factor
  lonvals = lonvar * rad_factor
  lat0_rad = lat0 * rad_factor
  lon0_rad = lon0 * rad_factor

  # ny,nx = latvals.shape # <-- not used??

  # Compute numpy arrays for all values, no loops
  clat,clon = np.cos(latvals), np.cos(lonvals)
  slat,slon = np.sin(latvals), np.sin(lonvals)
  delX = np.cos(lat0_rad)*np.cos(lon0_rad) - clat*clon
  delY = np.cos(lat0_rad)*np.sin(lon0_rad) - clat*slon
  delZ = np.sin(lat0_rad) - slat;
  dist_sq = delX**2 + delY**2 + delZ**2
  minindex_1d = dist_sq.argmin()  # 1D index of minimum element
  iy_min,ix_min = np.unravel_index(minindex_1d, latvals.shape)
  return iy_min,ix_min





if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,

      description=textwrap.dedent('''\
        Command line interface for utility functions that work on 
        dvmdostem inputs. This script may also be imported and used
        from other scripts (if you wish to import functions without 
        using this command line interface).

        The command line interface contains (or will in the future)
        different sub-commands for different types of operations.
        '''.format("")),

      epilog=textwrap.dedent(''''''),
  )
  subparsers = parser.add_subparsers(help='sub commands', dest='command')

  query_parser = subparsers.add_parser('query', help=textwrap.dedent('''\
    Query one or more dvmdostem inputs for various information.'''))
  query_parser.add_argument('--iyix-from-latlon', default=None, nargs=2, type=float,
      help="Find closest pixel to provided lat and lon arguments.")
  query_parser.add_argument('--latlon-file', 
      default='../snap-data/temporary-veg-from-LandCover_TEM_2005.tif', 
      help="The file to read from for getting lat/lon pixel offsets.")

  crop_parser = subparsers.add_parser('crop',help=textwrap.dedent('''\
      BROKEN - See notes below. Crop an input dataset, using offset and size. The 
      reason we need this in addition to the create_region_input.py script is because the 
      create_region_input.py script uses gdal_translate (or gdalwarp) to subset
      the original tif files, and for some reason that has problems creating 
      regions smaller than about 5x5 pixels. So in order to get a single pixel
      input dataset, we have to first create a larger dataset, and then crop it
      using this tool. Someday it might make sense to merge this script with the
      create_region_input.py script. 
      NOTE 1: Offsets are from upper left!
      NOTE 2: Offset reature seems broken as of 29/01/2021, when I can use the
      io_view.py tool to map the resulting datasets. No matter what values are
      passed for --yx the resulting dataset seems pinned in the upper left corner
      of the source. This may be due to the way that the projection attributes are
      being copied because gdal_translate doesn't seem to throw any errors. '''))
  crop_parser.add_argument('--yx', type=int, nargs=2, required=True, help="The Y, X position to start cropping")
  crop_parser.add_argument('--ysize', type=int, default=1, help="The number of pixels to take in the y dimension.")
  crop_parser.add_argument('--xsize', type=int, default=1, help="The number of pixels to take in the x dimension.")
  crop_parser.add_argument('input_folder', help="Path to a folder containing a set of dvmdostem inputs.")

  # EXAMPLES
  # ./input_utils.py crop --yx 0 0 --ysize 1 --xsize 1 demo-data/cru-ts40_ar5_rcp85_mri-cgcm3_Toolik_10x10

  climate_ts_plot_parser = subparsers.add_parser('climate-ts-plot', help=textwrap.dedent('''\
    Quick 'n dirty time series plots of the 4 climate driver variables for a 
    single pixel. Makes 2 figures, one for historic, one for projected.
    '''))
  climate_ts_plot_parser.add_argument('--type', choices=['spatial-temporal-summary', 'raw'], required=True, help="")
  climate_ts_plot_parser.add_argument('--yx', type=int, nargs=2, required=True, help="The Y, X position of the pixel to plot")
  climate_ts_plot_parser.add_argument('--stitch', action='store_true', help="Attempt to stitch together the historic and projected data along the time axis")
  #climate_ts_plot_parser.add_argument('--yrs-slice', type=?? help="")

  climate_ts_plot_parser.add_argument('input_folder', help="Path to a folder containing a set of dvmdostem inputs.")

  climate_gap_count_plot_parser = subparsers.add_parser('climate-gap-plot',
    help=textwrap.dedent('''Generates an image plot for each variable in the 
      input climate files (historic and projected). Each pixel in the image 
      shows the number of values along the time axis that have missing or no
      data.
    '''))
  climate_gap_count_plot_parser.add_argument('input_folder', help="Path to a folder containing a set of dvmdostem inputs.")

  args = parser.parse_args()

  print(args)

  if args.command == 'crop':
    verify_input_files(args.input_folder)
    crop_wrapper(args)

  if args.command == 'climate-ts-plot':
    #verify_input_files(args.input_folder)
    climate_ts_plot(args)

  if args.command == 'climate-gap-plot':
    climate_gap_count_plot(args)

  if args.command == 'query':
    if args.iyix_from_latlon:

      TMP_NC_FILE = '/tmp/WINNING.nc'

      # Convert to netcdf
      subprocess.call(['gdal_translate',
          #'-overwrite',
          '-of','netcdf',
          #'-t_srs', '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
          '-co', 'WRITE_LONLAT=YES',
          args.latlon_file,
          TMP_NC_FILE])

      # Or can set GDAL_DATA environment variable and use EPSG code:
      #GDAL_DATA=/home/UA/tcarman2/anaconda/share/gdal gdalwarp -of netcdf infile.tif outfile.nc -t_srs EPSG:4326

      ncfile = nc.Dataset(TMP_NC_FILE, 'r')
      latvar = ncfile.variables['lat']
      lonvar = ncfile.variables['lon']

      #from IPython import embed; embed()
      #toolik = {'lat':68.626480, 'lon':-149.594995}
      #bnza_lter = {'lat':64.70138, 'lon':-148.31034}
      #target = bnza_lter
      target = {'lat':args.iyix_from_latlon[0], 'lon':args.iyix_from_latlon[1]}
      iy,ix = tunnel_fast(latvar[:], lonvar[:], target['lat'], target['lon'])
      iy_fUL = len(ncfile.dimensions['y'])-iy
      print(('Target lat, lon:', target['lat'], target['lon']))
      print(('Delta with target lat, lon:', target['lat'] - latvar[iy,ix], target['lon'] - lonvar[iy,ix]))
      print(('lat, lon of closest match:', latvar[iy,ix], lonvar[iy,ix]))
      print(('indices of closest match iy, ix (FROM LOWER left):', iy, ix))
      print(('indices of closest match iy, ix (FROM UPPER left):', iy_fUL, ix))
      print('** NOTE: Use coords FROM UPPER LEFT to build/crop a new dataset with that pixel at the LOWER LEFT corner of the dataset!')
      print(('''

      NOTE:
      When gdal reads .tif files it uses the UPPER LEFT corner of the UPPER LEFT
      pixel as the origin. So the 0,0 pixel is the UPPER LEFT corner.

      When gdal_translate converts to netcdf, and the file is viewed with ncview
      the (i,j) pixel offsets are from the LOWER LEFT of the image. 

      When using the create_region_input.py script to select regions from the 
      SNAP tif files, use the following table to figure out what offsets to pass.

      Puts your "pixel of interest" at the desired place within the cropped region.
      =============================================================================

        @ UL of cropped region:                      iy={iy:}            ix={ix:}
        @ LL of cropped region:                      iy=({iy:}-YSIZE)+1  ix={ix:}
        @ LR of cropped region:                      iy=({iy:}-YSIZE)+1  ix=({ix:}-XSIZE)+1
        @ UR of cropped region:                      iy={iy:}            ix=({ix:}-XSIZE)+1

        @ approx center of cropped region:           iy={iy:}-(YSIZE/2)  ix={ix:}-(XSIZE/2)
      '''.format(iy=iy_fUL, ix=ix)))
      print()

      ncfile.close()
      os.remove(TMP_NC_FILE)
      exit()


