import sys
import os
import geomag
import re
import shutil
import urllib.request
import urllib.parse
import xml.dom.minidom
import datetime

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import loadmat
from scipy.io import savemat
from scipy.interpolate import interp1d
import scipy.linalg as LA
import pandas as pd
import shutil
import h5py
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import bst_helper_functions.bst_att_est as bae
import simplekml

import sys
import bst_log_utils.log_utils as lu


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

def generic_plot(data,dep_var, indep_var = 'SYSTEM_TIME'):
  axbase = None
  if(isinstance(dep_var[0],list)):
    for var in dep_var:
      axbase = generic_figure(data,var,indep_var,axbase)
  else:
    generic_figure(data,dep_var,indep_var,axbase)

def generic_figure(data,dep_var, indep_var, axbase):
  plt.figure()
  N = len(dep_var)
  for idx,var in enumerate(dep_var):
    if axbase == None:
      axbase = plt.subplot(N,1,1)
      axbase.plot(data[indep_var], data[var])
    else:
      ax = plt.subplot(N,1,idx+1,sharex=axbase)
      ax.plot(data[indep_var], data[var])
    plt.ylabel(var)
    plt.grid()
  plt.xlabel(indep_var)
  return axbase

def filter_mhp_products(data):
  fs = 100
  fc = 5
  w = fc / (fs / 2)
  b, a = signal.butter(12, w)

  data['ALPHA'] = signal.filtfilt(b,a,data['ALPHA'], padlen=150)
  data['BETA'] = signal.filtfilt(b,a,data['BETA'], padlen=150)
  data['Q'] = signal.filtfilt(b,a,data['Q'], padlen=150)
  data['TAS'] = signal.filtfilt(b,a,data['TAS'], padlen=150)
  return data

def filter_dp(data,fs=100,fc=5):
  w = fc / (fs / 2)
  b, a = signal.butter(12, w)
  if isinstance(data, pd.DataFrame):
    data['DYNAMIC_PRESSURE_0'] = signal.filtfilt(b,a,data['DYNAMIC_PRESSURE_0'], padlen=150)
    data['DYNAMIC_PRESSURE_1'] = signal.filtfilt(b,a,data['DYNAMIC_PRESSURE_1'], padlen=150)
    data['DYNAMIC_PRESSURE_2'] = signal.filtfilt(b,a,data['DYNAMIC_PRESSURE_2'], padlen=150)
    data['DYNAMIC_PRESSURE_3'] = signal.filtfilt(b,a,data['DYNAMIC_PRESSURE_3'], padlen=150)
    data['DYNAMIC_PRESSURE_4'] = signal.filtfilt(b,a,data['DYNAMIC_PRESSURE_4'], padlen=150)
    return data
  else: # Assume mhp struct from mat file
    data['dynamic_pressure'][0][0][:,0] = signal.filtfilt(b,a,data['dynamic_pressure'][0][0][:,0], padlen=150)
    data['dynamic_pressure'][0][0][:,1] = signal.filtfilt(b,a,data['dynamic_pressure'][0][0][:,1], padlen=150)
    data['dynamic_pressure'][0][0][:,2] = signal.filtfilt(b,a,data['dynamic_pressure'][0][0][:,2], padlen=150)
    data['dynamic_pressure'][0][0][:,3] = signal.filtfilt(b,a,data['dynamic_pressure'][0][0][:,3], padlen=150)
    data['dynamic_pressure'][0][0][:,4] = signal.filtfilt(b,a,data['dynamic_pressure'][0][0][:,4], padlen=150)
    return data

def plot_wind(lat,lon,u,v,steps=50,mu_latlon=None):
  if mu_latlon is None:
    x,y = latlon2local(lat,lon)
  else:
    x,y = latlon2local(lat,lon,origin=mu_latlon)
  plt.plot(x,y,color='grey')
  idx = np.arange(0,len(u),steps)
  plt.quiver(x[idx],y[idx],v[idx],u[idx])
  plt.grid()

def plot_s0_met(fname,filter=False):

  if fname[-3:] == 'mat': # .mat file
    mhp = loadmat(fname)['mhp']
    tmhp = mhp['system_time'][0][0].flatten()

  if filter:
    mhp = filter_dp(mhp)
  tmhp /= 60
  plt.figure()
  N = 8
  idx=1

  ax = plt.subplot(N,1,idx)
  idx+=1
  ax.plot(tmhp, mhp['dynamic_pressure'][0][0][:,0],'.')
  plt.ylabel('Dynamic Center [Pa]');
  plt.grid()

  ax = plt.subplot(N,1,idx,sharex=ax)
  idx+=1
  ax.plot(tmhp, mhp['dynamic_pressure'][0][0][:,1],'.',label='1')
  ax.plot(tmhp, mhp['dynamic_pressure'][0][0][:,3],'.',label='3')
  plt.ylabel('Alpha Ports [Pa]');
  plt.legend()
  plt.grid()

  ax = plt.subplot(N,1,idx,sharex=ax)
  idx+=1
  ax.plot(tmhp, mhp['dynamic_pressure'][0][0][:,2],'.',label='2')
  ax.plot(tmhp, mhp['dynamic_pressure'][0][0][:,4],'.',label='4')
  plt.ylabel('Beta Ports [Pa]');
  plt.legend()
  plt.grid()

  ax = plt.subplot(N,1,idx,sharex=ax)
  idx+=1
  ax.plot(tmhp, mhp['static_pressure'][0][0],'.')
  plt.ylabel('Static Pressure [hPa]');
  plt.grid()

  ax = plt.subplot(N,1,idx,sharex=ax)
  idx+=1
  ax.plot(tmhp, mhp['air_temperature'][0][0],'.')
  plt.ylabel('Temp [C]');
  plt.grid()

  ax = plt.subplot(N,1,idx,sharex=ax)
  idx+=1
  ax.plot(tmhp, mhp['humidity'][0][0],'.')
  plt.ylabel('RH [%]')
  plt.grid()

  ax = plt.subplot(N,1,idx,sharex=ax)
  idx+=1
  ax.plot(tmhp, mhp['gyroscope'][0][0][:,0]*180/np.pi,'.',label='x')
  ax.plot(tmhp, mhp['gyroscope'][0][0][:,1]*180/np.pi,'.',label='y')
  ax.plot(tmhp, mhp['gyroscope'][0][0][:,2]*180/np.pi,'.',label='z')
  plt.ylabel('Gyro [deg/s]')
  plt.legend()
  plt.grid()

  ax = plt.subplot(N,1,idx,sharex=ax)
  idx+=1
  ax.plot(tmhp, mhp['accelerometer'][0][0][:,0]*9.81,'.',label='x')
  ax.plot(tmhp, mhp['accelerometer'][0][0][:,1]*9.81,'.',label='y')
  ax.plot(tmhp, mhp['accelerometer'][0][0][:,2]*9.81,'.',label='z')
  plt.ylabel('Acc [m/s/s]')
  plt.legend()
  plt.grid()

  plt.xlabel('Time [min]')

def plot_derived(df):
  generic_plot(df,['ALPHA','BETA','Q'], indep_var = 'DATA_PRODUCT_TIME')

def plot_raw_data(df):
  plotvars = [['VELOCITY_N','VELOCITY_E','VELOCITY_D'],['STATIC_PRESSURE','AIR_TEMPERATURE','HUMIDITY'],['ACCELEROMETER_X','ACCELEROMETER_Y','ACCELEROMETER_Z'],['GYROSCOPE_X','GYROSCOPE_Y','GYROSCOPE_Z'],['MAGNETOMETER_X','MAGNETOMETER_Y','MAGNETOMETER_Z'],['DYNAMIC_PRESSURE_0','DYNAMIC_PRESSURE_1','DYNAMIC_PRESSURE_2','DYNAMIC_PRESSURE_3','DYNAMIC_PRESSURE_4'],['ALPHA','BETA','Q']]
  generic_plot(df,plotvars, indep_var = 'IMU_TIME')

def wind_ws_dir_2_uv(wspd,wdir):
  theta = 3*np.pi/2 - wdir
  u = wspd*np.cos(theta)
  v = wspd*np.sin(theta)
  return u,v

def wind_uv_2_ws_dir(u,v):
  wspd = np.linalg.norm((np.transpose([u,v])),axis=1)
  #wdir = np.arctan2(v,u)
  wdir = np.arctan2(u,v) + np.pi
  return wspd,np.mod(wdir,2*np.pi)

def wind_from_tas_alpha_beta(tas,alpha,beta,vg_x,vg_y,vg_z,q):
  Va_b = body_frame_wind(tas,alpha,beta)
  return wind_from_vab_vg_q(Va_b,np.transpose([vg_x,vg_y,vg_z]),q)

def wind_from_vab_vg_q(Va_b,Vg,q):
  Va_w = bae.qrot_vec(q,Va_b)
  return Vg - Va_w


