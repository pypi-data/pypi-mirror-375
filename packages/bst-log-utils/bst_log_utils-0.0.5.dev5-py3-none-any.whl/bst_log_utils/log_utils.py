import os
from collections import defaultdict
import re
import geomag
import datetime
import h5py
import netCDF4 as nc
import pytz

import ctypes
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from scipy.io import loadmat
from lxml import etree as ET
import simplekml
import shutil
import bst_helper_functions.geometry_utils as gu
import bst_helper_functions.bst_att_est as bae
import bst_log_utils.process_mhp as pm
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
pi = np.pi
k_correct = 1

def get_wp_leg_times(apname,waypoint_legs,
                     start_offset = 3,stop_offset = -3):

    command = get_log_command(apname)
    tlegs = np.empty((0,2))


    for wpts in waypoint_legs:
        num,nxt = wpts

        wpt = command['WAYPOINT']
        ts = command['t_WAYPOINT']
        keep_looking = True

        while keep_looking:
            # Reset legs
            leg = np.zeros((1,2))

            # Find a leg where wp goes num -> nxt
            idx = np.where(wpt == num)[0]
            if len(idx > 0): # Found num in remaining points
                wpt = wpt[idx[0]:]
                ts = ts[idx[0]:]

                # Find waypoint switch
                idx = np.where(wpt != num)[0]
                if len(idx > 0):
                    wpt = wpt[idx[0]:]
                    ts = ts[idx[0]:]
                    if wpt[0] == nxt:
                        # On the right leg, look for waypoint switch
                        leg[0,0] = ts[0] + start_offset
                        idx = np.where(wpt != nxt)[0]
                        if len(idx) > 0:
                            wpt = wpt[idx[0]:]
                            ts = ts[idx[0]:]
                            leg[0,1] = ts[0] - stop_offset
                            tlegs = np.append(tlegs,leg,axis=0)
            else:
                keep_looking = False

    return tlegs[np.argsort(tlegs[:,0]),:]

def parse_payload_channels(log_data, channel_ctypes_classes):
    payload_data_dict = {}

    for channel_class in channel_ctypes_classes:
        channel_num_str = channel_class.channel_number
        data_key_base = "PAYLOAD_DATA_CHANNEL_" + channel_num_str
        data_time_key = data_key_base + "_time"
        data_values_key =  data_key_base + "_vec"
        data_format = None
        if data_time_key in log_data.variables:
            if channel_num_str not in payload_data_dict:
                payload_data_dict[channel_num_str] = {}
            times = log_data[data_time_key][:]
            data = log_data[data_values_key][:]
            data_format = 0
        elif data_key_base in log_data.groups:
            if channel_num_str not in payload_data_dict:
                payload_data_dict[channel_num_str] = {}
            times = log_data[data_key_base]['system_time'][:]
            data = log_data[data_key_base]['buffer'][:].astype(np.int8)
            data_format = 1

        if channel_num_str in payload_data_dict:
            payload_data_dict[channel_num_str]["times"] = times
            for indx, _ in enumerate(times):
                if data_format == 0:
                    single_timestep_data = data[indx][0]
                elif data_format == 1:
                    single_timestep_data = data[indx]
                payload_data_struct = channel_class.from_buffer_copy(np.ctypeslib.as_ctypes(single_timestep_data))
                for attr, size in zip(payload_data_struct._fields_, payload_data_struct._sizes_):
                    attr_str = attr[0]
                    size_val = size[1]
                    if attr_str not in payload_data_dict[channel_num_str]:
                        payload_data_dict[channel_num_str][attr_str] = []
                    if size_val == 1:
                        payload_data_dict[channel_num_str][attr_str].append((getattr(payload_data_struct, attr_str)))
                    else:
                        data_array = getattr(payload_data_struct, attr_str).reshape(-1,size_val)

                        payload_data_dict[channel_num_str][attr_str].append(data_array)

           # print("Data Format = ", data_format)
    return payload_data_dict, data_format

def create_channel_ctypes_classes(channels_xml_trees):
  ctypes_classes_list = []
  for channel_xml_tree in channels_xml_trees:
    class CtypesClass(ctypes.Structure):
        _pack_ = 1
        _fields_ = create_ctypes_fields(channel_xml_tree)
        _sizes_ = create_ctypes_sizes(channel_xml_tree)
    CtypesClass.channel_number = channel_xml_tree.find("Number").text
    ctypes_classes_list.append(CtypesClass)

  return ctypes_classes_list

def create_ctypes_sizes(channel_xml_tree):
  # Returns:  List of tuples, [('field_name1', size1), ('field_name2', size2) ...]
  sizes = []
  fields_etrees = list(channel_xml_tree.find("Fields"))
  for field_etree in fields_etrees:
    field_name_string = field_etree.find("name").text.lower().replace(" ", "_")
    field_size = int(field_etree.find("size").text)
    sizes.append((field_name_string, field_size))

  return sizes

def create_ctypes_fields(channel_xml_tree):
  # Returns:  List of tuples, [('field_name1', ctype1), ('field_name2', ctype2) ...]
  fields = []
  fields_etrees = list(channel_xml_tree.find("Fields"))
  for field_etree in fields_etrees:
    field_name_string = field_etree.find("name").text.lower().replace(" ", "_")
    field_type_string = field_etree.find("type").text
    field_ctype = None
    if field_type_string == "CHAR": field_ctype = ctypes.c_char
    elif field_type_string == "DOUBLE": field_ctype = ctypes.c_double
    elif field_type_string == "FLOAT": field_ctype = ctypes.c_float
    elif field_type_string == "INT8": field_ctype = ctypes.c_int8
    elif field_type_string == "INT16": field_ctype = ctypes.c_int16
    elif field_type_string == "INT32": field_ctype = ctypes.c_int32
    elif field_type_string == "INT64": field_ctype = ctypes.c_int64
    elif field_type_string == "UINT8": field_ctype = ctypes.c_uint8
    elif field_type_string == "UINT16": field_ctype = ctypes.c_uint16
    elif field_type_string == "UINT32": field_ctype = ctypes.c_uint32
    elif field_type_string == "UINT64": field_ctype = ctypes.c_uint64
    fields.append((field_name_string, field_ctype))

  return fields

def load_app_channels_from_xml_as_etree(xml_fp):
  root = ET.parse(xml_fp).getroot()
  datalist = root.findall("PayloadDataList")
  channels = datalist[0].findall("Channel")
  # channels = [x for x in list(root[0]) if x.tag == "Channel"]
  return channels

def plot_background(xlim=None,ylim=None):
  from mpl_toolkits.basemap import Basemap
  if xlim is None:
    xlim = plt.xlim()
  if ylim is None:
    ylim = plt.ylim()

  lonmin,lonmax = plt.xlim()
  latmin,latmax = plt.ylim()
  pmap = Basemap(resolution='i',projection='cyl',
                 llcrnrlon=lonmin,llcrnrlat=latmin,
                 urcrnrlon=lonmax,urcrnrlat=latmax)
  pmap.arcgisimage(server="http://server.arcgisonline.com/ArcGIS",
                     service='World_Imagery', xpixels=1500, verbose=False)

def plot_traj(fname,bmap=False,xlim=None,ylim=None,color='C0',ax=None):
  gps,tgps = get_var(fname,'gps')

  tstart,tstop = flighttimes(fname)
  idx = get_time_indeces(gps['system_time'],tstart,tstop)
  if ax is None:
    fig,ax = plt.subplots(1,1)
  ax.plot(gps['longitude'][idx],gps['latitude'][idx],label=os.path.basename(fname),linewidth=5,color=color)
  if bmap:
    plot_background(xlim,ylim)

def make_kml(lat,lon,alt,fname,color=simplekml.Color.red):
  kml = simplekml.Kml()
  print('Writing to %s'%os.path.basename(fname))
  lonlatalt = np.vstack((lon,lat,alt)).T
  lin = kml.newlinestring(name=fname, coords=lonlatalt)
  lin.style.linestyle.color = color
  lin.style.linestyle.width = 2
  lin.altitudemode = simplekml.AltitudeMode.absolute
  kml.save(fname)

def xml2kml(fname,color='ff14F0F0'):
  wp = load_wp_from_xml(fname)
  make_kml(wp['latitude'],wp['longitude'],wp['altitude'],fname[:-4]+'.kml',color=color)

def plot_wp_from_xml(fname,color='k'):
  wp = load_wp_from_xml(fname)
  plot_wp_plan(wp,color)

def load_wp_from_xml(fname):
  root = ET.parse(fname).getroot()
  points = list(root)
  waypoint = {'num':[],'next':[],'latitude':[],'longitude':[],'altitude':[],'radius':[]}

  for pt in points:
    num = pt.find("num").text
    if num.isdigit():
      waypoint['num'].append(int(num))
    else:
      waypoint['num'].append(num)
    nxt = pt.find("next").text
    if nxt.isdigit():
      waypoint['next'].append(int(nxt))
    else:
      waypoint['next'].append(nxt)
    waypoint['latitude'].append(float(pt.find("latitude").text))
    waypoint['longitude'].append(float(pt.find("longitude").text))
    waypoint['altitude'].append(float(pt.find("altitude").text))
    waypoint['radius'].append(float(pt.find("radius").text))

  return waypoint

def plot_orbit(lat,lon,r,color):
  origin = np.array([lat,lon])
  th = np.linspace(0,2*np.pi,50)
  x = r*np.cos(th)
  y = r*np.sin(th)
  lat,lon = local2latlon(origin,x,y)
  plt.plot(lon,lat,'--',color=color)

def plot_wp_plan(wp,color='k'):
  loop = True
  i0 = np.argmin(wp['num'])
  while loop:
    plt.plot(wp['longitude'][i0],wp['latitude'][i0],'o',color=color)
    plt.text(wp['longitude'][i0],wp['latitude'][i0],str(wp['num'][i0]),color=color)
    if np.abs(wp['radius'][i0]) > 0:
      plot_orbit(wp['latitude'][i0],wp['longitude'][i0],wp['radius'][i0],color)
    if wp['next'][i0] == 255 or wp['next'][i0] == wp['num'][i0]:
      loop = False
    else:
      i1 = np.where(np.array(wp['num']) == wp['next'][i0])[0][0]
      plt.plot([wp['longitude'][i0],wp['longitude'][i1]],[wp['latitude'][i0],wp['latitude'][i1]],color=color,linestyle='--')
      if wp['next'][i0] < wp['num'][i0]:
        loop = False
      i0 = i1

def plot_wind(lat,lon,u,v,steps=50,mu_latlon=None):
  if mu_latlon is None:
    x,y = latlon2local(lat,lon)
  else:
    x,y = latlon2local(lat,lon,origin=mu_latlon)
  plt.plot(x[0],y[0],'s',color='red')
  plt.plot(x,y,color='grey')
  idx = np.arange(0,len(u),steps)
  plt.quiver(x[idx],y[idx],u[idx],v[idx])
  plt.grid()

def get_datetime_vec(timesec,dt_start,datetime_format="%Y-%m-%dT%H:%M:%SZ"):
  basetime = datetime.datetime.strptime(dt_start,datetime_format)
  tseconds = np.floor(timesec)
  tmicroseconds=np.round(1000000*(timesec - tseconds))
  return [basetime + datetime.timedelta(seconds=int(s),microseconds=int(ms)) for s,ms in zip(tseconds,tmicroseconds)]

def get_seconds_from_datetime(dt, dt_start,datetime_format = "%Y-%m-%dT%H:%M:%SZ"):
  basetime = datetime.datetime.strptime(dt_start,datetime_format)
  return np.array([(dt0-basetime).total_seconds() for dt0 in dt])

def weekseconds2unix(gpsweek, gpsseconds):
  datetimeformat = "%Y-%m-%d %H:%M:%S"
  gps_epoch = datetime.datetime.strptime("1980-01-06 00:00:00",datetimeformat)
  unix_epoch = datetime.datetime.strptime("1970-01-01 00:00:00",datetimeformat)
  gps2unix_ss = (gps_epoch - unix_epoch).total_seconds()

  microseconds = int((gpsseconds - np.floor(gpsseconds))*1e6)
  seconds = int(np.floor(gpsseconds))
  elapsed = datetime.timedelta(days=int(gpsweek*7),seconds=seconds,microseconds=microseconds)
  return elapsed.total_seconds() + gps2unix_ss

def weeksecondstoutc(gpsweek,gpsseconds,leapseconds=18,datetimeformat="%Y-%m-%d %H:%M:%S"):
  epoch = datetime.datetime.strptime("1980-01-06 00:00:00","%Y-%m-%d %H:%M:%S")

  microseconds = int((gpsseconds - np.floor(gpsseconds))*1e6)
  seconds = int(np.floor(gpsseconds))
  elapsed = datetime.timedelta(days=int(gpsweek*7),seconds=(seconds-leapseconds),microseconds=microseconds)
  return datetime.datetime.strftime(epoch + elapsed,datetimeformat)

def get_ap_basetime(fname):
  gps,tgps = get_var(fname,'gps')
  idx = np.where(gps['week'] > 0)[0][0]
  base_time = weekseconds2unix(float(gps['week'][idx]),float(gps['hour'][idx])*3600 + float(gps['minute'][idx])*60 + float(gps['seconds'][idx]))
  base_time -= gps['system_time'][idx]
  return base_time

def get_ground(fname):
  command,tcommand = get_var(fname,'command')
  state,tstate = get_var(fname,'state')
  idx = np.where(command['id'] == 1)[0]
  t_mode = tcommand[idx]
  mode = command['value'][idx]

  CLIMBOUT=4
  tclimb = t_mode[np.where(mode == CLIMBOUT)[0][0]]
  idx = np.where(tstate>=tclimb)[0][0]
  return state['altitude'][idx] - state['agl'][idx]

def flighttimes(fname,min_time = 0,fn=None):
  t_start = np.empty((0,0))
  t_stop = np.empty((0,0))

  command = get_log_command(fname)
  if command is None:
      return t_start,t_stop

  t_mode = command['t_FLIGHT_MODE']
  mode = command['FLIGHT_MODE']
  # FIXME, bad data?
  mode = mode[t_mode > 0]
  t_mode = t_mode[t_mode > 0]

  CLIMBOUT=4
  # If no climbout, use first instance of flying
  if np.size(np.where(mode == CLIMBOUT)[0]) == 0:
    CLIMBOUT=6
    # If no flying, use LAUNCH
    if np.size(np.where(mode == CLIMBOUT)[0]) == 0:
      CLIMBOUT=3

  if mode.size > 0 and np.max(mode) < 9:
    LANDED = 7
  else:
    LANDED = 9

  counter = 0
  while 1:
    in_launch = np.where(mode == CLIMBOUT)[0]
    if in_launch.size > 0:
      in_launch = in_launch[0]
      in_land = np.where(mode[in_launch:] == LANDED)[0]
      if in_land.size > 0:
        in_land = in_land[0]
        t_start = np.append(t_start, t_mode[in_launch])
        t_stop = np.append(t_stop, t_mode[in_launch+in_land])
        mode = mode[in_land+in_launch:]
        t_mode = t_mode[in_land+in_launch:]
        counter = counter+1
      else:
        t_start = np.append(t_start, t_mode[in_launch])
        t_stop = np.append(t_stop, t_mode[-1])
        break
    else:
      break

  if fn is not None:
    t_start = t_start[fn]
    t_stop = t_stop[fn]
  return t_start/k_correct,t_stop/k_correct

def get_mag_dec(latitude,longitude):
  return geomag.declination(latitude,longitude)*np.pi/180

## FIXME make this faster, far too slow right now.
def get_log_command(fname):

    cmd_vars = ['AUTOPILOT_MODE','FLIGHT_MODE','LANDING_MODE','ALT_MODE',
                'LAT_MODE','NAV_MODE','ENGINE_KILL','FLIGHT_TERMINATE',
                'ABORT','WAYPOINT','TURN_RATE','LAUNCH','LAND','ROLL',
                'PITCH','YAW','WPT_ALT','ROLL_RATE','PITCH_RATE','YAW_RATE',
                'ALTITUDE','VRATE','DOWNLOAD_LOG','TRIGGER_PAYLOAD',
                'TECS_MODE','SPEED','VELC_OR_TRIMS','X_POS','Y_POS','X_VEL',
                'Y_VEL','THRUST','MOMENT_X','MOMENT_Y','MOMENT_Z',
                'PAYLOAD_CONTROL','LOOK_AT','INVALID']
    cmd = {}
    for var in cmd_vars:
        cmd['t_'+var] = np.empty([])
        cmd[var] = np.empty([])

    # Prioritize telem packets
    telem_cont,ttelem_cont = get_var(fname,'telem_cont')
    telem_sys,ttelem_sys = get_var(fname,'telem_sys')
    skip_actual = False

    if telem_cont is not None:
        augment_vars = ['ROLL','PITCH','YAW','ROLL_RATE','PITCH_RATE','YAW_RATE',
                        'ALTITUDE','WAYPOINT','LOOK_AT','ALT_MODE','LAT_MODE',
                        'NAV_MODE','LANDING_MODE']
        # FIXME missing "velocity"
        new_vars = ['roll','pitch','yaw','roll_rate','pitch_rate','yaw_rate',
                    'altitude','waypoint','look_at_point','lat_mode','alt_mode',
                    'nav_mode','landing_status']
        for av,nv in zip(augment_vars,new_vars):
            cmd['t_'+av] = np.append(cmd['t_'+av],ttelem_cont)
            cmd[av] = np.append(cmd[av],telem_cont[nv])
        skip_actual=True
    if telem_sys is not None:
        augment_vars = ['AUTOPILOT_MODE','FLIGHT_MODE']
        new_vars = ['autopilot_mode','flight_mode']
        for av,nv in zip(augment_vars,new_vars):
            cmd['t_'+av] = np.append(cmd['t_'+av],ttelem_sys)
            cmd[av] = np.append(cmd[av],telem_sys[nv])
        skip_actual=True

    # FIXME - add this back once we sort out the multipliers on these packets
    if not skip_actual:
        command,tcommand = get_var(fname,'command')
        for idx,var in enumerate(cmd_vars):
            idx = np.where(command['id'] == idx)
            cmd['t_'+var] = np.append(cmd['t_'+var],tcommand[idx])
            cmd[var] = np.append(cmd[var],command['value'][idx])

    # Re-order all vars to make sure timing is correct
    for v in cmd_vars:
        if cmd['t_'+v].size > 1:
            idx = np.argsort(cmd['t_'+v])
            cmd['t_'+v] = cmd['t_'+v][idx]
            cmd[v] = cmd[v][idx]
    return cmd

def scan_logs(dir_path,allFiles=True):
  fnames = []
  for file in os.listdir(dir_path):
    # check only text files
    if file.endswith('.mat'):
      fnames.append(file)
    if file.endswith('.nc'):
      fnames.append(file)

  fnames = sorted(fnames)
  for fname in fnames:
    print_info_aplog(dir_path+fname,allFiles=allFiles)


def get_info_aplog(fname):
    sys_init,tsys_init = get_var(fname,'sys_init')
    if sys_init is None:
        return '',np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan
    if len(sys_init['sw_rev']) == 0:
        return '',np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan

    if sys_init['name'].dtype == 'int32':
        ac_type = ''
        ac_num = np.nan
    else:
        if sys_init['name'].dtype == 'int64':
            name = bytes(list(sys_init['name'][-1])).decode()
        elif sys_init['name'].dtype == 'S1' or sys_init['name'].dtype == 'S32':
            name = sys_init['name'][-1].tobytes().decode()
        else:
            name = sys_init['name'][-1]

        if len(name) < 6:
            ac_type = ''
            ac_num = np.nan
        elif name[2] == '-':
            ac_type = str(name[0:2])
            ac_num = int(name[3])
        elif name[5] == '?':
            ac_type = str(name[0:2])
            ac_num = np.nan
        else:
            ac_type = str(name[0:2])
            try:
              ac_num = int(name[2:6])
            except:
              ac_type = str(name)
              ac_num = np.nan

    sw_rev = sys_init['sw_rev'][-1]
    hw_rev = sys_init['hw_rev'][-1]
    svn_rev = hex(sys_init['svn_rev'][-1])
    comms_rev = sys_init['comms_rev'][-1]
    serial_num = hex(sys_init['serial_num'][-1])

    tstart,tstop = flighttimes(fname)
    num_flights = len(tstart)
    tof = np.sum(tstop-tstart)
    return ac_type,ac_num,serial_num,num_flights,tof,sw_rev,hw_rev,svn_rev,comms_rev

def print_info_aplog(fname,allFiles=True):

  ac_type,ac_num,serial_num,num_flights,tof,sw_rev,hw_rev,svn_rev,comms_rev = get_info_aplog(fname)
  if allFiles or num_flights > 0:
    print(os.path.basename(fname))
    if np.isnan(sw_rev):
      print('\tWARNING: No proper sys_init found')
    else:
      if np.isnan(ac_num):
        print('\tAircraft: %s (WARNING: Unknown aircraft name)'%(ac_type))
      else:
        print('\tAircraft: %s-%i'%(ac_type,ac_num))
      print('\tsw_rev: %s'%sw_rev)
      print('\thw_rev: %s'%hw_rev)
      print('\tsvn_rev: %s'%svn_rev)
      print('\tcomms_rev: %s'%comms_rev)
      print('\tserial_num: %s'%serial_num)
      print('\tLog length: %.2f min'%(get_imu_dt(fname)/60))
      print('\tDate/time: '+get_datetime_aplog(fname))
      tstart,tstop = flighttimes(fname)
      print('\tFlights (%i): '%num_flights)
      k=1
      for start,stop in zip(tstart,tstop):
        print('\t\t%i. '%k+get_datetime_aplog(fname,start)+' -> '+get_datetime_aplog(fname,stop)+ ' TOF: %.1f min'%((stop-start)/60))
        k += 1

def get_imu_dt(fname):
  acc,tacc = get_var(fname,'acc')
  if acc is None:
    acc,tacc = get_var(fname,'telem_pos')
    if acc is None:
      return 0.0
  return tacc[-1] - tacc[0]

def rename_aplog(fname):
  if fname[-4:] != '.mat':
    fname = fname+'.mat'
  if(os.path.exists(fname)):
    dt = get_datetime_aplog(fname)
    new_fname = fname[:-7] + dt[0:10]+'_'+dt[11:13]+dt[14:16]+dt[17:19]
    print('Copying %s to %s' %(fname[:-4], new_fname))
    shutil.copyfile(fname, new_fname+'.mat')
    if(os.path.exists(fname[:-4]+'.BIN')):
      shutil.copyfile(fname[:-4]+'.BIN', new_fname+'.BIN')
  else:
    print('Error, %s does not exist'%fname)

def print_datetime_aplog(fname):
    print('UTC of %s: '%fname, get_datetime_aplog(fname))

def get_datetime_aplog(fname,t_start = -1):

  gps,tgps = get_var(fname,'gps')
  if gps is None:
    # Try for an S0
    gps,tgps = get_var(fname,'telem_sys')
    if gps is None:
      return 'nan'
    else:
      gps['seconds'] = gps['milliseconds']/1000
  if np.sum(gps['week']) == 0:
    return 'nan'

  t_off = 0
  gps['week'][gps['week'] > 10000] = 0
  if t_start > 0:
    ind = np.where(tgps >= t_start)[0][0]
  else:
    ind = np.argmax(gps['week'])
    t_off = tgps[ind]

  return weeksecondstoutc(float(gps['week'][ind]),float(gps['hour'][ind])*3600 + float(gps['minute'][ind])*60 + float(gps['seconds'][ind]) - t_off)


def local2latlon(origin_deg, x, y):
    R_e       = 6378137
    th        = np.arctan2(x,y)
    r         = np.sqrt(x**2 + y**2)

    origin = origin_deg*np.pi/180
    lat = np.arcsin( np.sin(origin[0])*np.cos(r/R_e) + np.cos(origin[0])*np.sin(r/R_e)*np.cos(th))
    lon = origin[1] + np.arctan2(np.sin(th)*np.sin(r/R_e)*np.cos(origin[0]),np.cos(r/R_e)-np.sin(origin[0])*np.sin(lat))

    lat *= 180/np.pi
    lon *= 180/np.pi
    return (lat,lon)

def lla2dist(lat1, lon1, lat2, lon2):
  x,y = latlon2local(lat1,lon1, origin=np.array([lat2,lon2]))
  return np.linalg.norm([x,y])

def latlon2local(lat, lon,origin=None):
    if origin is None:
      origin = np.array([np.nanmean(lat),np.nanmean(lon)])
    originr = origin * np.pi/180
    latr = lat * np.pi/180
    lonr = lon*np.pi/180
    R_e = 6378137
    d_lat = latr - originr[0]
    d_lon = lonr - originr[1]

    # Range and bearing
    r = R_e*2*np.sqrt( (d_lat/2)**2 + np.cos(originr[0])*np.cos(latr)*(d_lon/2)**2 )
    th = np.arctan2( np.sin(d_lon)*np.cos(latr), np.cos(originr[0])*np.sin(latr) - np.sin(originr[0])*np.cos(latr)*np.cos(d_lon) )
    # Convert to cartesian
    y = r*np.cos(th)
    x = r*np.sin(th)
    return (x,y)


def get_cruise_power(fname,fn=None):
  sys_status,t_sys_status = get_var(fname,'sys_status')
  if t_sys_status is None:
    sys_status,t_sys_status = get_var(fname,'telem_sys')
    if t_sys_status is None:
      return np.nan
  start,stop = flighttimes(fname,fn=fn)
  ind = get_time_indeces(t_sys_status,start,stop)
  return np.nanmean(sys_status['batt_voltage'][ind] * sys_status['batt_current'][ind])

def print_useful_ap_stats(fname):
  min_h,max_h,P,max_da,min_wind,max_wind,max_ias,max_speed,max_vz,min_vz,max_T,min_T = get_useful_ap_stats(fname)
  print('Useful stats for %s'%fname)
  if P != None:
    print('\tPower Draw: %.1fW' % P)
  if min_h != None:
    print('\tAltitude (MSL): %.1fm -> %.1fm (change of %.1fm)' % (min_h,max_h,max_h-min_h))
  if max_da != None:
    print('\tMax Density Altitude: %.1fm' % (max_da))
  if max_wind != None:
    print('\tWind Speed: %.1fm/s -> %.1fm/s (change of %.1fm/s)' % (min_wind,max_wind,max_wind-min_wind))
  if max_vz != None:
    print('\tMax Climb and Descent: %.1fm/s and %.1fm/s)' % (max_vz,min_vz))
  if min_T != None:
    print('\tTemperature Range: %.1fC and %.1fC' % (min_T,max_T))

def get_useful_ap_stats(fname,fn=None):

  min_h = np.nan
  max_h = np.nan
  P = np.nan
  max_da = np.nan
  max_ias = np.nan
  max_speed = np.nan
  min_wind = np.nan
  max_wind = np.nan
  min_T = np.nan
  max_T = np.nan

  start,stop = flighttimes(fname,fn=fn)
  P = get_cruise_power(fname,fn=fn)

  state,tstate = get_var(fname,'state')
  gps,tgps = get_var(fname,'gps')
  stat_p,tstat_p = get_var(fname,'stat_p')
  ind = get_time_indeces(state['system_time'],start,stop)

  max_h = np.max(state['altitude'][ind])
  min_h = np.min(state['altitude'][ind])

  if type(state) == np.ndarray:
    if 'ias' in state.dtype.names:
      max_ias = np.max(state['ias'][ind])
  elif type(state) == dict:
    if 'ias' in state:
      max_ias = np.max(state['ias'][ind])

  add_wind=False
  if type(state) == np.ndarray:
    if 'wind_x' in state.dtype.names:
      add_wind = True
  if type(state) == dict:
    if 'wind_x' in state:
      add_wind = True
  if add_wind:
    wind_n = state['wind_x'][ind]
    wind_e = state['wind_y'][ind]
    wind_spd = 0*wind_n
    for wn,we,idx in zip(wind_n,wind_e,range(0,len(wind_spd))):
      wind_spd[idx] = np.linalg.norm((wn,we))

    if np.sum(wind_spd) > 0:
      min_wind = np.min(wind_spd)
      max_wind = np.max(wind_spd)


  ind = get_time_indeces(stat_p['system_time'],start,stop)
  if np.sum(stat_p['temperature'][ind] > 0):
    rho = compute_air_density(stat_p['temperature'][ind], stat_p['pressure'][ind])
    max_da = getDensityAlt(np.min(rho))
    max_T = np.max(stat_p['temperature'][ind])
    min_T = np.min(stat_p['temperature'][ind])

  ind = get_time_indeces(gps['system_time'],start,stop)
  max_speed = np.max(gps['speed'][ind])
  max_vz = np.max(gps['velocity.z'][ind])
  min_vz = np.min(gps['velocity.z'][ind])

  return (min_h,max_h,P,max_da,min_wind,max_wind,max_ias,max_speed,max_vz,min_vz,max_T,min_T)

def get_time_indeces(ts,tstart,tstop=None):
  if tstop is None:
    if tstart.ndim == 1:
      tstop = tstart[1]
      tstart = tstart[0]
    else:
      tstop = tstart[:,1]
      tstart = tstart[:,0]

  if isinstance(tstart,np.ndarray):
    first = True
    for start,stop in zip(tstart,tstop):
      if first:
        idx = np.where((ts >= start) & (ts <= stop))[0]
        first = False
      else:
        idx = np.concatenate((idx,np.where((ts > start) & (ts < stop))[0]))
  else:
    idx = np.where((ts >= tstart) & (ts <= tstop))[0]
  return idx

def find_nc_fname(folder,logname,flight_start):
    datetimeformat = "%Y-%m-%d_%H-%M-%S"
    epoch = datetime.datetime.strptime("1970-01-01_00-00-00",datetimeformat)
    elapsed = datetime.timedelta(seconds=(flight_start))
    return '%s%s_%s.nc'%(folder,datetime.datetime.strftime(epoch + elapsed,datetimeformat),logname)

def get_hf_var(hf, label):
    if hf.__contains__(label):
      return hf[label][:]
    else:
      return None

def get_mat_vars(fname):
  hf = h5py.File(fname, 'r')
  out_key = ['acc','act','tact','act_cal','tact_cal','advparam','tadvparam','agl','air_temperature','board_orientation','command','tcommand','cont_filt_param','tcont_filt_param','cont_param','tcont_param','dubins_path','dyn_p','gcs','gnss_orientation','gps','gyr','hs','ths','hw_error','thw_error','land_param','tland_param','launch_param','tlaunch_param','limits','tlimits','mag','map','mhp','mission_param','ndvi','payload_param','payload_trigger','ctrl_loops','tctrl_loops','power_on','sensor_cal','tsensor_cal','stat_p','state','surface_mix','tsurface_mix','sys_init','tsys_init','sys_status','tsys_status','vehicle_param','tvehicle_param','waypoint','twaypoint']
  in_key = ['/SENSORS_ACCELEROMETER_vec','/ACTUATORS_VALUES_vec','/ACTUATORS_VALUES_time','/ACTUATORS_CALIBRATION_vec','/ACTUATORS_CALIBRATION_time','/STATE_ESTIMATOR_PARAM_vec','/STATE_ESTIMATOR_PARAM_time','/SENSORS_AGL_vec','/SENSORS_AIR_TEMPERATURE','/SENSORS_BOARD_ORIENTATION_vec','/CONTROL_COMMAND_vec','/CONTROL_COMMAND_time','/CONTROL_FILTER_PARAMS_vec','/CONTROL_FILTER_PARAMS_time','/CONTROL_FLIGHT_PARAMS_vec','/CONTROL_FLIGHT_PARAMS_time','/DUBIN_PATH_vec','/SENSORS_DYNAMIC_PRESSURE_vec','/TELEMETRY_GCS_LOCATION_vec','/SENSORS_GNSS_ORIENTATION','/SENSORS_GPS_vec','/SENSORS_GYROSCOPE_vec','/INPUT_HANDSET_VALUES_vec','/INPUT_HANDSET_VALUES_time','/SYSTEM_HARDWARE_ERROR','/SYSTEM_HARDWARE_ERROR_time','/VEHICLE_LAND_PARAMS_vec','/VEHICLE_LAND_PARAMS_time','/VEHICLE_LAUNCH_PARAMS_vec','/VEHICLE_LAUNCH_PARAMS_time','/VEHICLE_LIMITS_vec','/VEHICLE_LIMITS_time','/SENSORS_MAGNETOMETER_vec','/HANDSET_CALIBRATION_vec','/SYSTEM_HARDWARE_ERROR','/MISSION_PARAMETERS_vec','/PAYLOAD_NDVI','/PAYLOAD_PARAMS_vec','/PAYLOAD_TRIGGER_vec','/CONTROL_PID_vec','/CONTROL_PID_time','/SYSTEM_POWER_ON_vec','/SENSORS_CALIBRATE_vec','/SENSORS_CALIBRATE_time','/SENSORS_STATIC_PRESSURE_vec','/STATE_STATE_vec','/ACTUATORS_MIXING_PARAMS_vec','/ACTUATORS_MIXING_PARAMS_time','/SYSTEM_INITIALIZE_vec','/ACTUATORS_CALIBRATION_time','/SYSTEM_HEALTH_AND_STATUS_vec','/SYSTEM_HEALTH_AND_STATUS_time','/VEHICLE_PARAMS_vec','/VEHICLE_PARAMS_time','/FLIGHT_PLAN_WAYPOINT_vec','/FLIGHT_PLAN_WAYPOINT_time']

  myVars = globals()
  for invar,outvar in zip(in_key,out_key):
    myVars.__setitem__(outvar, get_hf_var(hf,invar))

  return acc,act,tact,act_cal,tact_cal,advparam,tadvparam,agl,air_temperature,board_orientation,command,tcommand,cont_filt_param,tcont_filt_param,cont_param,tcont_param,dubins_path,dyn_p,gcs,gnss_orientation,gps,gyr,hs,ths,hw_error,thw_error,land_param,tland_param,launch_param,tlaunch_param,limits,tlimits,mag,map,mhp,mission_param,ndvi,payload_param,payload_trigger,ctrl_loops,tctrl_loops,power_on,sensor_cal,tsensor_cal,stat_p,state,surface_mix,tsurface_mix,sys_init,tsys_init,sys_status,tsys_status,vehicle_param,tvehicle_param,waypoint,twaypoint