def body_frame_wind(tas,alpha,beta,sfix=-1):
  if isinstance(tas,float):
    Va_b = np.zeros(3)
    Va_b[0] = tas*np.cos(alpha)*np.cos(beta)
    Va_b[1] = sfix*tas*np.sin(beta)
    Va_b[2] = sfix*tas*np.sin(alpha)*np.cos(beta)
  else:
    Va_b = np.zeros((len(tas),3))
    for idx,(vtas,a,b) in enumerate(zip(tas,alpha,beta)):
      Va_b[idx,0] = vtas*np.cos(a)*np.cos(b)
      Va_b[idx,1] = sfix*vtas*np.sin(b)
      Va_b[idx,2] = sfix*vtas*np.sin(a)*np.cos(b)

      #D = np.sqrt(1+np.tan(a)*np.tan(a) + np.tan(b)*np.tan(b))
      #Va_b[idx,0] = vtas/D
      #Va_b[idx,1] = vtas*np.tan(b)/D
      #Va_b[idx,2] = vtas*np.tan(a)/D
  return Va_b

def compute_alpha_beta_q(dP0,dP1,dP2,dP3,dP4,param_file = 'mhp_coeff_2023_02_23.mat'):
    # Param files:
    #  - mhp_coeff_2020_01_06.mat - original one on older probe with bulbous body done at NOAA ATDD
    #  - mhp_coeff_2021_05_19.mat - updated one at ATDD with v3 of the probe with slender body
    #  - mhp_coeff_2021_12_01.mat - S0 cal from NOAA ATDD

    mhp_coeff = loadmat(param_file)
    DP = (dP1 +  dP2 +  dP3 +  dP4)/4
    k_alpha = np.divide((dP1 - dP3) , (dP0 - DP))
    k_beta  = np.divide((dP2 - dP4) , (dP0 - DP))

    alpha = np.zeros(np.size(dP0))
    beta = np.zeros(np.size(dP0))
    q = np.zeros(np.size(dP0))
    order = int(np.sqrt(np.size(mhp_coeff['c_alpha']))-1)

    for i in range(len(DP)):
        k = mhp_meas_vector(k_alpha[i], k_beta[i],order+1)
        alpha[i] = np.dot(k, mhp_coeff['c_alpha'])
        beta[i] = np.dot(k, mhp_coeff['c_beta'])
        k_q = np.dot(k, mhp_coeff['c_q'])
        if(alpha[i] > np.pi/4):
          alpha[i] = np.pi/4
        if(beta[i] > np.pi/4):
          beta[i] = np.pi/4
        if(alpha[i] < -np.pi/4):
          alpha[i] = -np.pi/4
        if(beta[i] < -np.pi/4):
          beta[i] = -np.pi/4
        if(k_q >  0):
          k_q = 0
        if(k_q <  -1.0):
          k_q = -1.0

        q[i] = dP0[i] - k_q * (dP0[i] - DP[i])

    return alpha,beta,q

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

def compute_ias_tas(q,Ta,Ps,RH):
  rho_0 = 1.06
  ias = np.sign(q) * np.sqrt(2*abs(q)/rho_0)

  rho = compute_air_density(Ta,Ps,RH)

  tas = np.sign(q) * np.sqrt(2*abs(q)/rho)
  return ias,tas

def compute_data_products(data,param_file = 'mhp_coeff_2021_05_19.mat',S0_gcs_log = False):
  if S0_gcs_log:
    uas = loadmat(data)['uas']
    Ta = uas['user_payload'][0][0]['air_temperature'][0][0].flatten()
    RH = uas['user_payload'][0][0]['humidity'][0][0].flatten()
    idx = np.where(((Ta != 0) & (RH > 0) & (RH <= 100)))
    Ta = Ta[idx]
    RH = RH[idx]

    dP0 = uas['user_payload'][0][0]['dynamic_pressure'][0][0][idx,0].flatten()
    dP1 = uas['user_payload'][0][0]['dynamic_pressure'][0][0][idx,1].flatten()
    dP2 = uas['user_payload'][0][0]['dynamic_pressure'][0][0][idx,2].flatten()
    dP3 = uas['user_payload'][0][0]['dynamic_pressure'][0][0][idx,3].flatten()
    dP4 = uas['user_payload'][0][0]['dynamic_pressure'][0][0][idx,4].flatten()
    Ps = uas['user_payload'][0][0]['static_pressure'][0][0][idx].flatten()*100
    ts = uas['user_payload'][0][0]['ts'][0][0][idx].flatten()
  elif isinstance(data, pd.DataFrame):
    dP0 = data['DYNAMIC_PRESSURE_0'].to_numpy()
    dP1 = data['DYNAMIC_PRESSURE_1'].to_numpy()
    dP2 = data['DYNAMIC_PRESSURE_2'].to_numpy()
    dP3 = data['DYNAMIC_PRESSURE_3'].to_numpy()
    dP4 = data['DYNAMIC_PRESSURE_4'].to_numpy()
    Ta  = data['AIR_TEMPERATURE'].to_numpy()
    Ps  = data['STATIC_PRESSURE'].to_numpy()
    RH  = data['HUMIDITY'].to_numpy()
    ts  = data['DYNAMIC_PRESSURE_TIME_0'].to_numpy()

  elif data[-3:] == 'mat': # .mat file
    mhp = loadmat(data)['mhp']
    Ps  = np.ndarray.flatten(mhp['static_pressure'][0][0])*100
    idx = np.where(Ps > 0)
    Ps = Ps[idx]
    dP0 = mhp['dynamic_pressure'][0][0][idx,0].flatten()
    dP1 = mhp['dynamic_pressure'][0][0][idx,1].flatten()
    dP2 = mhp['dynamic_pressure'][0][0][idx,2].flatten()
    dP3 = mhp['dynamic_pressure'][0][0][idx,3].flatten()
    dP4 = mhp['dynamic_pressure'][0][0][idx,4].flatten()
    Ta  = np.ndarray.flatten(mhp['air_temperature'][0][0][idx])
    Ps  = np.ndarray.flatten(mhp['static_pressure'][0][0][idx])
    RH  = np.ndarray.flatten(mhp['humidity'][0][0][idx])
    ts  = np.ndarray.flatten(mhp['system_time'][0][0][idx])
  elif data[-3:] == '.nc': # netCDF file
    hf = h5py.File(data,'r')
    ts = hf['SENSORS_MHP_SENSORS_time'][:]
    mhp = hf['SENSORS_MHP_SENSORS_vec'][:]
    Ps  = mhp['static_pressure']
    idx = np.where(Ps > 0)
    Ps = Ps[idx]

    dP0 = mhp['dynamic_pressure_0'][idx]
    dP1 = mhp['dynamic_pressure_1'][idx]
    dP2 = mhp['dynamic_pressure_2'][idx]
    dP3 = mhp['dynamic_pressure_3'][idx]
    dP4 = mhp['dynamic_pressure_4'][idx]
    Ta  = mhp['air_temperature'][idx]
    RH  = mhp['humidity'][idx]
    ts = ts[idx]

  alpha,beta,q = compute_alpha_beta_q(dP0,dP1,dP2,dP3,dP4,param_file = param_file)
  ias,tas = compute_ias_tas(q,Ta,Ps,RH)

  # FIXME - add wind estimator function here
  u = 0*tas
  v = 0*tas
  w = 0*tas

  return alpha,beta,q,ias,tas,u,v,w,ts


def mhp_meas_vector(k_alpha, k_beta, order):
    col = 0
    k = np.zeros(order**2)
    for i in range(order):
        for j in range(order):
            k[col] = k_alpha**i * k_beta**j
            col = col+1
    return k

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
    elapsed = datetime.timedelta(days=(gpsweek*7),seconds=(gpsseconds))
    return elapsed.total_seconds() + gps2unix_ss

def weeksecondstoutc(gpsweek,gpsseconds,leapseconds=18,datetimeformat="%Y-%m-%d %H:%M:%S"):
    epoch = datetime.datetime.strptime("1980-01-06 00:00:00","%Y-%m-%d %H:%M:%S")
    elapsed = datetime.timedelta(days=(gpsweek*7),seconds=(gpsseconds-leapseconds))
    return datetime.datetime.strftime(epoch + elapsed,datetimeformat)

def get_ap_basetime(fname):
  if fname[-3:] == 'mat': # .mat file
    gps2 = loadmat(fname)['gps']
    gps = {'system_time':gps2['system_time'][0][0], 'week':gps2['week'][0][0], 'hour':gps2['hour'][0][0], 'minute':gps2['minute'][0][0], 'seconds':gps2['seconds'][0][0]}
  elif fname[-3:] == '.nc': # netCDF file
    hf = h5py.File(fname, 'r')
    gps = hf['/SENSORS_GPS_vec'][:]

  idx = np.where(gps['week'] > 0)[0][0]
  base_time = weekseconds2unix(float(gps['week'][idx]),float(gps['hour'][idx])*3600 + float(gps['minute'][idx])*60 + float(gps['seconds'][idx]))
  base_time -= gps['system_time'][idx]
  return base_time