def get_var(fname,varname):
  if fname[-3:] == 'mat': # .mat file
    return get_mat_var(fname,varname)
  elif fname[-3:] == '.nc': # netCDF file
    return get_nc_var(fname,varname)

def get_mat_var(fname,varname):
  try:
    var = loadmat(fname)[varname]
  except:
    return None,None

  var_out = {}

  for elem in var.dtype.names:
    if varname == 'payload_s0' and elem == 'ts':
      var_out['system_time'] = var['ts'][0][0].flatten()
    if varname == 'gps' and elem == 'velocity':
      var_out['velocity_x'] = var['velocity'][0][0]['x'][0][0].flatten()
      var_out['velocity_y'] = var['velocity'][0][0]['y'][0][0].flatten()
      var_out['velocity_z'] = var['velocity'][0][0]['z'][0][0].flatten()
    if varname == 'state' and elem == 'q':
      var_out['q0'] = var['q'][0][0][:,0]
      var_out['q1'] = var['q'][0][0][:,1]
      var_out['q2'] = var['q'][0][0][:,2]
      var_out['q3'] = var['q'][0][0][:,3]
    elif varname == 'state' and elem == 'wind':
      var_out['wind_x'] = var['wind'][0][0][:,0]
      var_out['wind_y'] = var['wind'][0][0][:,1]
      var_out['wind_z'] = var['wind'][0][0][:,2]
    elif varname == 'act' and elem == 'usec':
      for i in range(16):
        var_out['usec_actuator_'+str(i)] = var['usec'][0][0][:,i]
    elif (len(np.shape(var[elem][0][0])) == 1):
      var_out[elem] = var[elem][0][0].flatten()
    elif (np.shape(var[elem][0][0])[1] == 1):
      var_out[elem] = var[elem][0][0].flatten()
    else:
      var_out[elem] = var[elem][0][0]
  return var_out,var_out['system_time']


def get_nc_var(fname,varname):
  rg = nc.Dataset(fname, 'r')

  key = ['acc',
         'act',
         'act_cal',
         'advparam',
         'agl',
         'air_temperature',
         'board_orientation',
         'command',
         'cont_filt_param',
         'cont_param',
         'dubins_path',
         'dyn_p',
         'gcs',
         'gnss_orientation',
         'gps',
         'gyr',
         'hs',
         'hw_error',
         'land_param',
         'launch_param',
         'limits',
         'mag',
         'hs_cal',
         'mhp',
         'mission_param',
         'ndvi',
         'payload_param',
         'payload_trigger',
         'ctrl_loops',
         'power_on',
         'sensor_cal',
         'stat_p',
         'state',
         'surface_mix',
         'sys_init',
         'sys_status',
         'vehicle_param',
         'waypoint',
         'payload_s0',
         'hs_calibration',


         'telem_pos',
         'telem_gcs',
         'telem_press',
         'telem_gcs_svin',
         'telem_cont',
         'telem_ori',
         'telem_sys',
         'telem_payload',
         'payload_serial',
         'mag_current_cal',
         'mag_calibration',
         'gyro_calibration',
         'dynp_calibration',
         'flight_plan_map',
         'last_mapping_waypoint',
         'payload0',
         'payload1',
         'payload2',
         'payload3',
         'deployment_tube',
         'gnss_rtcm',
        ]


  nckey = [ '/SENSORS_ACCELEROMETER',
           '/ACTUATORS_VALUES',
           '/ACTUATORS_CALIBRATION',
           '/STATE_ESTIMATOR_PARAM',
           '/SENSORS_AGL',
           '/SENSORS_AIR_TEMPERATURE',
           '/SENSORS_BOARD_ORIENTATION',
           '/CONTROL_COMMAND',
           '/CONTROL_FILTER_PARAMS',
           '/CONTROL_FLIGHT_PARAMS',
           '/DUBIN_PATH',
           '/SENSORS_DYNAMIC_PRESSURE',
           '/TELEMETRY_GCS_LOCATION',
           '/SENSORS_GNSS_ORIENTATION',
           '/SENSORS_GPS',
           '/SENSORS_GYROSCOPE',
           '/INPUT_HANDSET_VALUES',
           '/SYSTEM_HARDWARE_ERROR',
           '/VEHICLE_LAND_PARAMS',
           '/VEHICLE_LAUNCH_PARAMS',
           '/VEHICLE_LIMITS',
           '/SENSORS_MAGNETOMETER',
           '/HANDSET_CALIBRATION',
           '/SENSORS_MHP_SENSORS',
           '/MISSION_PARAMETERS',
           '/PAYLOAD_NDVI',
           '/PAYLOAD_PARAMS',
           '/PAYLOAD_TRIGGER',
           '/CONTROL_PID',
           '/SYSTEM_POWER_ON',
           '/SENSORS_CALIBRATE',
           '/SENSORS_STATIC_PRESSURE',
           '/STATE_STATE',
           '/ACTUATORS_MIXING_PARAMS',
           '/SYSTEM_INITIALIZE',
           '/SYSTEM_HEALTH_AND_STATUS',
           '/VEHICLE_PARAMS',
           '/FLIGHT_PLAN_WAYPOINT',
           '/PAYLOAD_S0_SENSORS',
            '/HANDSET_CALIBRATION_vec',

           '/TELEMETRY_POSITION',
           '/TELEMETRY_GCS',
           '/TELEMETRY_PRESSURE',
           '/TELEMETRY_GCS_SVIN',
           '/TELEMETRY_CONTROL',
           '/TELEMETRY_ORIENTATION',
           '/TELEMETRY_SYSTEM',
           '/TELEMETRY_PAYLOAD',
           '/PAYLOAD_SERIAL',
           '/SENSORS_MAG_CURRENT_CAL',
           '/SENSORS_MAG_CALIBRATION',
           '/SENSORS_GYRO_CALIBRATION',
           '/SENSORS_DYNP_CALIBRATION',
           '/FLIGHT_PLAN_MAP',
           '/LAST_MAPPING_WAYPOINT',
           '/PAYLOAD_DATA_CHANNEL_0',
           '/PAYLOAD_DATA_CHANNEL_1',
           '/PAYLOAD_DATA_CHANNEL_2',
           '/PAYLOAD_DATA_CHANNEL_3',
           '/TELEMETRY_DEPLOYMENT_TUBE',
           '/SENSORS_GNSS_RTCM',
          ]

  tvar = None
  var = None
  if varname in key:
    ncname = nckey[key.index(varname)]
    if ncname[1:]+'_vec' in rg.variables.keys() and ncname[1:]+'_time' in rg.variables.keys() :
      var = rg[ncname+'_vec'][:]
      tvar = rg[ncname+'_time'][:].data
    elif ncname[1:] in rg.groups.keys():
      var = {}
      for v in rg[ncname].variables.keys():
        var[v] = rg[ncname][v][:].data
      if 'system_time' in var.keys():
        tvar = var['system_time']

#  if tvar is not None:
#    tvar,var = nc_correct(tvar, var, ncname)
  return var,tvar

def nc_correct(tvar, var, ncname):

  do_correction = True
  match ncname:
    case '/PAYLOAD_S0_SENSORS':
      elems = ['system_time','static_pressure','dynamic_pressure','air_temperature','humidity','laser_distance','ground_temperature','u','v','w']
      scales = [1000,10,10,100,100,100,100,100,100,100]
    case '/TELEMETRY_POSITION':
      scales = [1000,1e16,1e16,1000,1000,100,100,100,100]
      elems = ['system_time','latitude','longitude','altitude','gps_altitude','height','laser_distance','velocity','acceleration']
    #case '/TELEMETRY_GCS':
    case '/TELEMETRY_PRESSURE':
      elems = ['system_time','static_pressure','dynamic_pressure','air_temperature','humidity','wind','ias','tas','alpha','beta']
      scales = [1000,10,10,100,100,100,100,100,100,100]
    #case '/TELEMETRY_GCS_SVIN':
    case '/TELEMETRY_CONTROL':
      elems = ['system_time','roll','pitch','yaw','roll_rate','pitch_rate','yaw_rate','velocity','altitude','actuators']
      scales = [1000,10000,10000,10000,100,100,100,100,1000,100]
    case '/TELEMETRY_ORIENTATION':
      elems = ['system_time','q','omega','magnetometer']
      scales = [1000,10000,100,100]
    case '/TELEMETRY_SYSTEM':
      elems = ['system_time','batt_voltage','batt_current','batt_watt_hours','batt_percent','milliseconds','pdop']
      scales = [1000,1000,100,10,100,1000,100]
    case '/TELEMETRY_DEPLOYMENT_TUBE':
      elems = ['system_time','state', 'parachute_door', 'batt_voltage', 'error']
      scales = [1000,1,1,10,1,1]
    case _:
      do_correction = False

  if do_correction:
    for e,s in zip(elems,scales):
      if e in var.keys():
        var[e] = var[e]/s
        if e == 'system_time':
          tvar = tvar/s
  return tvar,var

def get_nc_var_old(fname,varname):
  rg = nc.Dataset(fname, 'r')
  key = ['acc',
  'act',
  'act_cal',
  'advparam',
  'agl',
  'air_temperature',
  'board_orientation',
  'command',
  'cont_filt_param',
  'cont_param',
  'dubins_path',
  'dyn_p',
  'gcs',
  'gnss_orientation',
  'gps',
  'gyr',
  'hs',
  'hw_error',
  'land_param',
  'launch_param',
  'limits',
  'mag',
  'map',
  'mhp',
  'mission_param',
  'ndvi',
  'payload_param',
  'payload_trigger',
  'ctrl_loops',
  'power_on',
  'sensor_cal',
  'stat_p',
  'state',
  'surface_mix',
  'sys_init',
  'sys_status',
  'vehicle_param',
  'waypoint',
  'payload_s0',
  ]
  nckey = [ '/SENSORS_ACCELEROMETER',
  '/ACTUATORS_VALUES',
  '/ACTUATORS_CALIBRATION',
  '/STATE_ESTIMATOR_PARAM',
  '/SENSORS_AGL',
  '/SENSORS_AIR_TEMPERATURE',
  '/SENSORS_BOARD_ORIENTATION',
  '/CONTROL_COMMAND',
  '/CONTROL_FILTER_PARAMS',
  '/CONTROL_FLIGHT_PARAMS',
  '/DUBIN_PATH',
  '/SENSORS_DYNAMIC_PRESSURE',
  '/TELEMETRY_GCS_LOCATION',
  '/SENSORS_GNSS_ORIENTATION',
  '/SENSORS_GPS',
  '/SENSORS_GYROSCOPE',
  '/INPUT_HANDSET_VALUES',
  '/SYSTEM_HARDWARE_ERROR',
  '/VEHICLE_LAND_PARAMS',
  '/VEHICLE_LAUNCH_PARAMS',
  '/VEHICLE_LIMITS',
  '/SENSORS_MAGNETOMETER',
  '/HANDSET_CALIBRATION',
  '/SYSTEM_HARDWARE_ERROR',
  '/MISSION_PARAMETERS',
  '/PAYLOAD_NDVI',
  '/PAYLOAD_PARAMS',
  '/PAYLOAD_TRIGGER',
  '/CONTROL_PID',
  '/SYSTEM_POWER_ON',
  '/SENSORS_CALIBRATE',
  '/SENSORS_STATIC_PRESSURE',
  '/STATE_STATE',
  '/ACTUATORS_MIXING_PARAMS',
  '/SYSTEM_INITIALIZE',
  '/SYSTEM_HEALTH_AND_STATUS',
  '/VEHICLE_PARAMS',
  '/FLIGHT_PLAN_WAYPOINT',
  '/PAYLOAD_S0_SENSORS',
  ]


  tvar = None
  var = None
  if varname in key:
    ncname = nckey[key.index(varname)]
    if ncname[1:]+'_vec' in rg.variables.keys() and ncname[1:]+'_time' in rg.variables.keys() :
      var = rg[ncname+'_vec'][:]
      tvar = rg[ncname+'_time'][:]

  if tvar is None:
    return var,tvar
  else:
    return var,tvar.data

def icon_ua(x0,psi,sc=1,col='black',ax=None):
  M = np.array([[np.cos(psi),np.sin(psi)],[-np.sin(psi),np.cos(psi)]])
  wing = np.array([[-1,0],[1,0]])
  body = np.array([[0,0.5],[0,-1]])
  tail = np.array([[-0.5,-1],[0.5,-1]])
  wing = sc*np.transpose(np.matmul(M,np.transpose(wing)))
  body = sc*np.transpose(np.matmul(M,np.transpose(body)))
  tail = sc*np.transpose(np.matmul(M,np.transpose(tail)))

  lines = []

  if ax is None:
    line, = plt.plot(wing[:,0]+x0[0], wing[:,1]+x0[1],color=col,linewidth=3)
    lines.append(line)
    line, = plt.plot(body[:,0]+x0[0], body[:,1]+x0[1],color=col,linewidth=1)
    lines.append(line)
    line, = plt.plot(tail[:,0]+x0[0], tail[:,1]+x0[1],color=col,linewidth=2)
    lines.append(line)
  else:
    line, = ax.plot(wing[:,0]+x0[0], wing[:,1]+x0[1],color=col,linewidth=3)
    lines.append(line)
    line, = ax.plot(body[:,0]+x0[0], body[:,1]+x0[1],color=col,linewidth=1)
    lines.append(line)
    line, = ax.plot(tail[:,0]+x0[0], tail[:,1]+x0[1],color=col,linewidth=2)
    lines.append(line)

  return lines

def decode_ap_err(err_code):
  err_vec = {'err':['ERROR_LOW_BATT',
                    'ERROR_HIGH_VOLTAGE',
                    'ERROR_NO_BATT',
                    'ERROR_NO_GPS',
                    'ERROR_NO_RADIO',
                    'ERROR_HIGH_CURRENT',
                    'ERROR_HIGH_TEMP',
                    'ERROR_ENGINE_OUT',
                    'ERROR_NAVIGATION_ERROR',
                    'ERROR_CONTROLLER_ERROR',
                    'ERROR_BAD_IAS',
                    'ERROR_FLYING_NO_PREFLIGHT',
                    'ERROR_NO_PAYLOAD_ACTUATOR',
                    'ERROR_BAD_FLIGHTPLAN',
                    'ERROR_NO_SD_CARD',
                    'ERROR_SD_CARD_ERROR',
                    'ERROR_GEOFENCE',
                    'ERROR_BAD_GPS',
                    'ERROR_NO_LASER',
                    'ERROR_NO_STATIC_PRESS',
                    'ERROR_NO_MAG',
                    'ERROR_COMM_LIMIT',
                    'ERROR_BAD_COMMS',
                    'ERROR_BAD_HANDSET',
                    'ERROR_BATT_LIMIT',
                    'ERROR_CRITICAL_BATT',
                    'ERROR_HW_FAULT',
                    'ERROR_BAD_PROPULSION',
                    'ERROR_ICING',
                    'ERROR_BAD_LAUNCH',
                    'ERROR_RESET_IN_FLIGHT',
                    'ERROR_REMOTE_ID'],
             'code':2**np.arange(0,32)}

  err_arr = []
  for err,code in zip(err_vec['err'],err_vec['code']):
    if err_code & code == code:
      err_arr.append(err)
  if len(err_arr) == 0:
    err_arr = ['ERROR_NO_ERROR']
  return err_arr


def plot_error_sequence(fname,err,ax=None,inflight=True):
  sys_status,tsys_status = get_var(fname,'sys_status')
  err_codes = sys_status['error_code']

  if inflight:
    start,stop = flighttimes(fname)
    idx = get_time_indeces(tsys_status,start,stop)
    tsys_status = tsys_status[idx]
    err_codes = err_codes[idx]

  err_vec = {'err':['ERROR_LOW_BATT',
                    'ERROR_HIGH_VOLTAGE',
                    'ERROR_NO_BATT',
                    'ERROR_NO_GPS',
                    'ERROR_NO_RADIO',
                    'ERROR_HIGH_CURRENT',
                    'ERROR_HIGH_TEMP',
                    'ERROR_ENGINE_OUT',
                    'ERROR_NAVIGATION_ERROR',
                    'ERROR_CONTROLLER_ERROR',
                    'ERROR_BAD_IAS',
                    'ERROR_FLYING_NO_PREFLIGHT',
                    'ERROR_NO_PAYLOAD_ACTUATOR',
                    'ERROR_BAD_FLIGHTPLAN',
                    'ERROR_NO_SD_CARD',
                    'ERROR_SD_CARD_ERROR',
                    'ERROR_GEOFENCE',
                    'ERROR_BAD_GPS',
                    'ERROR_NO_LASER',
                    'ERROR_NO_STATIC_PRESS',
                    'ERROR_NO_MAG',
                    'ERROR_COMM_LIMIT',
                    'ERROR_BAD_COMMS',
                    'ERROR_BAD_HANDSET',
                    'ERROR_BATT_LIMIT',
                    'ERROR_CRITICAL_BATT',
                    'ERROR_HW_FAULT',
                    'ERROR_BAD_PROPULSION',
                    'ERROR_ICING',
                    'ERROR_BAD_LAUNCH',
                    'ERROR_RESET_IN_FLIGHT',
                    'ERROR_REMOTE_ID',
                    ],
             'code':2**np.arange(0,32)}

  code = err_vec['code'][np.where(np.array(err_vec['err']) == err)[0]]

  if ax is not None:
    ax.plot(tsys_status, err_codes & code == code,label=err)
  else:
    plt.plot(tsys_status, err_codes & code == code,label=err)

def print_error_sequence(fname,inflight=True):
  sys_status,tsys_status = get_var(fname,'sys_status')
  err_codes = sys_status['error_code']

  if inflight:
    start,stop = flighttimes(fname)
    idx = get_time_indeces(tsys_status,start,stop)
    tsys_status = tsys_status[idx]
    err_codes = err_codes[idx]

  terr,err = get_err_sequence(tsys_status,err_codes)
  for te,e in zip(terr,err):
    print('t=%.2fs'%te,e)