def get_ground(fname):
  if fname[-3:] == 'mat': # AP File
    command = loadmat(fname)['command']
    tcommand = command['system_time'][0][0].flatten()
    command = {'id':command['id'][0][0].flatten(),'value':command['value'][0][0].flatten()}

    state = loadmat(fname)['state']
    tstate = state['system_time'][0][0].flatten()
    state = {'agl':state['agl'][0][0].flatten(),'altitude':state['altitude'][0][0].flatten()}
  elif fname[-3:] == '.nc': # netCDF file
    hf = h5py.File(fname, 'r')
    command = hf['/CONTROL_COMMAND_vec'][:]
    tcommand = hf['/CONTROL_COMMAND_time'][:]
    tstate = hf['/STATE_STATE_time'][:]
    state = hf['/STATE_STATE_vec'][:]

  idx = np.where(command['id'] == 1)[0]
  t_mode = tcommand[idx]
  mode = command['value'][idx]

  CLIMBOUT=4
  tclimb = t_mode[np.where(mode == CLIMBOUT)[0][0]]
  idx = np.where(tstate>=tclimb)[0][0]
  return state['altitude'][idx] - state['agl'][idx]

def flighttimes(fname):
  if fname[-3:] == 'mat': # AP File
    command2 = loadmat(fname)['command']
    command = {'id':command2['id'][0][0],'value':command2['value'][0][0]}
    tcommand = command2['system_time'][0][0]
  elif fname[-3:] == '.nc': # netCDF file
    hf = h5py.File(fname, 'r')
    command = hf['/CONTROL_COMMAND_vec'][:]
    tcommand = hf['/CONTROL_COMMAND_time'][:]

  ind = np.where(command['id'] == 1)
  t_mode = tcommand[ind]
  mode = command['value'][ind]

  CLIMBOUT=4
  # If no climbout, use first instance of flying
  if np.size(np.where(mode == CLIMBOUT)[0]) == 0:
    CLIMBOUT=6

  if np.max(mode) < 9:
    LANDED = 7
  else:
    LANDED = 9

  counter = 0
  t_start = np.empty((0,0))
  t_stop = np.empty((0,0))
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
#print('WARNING: no land time for flight %d'%(counter+1))
              t_start = np.append(t_start, t_mode[in_launch])
              t_stop = np.append(t_stop, t_mode[-1])
              break
      else:
          break

  return t_start,t_stop

def get_mag_dec(latitude,longitude):
  return geomag.declination(latitude,longitude)*np.pi/180

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def s02csv(matfile, param_file = 'mhp_coeff_2021_12_01.mat'):
    # Note, due to loadmat limitations, the path must be absolute.

    # The header for our CSV files (including misspellings)
    col1=['%STATIC_PRESSURE_TIME', 'STATIC_PRESSURE', 'MAGNETOMETER_TIME','MAGNETOMETER_X', 'MAGNETOMETER_Y', 'MAGNETOMETER_Z', 'IMU_TIME','ACCELEROMETER_X', 'ACCELEROMETER_Y', 'ACCELEROMETER_Z', 'GYROSCOPE_X','GYROSCOPE_Y', 'GYROSCOPE_Z', 'DYNAMIC_PRESSURE_TIME_0','DYNAMIC_PRESSURE_0', 'DYNAMIC_PRESSURE_TIME_1', 'DYNAMIC_PRESSURE_1','DYNAMIC_PRESSURE_TIME_2', 'DYNAMIC_PRESSURE_2','DYNAMIC_PRESSURE_TIME_3', 'DYNAMIC_PRESSURE_3','DYNAMIC_PRESSURE_TIME_4', 'DYNAMIC_PRESSURE_4', 'AIR_TEMPERATURE_TIME','AIR_TEMPERATURE', 'HUMIDITY_TIME', 'HUMIDITY', 'DATA_PRODUCT_TIME']
    col2=['%STATIC_PRESSURE_TIME', 'STATIC_PRESSURE', 'MAGNETOMETER_TIME','MAGNETOMETER_X', 'MAGNETOMETER_Y', 'MAGNETOMETER_Z', 'IMU_TIME','ACCELEROMETER_X', 'ACCELEROMETER_Y', 'ACCELEROMETER_Z', 'GYROSCOPE_X','GYROSCOPE_Y', 'GYROSCOPE_Z', 'DYNAMIC_PRESSURE_TIME_0','DYNAMIC_PRESSURE_0', 'DYNAMIC_PRESSURE_TIME_1', 'DYNAMIC_PRESSURE_1','DYNAMIC_PRESSURE_TIME_2', 'DYNAMIC_PRESSURE_2','DYNAMIC_PRESSURE_TIME_3', 'DYNAMIC_PRESSURE_3','DYNAMIC_PRESSURE_TIME_4', 'DYNAMIC_PRESSURE_4', 'AIR_TEMPERATURE_TIME','AIR_TEMPERATURE', 'HUMIDITY_TIME', 'HUMIDITY', 'DATA_PRODUCT_TIME','ALPHA', 'BETA', 'Q', 'TAS', 'IAS', 'U', 'V', 'W', 'Q_0', 'Q_1', 'Q_2','Q_3', 'GPS_TIME', 'GPS_WEEK', 'HOUR', 'MINUTE', 'SECONDS', 'LATTIUDE','LONGITUDE', 'ALTITUDE', 'VELOCITY_N', 'VELOCITY_E', 'VELOCITY_D','PDOP']

    mhp = loadmat(matfile)['mhp']
    mag = loadmat(matfile)['mag']
    gps = loadmat(matfile)['gps']
    state = loadmat(matfile)['state']

    # Interpolate all variables to the MHP system time. Not the best, but good enough for now
    ts = np.array(mhp['system_time'][0][0])

    mag_x = interp1d(np.squeeze(mag['system_time'][0][0]), np.squeeze(mag['x'][0][0]),fill_value='extrapolate')(ts)
    mag_y = interp1d(np.squeeze(mag['system_time'][0][0]), np.squeeze(mag['y'][0][0]),fill_value='extrapolate')(ts)
    mag_z = interp1d(np.squeeze(mag['system_time'][0][0]), np.squeeze(mag['z'][0][0]),fill_value='extrapolate')(ts)

    acc_x = np.reshape(mhp['accelerometer'][0][0][:,0],(len(ts),1))
    acc_y = np.reshape(mhp['accelerometer'][0][0][:,1],(len(ts),1))
    acc_z = np.reshape(mhp['accelerometer'][0][0][:,2],(len(ts),1))
    gyr_x = np.reshape(mhp['gyroscope'][0][0][:,0],(len(ts),1))
    gyr_y = np.reshape(mhp['gyroscope'][0][0][:,1],(len(ts),1))
    gyr_z = np.reshape(mhp['gyroscope'][0][0][:,2],(len(ts),1))

    dp0 = np.reshape(mhp['dynamic_pressure'][0][0][:,0],(len(ts),1))
    dp1 = np.reshape(mhp['dynamic_pressure'][0][0][:,1],(len(ts),1))
    dp2 = np.reshape(mhp['dynamic_pressure'][0][0][:,2],(len(ts),1))
    dp3 = np.reshape(mhp['dynamic_pressure'][0][0][:,3],(len(ts),1))
    dp4 = np.reshape(mhp['dynamic_pressure'][0][0][:,4],(len(ts),1))

    # Temporarily make a dataframe to use the processing function
    df = pd.DataFrame(np.concatenate((ts,mhp['static_pressure'][0][0],ts,mag_x,mag_y,mag_z,ts,acc_x,acc_y,acc_z,gyr_x,gyr_y,gyr_z,ts,dp0,ts,dp1,ts,dp2,ts,dp3,ts,dp4,ts,mhp['air_temperature'][0][0],ts,mhp['humidity'][0][0],ts),axis=1),columns=col1)

    alpha,beta,q,ias,tas,u,v,w = compute_data_products(df,param_file = param_file)
    alpha = np.reshape(alpha,(len(ts),1))
    beta = np.reshape(beta,(len(ts),1))
    q = np.reshape(q,(len(ts),1))
    ias = np.reshape(ias,(len(ts),1))
    tas = np.reshape(tas,(len(ts),1))
    u = np.reshape(u,(len(ts),1))
    v = np.reshape(v,(len(ts),1))
    w = np.reshape(w,(len(ts),1))

    N = len(state['system_time'][0][0])
    q0 = interp1d(np.squeeze(state['system_time'][0][0]), np.squeeze(np.reshape(state['q'][0][0][:,0],(N,1))), fill_value='extrapolate')(ts)
    q1 = interp1d(np.squeeze(state['system_time'][0][0]), np.squeeze(np.reshape(state['q'][0][0][:,1],(N,1))), fill_value='extrapolate')(ts)
    q2 = interp1d(np.squeeze(state['system_time'][0][0]), np.squeeze(np.reshape(state['q'][0][0][:,2],(N,1))), fill_value='extrapolate')(ts)
    q3 = interp1d(np.squeeze(state['system_time'][0][0]), np.squeeze(np.reshape(state['q'][0][0][:,3],(N,1))), fill_value='extrapolate')(ts)

    gps_week = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['week'][0][0]),fill_value='extrapolate')(ts)
    gps_hour = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['hour'][0][0]),fill_value='extrapolate')(ts)
    gps_minute = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['minute'][0][0]),fill_value='extrapolate')(ts)
    gps_seconds = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['seconds'][0][0]),fill_value='extrapolate')(ts)
    gps_lattiude = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['latitude'][0][0]),fill_value='extrapolate')(ts)
    gps_longitude = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['longitude'][0][0]),fill_value='extrapolate')(ts)
    gps_altitude = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['altitude'][0][0]),fill_value='extrapolate')(ts)
    gps_velocity_n = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['velocity'][0][0]['x'][0][0]),fill_value='extrapolate')(ts)
    gps_velocity_e = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['velocity'][0][0]['y'][0][0]),fill_value='extrapolate')(ts)
    gps_velocity_d = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['velocity'][0][0]['z'][0][0]),fill_value='extrapolate')(ts)
    gps_pdop = interp1d(np.squeeze(gps['system_time'][0][0]), np.squeeze(gps['pdop'][0][0]),fill_value='extrapolate')(ts)

    df = pd.DataFrame(np.concatenate((ts,mhp['static_pressure'][0][0],ts,mag_x,mag_y,mag_z,ts,acc_x,acc_y,acc_z,gyr_x,gyr_y,gyr_z,ts,dp0,ts,dp1,ts,dp2,ts,dp3,ts,dp4,ts,mhp['air_temperature'][0][0],ts,mhp['humidity'][0][0],ts,alpha,beta,q,ias,tas,u,v,w,q0,q1,q2,q3,ts,gps_week,gps_hour,gps_minute,gps_seconds,gps_lattiude,gps_longitude,gps_altitude,gps_velocity_n,gps_velocity_e,gps_velocity_d,gps_pdop),axis=1),columns=col2)

    print('Saving AP mat file to: ',matfile[:-3]+'csv')
    df.to_csv(matfile[:-3]+'csv',index=False,na_rep='nan')