def get_error_list(fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if tsys_status is None:
      sys_status,tsys_status = get_var(fname,'telem_sys')

    err_seq = []
    for num in sys_status['error_code']:
        arr = []
        for i in np.arange(0,32):
            code = 2**i
            if code & num == code:
                arr.append(i)
        err_seq.append(arr)

    all_values = []
    for sublist in err_seq:
        all_values.extend(sublist)

    unique_err = np.sort(np.array(list(set(all_values))))

    err_labels = ['ERROR_LOW_BATT',
                  'ERROR_HIGH_VOLTAGE',
                  'ERROR_NO_BATT',
                  'ERROR_NO_GPS',
                  'ERROR_NO_RADIO',
                  'ERROR_HIGH_CURRENT',
                  'ERROR_HIGH_TEMP',
                  'ERROR_ENGINE_OUT',
                  'ERROR_NAVIGATION_ERROR',
                  'ERROR_CONTROLLER_ERROR',
                  'ERROR_BAD_IAS',
                  'ERROR_FLYING_NO_PREFLIGHT',
                  'ERROR_NO_PAYLOAD_ACTUATOR',
                  'ERROR_BAD_FLIGHTPLAN',
                  'ERROR_NO_SD_CARD',
                  'ERROR_SD_CARD_ERROR',
                  'ERROR_GEOFENCE',
                  'ERROR_BAD_GPS',
                  'ERROR_NO_LASER',
                  'ERROR_NO_STATIC_PRESS',
                  'ERROR_NO_MAG',
                  'ERROR_COMM_LIMIT',
                  'ERROR_BAD_COMMS',
                  'ERROR_BAD_HANDSET',
                  'ERROR_BATT_LIMIT',
                  'ERROR_CRITICAL_BATT',
                  'ERROR_HW_FAULT',
                  'ERROR_BAD_PROPULSION',
                  'ERROR_ICING',
                  'ERROR_BAD_LAUNCH',
                  'ERROR_RESET_IN_FLIGHT',
                  'ERROR_REMOTE_ID']

    errL = []
    for index in unique_err:
        errL.append(err_labels[index])

    err_master = {}
    for idx,(eL,eV) in enumerate(zip(errL,unique_err)):
        ts = np.array([])
        for ti,eS in zip(tsys_status,err_seq):
            if eV in eS:
                ts = np.append(ts,ti)
        err_master[eL] = {'system_time':ts,
                          'value':ts*0 + idx}

    return err_master


def get_err_sequence(tsys_status, err_codes):
  idx = np.where(err_codes[:-1] != err_codes[1:])[0]
  terr = []
  err = []

  terr.append(tsys_status[0])
  err.append(decode_ap_err(err_codes[0]))
  for i in idx:
      terr.append(tsys_status[i])
      err.append(decode_ap_err(err_codes[i+1]))
  return terr,err

def plot_err_axis(terr,err,ax):
  k = 0
  col = [
      'xkcd:light blue gray',
      'xkcd:light yellow',
      'xkcd:tea green',
      'xkcd:baby pink',
  ]
  trange = 10
  for i,(te,e) in enumerate(zip(terr,err)):
    if i == len(terr)-1:
      ax.axvspan(te,ax.get_xlim()[1],color=col[i%len(col)])
    else:
      ax.axvspan(te,terr[i+1],color = col[i%len(col)])
    for e0 in e:
        ax.text(te,(k%trange)/trange,e0[6:])
        k+=1
  ax.yaxis.set_ticklabels([])
  ax.set_ylabel('Error Codes')

def compute_mixing_ratio(Td,Pa):
  # Td must be in C
  # Pa must be in Pa
  # Retuns "actual" mixing ratio in kg/kg
  # Links:
  #   mixing ratio: https://www.weather.gov/media/epz/wxcalc/mixingRatio.pdf
  #   vapor pressure: https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf
  c0 = 610.78
  c1 = 7.5
  c2 = 237.3

  e = c0*10 ** (c1*Td/(c2 + Td))
  return 0.62197 * e / (Pa-e)

def compute_dew_point(T,RH):
  # T must be in C
  # RH must be a percentage
  BETA =  17.62
  LAMBDA = 243.12
  H = np.log(RH/100.0) + (BETA*T) / (LAMBDA + T)
  return LAMBDA * H / (BETA - H)

def compute_rh(Td,T):
  # T and Td must be in C
  # Return RH as %
  BETA =  17.62
  LAMBDA = 243.12
  return np.exp(Td*BETA/(LAMBDA+Td) - T*BETA/(LAMBDA+T))*100


def compute_air_density(Ta, P, RH=0):
    # Ta in deg C
    # P in pascals
    # RH in %
    # Constants
    Ra = 287.05 # J/kgK dry air
    Rw = 461.495 # J/kgK vapor
    c0 = 610.78
    c1 = 7.5
    c2 = 237.3

    # Partial pressure of air and water vapor
    pv = c0*10 ** (c1*Ta/(c2 + Ta)) * RH/100 # partial pressure of saturated air
    pa = P - pv

    # Compute density
    return pa/(Ra * (Ta+273.15)) + pv / (Rw * (Ta+273.15))

def get_altimeter(stat_p,h):
  CONST_Tb =  288.15
  CONST_Lb =  -0.0065
  CONST_Rb =  8.31432
  CONST_M  = 0.0289644
  CONST_G  = 9.80665

  return stat_p * (CONST_Lb/CONST_Tb*h + 1.0) ** (CONST_G*CONST_M/CONST_Rb/CONST_Lb)

def statp2height(stat_p,Pb=101325.):
  CONST_Tb =  288.15
  CONST_Lb =  -0.0065
  CONST_Rb =  8.31432
  CONST_M  = 0.0289644
  CONST_G  = 9.80665

  return CONST_Tb/CONST_Lb * ( (Pb/stat_p) ** (CONST_Rb*CONST_Lb/CONST_G/CONST_M) - 1 )

def dynp2ias(q,rho=1.225):
  return np.sign(q) * np.sqrt(2*abs(q)/rho)

def compute_ias_tas(q,Ta,Ps,RH):
  rho_0 = 1.225
  ias = np.sign(q) * np.sqrt(2*abs(q)/rho_0)

  rho = compute_air_density(Ta,Ps,RH)

  tas = np.sign(q) * np.sqrt(2*abs(q)/rho)
  return ias,tas

def getDensityAlt(rho):
  return (44.3308 - 42.2665 * rho ** 0.234969) * 1000

def make_ticks(ax, packet_type=None, y_labels = None,fontsize=12):
  if packet_type is not None:
    match packet_type:
      case 'TrueFalse_t':
        y_labels = ['FALSE','TRUE']
      case 'DeploymentTubeState_t':
        y_labels = ['INIT','READY','ARMED','FLAP_OPEN','PARA_DEPLOYED','JETTISONED',
                    'AC_RELASED','SHUTDOWN','ERROR']
      case 'DeploymentTubeDoorStatus_t':
        y_labels = ['CLOSED','OPEN']
      case 'AutopilotMode_t':
        y_labels = ['INIT','AUTOMATIC','MANUAL','JOYSTICK','INVALID_MODE']
      case 'FlightMode_t':
        y_labels = ['INIT','PREFLIGHT','CALIBRATE','LAUNCH',
                    'CLIMBOUT','TRANSITION_TO_FORWARD','FLYING',
                    'TRANSITION_TO_HOVER','LANDING','LANDED',
                    'POSTFLIGHT','TERMINATE','INVALID_MODE']
      case 'LateralControlMode_t':
        y_labels = ['WINGS_LEVEL','COURSE_HOLD','RATES','ANGLES','COORDINATED',
                    'AUTO','EXTERNAL','INVALID']
      case 'AltitudeControlMode_t':
        y_labels = ['TAKE_OFF','HOLD','RATE','AUTO','LAND','EXTERNAL',
                    'DIRECT','INVALID']
      case 'LandingStatus_t':
        y_labels = ['INVALID','ENTER','TRACKING','HOLDING','FINAL','SHORT',
                    'LONG','LATERAL','MANUAL','COMMITTED']
      case 'NavigationControllerMode_t':
        y_labels = ['OFF','POS','PILOT_BODY','PILOT_WORLD','PILOT_BASE',
                    'WPT_HCMD','WPT','INVALID']
      case 'DeploymentTube_t':
        y_labels = ['INIT','READY','ARMED','FLAP_OPEN','PARA_DEPLOYED',
                      'JETTISONED','AC_RELASED','ERROR']
      case 'DubinsPathType_t':
        y_labels = ['RSR','LSL','LSR','RSL','LRL','RLR','ORBIT',
                      'HELIX','NEXT','GOTO','GOTO_MR']
      case 'GPSFixType_t':
        y_labels = ['NO_FIX','DEAD_RECKONING_ONLY','FIX_2D','FIX_3D',
                    'GNSS_DEAD_RECKONING','TIME_ONLY','DGPS','RTK']
      case 'TECSMode_t':
        y_labels = ['OFF','CLIMB','ALT_HOLD','VRATE','LAND','FLARE']



  y = np.arange(0,len(y_labels))
  ax.set_yticks(y)
  ax.set_yticklabels(y_labels, fontsize=fontsize)

def quat2ang_vec(Q):
    Q = np.asarray(Q)

    # If shape is (4,N), transpose to (N,4) for convenience
    if Q.shape[0] == 4 and Q.ndim == 2:
        Q = Q.T

    # Extract individual components
    q0 = Q[:, 0]
    q1 = Q[:, 1]
    q2 = Q[:, 2]
    q3 = Q[:, 3]

    # Vectorized formulas
    roll = np.arctan2(2*(q2*q3 + q0*q1),  q0*q0 - q1*q1 - q2*q2 + q3*q3)
    pitch = np.arcsin(2*(q0*q2 - q1*q3))
    yaw = np.arctan2(2*(q1*q2 + q0*q3),  q0*q0 + q1*q1 - q2*q2 - q3*q3)

    return roll, pitch, yaw

def log2ang(fname):
  state,tstate = get_var(fname,'state')

  if 'q' in state:
    Q = state['q']
  else:
    Q = np.transpose(np.vstack((state['q0'],state['q1'],state['q2'],state['q3'])))
  r,p,y = quat2ang_vec(Q)
  return r,p,y,tstate

def recompute_mag_yaw(fname):
  mag,tmag = get_var(fname,'mag')
  state,tstate = get_var(fname,'state')
  mission_param,tmission_param = get_var(fname,'mission_param')

  if 'q0' in state:
    Q = np.transpose(np.vstack((state['q0'],state['q1'],state['q2'],state['q3'])))
  else:
    Q = state['q']

  mx = interp1d(tmag,mag['x'],fill_value='extrapolate')(tstate)
  my = interp1d(tmag,mag['y'],fill_value='extrapolate')(tstate)
  mz = interp1d(tmag,mag['z'],fill_value='extrapolate')(tstate)

  mx = np.expand_dims(mx,axis=1)
  my = np.expand_dims(my,axis=1)
  mz = np.expand_dims(mz,axis=1)

  M_m = np.hstack([mx,my,mz])
  if mission_param is None:
    mag_dec = 0.0
  else:
    mag_dec = mission_param['mag_dec'][-1]

  Q = gu.mag_correct_q_vec(M_m,Q,mag_dec)

  rm,pm,ym = quat2ang_vec(Q)
  return tstate,ym

def get_rssivrange(fname,sname=None,fn=None):
  if sname is None:
    start,stop = flighttimes(fname,fn=fn)
    sys_status,ts = get_var(fname,'sys_status')
    if sys_status is None:
      return None,None
    gps,tgps = get_var(fname,'gps')
    if gps is None:
      return None,None
    gcs,tgcs = get_var(fname,'gcs')
    if gcs is None:
      idx = get_time_indeces(tgps,start,stop)[0]
      g_latlon = np.array([gps['latitude'][idx],gps['longitude'][idx]])
      xgs = 0*ts
      ygs = 0*ts
    else:
      g_latlon = np.array([np.nanmean(gcs['latitude']),np.nanmean(gcs['longitude'])])
      xg,yg = latlon2local(gcs['latitude'],gcs['longitude'],origin=g_latlon)
      xgs = interp1d(tgcs,xg,fill_value='extrapolate')(ts)
      ygs = interp1d(tgcs,yg,fill_value='extrapolate')(ts)

    xp,yp = latlon2local(gps['latitude'],gps['longitude'],origin=g_latlon)
    xps = interp1d(tgps,xp,fill_value='extrapolate')(ts)
    yps = interp1d(tgps,yp,fill_value='extrapolate')(ts)

    dist = xps*0
    for idx,(xp,yp,xg,yg) in enumerate(zip(xps,yps,xgs,ygs)):
      dist[idx] = np.linalg.norm([xp-xg,yp-yg])

    idx = get_time_indeces(ts,start,stop)
    return dist[idx],sys_status['rssi'][idx]

  else: # P3 probably
    telem_pos_s,ttelem_pos_s = get_var(sname,'telem_pos')
    telem_pos,ttelem_pos = get_var(fname,'telem_pos')
    telem_sys,ttelem_sys = get_var(fname,'telem_sys')

    idx = np.where(telem_sys['rssi'] < -10)
    rssi = interp1d(ttelem_sys[idx],telem_sys['rssi'][idx],fill_value='extrapolate')(ttelem_pos)

    week = np.max(telem_sys['week'])

    rg = nc.Dataset(sname,'r')
    seconds = (rg['/TELEMETRY_GCS']['hour'][:].data*3600 +rg['/TELEMETRY_GCS']['minute'][:].data * 60 + rg['/TELEMETRY_GCS']['seconds'][:].data).astype(float)
    idx = np.where(rg['/TELEMETRY_GCS']['hour'][:].data>0)[0][0]
    toff_gcs = weekseconds2unix(week,seconds[idx]) - rg['/TELEMETRY_GCS']['system_time'][:].data[idx]/1000
    ttelem_pos_s += toff_gcs

    seconds = (telem_sys['hour']*3600 +telem_sys['minute'] * 60 + telem_sys['milliseconds']/1000).astype(float)
    idx = np.where(telem_sys['hour']>0)[0][0]
    toff_ua = weekseconds2unix(week,seconds[idx]) - telem_sys['system_time'][idx]

    start,stop = flighttimes(fname)
    start += 30
    idx = get_time_indeces(ttelem_pos,start,stop)
    ttelem_pos += toff_ua

    ts = ttelem_pos[idx]
    lat_ua = telem_pos['latitude'][idx]
    lon_ua = telem_pos['longitude'][idx]
    alt_ua = telem_pos['altitude'][idx]
    rssi = rssi[idx]
    lat_s = interp1d(ttelem_pos_s,telem_pos_s['latitude'],fill_value='extrapolate')(ts)
    lon_s = interp1d(ttelem_pos_s,telem_pos_s['longitude'],fill_value='extrapolate')(ts)
    alt_s = interp1d(ttelem_pos_s,telem_pos_s['altitude'],fill_value='extrapolate')(ts)

    g_latlon = np.array([np.nanmean(lat_ua),np.nanmean(lon_ua)])
    xua,yua = latlon2local(lat_ua,lon_ua,origin=g_latlon)
    xgcs,ygcs = latlon2local(lat_s,lon_s,origin=g_latlon)

    dist = alt_s*0
    for i,(xp,yp,zp,xg,yg,zg) in enumerate(zip(xua,yua,alt_ua,xgcs,ygcs,alt_s)):
        dist[i] = np.linalg.norm(np.array([xp-xg,yp-yg,zp-zg]))
    return dist,rssi

def rssi_fun(d, n, C):
    return -n*np.log10(d) + C

def plot_rssivrange(fname,sname=None,ax=None,plot_raw=True,min_range=100,col='xkcd:dark grey'):

  d,rssi = get_rssivrange(fname,sname=sname)
  if plot_raw:
    if ax is None:
      plt.plot(d/1000,rssi,'o',label=os.path.basename(fname),color=col)
      plt.grid('on')
      plt.xlabel('Range [km]')
      plt.ylabel('RSSI [dbm]')
      plt.legend()
    else:
      ax.plot(d/1000,rssi,'o',label=os.path.basename(fname),color=col)
      ax.grid('on')
      ax.set_xlabel('Range [km]')
      ax.set_ylabel('RSSI [dbm]')
      ax.legend()


  rssi = rssi[d>min_range]
  d = d[d>min_range]
  v = curve_fit(rssi_fun, d, rssi)[0]
  n,C = v

  d2 = np.linspace(min_range, np.max(d),100)

  if ax is None:
    plt.plot(d2/1000,-n*np.log10(d2) + C,'--',color=col,linewidth=2)
  else:
    ax.plot(d2/1000,-n*np.log10(d2) + C,'--',color=col,linewidth=2)

def get_hs_list(fname,fname2=None,idx=-1):
  if fname2 is not None:
    hs_cal,ths_cal = get_var(fname2,'hs_cal')
  else:
    hs_cal,ths_cal = get_var(fname,'hs_cal')

  hs,ths = get_var(fname,'hs')

  HandsetFunction_t = [
    'HS_FUNC_UNUSED',
    'HS_FUNC_SET_AUTO',
    'HS_FUNC_SET_POS',
    'HS_FUNC_SET_PILOT',
    'HS_FUNC_L_AILERON',
    'HS_FUNC_L_ELEVATOR',
    'HS_FUNC_L_THROTTLE',
    'HS_FUNC_L_RUDDER',
    'HS_FUNC_L_FLAP',
    'HS_FUNC_L_GEAR',
    'HS_FUNC_L_PIVOT',
    'HS_FUNC_R_AILERON',
    'HS_FUNC_R_ELEVATOR',
    'HS_FUNC_R_THROTTLE',
    'HS_FUNC_R_RUDDER',
    'HS_FUNC_R_FLAP',
    'HS_FUNC_R_GEAR',
    'HS_FUNC_R_PIVOT',
    'HS_FUNC_PAYLOAD_1',
    'HS_FUNC_PAYLOAD_2',
    'HS_FUNC_PAYLOAD_3',
    'HS_FUNC_PAYLOAD_4',
    'HS_FUNC_PAYLOAD_5',
    'HS_FUNC_PAYLOAD_6',
    'HS_FUNC_PAYLOAD_7',
    'HS_FUNC_PAYLOAD_8',
    'HS_FUNC_PAYLOAD_9',
    'HS_FUNC_PAYLOAD_10',
    'HS_FUNC_PAYLOAD_11',
    'HS_FUNC_PAYLOAD_12',
    'HS_FUNC_PAYLOAD_13',
    'HS_FUNC_PAYLOAD_14',
    'HS_FUNC_PAYLOAD_15',
    'HS_FUNC_PAYLOAD_16',
    'HS_FUNC_ROLL',
    'HS_FUNC_PITCH',
    'HS_FUNC_ROLL_RATE',
    'HS_FUNC_PITCH_RATE',
    'HS_FUNC_YAW_RATE',
    'HS_FUNC_X_VEL',
    'HS_FUNC_Y_VEL',
    'HS_FUNC_Z_VEL',
    'HS_FUNC_THRUST',
    'HS_FUNC_SET_MOTORS',
    'HS_FUNC_SET_ACRO',
    'HS_FUNC_SET_ANGLE',
    'HS_FUNC_SET_COORD',
    'HS_FUNC_SET_BODY',
    'HS_FUNC_SET_WORLD',
    'HS_FUNC_SET_BASE',
    'HS_FUNC_INVALID',
  ]

  HandsetType_t = [
    'HS_TYPE_LINEAR',
    'HS_TYPE_TOGGLE',
    'HS_TYPE_3WAY',
    'HS_TYPE_INVALID',
  ]

  hs_list = {}

  hs_type = 'HS_TYPE_LINEAR'
  ilin = np.where(hs_cal['type'] == HandsetType_t.index(hs_type))[0]
  first = True
  for ch in np.arange(16):
    i = np.where(hs_cal['channel'][ilin] == ch)[0]
    if len(i) > 0:
      i = i[idx]
      hs_list[HandsetFunction_t[hs_cal['function_max'][ilin[i]]]] = {
          'channel':ch,
          'system_time':ths,
          'usec':hs['usec'][:,ch],
      }

  return hs_list

def get_surface_list(fname,fname2=None,firstlast=-1):
  act_type = [
    'ACT_UNUSED',
    'ACT_L_AILERON',
    'ACT_L_ELEVATOR',
    'ACT_L_THROTTLE',
    'ACT_L_RUDDER',
    'ACT_L_FLAP',
    'ACT_L_RUDDERVATOR',
    'ACT_L_ELEVON',
    'ACT_L_GEAR',
    'ACT_L_FRONT_PIVOT',
    'ACT_L_BACK_PIVOT',
    'ACT_R_AILERON',
    'ACT_R_ELEVATOR',
    'ACT_R_THROTTLE',
    'ACT_R_RUDDER',
    'ACT_R_FLAP',
    'ACT_R_RUDDERVATOR',
    'ACT_R_ELEVON',
    'ACT_R_GEAR',
    'ACT_R_FRONT_PIVOT',
    'ACT_R_BACK_PIVOT',
    'ACT_ROTOR',
    'ACT_PAYLOAD_1',
    'ACT_PAYLOAD_2',
    'ACT_PAYLOAD_3',
    'ACT_PAYLOAD_4',
    'ACT_PAYLOAD_5',
    'ACT_PAYLOAD_6',
    'ACT_PAYLOAD_7',
    'ACT_PAYLOAD_8',
    'ACT_PAYLOAD_9',
    'ACT_PAYLOAD_10',
    'ACT_PAYLOAD_11',
    'ACT_PAYLOAD_12',
    'ACT_PAYLOAD_13',
    'ACT_PAYLOAD_14',
    'ACT_PAYLOAD_15',
    'ACT_PAYLOAD_16',
    'ACT_INVALID',
  ]

  act_list = {}
  if fname2 is not None:
    act_cal,tact_cal = get_var(fname2,'act_cal')
  else:
    act_cal,tact_cal = get_var(fname,'act_cal')
  act,tact = get_var(fname,'act')
  if act is None: # Probably S0
    act,tact = get_var(fname,'telem_cont')
    act['usec'] = 0*act['actuators']
    for i in np.arange(np.shape(act['actuators'])[1]):
        idx = np.where(act_cal['channel'] == i)[0][-1]
        act['usec'][:,i] = ap_setusec(act['actuators'][:,i], act_cal['min_usec'][idx], act_cal['mid_usec'][idx], act_cal['max_usec'][idx])

  for ind,atype in enumerate(act_type):
    if atype == 'ACT_ROTOR':
      # Scan for multiple
      idx = np.where(act_cal['type']==ind)[0]
      rot_num,rot_idx = np.unique(act_cal['channel'][idx],return_index=True)
      for rnum,ridx in zip(rot_num,rot_idx):
        i = idx[ridx]
        act_list[atype+str(rnum)] = {'channel':act_cal['channel'][i],
                                     'max_usec':act_cal['max_usec'][i],
                                     'mid_usec':act_cal['mid_usec'][i],
                                     'min_usec':act_cal['min_usec'][i],
                                     'type':act_cal['type'][i],
                                     'system_time':act['system_time']/k_correct,
                                     'usec':act['usec'][:,act_cal['channel'][i]],
                                    }
    elif atype != 'ACT_UNUSED':
      if atype in act_list: # Need to iterate the number
        iterv = 0
        while atype+str(iterv) in act_list:
          iterv +=1
        atype = atype + str(iterv)

      i = np.where(act_cal['type']==ind)[0]
      if len(i) > 0:
        i  = i[firstlast]
        act_list[atype] = {'channel':act_cal['channel'][i],
                           'max_usec':act_cal['max_usec'][i],
                           'mid_usec':act_cal['mid_usec'][i],
                           'min_usec':act_cal['min_usec'][i],
                           'type':act_cal['type'][i],
                           'system_time':act['system_time']/k_correct,
                           'usec':act['usec'][:,act_cal['channel'][i]],
                          }
  return act_list

def ap_setusec(percent,min_usec,mid_usec,max_usec):
    usec = 0*percent
    if(max_usec > mid_usec):
        i = np.where(percent < 0)[0]
        usec[i] = (1+percent[i]) * (mid_usec - min_usec) + min_usec
        i = np.where(percent >= 0)[0]
        usec[i] = percent[i] * (max_usec - mid_usec) + mid_usec
    else:
        i = np.where(percent < 0)[0]
        usec[i] = -percent[i] * (min_usec - mid_usec) + mid_usec
        i = np.where(percent >= 0)[0]
        usec[i] = (1-percent[i]) * (mid_usec - max_usec) + max_usec
    return usec

def print_act_cal(fname,idx=-1):
  act_list = get_surface_list(fname,firstlast=idx)
  row =  "{:<8} {:<20} {:<6} {:>6} {:>6}"
  hrow = "{:<8} {:<20} {:<6} {:>6} {:>6}"
  headers = "Channel Type Min Mid Max".split()

  print(hrow.format(*headers))
  print("-" * 55)
  for atype in act_list:
    print(row.format(act_list[atype]['channel'],atype,act_list[atype]['min_usec'],act_list[atype]['mid_usec'],act_list[atype]['max_usec']))


def get_ctrl_loops(fname,idx=-1):
  sys_init,tsys_init = get_var(fname,'sys_init')
  ctrl_loops,tctrl_loops = get_var(fname,'ctrl_loops')
  if sys_init['vehicle_type'][idx] == 6:
    loop_names = ['ANG_TO_RATE',
                  'ROLL_RATE',
                  'PITCH_RATE',
                  'YAW_RATE',
                  'X_VEL_TO_ACC',
                  'Y_VEL_TO_ACC',
                  'POS',
                  'ALT',
                  'THRUST',
                  'ENG_2_THROTTLE',
                  'ENG_2_PITCH',
                  'TURNRATE_2_RUD',
                  'PITCH_2_ELEVATOR',
                  'ROLL_2_AIL',
                  'NAV_2_ROLL',
                  'IAS_2_VFF',
                 ]
  elif sys_init['vehicle_type'][idx] == 1:
    loop_names = [
                  'TURNRATE_2_RUD',
                  'PITCH_2_ELEVATOR',
                  'ROLL_2_AIL',
                  'NAV_2_ROLL',
                  'ENG_2_THROTTLE',
                  'ENG_2_PITCH',
                 ]
  loop_list = {}
  for i,ln in enumerate(loop_names):
    ind = np.where(ctrl_loops['id'] == i)[0]
    if len(ind)>0:
      ind = ind[idx]
      loop_list[ln] = {'p':ctrl_loops['p'][ind],
                       'i':ctrl_loops['i'][ind],
                       'd':ctrl_loops['d'][ind],
                       'min':ctrl_loops['output.min'][ind],
                       'max':ctrl_loops['output.max'][ind],
                      }
  return loop_list

def print_ctrl_loops(fname,idx=-1):
  loop_list = get_ctrl_loops(fname,idx=idx)
  row = "{:<20} {:<6.3f} {:<6.3f} {:<6.3f} {:<7.3f} {:<7.3f}"
  hrow =  "{:<20} {:<6} {:<6} {:<6} {:<7} {:<7}"
  headers = "Loop P I D MIN MAX".split()

  print(hrow.format(*headers))
  print("-" * 55)
  for ltype in loop_list:
    print(row.format(ltype,loop_list[ltype]['p'],loop_list[ltype]['i'],loop_list[ltype]['d'],loop_list[ltype]['min'],loop_list[ltype]['max']))

def print_mission_params(fname,idx=-1):
  var,tvar = get_var(fname,'mission_param')
  landings = ['Spiral','Vertical']
  launches = ['Hand','Bungee','Winch','Rolling','Car','Rail','Drop','Vertical']
  print('Altitude Min:        %.0fm'%var['altitude.min'][idx])
  print('Altitude Max:        %.0fm'%var['altitude.max'][idx])
  print('Range:               %.0fm'%var['max_range'][idx])
  print('Lost Comms Timeout:  %.0fs'%var['comm.seconds'][idx])
  if var['comm.waypoint'][idx] == 101:
    print('Lost Comms Waypoint: Landing')
  elif var['comm.waypoint'][idx] == 113:
    print('Lost Comms Waypoint: Takeoff')
  else:
    print('Lost Comms Waypoint: %.0f'%var['comm.waypoint'][idx])
  print('Launch:              %s'%launches[var['launch_type'][idx]])
  print('Land:                %s'%landings[var['land_type'][idx]])
  print('Min. Battery:        %.0f%%'%var['battery_min'][idx])
  print('Magnetic Dec.:       %.2f deg'%(var['mag_dec'][idx]*180/pi))

def print_mixing(fname,idx=-1):
  row = "{:<20} {:<10.3f}"
  hrow =  "{:<20} {:<10}"
  headers = "Mixer Value".split()

  print(hrow.format(*headers))
  print("-" * 40)

  var,tvar = get_var(fname,'surface_mix')
  if var is None:
    print('NO MIXING DATA')
  else:
    vname = 'mixing_roll_2_elevator'
    if vname in var.keys():
      print(row.format('Roll to Elevator',var[vname][idx]))
    vname = 'mixing_aileron_2_rudder'
    if vname in var.keys():
      print(row.format('Aileron to Rudder',var[vname][idx]))
    vname = 'mixing_flap_2_elevator'
    if vname in var.keys():
      print(row.format('Flap to Elevator',var[vname][idx]))


def print_limits(fname,idx=-1):
  var,tvar = get_var(fname,'limits')
  row = "{:<20} {:<10.1f} {:<10.1f}"
  row1 = "{:<31} {:<10.1f}"
  hrow =  "{:<20} {:<10} {:<10}"
  headers = "Limit Minimum Maximum".split()

  print(hrow.format(*headers))
  print("-" * 40)
  vname = 'ias'
  if vname+'.min' in var.keys():
    print(row.format('IAS',var[vname+'.min'][idx],var[vname+'.max'][idx]))
  sc = 180/pi
  vname = 'roll_angle'
  if vname+'.min' in var.keys():
    print(row.format('Roll Angle',var[vname+'.min'][idx]*sc,var[vname+'.max'][idx]*sc))
  vname = 'hover_roll_angle'
  if vname+'.min' in var.keys():
    print(row.format('Hover Roll Angle',var[vname+'.min'][idx]*sc,var[vname+'.max'][idx]*sc))
  vname = 'pitch_angle'
  if vname+'.min' in var.keys():
    print(row.format('Pitch Angle',var[vname+'.min'][idx]*sc,var[vname+'.max'][idx]*sc))
  vname = 'hover_pitch_angle'
  if vname+'.min' in var.keys():
    print(row.format('Hover Pitch Angle',var[vname+'.min'][idx]*sc,var[vname+'.max'][idx]*sc))
  vname = 'flightpath_angle'
  if vname+'.min' in var.keys():
    print(row.format('Flight Path',var[vname+'.min'][idx]*sc,var[vname+'.max'][idx]*sc))
  vname = 'flightpath_angle_flap'
  if vname+'.min' in var.keys():
    print(row.format('Flight Path Flap',var[vname+'.min'][idx]*sc,var[vname+'.max'][idx]*sc))
  if 'max_scale_factor' in var.keys():
    print(row1.format('IAS Gain',var['max_scale_factor'][idx]))
  vname = 'roll_rate'
  if vname in var.keys():
    print(row1.format('Roll Rate',var[vname][idx]*sc))
  vname = 'pitch_rate'
  if vname in var.keys():
    print(row1.format('Pitch Rate',var[vname][idx]*sc))
  vname = 'yaw_rate'
  if vname in var.keys():
    print(row1.format('Yaw Rate',var[vname][idx]*sc))
  vname = 'speed'
  if vname in var.keys():
    print(row1.format('Speed',var[vname][idx]))
  vname = 'vrate'
  if vname+'.min' in var.keys():
    print(row.format('Vertical Speed',var[vname+'.min'][idx],var[vname+'.max'][idx]))
  if 'max_pdop' in var.keys():
    print(row1.format('PDOP',var['max_pdop'][idx]))
  print("-" * 40)
  headers = "Timeouts Timeout Roll".split()
  print(hrow.format(*headers))
  if 'lost_gps' in var.keys():
   print(row.format('Lost GPS',var['lost_gps'][idx],var['lost_gps_roll'][idx]*180/pi))

def setup_subplot(ax,ylabel=None):
    ax.grid()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ss = ax.get_subplotspec()
    if ss.is_last_row():
        ax.set_xlabel('Time [s]',fontsize=12)
    else:
        ax.tick_params(bottom=False, labelbottom=False)
    if ylabel is not None:
        ax.set_ylabel(ylabel,fontsize=12)

def add_flying_bar(ax,fname):
    start,stop = flighttimes(fname)
    for t0,t1 in zip(start,stop):
        ax.axvspan(t0,t1,color='xkcd:light blue')
    ax.tick_params(bottom=False,labelbottom=False,left=False,labelleft=False)
    ax.set_ylabel('Flying',color='xkcd:light blue')
    ax.grid()

def create_subplot(N,ttl = None,ax_share = None, flight_bar=True):
    fig = plt.figure()
    if flight_bar:
        gs = gridspec.GridSpec(N+1,1,hspace=0.08,height_ratios=[0.02*N]+[1 for x in range(N)])
    else:
        gs = gridspec.GridSpec(N,1,hspace=0.08,height_ratios=[1 for x in range(N)])
    if ttl is not None:
        fig.suptitle(ttl, size=16)

    if ax_share is None:
        ax = fig.add_subplot(gs[0])
        ax_share = ax
    else:
        ax = fig.add_subplot(gs[0], sharex=ax_share)

    return fig,gs,ax_share,ax

def create_subplotN(N,ttl = None,ax_share = None, flight_bar=True):

    fig = plt.figure()
    subfig = fig.subfigures(1, len(N))
    if ttl is not None:
        subfig[0].suptitle(ttl, size=16)

    gs = []
    for i,n in enumerate(N):
        if flight_bar:
            gs.append(gridspec.GridSpec(N[i]+1,1,hspace=0.08,
                                         height_ratios=[0.02*N[i]]+[1 for x in range(N[i])],
                                         figure=subfig[i]))
        else:
            gs.append(gridspec.GridSpec(N[i],1,hspace=0.08,
                                         height_ratios=[1 for x in range(N[i])],
                                         figure=subfig[i]))

        if i == 0:
            if ax_share is None:
                ax = subfig[0].add_subplot(gs[0][0])
                ax_share = ax
            else:
                ax = subfig[0].add_subplot(gs[0][0], sharex=ax_share)

    return subfig,gs,ax_share,ax

def plot_handset(fname,idx=-1,ax_share=None,fname2=None,xmlname=None):
    hs_list = get_hs_list(fname,idx=idx,fname2=fname2)

    if len(hs_list) > 0:

        fig,gs,ax_share,ax = create_subplot(len(hs_list),
                                            ttl = 'Control Surfaces',
                                            ax_share = ax_share)
        add_flying_bar(ax,fname)

        for i,stype in enumerate(hs_list):
            ax = fig.add_subplot(gs[i+1],sharex=ax_share)
            ax.plot(hs_list[stype]['system_time'],hs_list[stype]['usec'],'.',color='xkcd:dark gray')
            setup_subplot(ax, ylabel=stype[4:])
    else:
        print("WARNING: No actuator types logged")
        ax = None
    return ax

def plot_s0_info(fname,ax_share=None):
    ori,tori = get_var(fname,'telem_ori')
    r,p,y = quat2ang_vec(ori['q'])
    cont,tcont = get_var(fname,'telem_cont')
    press,tpress = get_var(fname,'telem_press')
    pos,tpos = get_var(fname,'telem_pos')
    sog = 0*pos['velocity'][:,0]
    for i,vxy in enumerate(zip(pos['velocity'][:,0:2])):
        sog[i] = np.linalg.norm(vxy)


    fig,gs,ax_share,ax = create_subplot(5,ttl = 'S0 Info',ax_share = ax_share)
    add_flying_bar(ax,fname)

    ax = fig.add_subplot(gs[1],sharex=ax_share)
    ax.plot(tori,r*180/pi,color='xkcd:dark gray')
    ax.plot(tcont,cont['roll']*180/pi,'--',color='xkcd:red')
    setup_subplot(ax,ylabel='Roll')

    ax = fig.add_subplot(gs[2],sharex=ax_share)
    ax.plot(tori,p*180/pi,color='xkcd:dark gray')
    ax.plot(tcont,cont['pitch']*180/pi,'--',color='xkcd:red')
    setup_subplot(ax,ylabel='Pitch')

    ax = fig.add_subplot(gs[3],sharex=ax_share)
    ax.plot(tpress,press['ias'],color='xkcd:dark grey',label='IAS')
    ax.plot(tpress,press['tas'],color='xkcd:dark blue',label='TAS')
    ax.plot(tcont,cont['velocity'][:,0],'--',color='xkcd:red',label='IAS Command')
    ax.plot(tpos,sog,color='xkcd:green',label='GPS SOG')
    ax.legend()
    setup_subplot(ax,ylabel='IAS')

    ax = fig.add_subplot(gs[4],sharex=ax_share)
    ax.plot(tpos,pos['altitude'],color='xkcd:dark grey')
    ax.plot(tcont,cont['altitude'],'--',color='xkcd:red')
    setup_subplot(ax,ylabel = 'Altitude')

    ax = fig.add_subplot(gs[5],sharex=ax_share)
    ax.plot(tcont,cont['actuators'][:,0],label='L_AILERON')
    ax.plot(tcont,cont['actuators'][:,1],label='R_AILERON')
    ax.plot(tcont,cont['actuators'][:,2],label='L_THROTTLE')
    ax.plot(tcont,cont['actuators'][:,4],label='L_ELEVATOR')
    ax.plot(tcont,cont['actuators'][:,5],label='L_RUDDER')
    ax.legend()
    setup_subplot(ax,ylabel = 'Servos')


    return ax

def handle_roll(ax,fname):
    r,p,y,ts = log2ang(fname)
    com = get_log_command(fname)
    ax.plot(ts, r*180/pi, color='xkcd:dark gray')
    ax.plot(com['t_ROLL'], com['ROLL']*180/pi, '.-', color='xkcd:red')
    setup_subplot(ax, ylabel='Roll')

def handle_pitch(ax,fname):
    r,p,y,ts = log2ang(fname)
    com = get_log_command(fname)
    ax.plot(ts, p*180/pi, color='xkcd:dark gray')
    ax.plot(com['t_PITCH'], com['PITCH']*180/pi, '.-', color='xkcd:red')
    setup_subplot(ax, ylabel='Pitch')

def handle_yaw(ax,fname):
    r,p,y,ts = log2ang(fname)
    com = get_log_command(fname)
    ax.plot(ts, y*180/pi, color='xkcd:dark gray')
    ax.plot(com['t_YAW'], com['YAW']*180/pi, '.-', color='xkcd:red')
    setup_subplot(ax, ylabel='Yaw')

def handle_roll_rate(ax,fname):
    gyr,tgyr = get_var(fname,'gyr')
    com = get_log_command(fname)
    ax.plot(tgyr,gyr['x']*180/pi,color='xkcd:dark gray')
    ax.plot(com['t_ROLL_RATE']/k_correct,com['ROLL_RATE']*180/pi,'.-',color='xkcd:red')
    ax2 = ax.twinx()
    ax2.plot(com['t_MOMENT_X']/k_correct,com['MOMENT_X'])
    setup_subplot(ax2,ylabel='M_x')
    ax2.yaxis.label.set_color('C0')
    ax2.tick_params(axis='y', colors='C0')
    ax2.grid(visible=True,color='C0',alpha=0.5)
    setup_subplot(ax,ylabel='Roll Rate')

def handle_pitch_rate(ax,fname):
    gyr,tgyr = get_var(fname,'gyr')
    com = get_log_command(fname)
    ax.plot(tgyr,gyr['y']*180/pi,color='xkcd:dark gray')
    ax.plot(com['t_PITCH_RATE']/k_correct,com['PITCH_RATE']*180/pi,'.-',color='xkcd:red')
    ax2 = ax.twinx()
    ax2.plot(com['t_MOMENT_Y']/k_correct,com['MOMENT_Y'])
    setup_subplot(ax2,ylabel='M_y')
    ax2.yaxis.label.set_color('C0')
    ax2.tick_params(axis='y', colors='C0')
    ax2.grid(visible=True,color='C0',alpha=0.5)
    setup_subplot(ax,ylabel='Pitch Rate')

def handle_yaw_rate(ax,fname):
    gyr,tgyr = get_var(fname,'gyr')
    com = get_log_command(fname)
    ax.plot(tgyr,gyr['y']*180/pi,color='xkcd:dark gray')
    ax.plot(com['t_YAW_RATE']/k_correct,com['YAW_RATE']*180/pi,'.-',color='xkcd:red')
    ax2 = ax.twinx()
    ax2.plot(com['t_MOMENT_Z']/k_correct,com['MOMENT_Z'])
    setup_subplot(ax2,ylabel='M_z')
    ax2.yaxis.label.set_color('C0')
    ax2.tick_params(axis='y', colors='C0')
    ax2.grid(visible=True,color='C0',alpha=0.5)
    setup_subplot(ax,ylabel='Yaw Rate')

def handle_vx(ax,fname):
    gps,tgps = get_var(fname,'gps')
    com = get_log_command(fname)
    ax.plot(tgps,gps['velocity.x'],color='xkcd:dark gray')
    ax.plot(com['t_X_VEL']/k_correct,com['X_VEL'],'.-',color='xkcd:red')
    setup_subplot(ax,ylabel='X-Vel')

def handle_vy(ax,fname):
    gps,tgps = get_var(fname,'gps')
    com = get_log_command(fname)
    ax.plot(tgps,gps['velocity.y'],color='xkcd:dark gray')
    ax.plot(com['t_Y_VEL']/k_correct,com['Y_VEL'],'.-',color='xkcd:red')
    setup_subplot(ax,ylabel='Y-Vel')

def handle_vz(ax,fname):
    gps,tgps = get_var(fname,'gps')
    com = get_log_command(fname)
    ax.plot(tgps,gps['velocity.z'],color='xkcd:dark gray')
    ax.plot(com['t_VRATE']/k_correct,-com['VRATE'],'.-',color='xkcd:red')
    ax2 = ax.twinx()
    ax2.plot(com['t_THRUST']/k_correct,com['THRUST'])
    setup_subplot(ax2,ylabel='Thrust')
    ax2.yaxis.label.set_color('C0')
    ax2.tick_params(axis='y', colors='C0')
    ax2.grid(visible=True,color='C0',alpha=0.5)
    setup_subplot(ax,ylabel='Z-Vel')

def handle_ias(ax,fname):
    state,tstate = get_var(fname,'state')
    if state is not None:
        gps,tgps = get_var(fname,'gps')
        com = get_log_command(fname)
        ax.plot(tstate,state['ias'],color='xkcd:dark grey',label='IAS')
        ax.plot(com['t_SPEED']/k_correct,com['SPEED'],'.-',color='xkcd:red',label='Command')
        ax.plot(tgps,gps['speed'],color='xkcd:green',label='SOG')
    else:
        cont,tcont = get_var(fname,'telem_cont')
        press,tpress = get_var(fname,'telem_press')
        pos,tpos = get_var(fname,'telem_pos')
        sog = 0*pos['velocity'][:,0]
        for i,vxy in enumerate(zip(pos['velocity'][:,0:2])):
            sog[i] = np.linalg.norm(vxy)

        ax.plot(tpress,press['ias'],color='xkcd:dark grey',label='IAS')
        ax.plot(tpress,press['tas'],color='xkcd:blue',label='TAS')
        ax.plot(tcont,cont['velocity'][:,0],'--',color='xkcd:red',label='IAS Command')
        ax.plot(tpos,sog,color='xkcd:green',label='GPS SOG')

    ax.legend()
    setup_subplot(ax,ylabel='IAS')

def handle_winds(ax,fname):
    # FIXME - add other
    var,ts = get_var(fname,'payload_s0')
    if var is not None:
      ax.plot(ts,var['u'],'.-',label='u')
      ax.plot(ts,var['v'],'.-',label='v')
      ax.plot(ts,var['w'],'.-',label='w')
      ax.legend()
    else:
      var,ts = get_var(fname,'state')
      if var is not None:
        ax.plot(ts,var['wind'][:,0],'.-',label='u')
        ax.plot(ts,var['wind'][:,1],'.-',label='v')
        ax.plot(ts,var['wind'][:,2],'.-',label='w')
        ax.legend()

    setup_subplot(ax,ylabel='Winds')

def handle_humidity(ax,fname):
    # FIXME - add other
    s0,ts0 = get_var(fname,'payload_s0')
    if s0 is not None:
      ax.plot(ts0,s0['humidity'],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel='Humidity')

def handle_s0_act(ax,fname):
    cont,tcont = get_var(fname,'telem_cont')
    ax.plot(tcont,cont['actuators'][:,0],'.-',label='L_AILERON')
    ax.plot(tcont,cont['actuators'][:,1],'.-',label='R_AILERON')
    ax.plot(tcont,cont['actuators'][:,2],'.-',label='L_THROTTLE')
    ax.plot(tcont,cont['actuators'][:,4],'.-',label='L_ELEVATOR')
    ax.plot(tcont,cont['actuators'][:,5],'.-',label='L_RUDDER')
    ax.legend()
    setup_subplot(ax,ylabel = 'Actuators')

def handle_alphabeta(ax,fname):
    s0,ts = get_var(fname,'payload_s0')
    if s0 is not None:
        a,b,q = pm.compute_alpha_beta_q(s0['dynamic_pressure'][:,0],
                                        s0['dynamic_pressure'][:,1],
                                        s0['dynamic_pressure'][:,2],
                                        s0['dynamic_pressure'][:,3],
                                        s0['dynamic_pressure'][:,4],
            )
    ax.plot(ts,a*180/pi,'.-',label='alpha')
    ax.plot(ts,b*180/pi,'.-',label='beta')
    ax.legend()
    setup_subplot(ax,ylabel = '[deg]')


def handle_altitude(ax,fname):
    state,tstate = get_var(fname,'state')
    gps,tgps = get_var(fname,'gps')
    if state is None: # Probably an S0
        cont,tc = get_var(fname,'telem_cont')
        hc = cont['altitude']
        state,tstate = get_var(fname,'telem_pos')
        tgps = tstate
        gps_alt = state['gps_altitude']
    else:
        com = get_log_command(fname)
        tc = com['t_ALTITUDE'][com['ALTITUDE']>0.01]/k_correct
        hc = com['ALTITUDE'][com['ALTITUDE']>0.01]
        gps_alt = gps['altitude']

    ax.plot(tstate[state['altitude'] > 0],state['altitude'][state['altitude'] > 0],'.-',label='State')
    ax.plot(tc,hc,'.-',color='xkcd:red',label='Command')
    ax.plot(tgps,gps_alt,color='xkcd:green',label='GPS')
    ax.legend()
    setup_subplot(ax,ylabel='Alt')

def handle_acc(ax,fname):
    acc,tacc = get_var(fname,'acc')
    ax.plot(tacc,acc['x'],'.-',label='x')
    ax.plot(tacc,acc['y'],'.-',label='y')
    ax.plot(tacc,acc['z'],'.-',label='z')
    setup_subplot(ax,ylabel='Acc [m/s/s]')
    ax.legend()

def handle_gyr(ax,fname):
    gyr,tgyr = get_var(fname,'gyr')
    ax.plot(tgyr,gyr['x']*180/pi,'.-')
    ax.plot(tgyr,gyr['y']*180/pi,'.-')
    ax.plot(tgyr,gyr['z']*180/pi,'.-')
    setup_subplot(ax,ylabel='Gyr [deg/s]')

def handle_mag(ax,fname):
    mag,tmag = get_var(fname,'mag')
    if mag is not None:
      ax.plot(tmag,mag['x'],'.-')
      ax.plot(tmag,mag['y'],'.-')
      ax.plot(tmag,mag['z'],'.-')
      setup_subplot(ax,ylabel='Mag [mGauss]')

def handle_batt_current(ax,fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if tsys_status is None:
      sys_status,tsys_status = get_var(fname,'telem_sys')
    tsys_status /= k_correct
    var = 'batt_voltage'
    ax.plot(tsys_status,sys_status[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)

def handle_batt_voltage(ax,fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if tsys_status is None:
      sys_status,tsys_status = get_var(fname,'telem_sys')
    tsys_status /= k_correct
    var = 'batt_current'
    ax.plot(tsys_status,sys_status[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)

def handle_batt_power(ax,fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if tsys_status is None:
      sys_status,tsys_status = get_var(fname,'telem_sys')
    tsys_status /= k_correct
    ax.plot(tsys_status,sys_status['batt_voltage'] * sys_status['batt_current'],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel='Power [watts]')

def handle_batt_percent(ax,fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if tsys_status is None:
      sys_status,tsys_status = get_var(fname,'telem_sys')
    tsys_status /= k_correct
    var = 'batt_percent'
    ax.plot(tsys_status,sys_status[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)

def handle_batt_watt_hours(ax,fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if tsys_status is None:
      sys_status,tsys_status = get_var(fname,'telem_sys')
    tsys_status /= k_correct
    var = 'batt_watt_hours'
    if var not in sys_status.keys():
      var = 'batt_coulomb_count'
    ax.plot(tsys_status,sys_status[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)

def handle_rssi(ax,fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if tsys_status is None:
      sys_status,tsys_status = get_var(fname,'telem_sys')
    tsys_status /= k_correct
    var = 'rssi'
    ax.plot(tsys_status,sys_status[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)

def handle_error_list(ax,fname):
    plot_error_list(ax,fname)

def handle_latitude(ax,fname):
    gps,tgps = get_var(fname,'gps')
    var = 'latitude'
    ax.plot(tgps,gps[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)
    ax.ticklabel_format(useOffset=False)

def handle_longitude(ax,fname):
    gps,tgps = get_var(fname,'gps')
    var = 'longitude'
    ax.plot(tgps,gps[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)
    ax.ticklabel_format(useOffset=False)

def handle_gps_alt(ax,fname):
    gps,tgps = get_var(fname,'gps')
    var = 'altitude'
    ax.plot(tgps,gps[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)

def handle_gps_speed(ax,fname):
    gps,tgps = get_var(fname,'gps')
    var = 'speed'
    ax.plot(tgps,gps[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)

def handle_gps_course(ax,fname):
    gps,tgps = get_var(fname,'gps')
    var = 'course'
    ax.plot(tgps,gps[var],'.-',color='xkcd:dark gray')
    setup_subplot(ax,ylabel=var)

def handle_satellites(ax,fname):
    gps,tgps = get_var(fname,'gps')
    var = 'satellites'
    ax.step(tgps,gps[var],'.-',color='xkcd:dark gray',where='post')
    setup_subplot(ax,ylabel=var)

def handle_pdop(ax,fname):
    gps,tgps = get_var(fname,'gps')
    var = 'pdop'
    ax.step(tgps,gps[var],'.-',color='xkcd:dark gray',where='post')
    setup_subplot(ax,ylabel=var)

def handle_fix_type(ax,fname):
    gps,tgps = get_var(fname,'gps')
    var = 'fix_type'
    ax.step(tgps,gps[var],color='xkcd:dark gray',where='post')
    setup_subplot(ax,ylabel=var)
    make_ticks(ax,packet_type='GPSFixType_t')

def handle_gps_vel(ax,fname):
    gps,tgps = get_var(fname,'gps')
    ax.plot(tgps,gps['velocity.x'],'.-',label='x',color='xkcd:dark gray')
    ax.plot(tgps,gps['velocity.y'],'.-',label='y',color='xkcd:gray')
    ax.plot(tgps,gps['velocity.z'],'.-',label='z',color='xkcd:blue')
    ax.legend()
    setup_subplot(ax,ylabel='Velocities')

def handle_gps_utc(ax,fname):
    gps,tgps = get_var(fname,'gps')
    ax.plot(tgps,gps['hour'],'.-',label='hh',color='xkcd:dark gray')
    ax.plot(tgps,gps['minute'],'.-',label='mmm',color='xkcd:gray')
    ax.plot(tgps,gps['seconds'],'.-',label='ss',color='xkcd:blue')
    setup_subplot(ax,ylabel='UTC')
    ax.legend()

def handle_ap_mode(ax,fname):
    plot_ap_modes(fname,ax,'AUTOPILOT_MODE','AutopilotMode_t')
def handle_flight_mode(ax,fname):
    plot_ap_modes(fname,ax,'FLIGHT_MODE','FlightMode_t')
def handle_landing_mode(ax,fname):
    plot_ap_modes(fname,ax,'LANDING_MODE','LandingStatus_t')
def handle_alt_mode(ax,fname):
    plot_ap_modes(fname,ax,'ALT_MODE','AltitudeControlMode_t')
def handle_lat_mode(ax,fname):
    plot_ap_modes(fname,ax,'LAT_MODE','LateralControlMode_t')
def handle_nav_mode(ax,fname):
    plot_ap_modes(fname,ax,'NAV_MODE','NavigationControllerMode_t')
def handle_engine_kill(ax,fname):
    plot_ap_modes(fname,ax,'ENGINE_KILL','TrueFalse_t')
def handle_flight_terminate(ax,fname):
    plot_ap_modes(fname,ax,'FLIGHT_TERMINATE','TrueFalse_t')
def handle_tecs_mode(ax,fname):
    plot_ap_modes(fname,ax,'TECS_MODE','TECSMode_t')

def plot_ap_modes(fname,ax,varname,packetname):
    com = get_log_command(fname)
    idx = np.where(((com['t_'+varname] < 1e16)) & ((abs(com[varname]) < 256)))[0] #FIXME
    ax.step(com['t_'+varname][idx]/k_correct,com[varname][idx],color='xkcd:dark grey',where='post')
    setup_subplot(ax,ylabel=varname)
    make_ticks(ax, packet_type = packetname)

def handle_waypoints(ax,fname):
    com = get_log_command(fname)
    ax.step(com['t_WAYPOINT']/k_correct,com['WAYPOINT'],color='xkcd:dark grey',where='post')
    setup_subplot(ax,ylabel='Waypoint Num')

def handle_lost_comm(ax,fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if sys_status is None: # Try GCS
        sys_status,tsys_status = get_var(fname,'telem_sys')
    tsys_status /= k_correct
    idx = np.where(tsys_status < 1e16)[0]
    ax.step(tsys_status[idx],sys_status['lost_comm'][idx],color='xkcd:dark grey')
    setup_subplot(ax,ylabel='lost_comm')
    make_ticks(ax, packet_type = 'TrueFalse_t')

def handle_lost_gps(ax,fname):
    sys_status,tsys_status = get_var(fname,'sys_status')
    if sys_status is None: # Try GCS
        sys_status,tsys_status = get_var(fname,'telem_sys')
    tsys_status /= k_correct
    idx = np.where(tsys_status < 1e16)[0]
    ax.step(tsys_status[idx],sys_status['lost_gps'][idx],color='xkcd:dark grey')
    setup_subplot(ax,ylabel='lost_gps')
    make_ticks(ax, packet_type = 'TrueFalse_t')

def plot_surfaces(ax,fname,surf_list=None, firstlast=-1,fname2=None,xmlname=None):
    act_list = get_surface_list(fname,fname2=fname2)
    if surf_list is None:
        surf_list = act_list.keys()
    if len(act_list) > 0:
        for stype in surf_list:
            if stype in act_list.keys():
              ax.plot(act_list[stype]['system_time'],act_list[stype]['usec'],'o-',label=stype[4:],alpha=0.5)
        setup_subplot(ax, ylabel='Surfaces [usec]')
        ax.legend()
    else:
      print('plot_surfaces: WARNING - no surfaces found, try an fname2 or xml')


def handle_motor_surfaces(ax,fname):
    motor_list = [
      'ACT_L_THROTTLE',
      'ACT_L_FRONT_PIVOT',
      'ACT_L_BACK_PIVOT',
      'ACT_R_THROTTLE',
      'ACT_R_GEAR',
      'ACT_R_FRONT_PIVOT',
      'ACT_R_BACK_PIVOT',
      'ACT_ROTOR',
    ] + ['ACT_ROTOR'+str(i) for i in range(16)]
    plot_surfaces(ax,fname,surf_list=motor_list)


def handle_aero_surfaces(ax,fname,fname2=None):
    aero_list = [
      'ACT_L_AILERON',
      'ACT_L_ELEVATOR',
      'ACT_L_RUDDER',
      'ACT_L_FLAP',
      'ACT_L_RUDDERVATOR',
      'ACT_L_ELEVON',
      'ACT_R_AILERON',
      'ACT_R_ELEVATOR',
      'ACT_R_RUDDER',
      'ACT_R_FLAP',
      'ACT_R_RUDDERVATOR',
      'ACT_R_ELEVON',
    ]
    plot_surfaces(ax,fname,surf_list=aero_list)

def handle_tails(ax,fname,fname2=None):
    aero_list = [
      'ACT_L_ELEVATOR',
      'ACT_L_RUDDER',
      'ACT_L_RUDDERVATOR',
      'ACT_R_ELEVATOR',
      'ACT_R_RUDDER',
      'ACT_R_RUDDERVATOR',
    ]
    plot_surfaces(ax,fname,surf_list=aero_list)


def handle_wings(ax,fname,fname2=None):
    aero_list = [
      'ACT_L_AILERON',
      'ACT_L_FLAP',
      'ACT_L_ELEVON',
      'ACT_R_AILERON',
      'ACT_R_FLAP',
      'ACT_R_ELEVON',
    ]
    plot_surfaces(ax,fname,surf_list=aero_list)


def plot_library(fname=None, ax=None, ptype=None,displayOnly=False,returnCatList=False,returnList=False):
    case_handlers = {
        'roll': handle_roll,
        'pitch': handle_pitch,
        'yaw': handle_yaw,
        'roll_rate': handle_roll_rate,
        'pitch_rate': handle_pitch_rate,
        'yaw_rate': handle_yaw_rate,
        'vx': handle_vx,
        'vy': handle_vy,
        'vz': handle_vz,
        'ias': handle_ias,
        'altitude': handle_altitude,
        'acc': handle_acc,
        'gyr': handle_gyr,
        'mag': handle_mag,
        'batt_current': handle_batt_current,
        'batt_voltage': handle_batt_voltage,
        'batt_power': handle_batt_power,
        'batt_percent': handle_batt_percent,
        'batt_watt_hours': handle_batt_watt_hours,
        'rssi': handle_rssi,
        'error_list': handle_error_list,
        'latitude': handle_latitude,
        'longitude': handle_longitude,
        'gps_alt': handle_gps_alt,
        'gps_speed': handle_gps_speed,
        'satellites': handle_satellites,
        'pdop': handle_pdop,
        'fix_type': handle_fix_type,
        'gps_vel': handle_gps_vel,
        'gps_utc': handle_gps_utc,
        'ap_mode': handle_ap_mode,
        'flight_mode': handle_flight_mode,
        'landing_mode': handle_landing_mode,
        'alt_mode': handle_alt_mode,
        'lat_mode': handle_lat_mode,
        'nav_mode': handle_nav_mode,
        'engine_kill': handle_engine_kill,
        'flight_terminate': handle_flight_terminate,
        'tecs_mode': handle_tecs_mode,
        'waypoints': handle_waypoints,
        'lost_comm': handle_lost_comm,
        'lost_gps': handle_lost_gps,
        'motors' : handle_motor_surfaces,
        'aero_surf' : handle_aero_surfaces,
        'wings' : handle_wings,
        'tail' : handle_tails,
        'winds' : handle_winds,
        'humidity' : handle_humidity,
        's0_act' : handle_s0_act,
        'alpha_beta' : handle_alphabeta,
    }
    plot_categories = {
        'attitude': ['roll', 'pitch', 'yaw','roll_rate', 'pitch_rate', 'yaw_rate'],
        'posvel':['ias', 'altitude', 'vx', 'vy', 'vz'],
        'imu': ['acc', 'gyr', 'mag'],
        'sys_status': ['batt_current','batt_voltage','batt_power','batt_percent','batt_watt_hours','rssi','error_list'],
        'gps':['latitude', 'longitude', 'gps_alt', 'gps_speed', 'satellites', 'pdop', 'fix_type', 'gps_vel', 'gps_utc'],
        'modes':['ap_mode', 'flight_mode', 'landing_mode', 'alt_mode', 'lat_mode', 'nav_mode', 'engine_kill', 'flight_terminate', 'tecs_mode', 'waypoints', 'lost_comm', 'lost_gps'],
        'actuators': ['motors', 'aero_surf', 'wings', 'tail'],
        'atmo': ['winds', 'humidity'],
    }
    if returnCatList:
        final_plot_categories = defaultdict(list)

        # Copy explicitly defined categories
        for cat, ptypes in plot_categories.items():
            for p in ptypes:
                if p in case_handlers:  # only include valid keys
                    final_plot_categories[cat].append(p)

        # Add missing handlers into "Uncategorized"
        for p in case_handlers.keys():
            if not any(p in plist for plist in final_plot_categories.values()):
                final_plot_categories["Uncategorized"].append(p)

        # Convert back to dict if desired
        return dict(final_plot_categories)
    elif returnList:
        return case_handlers.keys()
    else:
        if ptype not in case_handlers:
            setup_subplot(ax, ylabel='MISSING: '+ptype)
            valid_ptypes = list(case_handlers.keys())
            print('MISSING: %s, USE: '%ptype,end='')
            print(valid_ptypes)
        else:
            case_handlers[ptype](ax,fname)


def premade_plot_libs(ltype=None,displayOnly=False):
    libs = {
        'fw_control': ['roll','pitch','ias','altitude'],
        'mr_control_att': ['roll','roll_rate','pitch','pitch_rate','yaw','yaw_rate'],
        'mr_control_posvel': ['vx','vy','vz','altitude'],
        'vt_control_posvel': ['vx','vy','vz','altitude','ias'],
        'imu':['acc','gyr','mag'],
        'sys_status':['batt_current','batt_voltage','batt_power','batt_percent','batt_watt_hours','rssi','error_list'],
        'gps':['latitude','longitude','gps_alt','gps_speed','satellites','pdop','fix_type','gps_vel','gps_utc'],
        'ap_modes':['ap_mode','flight_mode','landing_mode','alt_mode','lat_mode','nav_mode','engine_kill','flight_terminate','tecs_mode','waypoints','lost_comm','lost_gps'],
    }
    if displayOnly:
        print('Plot Options in Pre-made Library:')
        for k in libs.keys():
            print('\t%s: '%k,end='')
            print(libs[k])
    else:
        if ltype not in libs.keys():
            print('premade_plot_libs: %s not found in: '%ltype,end='')
            print(libs.keys())
        else:
            return libs[ltype]

def _visible_y_range(ax):
    x0, x1 = ax.get_xlim()
    ys = []

    # Lines
    for line in ax.lines:
        x = np.asarray(line.get_xdata())
        y = np.asarray(line.get_ydata())
        m = np.isfinite(x) & np.isfinite(y) & (x >= x0) & (x <= x1)
        if np.any(m):
            ys.append(y[m])

    # Scatter (PathCollections)
    for col in ax.collections:
        offs = col.get_offsets()
        if offs is not None and len(offs):
            x = np.asarray(offs[:, 0])
            y = np.asarray(offs[:, 1])
            m = np.isfinite(x) & np.isfinite(y) & (x >= x0) & (x <= x1)
            if np.any(m):
                ys.append(y[m])

    if not ys:
        return None
    yall = np.concatenate(ys)
    ymin = np.nanmin(yall)
    ymax = np.nanmax(yall)
    if not np.isfinite(ymin) or not np.isfinite(ymax):
        return None
    if ymin == ymax:  # avoid zero-height view
        delta = 1 if ymin == 0 else abs(ymin) * 0.1
        ymin -= delta; ymax += delta
    return ymin, ymax

def autoscale_y_to_xlim(ax, margin=0.05):
    rng = _visible_y_range(ax)
    if rng is None:
        return
    ymin, ymax = rng
    pad = (ymax - ymin) * margin
    ax.set_ylim(ymin - pad, ymax + pad)

def enable_auto_yscale_on_xlim(ax):
    def _on_xlim_changed(event_ax):
        autoscale_y_to_xlim(event_ax)
    ax.callbacks.connect("xlim_changed", _on_xlim_changed)

def plot_data_arrays(fname, ptypes,ax_share=None):
    if len(ptypes) > 1:
        subfig,gs,ax_share,ax = create_subplotN([len(p) for p in ptypes],ax_share = ax_share)
        add_flying_bar(ax,fname)
        for i,ptype in enumerate(ptypes):
            for j,p in enumerate(ptype):
                if j == 0 and i > 0:
                    ax = subfig[i].add_subplot(gs[i][0],sharex=ax_share)
                    add_flying_bar(ax,fname)
                ax = subfig[i].add_subplot(gs[i][j+1],sharex=ax_share)
                enable_auto_yscale_on_xlim(ax)
                plot_library(fname,ax,p)
    else:
        ptypes = ptypes[0]
        fig,gs,ax_share,ax = create_subplot(len(ptypes),ax_share = ax_share)
        add_flying_bar(ax,fname)
        for i,ptype in enumerate(ptypes):
            ax = fig.add_subplot(gs[i+1],sharex=ax_share)
            enable_auto_yscale_on_xlim(ax)
            plot_library(fname,ax,ptype)
    return ax


def plot_error_list(ax,fname):
  err_list = get_error_list(fname)
  for k in err_list.keys():
    ax.plot(err_list[k]['system_time']/k_correct,err_list[k]['value'],'ok')
  make_ticks(ax,y_labels=err_list.keys())
  setup_subplot(ax,ylabel='Errors')

def set_plot_range(fname,ax,textra = 2,fnum = None):
    start,stop = flighttimes(fname)
    if fnum is None:
        for k,(t0,t1) in enumerate(zip(start,stop)):
            print('Flight %i. '%(k+1) +
                  get_datetime_aplog(fname,t0)+
                  ' -> '+get_datetime_aplog(fname,t1)+
                  ' TOF: %.1f min'%((t1-t0)/60))
        fnum = int(input('Select #: '))

    fnum -= 1
    if fnum < 0 or fnum > len(start):
        print('WARNING: Flight #%i is not within range'%fnum)
    else:
        ax.set_xlim([start[fnum]-textra, stop[fnum]+textra])

def good_lat(lat: float) -> bool:
    return abs(lat) >= 0 and abs(lat) <= 90

def good_lon(lon: float) -> bool:
    return abs(lon) >= 0 and abs(lon) <= 180

def get_gps_info(fname, is_gcs_log=False):
    start, stop = flighttimes(fname)
    if is_gcs_log:
        gps, tgps = get_var(fname, 'telem_sys')
    else:
        gps, tgps = get_var(fname, 'gps')

    idx = get_time_indeces(tgps, start, stop)

    gps_week = gps['week'][idx]
    gps_hour = gps['hour'][idx]
    gps_minute = gps['minute'][idx]

    if is_gcs_log:
        gps_seconds = gps['milliseconds'][idx] / 1000
    else:
        gps_seconds = gps['seconds'][idx]

    gps_epoch = datetime.datetime(1980, 1, 6, tzinfo=pytz.utc)
    start_time = gps_epoch + datetime.timedelta(
        weeks=int(gps_week[0]),
        hours=int(gps_hour[0]),
        minutes=int(gps_minute[0]),
        seconds=int(gps_seconds[0]))
    end_time = gps_epoch + datetime.timedelta(
        weeks=int(gps_week[-1]),
        hours=int(gps_hour[-1]),
        minutes=int(gps_minute[-1]),
        seconds=int(gps_seconds[-1]))

    if is_gcs_log:
        gps, _ = get_var(fname, 'telem_pos')

    lats = gps['latitude'][idx]
    lons = gps['longitude'][idx]
    alts = gps['altitude'][idx]

    good_idx = []
    filt_lats = [
        val for idx, val in enumerate(lats)
        if good_lat(val) and good_idx.append(idx) == None
    ]
    filt_lons = [lons[i] for i in good_idx]
    filt_alts = [alts[i] for i in good_idx]

    good_idx = []
    filt_lons = [
        val for idx, val in enumerate(filt_lons)
        if good_lon(val) and good_idx.append(idx) == None
    ]
    filt_lats = [filt_lats[i] for i in good_idx]
    filt_alts = [filt_alts[i] for i in good_idx]

    avg_lat = np.nanmean(filt_lats)
    avg_lon = np.nanmean(filt_lons)

    coords = []
    for i in range(0, len(filt_lats)):
        if len(filt_lons) < i - 1 or len(filt_alts) < i - 1:
            break

        coords.append([
            float(filt_lats[i]),
            float(filt_lons[i]),
            float(filt_alts[i])])

    return start_time, end_time, float(avg_lat), float(avg_lon), coords


def mag_curr_gains(fname,t0=None,t1=None,t2=None):
    mag,tmag = get_var(fname,'mag')
    sys,tsys = get_var(fname,'sys_status')

    fig,ax = plt.subplots(5,1,sharex=True)
    i = 0

    ax[i].plot(tsys,sys['batt_current'],'.-',label='I',color='xkcd:dark gray')
    ax[i].plot(tsys,sys['batt_voltage'],'.-',label='A',color='xkcd:dark green')
    ax[i].grid()
    ax[i].legend()
    ax[i].set_ylabel('Batter')
    if t0 is not None:
        ax[i].axvspan(t0[0],t0[1],alpha=0.5,color='xkcd:green')
        ax[i].axvspan(t1[0],t1[1],alpha=0.5,color='xkcd:yellow')
        ax[i].axvspan(t2[0],t2[1],alpha=0.5,color='xkcd:red')
    i+=1

    acc,tacc = get_var(fname,'acc')
    ts,ym = recompute_mag_yaw(fname)
    ax[i].plot(ts,ym*180/pi,'.-',color='xkcd:dark gray')
    #ax[i].plot(tacc,acc['x'],'.')
    ax[i].grid()
    ax[i].set_ylabel('Yaw')
    #ax[i].set_ylabel('Acc')

    if t0 is not None:
        ax[i].axvspan(t0[0],t0[1],alpha=0.5,color='xkcd:green')
        ax[i].axvspan(t1[0],t1[1],alpha=0.5,color='xkcd:yellow')
        ax[i].axvspan(t2[0],t2[1],alpha=0.5,color='xkcd:red')
    i+=1

    ax[i].plot(tmag,mag['x'],'.-',color='xkcd:dark gray')
    ax[i].grid()
    ax[i].set_ylabel('Mx')
    if t0 is not None:
        ax[i].axvspan(t0[0],t0[1],alpha=0.5,color='xkcd:green')
        ax[i].axvspan(t1[0],t1[1],alpha=0.5,color='xkcd:yellow')
        ax[i].axvspan(t2[0],t2[1],alpha=0.5,color='xkcd:red')
    i+=1
    ax[i].plot(tmag,mag['y'],'.-',color='xkcd:dark gray')
    ax[i].grid()
    ax[i].set_ylabel('My')
    if t0 is not None:
        ax[i].axvspan(t0[0],t0[1],alpha=0.5,color='xkcd:green')
        ax[i].axvspan(t1[0],t1[1],alpha=0.5,color='xkcd:yellow')
        ax[i].axvspan(t2[0],t2[1],alpha=0.5,color='xkcd:red')
    i+=1
    ax[i].plot(tmag,mag['z'],'.-',color='xkcd:dark gray')
    ax[i].grid()
    ax[i].set_ylabel('Mz')

    if t0 is not None:
        ax[-1].set_xlim([t0[0]-10, t2[1]+10])
        ax[i].axvspan(t0[0],t0[1],alpha=0.5,color='xkcd:green')
        ax[i].axvspan(t1[0],t1[1],alpha=0.5,color='xkcd:yellow')
        ax[i].axvspan(t2[0],t2[1],alpha=0.5,color='xkcd:red')


    if t0 is not None:
        idx = get_time_indeces(tsys,t0)
        mfit_curr = np.array([
            np.mean(sys['batt_current'][get_time_indeces(tsys,t0)]),
            np.mean(sys['batt_current'][get_time_indeces(tsys,t1)]),
            np.mean(sys['batt_current'][get_time_indeces(tsys,t2)]),
        ])

        mx = mag['x'] - np.mean(mag['x'][get_time_indeces(tmag,t0)])
        my = mag['y'] - np.mean(mag['y'][get_time_indeces(tmag,t0)])
        mz = mag['z'] - np.mean(mag['z'][get_time_indeces(tmag,t0)])

        mfit_mx = np.array([
            np.mean(mx[get_time_indeces(tmag,t0)]),
            np.mean(mx[get_time_indeces(tmag,t1)]),
            np.mean(mx[get_time_indeces(tmag,t2)]),
        ])
        mfit_my = np.array([
            np.mean(my[get_time_indeces(tmag,t0)]),
            np.mean(my[get_time_indeces(tmag,t1)]),
            np.mean(my[get_time_indeces(tmag,t2)]),
        ])

        mfit_mz = np.array([
            np.mean(mz[get_time_indeces(tmag,t0)]),
            np.mean(mz[get_time_indeces(tmag,t1)]),
            np.mean(mz[get_time_indeces(tmag,t2)]),
        ])


        p_x = np.polyfit(mfit_curr, mfit_mx,1)
        p_y = np.polyfit(mfit_curr, mfit_my,1)
        p_z = np.polyfit(mfit_curr, mfit_mz,1)

        plt.figure()
        plt.plot(mfit_curr,mfit_mx,'o',color='C0',label='Mx')
        plt.plot(mfit_curr,p_x[1]+p_x[0]*mfit_curr,'--',color='C0')
        plt.plot(mfit_curr,mfit_my,'o',color='C1',label='My')
        plt.plot(mfit_curr,p_y[1]+p_y[0]*mfit_curr,'--',color='C1')
        plt.plot(mfit_curr,mfit_mz,'o',color='C2',label='Mz')
        plt.plot(mfit_curr,p_z[1]+p_z[0]*mfit_curr,'--',color='C2')
        plt.grid()
        plt.xlabel('Current')
        plt.ylabel('Mag Deviation [mgauss]')
        plt.legend()

        print('<mag_correction_xb>%f</mag_correction_xb>'% p_x[1])
        print('<mag_correction_xm>%f</mag_correction_xm>'% p_x[0])
        print('<mag_correction_yb>%f</mag_correction_yb>'% p_y[1])
        print('<mag_correction_ym>%f</mag_correction_ym>'% p_y[0])
        print('<mag_correction_zb>%f</mag_correction_zb>'% p_z[1])
        print('<mag_correction_zm>%f</mag_correction_zm>'% p_z[0])

import glob, json
import ipywidgets as widgets
from IPython.display import display, clear_output

def launch_data_plotter(interactive=True):

    # Directories
    base_dir = os.path.expanduser("~/.bst_plotting")
    upload_dir = os.path.join(base_dir, "uploads")
    user_layout_dir = os.path.join(base_dir, "user_layouts")
    default_layout_dir = os.path.join(base_dir, "default_layouts")

    for d in [upload_dir, user_layout_dir, default_layout_dir]:
        os.makedirs(d, exist_ok=True)

    # --- Categorized plots from your library ---
    plot_categories = plot_library(returnCatList=True)

    # --- Helper: build categorized dropdown ---
    def make_ptype_dropdown(value=None):
        options = []
        for cat, ptypes in plot_categories.items():
            if ptypes:
                options.append((f"--- {cat} ---", None))
                for p in ptypes:
                    options.append((f"  {p}", p))
        return widgets.Dropdown(
            options=options,
            description="",
            value=value if value in [opt[1] for opt in options] else None,
            layout=widgets.Layout(width="180px")
        )

    # --- Plot widget with delete button ---
    def make_plot_widget(col_box, value=None):
        dd = make_ptype_dropdown(value)
        remove_btn = widgets.Button(description="❌", layout=widgets.Layout(width="32px"))
        remove_btn.style.button_color = 'white'
        box = widgets.HBox([dd, remove_btn], layout=widgets.Layout(justify_content="center"))

        def on_remove(_):
            children = list(col_box.children[:-1])  # exclude +Row
            if box in children:
                children.remove(box)
                if not children:  # no rows left → remove entire column
                    remove_column(col_box)
                else:
                    col_box.children = tuple(children + [col_box.children[-1]])

        remove_btn.on_click(on_remove)
        return box

    # --- Column builder ---
    def make_column(values=None):
        add_row_btn = widgets.Button(description="➕",layout=widgets.Layout(width="32px"))
        add_row_btn.style.button_color = 'white'
        add_row_box = widgets.HBox([add_row_btn], layout=widgets.Layout(justify_content="center"))
        col_box = widgets.VBox([])

        def on_add_row(_):
            pw = make_plot_widget(col_box)
            col_box.children = tuple(list(col_box.children[:-1]) + [pw] + [col_box.children[-1]])

        add_row_btn.on_click(on_add_row)

        children = []
        if values:
            for v in values:
                children.append(make_plot_widget(col_box, v))
        else:
            children.append(make_plot_widget(col_box))
        children.append(add_row_box)
        col_box.children = children
        return col_box

    # --- Global layout ---
    columns = []
    columns_box = widgets.HBox([], layout=widgets.Layout(align_items="flex-start"))

    def add_column(values=None):
        col = make_column(values)
        columns.append(col)
        rebuild_columns_box()

    def remove_column(col_box):
        if col_box in columns:
            columns.remove(col_box)
            rebuild_columns_box()

    def rebuild_columns_box():
        children = list(columns)
        # add +Column button at far right
        add_col_btn = widgets.Button(description="➕",layout=widgets.Layout(width="28px"))
        add_col_btn.style.button_color = 'white'
        add_col_btn.on_click(lambda _: add_column())
        children.append(widgets.VBox([add_col_btn], layout=widgets.Layout(justify_content="center")))
        columns_box.children = children

    add_column()  # start with one column

    # --- File Upload & Recent Files ---
    file_upload = widgets.FileUpload(accept=".nc", multiple=False)
    file_dropdown = widgets.Dropdown(
        options=["-- Select Recent File --"] + os.listdir(upload_dir),
        description="Files:"
    )

    def refresh_file_dropdown():
        file_dropdown.options = ["-- Select Recent File --"] + os.listdir(upload_dir)

    def on_upload_change(change):
        for filename, f in file_upload.value.items():
            save_path = os.path.join(upload_dir, filename)
            with open(save_path, "wb") as fh:
                fh.write(f["content"])
        refresh_file_dropdown()
        file_upload.value.clear()

    file_upload.observe(on_upload_change, names="value")

    # --- Output + Plot Button ---
    output = widgets.Output()
    plot_button = widgets.Button(description="Plot", button_style="success")

    def get_layout():
        layout = []
        for col in columns:
            col_layout = []
            for child in col.children:
                if isinstance(child, widgets.HBox) and len(child.children) == 2:
                    dd = child.children[0]
                    if dd.value:
                        col_layout.append(dd.value)
            if col_layout:
                layout.append(col_layout)
        return layout

    def on_plot_clicked(_):
        with output:
            clear_output()
            layout = get_layout()
            fname = None
            if file_dropdown.value and file_dropdown.value != "-- Select Recent File --":
                fname = os.path.join(upload_dir, file_dropdown.value)

            if fname and layout:
                plot_data_arrays(fname, layout)
            else:
                print("Please select a file and plot types.")

    plot_button.on_click(on_plot_clicked)

    # --- Save & Load Layouts ---
    layout_name_text = widgets.Text(placeholder="Layout name...")
    save_layout_btn = widgets.Button(description="Save Layout", button_style="success")

    def build_layout_options():
        opts = [("--- Default Layouts ---", None)]
        opts += [(f"  {f}", os.path.join(default_layout_dir, f)) for f in os.listdir(default_layout_dir) if f.endswith(".json")]
        opts += [("--- User Layouts ---", None)]
        opts += [(f"  {f}", os.path.join(user_layout_dir, f)) for f in os.listdir(user_layout_dir) if f.endswith(".json")]
        return opts

    load_layout_dd = widgets.Dropdown(options=build_layout_options())
    load_layout_btn = widgets.Button(description="Load Layout", button_style="info")

    def refresh_layout_dropdown():
        load_layout_dd.options = build_layout_options()

    def on_save_layout(_):
        name = layout_name_text.value.strip()
        if not name:
            return
        save_path = os.path.join(user_layout_dir, name + ".json")
        with open(save_path, "w") as f:
            json.dump(get_layout(), f, indent=2)
        refresh_layout_dropdown()
        layout_name_text.value = ""

    def on_load_layout(_):
        path = load_layout_dd.value
        if not path or not path.endswith(".json"):
            return
        with open(path, "r") as f:
            layout = json.load(f)

        # reset columns
        columns.clear()
        col_objs = []
        for col_values in layout:
            col_objs.append(make_column(col_values))
        columns.extend(col_objs)
        rebuild_columns_box()

    save_layout_btn.on_click(on_save_layout)
    load_layout_btn.on_click(on_load_layout)

    # --- Display UI ---
    ui = widgets.VBox([
        widgets.HBox([file_upload, file_dropdown]),
        widgets.HBox([layout_name_text, save_layout_btn, load_layout_dd, load_layout_btn]),
        columns_box,
        plot_button,
        output
    ])
    if interactive:
        display(ui)
    return ui