def get_time_offset(df):
  ind = np.where(df['GPS_WEEK'] == np.max(df['GPS_WEEK']))[0][0]

  return (df['HOUR'][ind]*3600 + df['MINUTE'][ind]*60 + df['SECONDS'][ind]) - df['GPS_TIME'][ind]

def get_estimator_data(fname, use_mhp_struct = False):
  if fname[-3:] == 'mat': # AP File
    gps = loadmat(fname)['gps']
    ind = np.where(gps['pdop'][0][0] < 2)
    mean_lat = np.mean(gps['latitude'][0][0][ind])
    mean_lon = np.mean(gps['longitude'][0][0][ind])

    if use_mhp_struct:
      mhp = loadmat(fname)['mhp']

      ts = np.squeeze(mhp['system_time'][0][0])
      ax = -np.squeeze(mhp['accelerometer'][0][0][:,0])*9.8
      ay = -np.squeeze(mhp['accelerometer'][0][0][:,1])*9.8
      az = -np.squeeze(mhp['accelerometer'][0][0][:,2])*9.8

      gx = np.squeeze(mhp['gyroscope'][0][0][:,0])
      gy = np.squeeze(mhp['gyroscope'][0][0][:,1])
      gz = np.squeeze(mhp['gyroscope'][0][0][:,2])

    else:
      acc = loadmat(fname)['acc']
      gyr = loadmat(fname)['gyr']
      ts = np.squeeze(gyr['system_time'][0][0])

      ax = -interp1d(np.squeeze(acc['system_time'][0][0]), np.squeeze(acc['x'][0][0]),fill_value='extrapolate')(ts)
      ay = -interp1d(np.squeeze(acc['system_time'][0][0]), np.squeeze(acc['y'][0][0]),fill_value='extrapolate')(ts)
      az = -interp1d(np.squeeze(acc['system_time'][0][0]), np.squeeze(acc['z'][0][0]),fill_value='extrapolate')(ts)

      gx = interp1d(np.squeeze(gyr['system_time'][0][0]), np.squeeze(gyr['x'][0][0]),fill_value='extrapolate')(ts)
      gy = interp1d(np.squeeze(gyr['system_time'][0][0]), np.squeeze(gyr['y'][0][0]),fill_value='extrapolate')(ts)
      gz = interp1d(np.squeeze(gyr['system_time'][0][0]), np.squeeze(gyr['z'][0][0]),fill_value='extrapolate')(ts)

    # Add the mags
    mag = loadmat(fname)['mag']
    mx = interp1d(np.squeeze(mag['system_time'][0][0]), np.squeeze(mag['x'][0][0]),fill_value='extrapolate')(ts)
    my = interp1d(np.squeeze(mag['system_time'][0][0]), np.squeeze(mag['y'][0][0]),fill_value='extrapolate')(ts)
    mz = interp1d(np.squeeze(mag['system_time'][0][0]), np.squeeze(mag['z'][0][0]),fill_value='extrapolate')(ts)

  elif fname[-3:] == 'csv': # MHP File

    data = pd.read_csv(fname)
    ind = np.squeeze(np.where( (data['PDOP'].values < 3) & (data['PDOP'].values > 0)))
    mean_lat = np.mean(data['LATITUDE'][ind])
    mean_lon = np.mean(data['LONGITUDE'][ind])

    ts = np.squeeze(data['IMU_TIME'].values)
    ind = np.where(ts>10)
    ts = ts[ind]
    gx = np.squeeze(data['GYROSCOPE_X'].values[ind])
    gy = np.squeeze(data['GYROSCOPE_Y'].values[ind])
    gz = np.squeeze(data['GYROSCOPE_Z'].values[ind])

    ax = -np.squeeze(data['ACCELEROMETER_X'].values[ind])*9.8
    ay = -np.squeeze(data['ACCELEROMETER_Y'].values[ind])*9.8
    az = -np.squeeze(data['ACCELEROMETER_Z'].values[ind])*9.8

    mx = np.squeeze(data['MAGNETOMETER_X'].values[ind])
    my = np.squeeze(data['MAGNETOMETER_Y'].values[ind])
    mz = np.squeeze(data['MAGNETOMETER_Z'].values[ind])


  mag_dec = get_mag_dec(mean_lat,mean_lon)
  if np.isnan(mag_dec):
    mag_dec = 0
  qdec = [np.cos(mag_dec/2),0,0,np.sin(mag_dec/2)]

  gyr_data = np.transpose(np.stack([gx,gy,gz]))
  acc_data = np.transpose(np.stack([ax,ay,az]))
  mag_data = np.transpose(np.stack([mx,my,mz]))

  return (ts,gyr_data,acc_data,mag_data,qdec)


def get_log_command(fname):

  hf = h5py.File(fname, 'r')
  tcommand = hf['/CONTROL_COMMAND_time'][:]
  command = hf['/CONTROL_COMMAND_vec'][:]

  cmd_vars = [
  'AUTOPILOT_MODE',
  'FLIGHT_MODE',
  'LANDING_MODE',
  'ALT_MODE',
  'LAT_MODE',
  'NAV_MODE',
  'ENGINE_KILL',
  'FLIGHT_TERMINATE',
  'ABORT',
  'WAYPOINT',
  'TURN_RATE',
  'LAUNCH',
  'LAND',
  'ROLL',
  'PITCH',
  'YAW',
  'WPT_ALT',
  'ROLL_RATE',
  'PITCH_RATE',
  'YAW_RATE',
  'ALTITUDE',
  'VRATE',
  'DOWNLOAD_LOG',
  'TRIGGER_PAYLOAD',
  'TECS_MODE',
  'SPEED',
  'VELC_OR_TRIMS',
  'X_POS',
  'Y_POS',
  'X_VEL',
  'Y_VEL',
  'THRUST',
  'MOMENT_X',
  'MOMENT_Y',
  'MOMENT_Z',
  'PAYLOAD_CONTROL',
  'LOOK_AT',
  'INVALID',
  ]

  cmd = {}
  for idx,var in enumerate(cmd_vars):
    idx = np.where(command['id'] == idx)
    cmd['t_'+var] = tcommand[idx]
    cmd[var] = command['value'][idx]
  return cmd

def scan_logs(dir_path):
  fnames = []
  for file in os.listdir(dir_path):
    # check only text files
    if file.endswith('.mat'):
      fnames.append(file)
    if file.endswith('.nc'):
      fnames.append(file)

  fnames = sorted(fnames)
  for fname in fnames:
    print_info_aplog(dir_path+fname)

def get_info_aplog(fname):
  if fname[-3:] == 'mat': # AP File
    sys_init = loadmat(fname)['sys_init']
    sys_init = {'name':sys_init['name'][0][0].flatten(),
                'sw_rev':sys_init['sw_rev'][0][0].flatten(),
                'hw_rev':sys_init['hw_rev'][0][0].flatten(),
                'svn_rev':sys_init['svn_rev'][0][0].flatten(),
                'comms_rev':sys_init['comms_rev'][0][0].flatten(),
                'serial_num':sys_init['serial_num'][0][0].flatten(),
               }
  elif fname[-3:] == '.nc': # netCDF file
    hf = h5py.File(fname, 'r')
    sys_init = hf['/SYSTEM_INITIALIZE_vec'][:]

  if sys_init['name'].dtype == 'S1':
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
    ac_num = int(name[2:6])

  sw_rev = sys_init['sw_rev'][-1]
  hw_rev = sys_init['hw_rev'][-1]
  svn_rev = hex(sys_init['svn_rev'][-1])
  comms_rev = sys_init['comms_rev'][-1]
  serial_num = hex(sys_init['serial_num'][-1])

  tstart,tstop = flighttimes(fname)
  num_flights = len(tstart)
  tof = np.sum(tstop-tstart)
  return ac_type,ac_num,serial_num,num_flights,tof,sw_rev,hw_rev,svn_rev,comms_rev

def print_info_aplog(fname):

  print(os.path.basename(fname))
  ac_type,ac_num,serial_num,num_flights,tof,sw_rev,hw_rev,svn_rev,comms_rev = get_info_aplog(fname)
  print('\tAircraft: %s-%i'%(ac_type,ac_num))
  print('\tsw_rev: %s'%sw_rev)
  print('\thw_rev: %s'%hw_rev)
  print('\tsvn_rev: %s'%svn_rev)
  print('\tcomms_rev: %s'%comms_rev)
  print('\tserial_num: %s'%serial_num)
  print('\tDate/time: '+get_datetime_aplog(fname))
  tstart,tstop = flighttimes(fname)
  print('\tFlights (%i): '%num_flights)
  k=1
  for start,stop in zip(tstart,tstop):
    print('\t\t%i. '%k+get_datetime_aplog(fname,start)+' -> '+get_datetime_aplog(fname,stop)+ ' TOF: %.1f min'%((stop-start)/60))
    k += 1

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
  if fname[-3:] == 'mat': # AP File
    gps2 = loadmat(fname)['gps']
    gps = {'system_time':gps2['system_time'][0][0].flatten(), 'week':gps2['week'][0][0].flatten(), 'hour':gps2['hour'][0][0].flatten(), 'minute':gps2['minute'][0][0].flatten(), 'seconds':gps2['seconds'][0][0].flatten()}
  elif fname[-3:] == '.nc': # netCDF file
    hf = h5py.File(fname, 'r')
    gps = hf['/SENSORS_GPS_vec'][:]

  if np.sum(gps['week']) == 0:
    return 'nan'

  t_off = 0
  if t_start > 0:
    ind = np.where(gps['system_time'] > t_start)[0]
  else:
    ind = np.where(gps['week'] > 0)[0]
    t_off = gps['system_time'][ind][0]
  if len(ind) == 0:
    return 'nan'
  else:
    return weeksecondstoutc(float(gps['week'][ind][0]),float(gps['hour'][ind][0])*3600 + float(gps['minute'][ind][0])*60 + float(gps['seconds'][ind][0]) - t_off)


def get_datetime_mhp(df):
    ind = np.where(df['GPS_WEEK'] == np.max(df['GPS_WEEK']))[0][0]
    return weeksecondstoutc(df['GPS_WEEK'][ind],df['HOUR'][ind]*3600 + df['MINUTE'][ind]*60 + df['SECONDS'][ind])

def print_datetime_mhp(df):
    print('UTC of Log: '+get_datetime_mhp(df))

def shift_times(df, t_shift):
    df['%STATIC_PRESSURE_TIME']   = df['%STATIC_PRESSURE_TIME'] + t_shift
    df['MAGNETOMETER_TIME']       = df['MAGNETOMETER_TIME'] + t_shift
    df['IMU_TIME']                = df['IMU_TIME'] + t_shift
    df['DYNAMIC_PRESSURE_TIME_0'] = df['DYNAMIC_PRESSURE_TIME_0'] + t_shift
    df['DYNAMIC_PRESSURE_TIME_1'] = df['DYNAMIC_PRESSURE_TIME_1'] + t_shift
    df['DYNAMIC_PRESSURE_TIME_2'] = df['DYNAMIC_PRESSURE_TIME_2'] + t_shift
    df['DYNAMIC_PRESSURE_TIME_3'] = df['DYNAMIC_PRESSURE_TIME_3'] + t_shift
    df['DYNAMIC_PRESSURE_TIME_4'] = df['DYNAMIC_PRESSURE_TIME_4'] + t_shift
    df['AIR_TEMPERATURE_TIME']    = df['AIR_TEMPERATURE_TIME'] + t_shift
    df['HUMIDITY_TIME']           = df['HUMIDITY_TIME'] + t_shift
    df['DATA_PRODUCT_TIME']       = df['DATA_PRODUCT_TIME'] + t_shift
    df['GPS_TIME']                = df['GPS_TIME'] + t_shift

    return df

def zero_pressures(df,t_start=0,t_stop=3):
    ind = np.where((df['DYNAMIC_PRESSURE_TIME_0'] >= t_start) & (df['DYNAMIC_PRESSURE_TIME_0'] <= t_stop))[0]
    print('Zeroes were (%.3f,%.3f,%.3f,%.3f,%.3f) Pa'%(np.mean(df['DYNAMIC_PRESSURE_0'][ind]),np.mean(df['DYNAMIC_PRESSURE_1'][ind]),np.mean(df['DYNAMIC_PRESSURE_2'][ind]),np.mean(df['DYNAMIC_PRESSURE_3'][ind]),np.mean(df['DYNAMIC_PRESSURE_4'][ind])))
    df['DYNAMIC_PRESSURE_0'] = df['DYNAMIC_PRESSURE_0'] - np.mean(df['DYNAMIC_PRESSURE_0'][ind])
    df['DYNAMIC_PRESSURE_1'] = df['DYNAMIC_PRESSURE_1'] - np.mean(df['DYNAMIC_PRESSURE_1'][ind])
    df['DYNAMIC_PRESSURE_2'] = df['DYNAMIC_PRESSURE_2'] - np.mean(df['DYNAMIC_PRESSURE_2'][ind])
    df['DYNAMIC_PRESSURE_3'] = df['DYNAMIC_PRESSURE_3'] - np.mean(df['DYNAMIC_PRESSURE_3'][ind])
    df['DYNAMIC_PRESSURE_4'] = df['DYNAMIC_PRESSURE_4'] - np.mean(df['DYNAMIC_PRESSURE_4'][ind])

    return df

def recompute_data_product(df):
    alpha,beta,q,ias,tas,u,v,w = compute_data_products(df)
    df['ALPHA'] = alpha
    df['BETA'] = beta
    df['Q'] = q
    df['IAS'] = ias
    df['TAS'] = tas
    df['U'] = u
    df['V'] = v
    df['W'] = w
    return df

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


def getDensityAlt(rho):
		return (44.3308 - 42.2665 * rho ** 0.234969) * 1000

def get_cruise_power(fname):
  hf = h5py.File(fname, 'r')
  sys_status = hf['/SYSTEM_HEALTH_AND_STATUS_vec'][:]
  t_sys_status = hf['/SYSTEM_HEALTH_AND_STATUS_time'][:]
  start,stop = flighttimes(fname)
  ind = get_time_indeces(t_sys_status,start,stop)
  return np.mean(sys_status['batt_voltage'][ind] * sys_status['batt_current'][ind])

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

def get_useful_ap_stats(fname):

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

  start,stop = flighttimes(fname)

  P = get_cruise_power(fname)
  hf = h5py.File(fname, 'r')
  gps = hf['/SENSORS_GPS_vec'][:]
  state = hf['/STATE_STATE_vec'][:]
  stat_p = hf['/SENSORS_STATIC_PRESSURE_vec'][:]

  ind = get_time_indeces(state['system_time'],start,stop)

  max_h = np.max(state['altitude'][ind])
  min_h = np.min(state['altitude'][ind])


  if 'ias' in state.dtype.names:
    max_ias = np.max(state['ias'][ind])

  if 'wind_x' in state.dtype.names:
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
  max_vz = np.max(gps['velocity_z'][ind])
  min_vz = np.min(gps['velocity_z'][ind])

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

def kolm_fit1(ts,u):
  fs = 1/np.mean(np.diff(ts))
  f, Pxx_den = signal.periodogram(u,fs)
  Pxx_den = Pxx_den[f > 0]
  f = f[f > 0]
  plt.loglog(f, Pxx_den,'.',label='Data')
  f_slope = np.linspace(np.min(f[1:]),np.max(f[1:]),num=100)
  plt.loglog(f_slope, (50*f_slope) **(-5/3),label='-5/3 Kolmogorovs Fit')
  plt.xlabel('frequency [Hz]')
  plt.ylabel('PSD [V**2/Hz]')
  plt.grid()

def kolm_fit(ts,u,v,w):

  plt.subplot(1,3,1)
  kolm_fit1(ts,u)
  plt.title('U-Wind')

  plt.subplot(1,3,2)
  kolm_fit1(ts,v)
  plt.title('V-Wind')

  plt.subplot(1,3,3)
  kolm_fit1(ts,w)
  plt.title('W-Wind')

import xml.etree.ElementTree as ET

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

def update_wind_aplog(fname,twind,W):

  outfile = fname[:-4] + '_wind' + fname[-4:]
  if fname[-3:] == 'mat': # .mat file
    data = loadmat(fname)

    u = interp1d(twind,W[:,0],fill_value='extrapolate')(data['state']['system_time'][0][0])
    v = interp1d(twind,W[:,1],fill_value='extrapolate')(data['state']['system_time'][0][0])
    w = interp1d(twind,W[:,2],fill_value='extrapolate')(data['state']['system_time'][0][0])
    data['state']['wind'][0][0][:,0] = u.flatten()
    data['state']['wind'][0][0][:,1] = v.flatten()
    data['state']['wind'][0][0][:,2] = w.flatten()

    # Save to file
    savemat(outfile,data)
  else:
    print('ERROR: Not a valid filetype: %s' % fname)

  print('Saving with new mag calibration to: %s' % outfile)
  return outfile

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
                    'ERROR_RESET_IN_FLIGHT'],
             'code':2**np.arange(0,31)}

  err_arr = []
  for err,code in zip(err_vec['err'],err_vec['code']):
    if err_code & code == code:
      err_arr.append(err)
  if len(err_arr) == 0:
    err_arr = ['ERROR_NO_ERROR']
  return err_arr


def print_error_sequence(fname,inflight=True):
  if fname[-3:] == 'mat': # .mat file
    sys_status = loadmat(fname)['sys_status']
    tsys_status = sys_status['system_time'][0][0].flatten()
    err_codes = sys_status['error_code'][0][0].flatten()
  elif fname[-3:] == '.nc': # netCDF file
    hf = h5py.File(fname, 'r')
    sys_status = hf['/SYSTEM_HEALTH_AND_STATUS_vec'][:]
    tsys_status = hf['/SYSTEM_HEALTH_AND_STATUS_time'][:]
    err_codes = sys_status['error_code']

  if inflight:
    start,stop = flighttimes(fname)
    idx = get_time_indeces(tsys_status,start,stop)
    tsys_status = tsys_status[idx]
    err_codes = err_codes[idx]

  idx = np.where(err_codes[:-1] != err_codes[1:])[0]

  print('t=%.2fs'%tsys_status[0],decode_ap_err(err_codes[0]))
  for i in idx:
    print('t=%.2fs'%tsys_status[i],decode_ap_err(err_codes[i+1]))

def filter_abq(alpha,beta,q):
    print('Filtering alpha, beta, q')
    fs = 100
    fc = 5
    w = fc / (fs / 2)
    b, a = signal.butter(12, w)

    alpha = signal.filtfilt(b,a,alpha, padlen=150)
    beta = signal.filtfilt(b,a,beta, padlen=150)
    q = signal.filtfilt(b,a,q, padlen=150)
    return alpha,beta,q

class MagCal:
  "Python class for magnetic calibration"
  def __init__(self):
    self.calibrated = False
    self.b = np.array([0.,0.,0.])
    self.rot = np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
    self.cal_file = None
    self.field = 50

  def init(self,fname):
    if fname[-3:] == 'xml':
      tree = ET.parse(fname)
      root = tree.getroot()

      field = root.find('mag_calibration_field')
      self.field = float(field.find('float').text)

      bias = root.find('mag_calibration_bias')
      for idx,b in enumerate(bias.findall('float')):
        self.b[idx] = float(b.text)

      scale = root.find('mag_calibration_scale')
      for idx,r in enumerate(scale.findall('float')):
        self.rot[int(idx/3),idx%3] = float(r.text)
      self.calibrated = True

    else:
      self.cal_file = fname
      t,x,y,z = self.mag_load(fname)
      b,rot,field = self.mag_calibrate(x,y,z)
      self.b = b
      self.rot = rot
      self.field = field
      self.calibrated = True

  def mag_calibrate(self,x,y,z):
    d = np.matrix(np.concatenate([x*x,2*x*y,2*x*z,y*y,2*y*z,z*z,x,y,z,np.ones(x.shape)],axis=1))

    eigVals, eigVecs = np.linalg.eig(d.T*d)

    idx = np.argmin(eigVals)

    beta = np.asarray(eigVecs[:,idx]).flatten()
    A = np.matrix([[beta[0],beta[1],beta[2]] , [beta[1],beta[3],beta[4]],[beta[2],beta[4],beta[5]]])
    dA = np.linalg.det(A)
    if dA < 0:
      A = -A
      beta = -beta
      dA = -dA

    b = np.asarray(-1/2 * np.linalg.inv(A) * np.asmatrix(beta[6:9]).T).flatten()
    rot = LA.sqrtm(A/ (dA ** (1/3)))
    field = np.sqrt(np.abs(A[0,0]*b[0]*b[0]+2*A[1,0]*b[1]*b[0] + 2*A[2,0]*b[2]*b[0]+ A[1,1]*b[1]*b[1]+ 2*A[2,1]*b[1]*b[2]+ A[2,2]*b[2]*b[2]-beta[-1]))
    field = field/ (dA ** (1/6))
    return (b,rot,field)

  def save_xml(self,xml_fname):
    if self.calibrated:
      root = ET.Element("mag_calibration")

      m1 = ET.Element("mag_calibration_field")
      root.append (m1)
      b = ET.SubElement(m1, "float")
      b.text = str(self.field)

      m1 = ET.Element("mag_calibration_bias")
      root.append (m1)
      for i in range(0,3):
        b = ET.SubElement(m1, "float")
        b.text = str(self.b[i])

      m1 = ET.Element("mag_calibration_scale")
      root.append (m1)
      for i in range(0,3):
        for j in range(0,3):
          b = ET.SubElement(m1, "float")
          b.text = str(self.rot[i,j])

      tree = ET.ElementTree(root)
      with open (xml_fname, 'wb') as files:
        tree.write(files)

    else:
      print('Error, not calibrated object, %s NOT written' % xml_fname)

  def print_calibration(self):
    if not self.calibrated:
      print('WARNING!!! This object is not calibrated')
    print('Calibration from %s' % self.cal_file);
    print('\tField Strength:\n\t\t%.2f' % self.field);
    print('\tBias:\n\t\t%6.3f\n\t\t%6.3f\n\t\t%6.3f' % (self.b[0],self.b[1],self.b[2]));
    print('\tMatrix:')
    print('\t\t%6.3f, %6.3f, %6.3f' % (self.rot[0,0],self.rot[0,1],self.rot[0,2]));
    print('\t\t%6.3f, %6.3f, %6.3f' % (self.rot[1,0],self.rot[1,1],self.rot[1,2]));
    print('\t\t%6.3f, %6.3f, %6.3f' % (self.rot[2,0],self.rot[2,1],self.rot[2,2]));

  def print_xml(self,fname=None):
    if not self.calibrated:
      print('WARNING!!! This object is not calibrated')

    if fname is not None:
      f = open(fname,'w')
    else:
      f = sys.stdout
    print('<param>',file=f)
    print('   <vehicle class="com.blackswifttech.swifttab.parameters.xml.fixedwing.FWVehicle">',file=f)
    print('      <sensors>',file=f)
    print('         <mag_calibration_bias>  ',file=f)
    print('            <numberData>%f</numberData>    '%self.b[0],file=f)
    print('            <numberData>%f</numberData>    '%self.b[1],file=f)
    print('            <numberData>%f</numberData>    '%self.b[2],file=f)
    print('         </mag_calibration_bias> ',file=f)
    print('         <mag_calibration_scale> ',file=f)
    print('            <numberData>%f</numberData>    '%self.rot[0,0],file=f)
    print('            <numberData>%f</numberData>    '%self.rot[0,1],file=f)
    print('            <numberData>%f</numberData>    '%self.rot[0,2],file=f)
    print('            <numberData>%f</numberData>    '%self.rot[1,0],file=f)
    print('            <numberData>%f</numberData>    '%self.rot[1,1],file=f)
    print('            <numberData>%f</numberData>    '%self.rot[1,2],file=f)
    print('            <numberData>%f</numberData>    '%self.rot[2,0],file=f)
    print('            <numberData>%f</numberData>    '%self.rot[2,1],file=f)
    print('            <numberData>%f</numberData>    '%self.rot[2,2],file=f)
    print('         </mag_calibration_scale>',file=f)
    print('         <sensor_type>UNKNOWN_SENSOR</sensor_type>',file=f)
    print('      </sensors>',file=f)
    print('   </vehicle>',file=f)
    print('</param>',file=f)
    if fname is not None:
      f.close()

  def print_dot_h(self):
    if not self.calibrated:
      print('WARNING!!! This object is not calibrated')

    print('#define  MAG_M_0_0  %f'%self.rot[0,0])
    print('#define  MAG_M_1_0  %f'%self.rot[1,0])
    print('#define  MAG_M_2_0  %f'%self.rot[2,0])
    print('#define  MAG_M_0_1  %f'%self.rot[0,1])
    print('#define  MAG_M_1_1  %f'%self.rot[1,1])
    print('#define  MAG_M_2_1  %f'%self.rot[2,1])
    print('#define  MAG_M_0_2  %f'%self.rot[0,2])
    print('#define  MAG_M_1_2  %f'%self.rot[1,2])
    print('#define  MAG_M_2_2  %f'%self.rot[2,2])
    print('')
    print('#define  MAG_B_0    %f'%self.b[0])
    print('#define  MAG_B_1    %f'%self.b[1])
    print('#define  MAG_B_2    %f'%self.b[2])

  def correct_mags(self,x,y,z):
    X = np.matrix(np.concatenate([x,y,z],axis=1))
    Xc = (X - self.b)*self.rot
    xc = np.asarray(Xc[:,0])
    yc = np.asarray(Xc[:,1])
    zc = np.asarray(Xc[:,2])

    return (xc,yc,zc)

  def decorrect_mags(self,x,y,z):
    X = np.matrix(np.concatenate([x,y,z],axis=1))
    Xc = X *np.linalg.inv(self.rot) + self.b
    xc = np.asarray(Xc[:,0])
    yc = np.asarray(Xc[:,1])
    zc = np.asarray(Xc[:,2])

    return (xc,yc,zc)

  def correct_mags_log(self,fname):
    if not self.calibrated:
      print('WARNING!!! This object is not calibrated')

    # Load and run through calibration
    t,x,y,z = self.mag_load(fname)
    xc,yc,zc = self.correct_mags(x,y,z)
    outfile = fname[:-4] + '_mag' + fname[-4:]

    if fname[-3:] == 'mat': # .mat file
      data = loadmat(fname)
      data['mag']['x'][0][0] = xc
      data['mag']['y'][0][0] = yc
      data['mag']['z'][0][0] = zc
      # Save to file
      savemat(outfile,data)

    elif fname[-3:] == 'csv': # .csv file
      data = pd.read_csv(fname).dropna()
      data['MAGNETOMETER_X'] = xc
      data['MAGNETOMETER_Y'] = yc
      data['MAGNETOMETER_Z'] = zc
      # Save to file
      data.to_csv(outfile,index=False)

    else:
      print('ERROR: Not a valid filetype: %s' % fname)

    print('Saving with new mag calibration to: %s' % outfile)
    return outfile

  def decorrect_mags_log(self,fname):
    if not self.calibrated:
      print('WARNING!!! This object is not calibrated')

    # Load and run through calibration
    t,x,y,z = self.mag_load(fname)
    xc,yc,zc = self.decorrect_mags(x,y,z)
    outfile = fname[:-4] + '_demag' + fname[-4:]

    if fname[-3:] == 'mat': # .mat file
      data = loadmat(fname)
      data['mag']['x'][0][0] = xc
      data['mag']['y'][0][0] = yc
      data['mag']['z'][0][0] = zc
      # Save to file
      savemat(outfile,data)

    elif fname[-3:] == 'csv': # .csv file
      data = pd.read_csv(fname).dropna()
      data['MAGNETOMETER_X'] = xc
      data['MAGNETOMETER_Y'] = yc
      data['MAGNETOMETER_Z'] = zc
      # Save to file
      data.to_csv(outfile,index=False)

    else:
      print('ERROR: Not a valid filetype: %s' % fname)

    print('Saving with new mag calibration to: %s' % outfile)
    return outfile

  def plot_3D_mags(self,fname):
    t,x,y,z = self.mag_load(fname)

    if self.calibrated:
      xc,yc,zc = self.correct_mags(x,y,z)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_box_aspect(aspect=(1,1,1));
    ax.scatter(x, y, z, marker='.',label='raw')
    if self.calibrated:
      ax.scatter(xc, yc, zc, marker='.',label='calibrated')

    ax.set_xlabel('Mx')
    ax.set_ylabel('My')
    ax.set_zlabel('Mz')
    plt.title('3D Magnetometer Readings')
    ax.legend()

    plt.show()

  def plot_3D_mags_shift(self,fname):
    t,x,y,z = self.mag_load(fname)

    xc,yc,zc = self.correct_mags(x,y,z)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_box_aspect(aspect=(1,1,1));
    for x1,x2,y1,y2,z1,z2 in zip(x,xc,y,yc,z,zc):
      ax.plot([x1,x2],[y1,y2],zs=[z1,z2],color='grey')
    ax.scatter(x, y, z, marker='.',label='raw')
    ax.scatter(xc, yc, zc, marker='.',label='calibrated')

    ax.set_xlabel('Mx')
    ax.set_ylabel('My')
    ax.set_zlabel('Mz')
    plt.title('3D Magnetometer Readings')
    ax.legend()

    plt.show()

  def plot_timeseries_mags(self,fname):
    t,x,y,z = self.mag_load(fname)
    if self.calibrated:
      xc,yc,zc = self.correct_mags(x,y,z)

    plt.figure()
    axbase = plt.subplot(3,1,1)
    axbase.plot(t, x)
    if self.calibrated:
      axbase.plot(t, xc)
    plt.ylabel('Mx')
    plt.grid()
    plt.title('Magnetic Time Series')

    ax = plt.subplot(3,1,2, sharex=axbase)
    ax.plot(t, y)
    if self.calibrated:
      ax.plot(t, yc)
    plt.ylabel('My')
    plt.grid()

    ax = plt.subplot(3,1,3, sharex=axbase)
    ax.plot(t, z)
    if self.calibrated:
      ax.plot(t, zc)
    plt.ylabel('Mz')
    plt.grid()

    plt.show()

  def plot_2D_mags(self,fname):
    t,x,y,z = self.mag_load(fname)

    if self.calibrated:
      xc,yc,zc = self.correct_mags(x,y,z)

    th = np.linspace(0,2*np.pi,num=100)
    plt.figure()
    ax = plt.subplot(1,3,1)
    ax.plot(x, y,'.')
    if self.calibrated:
      ax.plot(xc, yc,'.')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('Mx')
    plt.ylabel('My')
    plt.grid()
    ax.axis('equal')

    ax = plt.subplot(1,3,2)
    ax.plot(x, z,'.')
    if self.calibrated:
      ax.plot(xc, zc,'.')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('Mx')
    plt.ylabel('Mz')
    plt.title(os.path.basename(fname))
    plt.grid()
    ax.axis('equal')

    ax = plt.subplot(1,3,3)
    ax.plot(y, z,'.',label='raw')
    if self.calibrated:
      ax.plot(yc, zc,'.',label='calibrated')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('My')
    plt.ylabel('Mz')
    plt.grid()
    plt.legend()
    ax.axis('equal')


    plt.show()

  def plot_2D_mags_shift(self,fname):

    t,x,y,z = self.mag_load(fname)

    xc,yc,zc = self.correct_mags(x,y,z)

    th = np.linspace(0,2*np.pi,num=100)
    plt.figure()
    ax = plt.subplot(1,3,1)
    for x1,x2,y1,y2 in zip(x,xc,y,yc):
      ax.plot([x1,x2],[y1,y2],color='gray')
    ax.plot(x, y,'.')
    ax.plot(xc, yc,'.')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('Mx')
    plt.ylabel('My')
    plt.grid()
    ax.axis('equal')

    ax = plt.subplot(1,3,2)
    for x1,x2,z1,z2 in zip(x,xc,z,zc):
      ax.plot([x1,x2],[z1,z2],color='gray')
    ax.plot(x, z,'.')
    ax.plot(xc, zc,'.')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('Mx')
    plt.ylabel('Mz')
    plt.grid()
    ax.axis('equal')

    ax = plt.subplot(1,3,3)
    for y1,y2,z1,z2 in zip(y,yc,z,zc):
      ax.plot([y1,y2],[z1,z2],color='gray')
    ax.plot(y, z,'.',label='raw')
    ax.plot(yc, zc,'.',label='calibrated')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('My')
    plt.ylabel('Mz')
    plt.grid()
    plt.legend()
    ax.axis('equal')

    plt.show()

  def mag_load(self,fname):
    if fname[-3:] == 'mat': # .mat file
      mag = loadmat(fname)['mag']
      t = mag['system_time'][0][0]
      x = mag['x'][0][0]
      y = mag['y'][0][0]
      z = mag['z'][0][0]
    elif fname[-3:] == '.nc': # .nc file
      mag,tmag = lu.get_var(fname,'mag')
      t = tmag.reshape(-1,1)
      x = mag['x'].reshape(-1,1)
      y = mag['y'].reshape(-1,1)
      z = mag['z'].reshape(-1,1)
    elif fname[-3:] == 'csv': # .csv file
      data = pd.read_csv(fname)
      data = data[['MAGNETOMETER_TIME','MAGNETOMETER_X','MAGNETOMETER_Y','MAGNETOMETER_Z']]
      data = data.dropna()
      t = np.array([data['MAGNETOMETER_TIME'].values]).T
      x = np.array([data['MAGNETOMETER_X'].values]).T
      y = np.array([data['MAGNETOMETER_Y'].values]).T
      z = np.array([data['MAGNETOMETER_Z'].values]).T

    return (t,x,y,z)

  def check_mags_mag(self,Mx,My,Mz):
    mm = 0*Mx
    for idx,(mx,my,mz) in enumerate(zip(Mx,My,Mz)):
      mm[idx] = np.linalg.norm([mx,my,mz])
    return mm


class AccCal:
  "Python class for accelerometr calibration"
  def __init__(self):
    self.calibrated = False
    self.b = np.array([0.,0.,0.])
    self.rot = np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
    self.cal_file = None
    self.field = 9.81

  def init(self,fname):
    if fname[-3:] == 'xml':
      tree = ET.parse(fname)
      root = tree.getroot()

      field = root.find('acc_calibration_field')
      self.field = float(field.find('float').text)

      bias = root.find('acc_calibration_bias')
      for idx,b in enumerate(bias.findall('float')):
        self.b[idx] = float(b.text)

      scale = root.find('acc_calibration_scale')
      for idx,r in enumerate(scale.findall('float')):
        self.rot[int(idx/3),idx%3] = float(r.text)
      self.calibrated = True

    else:
      self.cal_file = fname
      t,x,y,z = self.acc_load_cal(fname)

      d = np.matrix(np.concatenate([x*x,2*x*y,2*x*z,y*y,2*y*z,z*z,x,y,z,np.ones(x.shape)],axis=1))

      eigVals, eigVecs = np.linalg.eig(d.T*d)

      idx = np.argmin(eigVals)

      beta = np.asarray(eigVecs[:,idx]).flatten()
      A = np.matrix([[beta[0],beta[1],beta[2]] , [beta[1],beta[3],beta[4]],[beta[2],beta[4],beta[5]]])
      dA = np.linalg.det(A)
      dA
      if dA < 0:
        A = -A
        beta = -beta
        dA = -dA

      b = np.asarray(-1/2 * np.linalg.inv(A) * np.asmatrix(beta[6:9]).T).flatten()
      rot = LA.sqrtm(A/ (dA ** (1/3)))
      field = np.sqrt(np.abs(A[0,0]*b[0]*b[0]+2*A[1,0]*b[1]*b[0] + 2*A[2,0]*b[2]*b[0]+ A[1,1]*b[1]*b[1]+ 2*A[2,1]*b[1]*b[2]+ A[2,2]*b[2]*b[2]-beta[-1]))

      self.b = b
      self.rot = rot
      self.field = field/ (dA ** (1/6))
      self.calibrated = True

  def save_xml(self,xml_fname):
    if self.calibrated:
      root = ET.Element("acc_calibration")

      m1 = ET.Element("acc_calibration_field")
      root.append (m1)
      b = ET.SubElement(m1, "float")
      b.text = str(self.field)

      m1 = ET.Element("acc_calibration_bias")
      root.append (m1)
      for i in range(0,3):
        b = ET.SubElement(m1, "float")
        b.text = str(self.b[i])

      m1 = ET.Element("acc_calibration_scale")
      root.append (m1)
      for i in range(0,3):
        for j in range(0,3):
          b = ET.SubElement(m1, "float")
          b.text = str(self.rot[i,j])

      tree = ET.ElementTree(root)
      with open (xml_fname, 'wb') as files:
        tree.write(files)

    else:
      print('Error, not calibrated object, %s NOT written' % xml_fname)

  def print_calibration(self):
    if not self.calibrated:
      print('WARNING!!! This object is not calibrated')
    print('Calibration from %s' % self.cal_file);
    print('\tField Strength:\n\t\t%.4f' % self.field);
    print('\tBias:\n\t\t%6.3f\n\t\t%6.3f\n\t\t%6.3f' % (self.b[0],self.b[1],self.b[2]));
    print('\tMatrix:')
    print('\t\t%6.3f, %6.3f, %6.3f' % (self.rot[0,0],self.rot[0,1],self.rot[0,2]));
    print('\t\t%6.3f, %6.3f, %6.3f' % (self.rot[1,0],self.rot[1,1],self.rot[1,2]));
    print('\t\t%6.3f, %6.3f, %6.3f' % (self.rot[2,0],self.rot[2,1],self.rot[2,2]));

  def correct_acc(self,x,y,z):
    X = np.matrix(np.concatenate([x,y,z],axis=1))
    Xc = (X - self.b)*self.rot
    xc = np.asarray(Xc[:,0])
    yc = np.asarray(Xc[:,1])
    zc = np.asarray(Xc[:,2])

    return (xc,yc,zc)

  def correct_acc_log(self,fname):
    if not self.calibrated:
      print('WARNING!!! This object is not calibrated')

    # Load and run through calibration
    t,x,y,z = self.acc_load(fname)
    xc,yc,zc = self.correct_acc(x,y,z)
    outfile = fname[:-4] + '_acc' + fname[-4:]

    if fname[-3:] == 'mat': # .mat file
      data = loadmat(fname)
      data['acc']['x'][0][0] = xc
      data['acc']['y'][0][0] = yc
      data['acc']['z'][0][0] = zc
      # Save to file
      savemat(outfile,data)

    elif fname[-3:] == 'csv': # .csv file
      data = pd.read_csv(fname).dropna()
      data['ACCELEROMETER_X'] = xc
      data['ACCELEROMETER_Y'] = yc
      data['ACCELEROMETER_Z'] = zc
      # Save to file
      data.to_csv(outfile,index=False)

    else:
      print('ERROR: Not a valid filetype: %s' % fname)

    print('Saving with new acc calibration to: %s' % outfile)
    return outfile

  def plot_3D_acc(self,fname):
    t,x,y,z = self.acc_load_cal(fname)

    if self.calibrated:
      xc,yc,zc = self.correct_acc(x,y,z)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_box_aspect(aspect=(1,1,1));
    ax.scatter(x, y, z, marker='.',label='raw')
    if self.calibrated:
      ax.scatter(xc, yc, zc, marker='.',label='calibrated')

    ax.set_xlabel('Ax')
    ax.set_ylabel('Ay')
    ax.set_zlabel('Az')
    plt.title('3D Accelerometer Readings')
    ax.legend()

    plt.show()

  def plot_timeseries_acc(self,fname):
    t,x,y,z = self.acc_load(fname)
    t2,x2,y2,z2 = self.acc_load_cal(fname)
    if self.calibrated:
      xc,yc,zc = self.correct_acc(x,y,z)

    plt.figure()
    axbase = plt.subplot(3,1,1)
    axbase.plot(t, x,label='Raw')
    if self.calibrated:
      axbase.plot(t, xc,label='Cal')

    axbase.plot(t2, x2,'o',color='C0')
    plt.legend()
    plt.ylabel('Ax')
    plt.grid()
    plt.title('Acc Time Series')

    ax = plt.subplot(3,1,2, sharex=axbase)
    ax.plot(t, y)
    if self.calibrated:
      ax.plot(t, yc)
    ax.plot(t2, y2,'o',color='C0')
    plt.ylabel('Ay')
    plt.grid()

    ax = plt.subplot(3,1,3, sharex=axbase)
    ax.plot(t, z)
    if self.calibrated:
      ax.plot(t, zc)
    ax.plot(t2, z2,'o',color='C0')
    plt.ylabel('Az')
    plt.grid()

    plt.show()

  def plot_2D_acc(self,fname):
    t,x,y,z = self.acc_load_cal(fname)

    if self.calibrated:
      xc,yc,zc = self.correct_acc(x,y,z)

    th = np.linspace(0,2*np.pi,num=100)
    plt.figure()
    ax = plt.subplot(1,3,1)
    ax.plot(x, y,'.')
    if self.calibrated:
      ax.plot(xc, yc,'.')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('Ax')
    plt.ylabel('Ay')
    plt.grid()
    ax.axis('equal')

    ax = plt.subplot(1,3,2)
    ax.plot(x, z,'.')
    if self.calibrated:
      ax.plot(xc, zc,'.')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('Ax')
    plt.ylabel('Az')
    plt.grid()
    ax.axis('equal')

    ax = plt.subplot(1,3,3)
    ax.plot(y, z,'.',label='raw')
    if self.calibrated:
      ax.plot(yc, zc,'.',label='calibrated')
    ax.plot(self.field*np.cos(th), self.field*np.sin(th),'--k')
    plt.xlabel('Ay')
    plt.ylabel('Az')
    plt.grid()
    plt.legend()
    ax.axis('equal')


    plt.show()

  def acc_load(self,fname):
    g = 9.81
    if fname[-3:] == 'mat': # .mat file
      acc = loadmat(fname)['acc']
      return acc['system_time'][0][0][:],acc['x'][0][0][:],acc['y'][0][0][:],acc['z'][0][0][:]
    elif fname[-3:] == 'csv': # .csv file
      data = pd.read_csv(fname)
      return np.array([data['IMU_TIME'].values]).T,g*np.array([data['ACCELEROMETER_X'].values]).T,g*np.array([data['ACCELEROMETER_Y'].values]).T,g*np.array([data['ACCELEROMETER_Z'].values]).T

  def acc_load_cal(self,fname):
    t,ax,ay,az = self.acc_load(fname)
    df = pd.DataFrame(np.concatenate((t,ax,ay,az),axis=1), columns = ['system_time','x','y','z'])

    idx = np.where( ((df.x.rolling(20).std() < 0.05) &
                     (df.y.rolling(20).std() < 0.05) &
                     (df.z.rolling(20).std() < 0.05)) )[0]

    return t[idx],ax[idx],ay[idx],az[idx]
