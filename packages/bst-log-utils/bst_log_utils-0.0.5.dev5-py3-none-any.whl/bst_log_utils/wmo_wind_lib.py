# Functions
import datetime

import sys
import pathlib
cur_path = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(cur_path) + "/")

import process_mhp as pm
import bst_helper_functions.bst_att_est as bae
import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import pandas as pd
import h5py

from scipy.interpolate import interp1d
from scipy.io import loadmat
from scipy.io import whosmat
from scipy.optimize import curve_fit
from scipy.optimize import minimize_scalar
from scipy import stats
from scipy import signal
from scipy import fftpack

import bst_log_utils.log_utils as lu

import netCDF4 as nc
import simplekml
import os
import datetime
import geomag
from circle_fit import taubinSVD
from lxml import etree as ET


m2ft = 3.28084
pi = np.pi
ft2m = 1/m2ft
kts2ms = 0.51445

def parse_dropsonde(fname):
    data = nc.Dataset(fname)
    date_str = data['time'].units[14:]

    sonde = {'fname':os.path.basename(fname),'epoch_time':datetime.datetime.strptime(date_str,"%Y-%m-%d %H:%M:%S %Z")}
    ts = data['time'][:].data
    for var in data.variables.keys():
        sonde[var] = data[var][:].data
        idx = np.where(sonde[var] == -999)[0]
        #sonde[var][sonde[var] == -999] = np.nan
        if (( (np.size(sonde[var])>1) & (len(idx) > 0) & (len(idx) < len(ts)) )):
            idx = np.where(sonde[var] != -999)[0]
            sonde[var] = interp1d(ts[idx],sonde[var][idx],fill_value='extrapolate')(ts)
    sonde['datetime'] = [sonde['epoch_time'] + datetime.timedelta(seconds=s) for s in sonde['time']]
    # Add extra variables to match BST names
    sonde_vars = ['rh','pres','tdry','u_wind','v_wind','alt']
    bst_vars = ['relative_humidity','pressure','air_temperature','wind_u','wind_v','altitude']
    for svar,bvar in zip(sonde_vars,bst_vars):
        sonde[bvar] = sonde[svar]
    return sonde



####################################################################################################
def normalize_log_data(fname,tfull=None,logtype='ap',recompute_yaw=None,recompute_mhp=None,ground=None,useGPStime=False):
    ##################### New S0 log netCDF ####################################
    if logtype == 's0_gcs_nc':

        payload_s0,tpayload_s0 = lu.get_nc_var(fname,'payload_s0')
        telem_pos,ttelem_pos   = lu.get_nc_var(fname,'telem_pos')
        telem_ori,ttelem_ori   = lu.get_nc_var(fname,'telem_ori')
        telem_sys,ttelem_sys   = lu.get_nc_var(fname,'telem_sys')

        if useGPStime:
            ts = ttelem_pos
        else:
            ts = tpayload_s0

        # Fix lat/lonalt
        lat = telem_pos['latitude']
        lon = telem_pos['longitude']
        alt = telem_pos['altitude']

        vg_x = telem_pos['velocity'][:,0]
        vg_y = telem_pos['velocity'][:,1]
        vg_z = telem_pos['velocity'][:,2]

        vg_x   = interp1d(ttelem_pos,vg_x,fill_value='extrapolate')(ts)
        vg_y   = interp1d(ttelem_pos,vg_y,fill_value='extrapolate')(ts)
        vg_z   = interp1d(ttelem_pos,vg_z,fill_value='extrapolate')(ts)
        lat    = interp1d(ttelem_pos,lat,fill_value='extrapolate')(ts)
        lon    = interp1d(ttelem_pos,lon,fill_value='extrapolate')(ts)
        alt    = interp1d(ttelem_pos,alt,fill_value='extrapolate')(ts)
        wind_u = interp1d(tpayload_s0,payload_s0['u'])(ts)
        wind_v = interp1d(tpayload_s0,payload_s0['v'])(ts)
        wind_w = interp1d(tpayload_s0,payload_s0['w'])(ts)

        temp     = interp1d(tpayload_s0,payload_s0['air_temperature'])(ts)
        humidity = interp1d(tpayload_s0,payload_s0['humidity'])(ts)
        stat_p   = interp1d(tpayload_s0,payload_s0['static_pressure'][:,0])(ts)

        idx = np.where(((temp != 0) & (humidity > 0) & (humidity <= 100)))

        temp     = interp1d(ts[idx],temp[idx],fill_value='extrapolate')(ts)
        humidity = interp1d(ts[idx],humidity[idx],fill_value='extrapolate')(ts)
        stat_p   = interp1d(ts[idx],stat_p[idx],fill_value='extrapolate')(ts)

        tsurf    = interp1d(tpayload_s0,payload_s0['ground_temperature'])(ts)
        laseralt = interp1d(tpayload_s0,payload_s0['laser_distance'])(ts)

        Q = np.transpose([interp1d(ttelem_ori,telem_ori['q'][:,0],fill_value='extrapolate')(ts),
                          interp1d(ttelem_ori,telem_ori['q'][:,1],fill_value='extrapolate')(ts),
                          interp1d(ttelem_ori,telem_ori['q'][:,2],fill_value='extrapolate')(ts),
                          interp1d(ttelem_ori,telem_ori['q'][:,3],fill_value='extrapolate')(ts)])
        magx = interp1d(ttelem_ori,telem_ori['magnetometer'][:,0],fill_value='extrapolate')(ts)
        magy = interp1d(ttelem_ori,telem_ori['magnetometer'][:,1],fill_value='extrapolate')(ts)
        magz = interp1d(ttelem_ori,telem_ori['magnetometer'][:,2],fill_value='extrapolate')(ts)
        if recompute_yaw is not None:
            mx = magx
            my = magy
            mz = magz

            Qap_rp = bae.quat_rponly(Q)
            mag_dec = geomag.declination(np.nanmean(lat),np.nanmean(lon))*pi/180
            magcal = pm.MagCal()
            magcal.init(recompute_yaw)

            mx = np.expand_dims(mx,axis=1)
            my = np.expand_dims(my,axis=1)
            mz = np.expand_dims(mz,axis=1)

            magx,magy,magz = magcal.correct_mags(mx,my,mz)
            M_m = np.hstack([magx,magy,magz])
            Q = bae.mag_correct_q_vec(M_m,Q,mag_dec=mag_dec)

        if recompute_mhp is None:
            print('NOT IMPLEMENTED!!! Add code and re-run')
        else:
            dp0 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,0])(ts)
            dp1 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,1])(ts)
            dp2 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,2])(ts)
            dp3 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,3])(ts)
            dp4 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,4])(ts)
            alpha,beta,q= pm.compute_alpha_beta_q(dp0,dp1,dp2,dp3,dp4,param_file=recompute_mhp)
            ias,tas = lu.compute_ias_tas(q,temp,stat_p,humidity)

        seconds = telem_sys['hour'].astype(float)*3600 + telem_sys['minute'].astype(float)*60 + telem_sys['milliseconds'].astype(float)/1000
        idx = np.where(telem_sys['week'] == np.nanmax(telem_sys['week']))[0][0]
        toffset = stats.mode(seconds[idx] - ttelem_sys[idx])[0]

        if tfull is not None:
            idx = np.where(ttelem_sys >= tfull[0])[0][0]
        else:
            idx = idx[0]

        week = telem_sys['week'][idx]
        seconds = ttelem_sys[idx]+toffset

        time_since_str = lu.weeksecondstoutc(week,seconds,datetimeformat = "%Y-%m-%dT%H:%M:%SZ")
        time_offset = lu.weekseconds2unix(week, seconds - ttelem_sys[idx])
    ##################### Old S0 (SGP) #############################################
    elif logtype == 'ap_s0_old':
        state = loadmat(fname)['state']
        state = {'system_time':state['system_time'][0][0].flatten(),
                 'q0':state['q'][0][0][:,0].flatten(),
                 'q1':state['q'][0][0][:,1].flatten(),
                 'q2':state['q'][0][0][:,2].flatten(),
                 'q3':state['q'][0][0][:,3].flatten(),
                 'wind_x':state['wind'][0][0][:,0].flatten(),
                 'wind_y':state['wind'][0][0][:,1].flatten(),
                 'wind_z':state['wind'][0][0][:,2].flatten(),
                }
        gps = loadmat(fname)['gps']
        gps = {'system_time':gps['system_time'][0][0].flatten(),
               'latitude':gps['latitude'][0][0].flatten(),
               'longitude':gps['longitude'][0][0].flatten(),
               'altitude':gps['altitude'][0][0].flatten(),
               'velocity_x':gps['velocity'][0][0]['x'][0][0].flatten(),
               'velocity_y':gps['velocity'][0][0]['y'][0][0].flatten(),
               'velocity_z':gps['velocity'][0][0]['z'][0][0].flatten(),
               'week':gps['week'][0][0].flatten(),
               'hour':gps['hour'][0][0].flatten(),
               'minute':gps['minute'][0][0].flatten(),
               'seconds':gps['seconds'][0][0].flatten(),
              }

        mag = loadmat(fname)['mag']
        mag = {'system_time':mag['system_time'][0][0].flatten(),
               'x':mag['x'][0][0].flatten(),
               'y':mag['y'][0][0].flatten(),
               'z':mag['z'][0][0].flatten(),
              }
        mhp = loadmat(fname)['mhp']
        mhp = {'system_time':mhp['system_time'][0][0].flatten(),
               'static_pressure':mhp['static_pressure'][0][0].flatten(),
               'dynamic_pressure_0':mhp['dynamic_pressure'][0][0][:,0].flatten(),
               'dynamic_pressure_1':mhp['dynamic_pressure'][0][0][:,1].flatten(),
               'dynamic_pressure_2':mhp['dynamic_pressure'][0][0][:,2].flatten(),
               'dynamic_pressure_3':mhp['dynamic_pressure'][0][0][:,3].flatten(),
               'dynamic_pressure_4':mhp['dynamic_pressure'][0][0][:,4].flatten(),
               'air_temperature':mhp['air_temperature'][0][0].flatten(),
               'humidity':mhp['humidity'][0][0].flatten(),
              }
        # Switch all variables to 'ts' time
        ts = state['system_time']
        Q = np.transpose([state['q0'],state['q1'],state['q2'],state['q3']])

        lat    = interp1d(gps['system_time'],gps['latitude'], fill_value='extrapolate')(ts)
        lon    = interp1d(gps['system_time'],gps['longitude'], fill_value='extrapolate')(ts)
        alt    = interp1d(gps['system_time'],gps['altitude'], fill_value='extrapolate')(ts)
        vg_x   = interp1d(gps['system_time'],gps['velocity_x'],fill_value='extrapolate')(ts)
        vg_y   = interp1d(gps['system_time'],gps['velocity_y'],fill_value='extrapolate')(ts)
        vg_z   = interp1d(gps['system_time'],gps['velocity_z'],fill_value='extrapolate')(ts)

        magx = interp1d(mag['system_time'],mag['x'],fill_value='extrapolate')(ts)
        magy = interp1d(mag['system_time'],mag['y'],fill_value='extrapolate')(ts)
        magz = interp1d(mag['system_time'],mag['z'],fill_value='extrapolate')(ts)

        idx = np.where(((mhp['static_pressure'] > 0) & (mhp['air_temperature'] != 0) & (mhp['humidity'] > 0) & (mhp['humidity'] <= 100)))[0]

        temp     = interp1d(mhp['system_time'][idx],mhp['air_temperature'][idx],fill_value='extrapolate')(ts)
        humidity = interp1d(mhp['system_time'][idx],mhp['humidity'][idx],fill_value='extrapolate')(ts)
        stat_p   = interp1d(mhp['system_time'][idx],mhp['static_pressure'][idx],fill_value='extrapolate')(ts)

        wind_u   = interp1d(state['system_time'],state['wind_y'],fill_value='extrapolate')(ts)
        wind_v   = interp1d(state['system_time'],state['wind_x'],fill_value='extrapolate')(ts)
        wind_w   = interp1d(state['system_time'],state['wind_z'],fill_value='extrapolate')(ts)

        if recompute_yaw is not None:
            mx = magx
            my = magy
            mz = magz

            Qap_rp = bae.quat_rponly(Q)
            mag_dec = geomag.declination(np.nanmean(lat),np.nanmean(lon))*pi/180
            magcal = pm.MagCal()
            magcal.init(recompute_yaw)

            mx = np.expand_dims(mx,axis=1)
            my = np.expand_dims(my,axis=1)
            mz = np.expand_dims(mz,axis=1)

            magx,magy,magz = magcal.correct_mags(mx,my,mz)
            M_m = np.hstack([magx,magy,magz])
            Q = bae.mag_correct_q_vec(M_m,Q,mag_dec=mag_dec)

        if recompute_mhp is None:
            print('NOT IMPLEMENTED!!! Add code and re-run')
        else:
            dp0 = interp1d(mhp['system_time'],mhp['dynamic_pressure_0'],fill_value='extrapolate')(ts)
            dp1 = interp1d(mhp['system_time'],mhp['dynamic_pressure_1'],fill_value='extrapolate')(ts)
            dp2 = interp1d(mhp['system_time'],mhp['dynamic_pressure_2'],fill_value='extrapolate')(ts)
            dp3 = interp1d(mhp['system_time'],mhp['dynamic_pressure_3'],fill_value='extrapolate')(ts)
            dp4 = interp1d(mhp['system_time'],mhp['dynamic_pressure_4'],fill_value='extrapolate')(ts)
            alpha,beta,q= pm.compute_alpha_beta_q(dp0,dp1,dp2,dp3,dp4,param_file=recompute_mhp)
            alpha,beta,q= pm.filter_abq(alpha,beta,q)
            ias,tas = lu.compute_ias_tas(q,temp,stat_p,humidity)

        idx = np.argmax(gps['hour'])
        week = float(gps['week'][idx])
        seconds = float(gps['hour'][idx])*3600 + float(gps['minute'][idx])*60 + float(gps['seconds'][idx]) - float(gps['system_time'][idx])

        time_since_str = lu.weeksecondstoutc(week,seconds,datetimeformat = "%Y-%m-%dT%H:%M:%SZ")
        time_offset = lu.weekseconds2unix(week, seconds)
    ##################### Current S0 ###############################################
    if logtype == 'ap_s0':
        state,tstate = lu.get_var(fname,'state')

        payload_s0,tpayload_s0 = lu.get_var(fname,'payload_s0')

        mag,tmag = lu.get_var(fname,'mag')
        gps,tgps = lu.get_var(fname,'gps')

        # Switch all variables to 'ts' time
        ts = state['system_time']
        ts = np.unique(ts) # ensure monotonic_increase

        Q = np.transpose([
            interp1d(state['system_time'],state['q'][:,0],fill_value = 'extrapolate')(ts),
            interp1d(state['system_time'],state['q'][:,1],fill_value = 'extrapolate')(ts),
            interp1d(state['system_time'],state['q'][:,2],fill_value = 'extrapolate')(ts),
            interp1d(state['system_time'],state['q'][:,3],fill_value = 'extrapolate')(ts)])

        lat    = interp1d(gps['system_time'],gps['latitude'], fill_value='extrapolate')(ts)
        lon    = interp1d(gps['system_time'],gps['longitude'], fill_value='extrapolate')(ts)
        alt    = interp1d(gps['system_time'],gps['altitude'], fill_value='extrapolate')(ts)
        vg_x   = interp1d(gps['system_time'],gps['velocity.x'],fill_value='extrapolate')(ts)
        vg_y   = interp1d(gps['system_time'],gps['velocity.y'],fill_value='extrapolate')(ts)
        vg_z   = interp1d(gps['system_time'],gps['velocity.z'],fill_value='extrapolate')(ts)

        magx = interp1d(mag['system_time'],mag['x'],fill_value='extrapolate')(ts)
        magy = interp1d(mag['system_time'],mag['y'],fill_value='extrapolate')(ts)
        magz = interp1d(mag['system_time'],mag['z'],fill_value='extrapolate')(ts)

        idx = np.where(((payload_s0['air_temperature'] != 0) & (payload_s0['humidity'] > 0) & (payload_s0['humidity'] <= 100)))[0]

        temp     = interp1d(payload_s0['system_time'][idx],payload_s0['air_temperature'][idx],fill_value='extrapolate')(ts)
        humidity = interp1d(payload_s0['system_time'][idx],payload_s0['humidity'][idx],fill_value='extrapolate')(ts)
        stat_p   = interp1d(payload_s0['system_time'][idx],payload_s0['static_pressure'][idx,0],fill_value='extrapolate')(ts)

        wind_u   = interp1d(payload_s0['system_time'],payload_s0['u'],fill_value='extrapolate')(ts)
        wind_v   = interp1d(payload_s0['system_time'],payload_s0['v'],fill_value='extrapolate')(ts)
        wind_w   = interp1d(payload_s0['system_time'],payload_s0['w'],fill_value='extrapolate')(ts)

        if recompute_yaw is not None:
            mx = magx
            my = magy
            mz = magz

            Qap_rp = bae.quat_rponly(Q)
            mag_dec = geomag.declination(np.nanmean(lat),np.nanmean(lon))*pi/180
            magcal = pm.MagCal()
            magcal.init(recompute_yaw)

            mx = np.expand_dims(mx,axis=1)
            my = np.expand_dims(my,axis=1)
            mz = np.expand_dims(mz,axis=1)

            magx,magy,magz = magcal.correct_mags(mx,my,mz)
            M_m = np.hstack([magx,magy,magz])
            Q = bae.mag_correct_q_vec(M_m,Q,mag_dec=mag_dec)

        if recompute_mhp is None:
            print('NOT IMPLEMENTED!!! Add code and re-run')
        else:
            dp0 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,0],fill_value='extrapolate')(ts)
            dp1 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,1],fill_value='extrapolate')(ts)
            dp2 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,2],fill_value='extrapolate')(ts)
            dp3 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,3],fill_value='extrapolate')(ts)
            dp4 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][:,4],fill_value='extrapolate')(ts)
            alpha,beta,q= pm.compute_alpha_beta_q(dp0,dp1,dp2,dp3,dp4,param_file=recompute_mhp)
            ias,tas = lu.compute_ias_tas(q,temp,stat_p,humidity)

        idx = np.argmax(gps['week'])
        week = float(gps['week'][idx])
        seconds = float(gps['hour'][idx])*3600 + float(gps['minute'][idx])*60 + float(gps['seconds'][idx]) - float(gps['system_time'][idx])

        time_since_str = lu.weeksecondstoutc(week,seconds,datetimeformat = "%Y-%m-%dT%H:%M:%SZ")
        time_offset = lu.weekseconds2unix(week, seconds)
    ##################### S0 GCS from Tammy ########################################
    if logtype == 's0_gcs_v2':
        payload_s0,tpayload_s0 = lu.get_var(fname,'payload_s0')
        gps,tgps               = lu.get_var(fname,'gps')
        mag,tmag               = lu.get_var(fname,'mag')
        state,tstate           = lu.get_var(fname,'state')
        if useGPStime:
          ts = tgps
        else:
          ts = tpayload_s0

        # Fix lat/lonalt
        lat = state['latitude']
        lon = state['longitude']
        alt = state['altitude']

        vg_x = gps['velocity_x']
        idx = np.where(vg_x < 300)
        vg_x = vg_x[idx]
        vg_y = gps['velocity_y'][idx]
        vg_z = gps['velocity_z'][idx]
        tgps = tgps[idx]

        vg_x   = interp1d(tgps,vg_x,fill_value='extrapolate')(ts)
        vg_y   = interp1d(tgps,vg_y,fill_value='extrapolate')(ts)
        vg_z   = interp1d(tgps,vg_z,fill_value='extrapolate')(ts)
        lat    = interp1d(tstate,lat,fill_value='extrapolate')(ts)
        lon    = interp1d(tstate,lon,fill_value='extrapolate')(ts)
        alt    = interp1d(tstate,alt,fill_value='extrapolate')(ts)
        wind_u = interp1d(tpayload_s0,payload_s0['u'])(ts)
        wind_v = interp1d(tpayload_s0,payload_s0['v'])(ts)
        wind_w = interp1d(tpayload_s0,payload_s0['w'])(ts)

        temp     = interp1d(tpayload_s0,payload_s0['air_temperature'])(ts)
        humidity = interp1d(tpayload_s0,payload_s0['humidity'])(ts)
        stat_p   = interp1d(tpayload_s0,payload_s0['static_pressure'][0,:])(ts)

        idx = np.where(((temp != 0) & (humidity > 0) & (humidity <= 100)))

        temp     = interp1d(ts[idx],temp[idx],fill_value='extrapolate')(ts)
        humidity = interp1d(ts[idx],humidity[idx],fill_value='extrapolate')(ts)
        stat_p   = interp1d(ts[idx],stat_p[idx],fill_value='extrapolate')(ts)

        tsurf    = interp1d(tpayload_s0,payload_s0['ground_temperature'])(ts)
        laseralt = interp1d(tpayload_s0,payload_s0['laser_distance'])(ts)

        Q = np.transpose([interp1d(tstate,state['q0'],fill_value='extrapolate')(ts),
                          interp1d(tstate,state['q1'],fill_value='extrapolate')(ts),
                          interp1d(tstate,state['q2'],fill_value='extrapolate')(ts),
                          interp1d(tstate,state['q3'],fill_value='extrapolate')(ts)])
        magx = interp1d(tmag,mag['x'],fill_value='extrapolate')(ts)
        magy = interp1d(tmag,mag['y'],fill_value='extrapolate')(ts)
        magz = interp1d(tmag,mag['z'],fill_value='extrapolate')(ts)
        if recompute_yaw is not None:
            mx = magx
            my = magy
            mz = magz

            Qap_rp = bae.quat_rponly(Q)
            mag_dec = geomag.declination(np.nanmean(lat),np.nanmean(lon))*pi/180
            magcal = pm.MagCal()
            magcal.init(recompute_yaw)

            mx = np.expand_dims(mx,axis=1)
            my = np.expand_dims(my,axis=1)
            mz = np.expand_dims(mz,axis=1)

            magx,magy,magz = magcal.correct_mags(mx,my,mz)
            M_m = np.hstack([magx,magy,magz])
            Q = bae.mag_correct_q_vec(M_m,Q,mag_dec=mag_dec)

        if recompute_mhp is None:
            print('NOT IMPLEMENTED!!! Add code and re-run')
        else:
            dp0 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][0,:])(ts)
            dp1 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][1,:])(ts)
            dp2 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][2,:])(ts)
            dp3 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][3,:])(ts)
            dp4 = interp1d(tpayload_s0,payload_s0['dynamic_pressure'][4,:])(ts)
            alpha,beta,q= pm.compute_alpha_beta_q(dp0,dp1,dp2,dp3,dp4,param_file=recompute_mhp)
            ias,tas = lu.compute_ias_tas(q,temp,stat_p,humidity)

        seconds = gps['hour'].astype(float)*3600 + gps['minute'].astype(float)*60 + gps['seconds'].astype(float)
        idx = np.where(gps['week'] > 0)
        toffset = stats.mode(seconds[idx] - gps['system_time'][idx])[0][0]

        if tfull is not None:
          idx = np.where(gps['system_time'] >= tfull[0])[0][0]
        else:
          idx = np.where(gps['week'] > 0)

        week = gps['week'][idx]
        seconds = gps['system_time'][idx]+toffset

        time_since_str = lu.weeksecondstoutc(week,seconds,datetimeformat = "%Y-%m-%dT%H:%M:%SZ")
        time_offset = lu.weekseconds2unix(week, seconds - gps['system_time'][idx])

    ##################### S0 GCS from Clear Air ####################################
    if logtype == 's0_gcs_v1':
        uas = loadmat(fname)['uas']
        ts = uas['user_payload'][0][0]['ts'][0][0].flatten()
        vg_x = interp1d(uas['telemetry_position'][0][0]['ts'][0][0].flatten(),uas['telemetry_position'][0][0]['velocity_x'][0][0].flatten(),fill_value='extrapolate')(ts)
        vg_y = interp1d(uas['telemetry_position'][0][0]['ts'][0][0].flatten(),uas['telemetry_position'][0][0]['velocity_y'][0][0].flatten(),fill_value='extrapolate')(ts)
        vg_z = interp1d(uas['telemetry_position'][0][0]['ts'][0][0].flatten(),uas['telemetry_position'][0][0]['velocity_z'][0][0].flatten(),fill_value='extrapolate')(ts)
        lat = interp1d(uas['telemetry_position'][0][0]['ts'][0][0].flatten(),uas['telemetry_position'][0][0]['lat'][0][0].flatten(),fill_value='extrapolate')(ts)
        lon = interp1d(uas['telemetry_position'][0][0]['ts'][0][0].flatten(),uas['telemetry_position'][0][0]['lon'][0][0].flatten(),fill_value='extrapolate')(ts)
        alt = interp1d(uas['telemetry_position'][0][0]['ts'][0][0].flatten(),uas['telemetry_position'][0][0]['alt'][0][0].flatten(),fill_value='extrapolate')(ts)
        wind_u = interp1d(uas['telemetry_pressure'][0][0]['ts'][0][0].flatten(),uas['telemetry_pressure'][0][0]['wind_y'][0][0].flatten(),fill_value='extrapolate')(ts)
        wind_v = interp1d(uas['telemetry_pressure'][0][0]['ts'][0][0].flatten(),uas['telemetry_pressure'][0][0]['wind_x'][0][0].flatten(),fill_value='extrapolate')(ts)
        wind_w = interp1d(uas['telemetry_pressure'][0][0]['ts'][0][0].flatten(),uas['telemetry_pressure'][0][0]['wind_z'][0][0].flatten(),fill_value='extrapolate')(ts)

        temp = uas['user_payload'][0][0]['air_temperature'][0][0].flatten()
        humidity = uas['user_payload'][0][0]['humidity'][0][0].flatten()
        idx = np.where(((temp != 0) & (humidity > 0) & (humidity <= 100)))

        tpth = uas['user_payload'][0][0]['ts'][0][0][idx].flatten()
        temp = temp[idx]
        humidity = humidity[idx]
        stat_p = uas['user_payload'][0][0]['static_pressure'][0][0][idx].flatten()*100

        temp = interp1d(tpth,temp,fill_value='extrapolate')(ts)
        humidity = interp1d(tpth,humidity,fill_value='extrapolate')(ts)
        stat_p = interp1d(tpth,stat_p,fill_value='extrapolate')(ts)

        tsurf = uas['user_payload'][0][0]['ground_temperature'][0][0].flatten()
        laseralt = uas['user_payload'][0][0]['laser_distance'][0][0].flatten()

        if recompute_yaw is None:
            Q = np.transpose([uas['telemetry_orientation'][0][0]['q0'][0][0].flatten(),
                          uas['telemetry_orientation'][0][0]['q1'][0][0].flatten(),
                          uas['telemetry_orientation'][0][0]['q2'][0][0].flatten(),
                          uas['telemetry_orientation'][0][0]['q3'][0][0].flatten()])

            magx = uas['telemetry_orientation'][0][0]['magnetometer_x'][0][0].flatten()
            magy = uas['telemetry_orientation'][0][0]['magnetometer_y'][0][0].flatten()
            magz = uas['telemetry_orientation'][0][0]['magnetometer_z'][0][0].flatten()
        else:
            Q = np.transpose([uas['telemetry_orientation'][0][0]['q0'][0][0].flatten(),
                          uas['telemetry_orientation'][0][0]['q1'][0][0].flatten(),
                          uas['telemetry_orientation'][0][0]['q2'][0][0].flatten(),
                          uas['telemetry_orientation'][0][0]['q3'][0][0].flatten()])

            mx = interp1d(uas['telemetry_orientation'][0][0]['ts'][0][0].flatten(),uas['telemetry_orientation'][0][0]['magnetometer_x'][0][0].flatten(),fill_value = 'extrapolate')(ts)
            my = interp1d(uas['telemetry_orientation'][0][0]['ts'][0][0].flatten(),uas['telemetry_orientation'][0][0]['magnetometer_y'][0][0].flatten(),fill_value = 'extrapolate')(ts)
            mz = interp1d(uas['telemetry_orientation'][0][0]['ts'][0][0].flatten(),uas['telemetry_orientation'][0][0]['magnetometer_z'][0][0].flatten(),fill_value = 'extrapolate')(ts)

            Qap_rp = bae.quat_rponly(Q)
            Qap_rp = np.transpose([interp1d(uas['telemetry_orientation'][0][0]['ts'][0][0].flatten(),Qap_rp[:,0],fill_value='extrapolate')(ts),
                                   interp1d(uas['telemetry_orientation'][0][0]['ts'][0][0].flatten(),Qap_rp[:,1],fill_value='extrapolate')(ts),
                                   interp1d(uas['telemetry_orientation'][0][0]['ts'][0][0].flatten(),Qap_rp[:,2],fill_value='extrapolate')(ts),
                                   interp1d(uas['telemetry_orientation'][0][0]['ts'][0][0].flatten(),Qap_rp[:,3],fill_value='extrapolate')(ts)])

            mag_dec = geomag.declination(np.nanmean(lat),np.nanmean(lon))*pi/180
            magcal = pm.MagCal()
            magcal.init(recompute_yaw)

            mx = np.expand_dims(mx,axis=1)
            my = np.expand_dims(my,axis=1)
            mz = np.expand_dims(mz,axis=1)

            magx,magy,magz = magcal.correct_mags(mx,my,mz)
            M_m = np.hstack([magx,magy,magz])
            Q = bae.mag_correct_q_vec(M_m,Qap_rp,mag_dec=mag_dec)

        if recompute_mhp is None:
            print('NOT IMPLEMENTED!!! Add code and re-run')
        else:
            alpha,beta,q,ias,tas,u,v,w,tpay = pm.compute_data_products(fname,
                                                                       param_file=recompute_mhp,
                                                                       S0_gcs_log=True)
            alpha = interp1d(tpay,alpha,fill_value='extrapolate')(ts)
            beta = interp1d(tpay,beta,fill_value='extrapolate')(ts)
            tas = interp1d(tpay,tas,fill_value='extrapolate')(ts)

        idx = np.argmax(uas['sys'][0][0]['hour'][0][0])
        week = float(uas['sys'][0][0]['week'][0][0][idx])
        seconds = float(uas['sys'][0][0]['hour'][0][0][idx])*3600 + float(uas['sys'][0][0]['min'][0][0][idx])*60 + float(uas['sys'][0][0]['sec'][0][0][idx]) - float(uas['sys'][0][0]['ts'][0][0][idx])
        time_since_str = lu.weeksecondstoutc(week,seconds,datetimeformat = "%Y-%m-%dT%H:%M:%SZ")
        time_offset = lu.weekseconds2unix(week, seconds)

    ##################### S1 or S2 with Separate MHP ###############################
    elif logtype == 'ap_with_mhp':
        # fname must be an array with:
        # fname[0]: ap log as a netCDF or .mat file
        # fname[1]: mhp log as a CSV file
        # fname[2]: toff that puts the AP time into MHP time
        apname = fname[0]
        mhpname = fname[1]
        toff = fname[2]

        state,tstate = lu.get_var(apname,'state')
        gps,tgps = lu.get_var(apname,'gps')

        mhp = pd.read_csv(mhpname)
        mhp = mhp.dropna()
        #mhp = pm.filter_mhp_products(mhp)

        tmhp = mhp['IMU_TIME'].to_numpy()-toff

        magcal = pm.MagCal()
        if 'q0' in state.keys():
          Qap = np.transpose(np.vstack((state['q0'],state['q1'],state['q2'],state['q3'])))
        else:
          Qap = state['q']
        if recompute_yaw is None:
            Q = np.transpose([interp1d(tstate,Qap[:,0],fill_value="extrapolate")(tmhp),
                              interp1d(tstate,Qap[:,1],fill_value="extrapolate")(tmhp),
                              interp1d(tstate,Qap[:,2],fill_value="extrapolate")(tmhp),
                              interp1d(tstate,Qap[:,3],fill_value="extrapolate")(tmhp)])
            magx = np.array([mhp['MAGNETOMETER_X'].values]).T
            magy = np.array([mhp['MAGNETOMETER_Y'].values]).T
            magz = np.array([mhp['MAGNETOMETER_Z'].values]).T
        else:
            Qap_rp = bae.quat_rponly(Qap)
            Q = np.transpose([interp1d(tstate,Qap_rp[:,0],fill_value="extrapolate")(tmhp),
                              interp1d(tstate,Qap_rp[:,1],fill_value="extrapolate")(tmhp),
                              interp1d(tstate,Qap_rp[:,2],fill_value="extrapolate")(tmhp),
                              interp1d(tstate,Qap_rp[:,3],fill_value="extrapolate")(tmhp)])
            mag_dec = geomag.declination(np.nanmean(mhp['LATITUDE']),np.nanmean(mhp['LONGITUDE']))*pi/180
            magcal.init(recompute_yaw)

            magx,magy,magz = magcal.correct_mags(np.array([mhp['MAGNETOMETER_X'].values]).T,
                                                 np.array([mhp['MAGNETOMETER_Y'].values]).T,
                                                 np.array([mhp['MAGNETOMETER_Z'].values]).T)
            M_m = np.hstack([magx,magy,magz])
            Q = bae.mag_correct_q_vec(M_m,Q,mag_dec=mag_dec)

        ts = tmhp

        wind_u = mhp['U'].to_numpy()
        wind_v = mhp['V'].to_numpy()
        wind_w = mhp['W'].to_numpy()
        temp = mhp['AIR_TEMPERATURE'].to_numpy()
        humidity = mhp['HUMIDITY'].to_numpy()
        stat_p = mhp['STATIC_PRESSURE'].to_numpy()

        if recompute_mhp is None:
            alpha = mhp['ALPHA'].to_numpy()
            beta = mhp['BETA'].to_numpy()
            tas = mhp['TAS'].to_numpy()
        else:
            dp0 = mhp['DYNAMIC_PRESSURE_0'].to_numpy()
            dp1 = mhp['DYNAMIC_PRESSURE_1'].to_numpy()
            dp2 = mhp['DYNAMIC_PRESSURE_2'].to_numpy()
            dp3 = mhp['DYNAMIC_PRESSURE_3'].to_numpy()
            dp4 = mhp['DYNAMIC_PRESSURE_4'].to_numpy()
            alpha,beta,q= pm.compute_alpha_beta_q(dp0,dp1,dp2,dp3,dp4,param_file=recompute_mhp)
            ias,tas = lu.compute_ias_tas(q,temp,stat_p,humidity)

        lat =  interp1d(tgps,gps['latitude'],  fill_value='extrapolate')(tmhp)
        lon =  interp1d(tgps,gps['longitude'], fill_value='extrapolate')(tmhp)
        alt =  interp1d(tgps,gps['altitude'],  fill_value='extrapolate')(tmhp)
        if 'velocity.x' in gps.keys():
          vg_x = interp1d(tgps,gps['velocity.x'],fill_value='extrapolate')(tmhp)
          vg_y = interp1d(tgps,gps['velocity.y'],fill_value='extrapolate')(tmhp)
          vg_z = interp1d(tgps,gps['velocity.z'],fill_value='extrapolate')(tmhp)
        else:
          vg_x = interp1d(tgps,gps['velocity_x'],fill_value='extrapolate')(tmhp)
          vg_y = interp1d(tgps,gps['velocity_y'],fill_value='extrapolate')(tmhp)
          vg_z = interp1d(tgps,gps['velocity_z'],fill_value='extrapolate')(tmhp)

        mag_dec = geomag.declination(np.nanmean(lat),np.nanmean(lon))*pi/180

        #idx = np.where(gps['week']>0)[0][0]
        idx = np.argmax(gps['hour'])
        week = float(gps['week'][idx])
        seconds = float(gps['hour'][idx])*3600 + float(gps['minute'][idx])*60 + float(gps['seconds'][idx]) - float(tgps[idx])

        time_since_str = lu.weeksecondstoutc(week,seconds,datetimeformat = "%Y-%m-%dT%H:%M:%SZ")
        time_offset = lu.weekseconds2unix(week, seconds)

    elif logtype == 'altius':

        df = pd.read_csv(fname)
        ts = df['Time Since Launch'].to_numpy()*60
        r = df[' ALTIUS Roll (deg)'].to_numpy()*pi/180
        p = df[' ALTIUS Pitch (deg)'].to_numpy()*pi/180
        y = df[' ALTIUS Yaw (deg)'].to_numpy()*pi/180
        lat = df[' ALTIUS GPS Lat (deg)'].to_numpy()
        lon = df[' ALTIUS GPS Long (deg)'].to_numpy()
        alt = df['ALTIUS GPS Alt (ft MSL)'].to_numpy()*ft2m
        vg_x = df[' ALTIUS INS Velocity North (kts)'].to_numpy()*kts2ms
        vg_y = df[' ALTIUS INS Velocity East (kts)'].to_numpy()*kts2ms
        vg_z = df['ALTIUS INS Velocity Down (kts)'].to_numpy()*kts2ms
        magx = vg_x*0
        magy = vg_x*0
        magz = vg_x*0
        alpha = df[' BST MHTP Alpha (deg)'].to_numpy()*pi/180
        beta = df[' BST MHTP Beta (deg)'].to_numpy()*pi/180
        tas = df['BST MHTP IAS (kts)'].to_numpy()
        #tas = df['ALTIUS TAS (kts)']*kts2ms
        temp = df['Vaisala Air Temp (°C)'].to_numpy()
        humidity = df['Vaisala Air Rel Hum (%)'].to_numpy()
        stat_p = df['Vaisala Air Press (mbar)'].to_numpy()
        wind_u = df['ALTIUS Wind North (kts)'].to_numpy()*kts2ms
        wind_v = df['ALTIUS Wind East (kts)'].to_numpy()*kts2ms
        wind_w = df['ALTIUS Wind Down (kts)'].to_numpy()*kts2ms

        Q = bae.ang2quat_vec(r,p,y)

        week2sec = 604800.
        week = int(np.floor(df['GPS Time'][0]/week2sec))
        seconds = df['GPS Time'][0] - float(week)*week2sec - ts[0]

        time_since_str = lu.weeksecondstoutc(week,seconds,datetimeformat = "%Y-%m-%dT%H:%M:%SZ")
        time_offset = lu.weekseconds2unix(week, seconds)

    sog = np.linalg.norm((np.transpose([vg_x,vg_y])),axis=1)
    course = np.arctan2(vg_y,vg_x)
    r,p,y = bae.quat2ang_vec(Q)
    wspd,wdir = pm.wind_uv_2_ws_dir(wind_u,wind_v)
    ts = np.float64(ts)
    data = {'aptime':ts,
            'time':ts+time_offset,
            'Q': Q,
            'roll': r,
            'pitch': p,
            'yaw': y,
            'lat': lat,
            'lon': lon,
            'altitude': alt,
            'vg_x': vg_x,
            'vg_y': vg_y,
            'vg_z': vg_z,
            'magx': magx.flatten(),
            'magy': magy.flatten(),
            'magz': magz.flatten(),
            'alpha': alpha,
            'beta': beta,
            'tas': tas,
            'sog': sog,
            'course': course,
            'air_temperature': temp+273.15,
            'relative_humidity': humidity,
            'pressure': stat_p,
            'dew_point_temperature': pm.compute_dew_point(temp,humidity)+273.15,
            'humidity_mixing_ratio': pm.compute_mixing_ratio(pm.compute_dew_point(temp,humidity),stat_p),
            'wind_u': wind_u,
            'wind_v': wind_v,
            'wind_w': wind_w,
            'wind_speed': wspd,
            'wind_direction': wdir*180/pi,
            'time_since_str':time_since_str,
           }
    if 'tsurf' in locals():
        data['tsurf'] = tsurf
    if 'laseralt' in locals():
        data['laseralt'] = laseralt
    if ground is not None:
        data['height'] = data['altitude']-ground

    if tfull is not None:
        idx = lu.get_time_indeces(data['aptime'],tfull)
        for key in data.keys():
            if np.ndim(data[key]) == 1:
                data[key] = data[key][idx]
            if np.ndim(data[key]) == 2:
                data[key] = data[key][idx,:]

    return data

def sin_fun(th, th0, a,b):
    return np.sin(th+th0)*a+b

def compute_arcpoint(x,y):
    d = np.linalg.norm([-x,1-y])
    th = 2*np.arcsin(d/2)
    if x < 0:
        th = 2*pi - th
    return th


def get_circle_wind(lat,lon,sog,tas,plot=False):

    x,y = lu.latlon2local(lat,lon)
    xc, yc, r, sigma = taubinSVD(np.transpose([x,y]))
    xp = (x-xc)/r
    yp = (y-yc)/r

    xp_c = 0*xp
    yp_c = 0*yp
    for i,(x,y) in enumerate(zip(xp,yp)):
        res = np.linalg.norm([x,y])
        xp_c[i] = x/res
        yp_c[i] = y/res

    th = 0*xp
    for i,(x,y) in enumerate(zip(xp_c,yp_c)):
        th[i] = compute_arcpoint(x,y)

    speed = sog - tas
    v = curve_fit(sin_fun, th,speed)[0]

    sf_tas = (v[2]+np.mean(tas))/np.mean(tas)
    speed = sog - tas*sf_tas
    v = curve_fit(sin_fun, th,speed)[0]

    wspd = np.abs(v[1])
    f_dir = np.sign(np.diff(th))
    f_dir = f_dir[f_dir != 0]
    f_dir = stats.mode(f_dir)[0]

    if v[1] < 0:
        th_max = 3*pi/2 - v[0]
    else:
        th_max = pi/2 - v[0]
    wdir = th_max - pi/2*f_dir
    wdir = np.mod(wdir , 2*pi)

    if plot:
        phi = np.linspace(0,2*pi,100)
        spd_norm = sin_fun(phi,v[0],v[1],v[2])
        spd_norm -= np.min(spd_norm)
        spd_norm /= np.max(spd_norm)
        fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
        fig.tight_layout()
        ax[0].axis('equal')
        ax[0].grid()
        ax[0].fill(np.sin(phi) + spd_norm*np.sin(phi),np.cos(phi) + spd_norm*np.cos(phi),'gray')
        ax[0].fill(np.sin(phi),np.cos(phi),'white')

        spd_norm2 = 0*speed + speed
        spd_norm2 -= np.min(spd_norm2)
        spd_norm2 /= np.max(spd_norm2)
        ax[0].plot(np.sin(th) + spd_norm2*np.sin(th),np.cos(th) + spd_norm2*np.cos(th),'ok')

        max_sog = np.max(sog)
        #for x,y,s,psi in zip(xp,yp,sog,data['yaw'][idx]):
        #    lu.icon_ua([x,y],psi,sc=1/30,ax=ax[0])

        th_min = np.mod(th_max + pi,2*pi)
        X = np.arange(-1, 1.1, .5)
        Y = np.arange(-1, 1.1, .5)
        theta = 3*pi/2 - wdir
        U = np.zeros((len(X),len(Y))) + wspd*np.cos(theta)
        V = np.zeros((len(X),len(Y))) + wspd*np.sin(theta)
        ax[0].set_title('wspd = %.1f m/s, wdir = %.1f deg'%(wspd,wdir*180/pi))
        ax[0].quiver(X, Y, U, V,width=0.002,pivot='middle')
        ax[0].quiver(np.sin(th_max), np.cos(th_max), -wspd*np.sin(wdir), -wspd*np.cos(wdir),color='red',width=0.004,pivot='middle')
        ax[0].quiver(np.sin(th_min), np.cos(th_min), -wspd*np.sin(wdir), -wspd*np.cos(wdir),color='red',width=0.004,pivot='middle')

        ax[1].plot(th*180/pi,speed,'ok')
        ax[1].plot(phi*180/pi, sin_fun(phi,v[0],v[1],v[2]),'--',color='gray')
        ax[1].set_xlabel('Angle on circle [deg]')
        ax[1].set_ylabel('Speed (sog - tas) [m/s]')
        ax[1].plot(np.array([th_max, th_max])*180/pi,[0, v[1]+v[2]],'--',color='gray')
        ax[1].plot(np.array([th_min, th_min])*180/pi,[0,-v[1]+v[2]],'--',color='gray')
        ax[1].grid()
        ax2 = fig.add_axes([.75, .75, .2, .2])
        ax2.grid('on')
        ax2.plot(lon,lat,'.k')
        ax2.ticklabel_format(useOffset=False)

    u,v = pm.wind_ws_dir_2_uv(wspd,wdir)
    return wspd,wdir,u,v,sf_tas

def get_circle_wind2(course,sog,tas,plot=False):
    speed = sog - tas
    v = curve_fit(cos_fun, course,speed)[0]

    sf_tas = (v[2]+np.mean(tas))/np.mean(tas)
    speed = sog - tas*sf_tas
    v = curve_fit(cos_fun, course,speed)[0]

    wspd = np.abs(v[1])

    f_dir = np.sign(np.diff(course))
    f_dir = f_dir[f_dir != 0]
    f_dir = stats.mode(f_dir)[0][0]

    # Old method, didn't work for v[1] is -ve
    wdir = np.mod(-v[0]+pi , 2*pi)

#if v[1] < 0:
#        th_max = 3*pi/2 - v[0]
#    else:
#        th_max = pi/2 - v[0]
#    wdir = th_max - pi/2*f_dir
#    wdir = np.mod(wdir , 2*pi)

    ut,vt = pm.wind_ws_dir_2_uv(wspd,wdir)
    if plot:
        th = np.linspace(-pi,pi,100)
        fig,ax = plt.subplots(1,1)

        ax.plot(course*180/pi,speed,'.')
        ax.plot(th*180/pi,cos_fun(th,v[0],v[1],v[2]),'-r')
        ax.set_title('wspd = %.1f m/s, wdir = %.1f deg'%(wspd,wdir*180/pi))
        ax.set_xlabel('Angle on circle [deg]')
        ax.set_ylabel('Speed (sog - tas) [m/s]')
    return wspd,wdir,ut,vt,sf_tas

def check_circle_wind(data,tcirc,fit_type=1):
    fig, ax = plt.subplots(4, 1, sharex=True)
    for a in ax:
        a.grid()
    fig.tight_layout()

    ax[0].plot(data['aptime'], data['wind_u'],'--',color='gray')
    ax[1].plot(data['aptime'], data['wind_v'],'--',color='gray')
    ax[2].plot(data['aptime'], data['wind_speed'],'--',color='gray')
    ax[3].plot(data['aptime'], data['wind_direction'],'--',color='gray')
    ax[0].set_ylabel('wind_u')
    ax[1].set_ylabel('wind_v')
    ax[2].set_ylabel('wind_speed')
    ax[3].set_ylabel('wind_direction')

    for tr in tcirc:
        idx = lu.get_time_indeces(data['aptime'],tr)
        if fit_type == 1:
            wspd,wdir,ut,vt,sf = get_circle_wind(data['lat'][idx],data['lon'][idx],data['sog'][idx],data['tas'][idx],plot=False)
        if fit_type == 2:
            wspd,wdir,ut,vt,sf = get_circle_wind2(data['course'][idx],data['sog'][idx],data['tas'][idx],plot=False)

        ax[0].plot(data['aptime'][idx], data['wind_u'][idx],color='k',linewidth=2)
        ax[0].plot(np.array([data['aptime'][idx[0]], data['aptime'][idx[-1]]]), ut*np.array([1.,1.]),'--r')

        ax[1].plot(data['aptime'][idx], data['wind_v'][idx],color='k',linewidth=2)
        ax[1].plot(np.array([data['aptime'][idx[0]], data['aptime'][idx[-1]]]), vt*np.array([1.,1.]),'--r')

        ax[2].plot(data['aptime'][idx], data['wind_speed'][idx],color='k',linewidth=2)
        ax[2].plot(np.array([data['aptime'][idx[0]], data['aptime'][idx[-1]]]), wspd*np.array([1.,1.]),'--r')

        ax[3].plot(data['aptime'][idx], data['wind_direction'][idx],color='k',linewidth=2)
        ax[3].plot(np.array([data['aptime'][idx[0]], data['aptime'][idx[-1]]]), wdir*180/pi*np.array([1.,1.]),'--r')

        return ax

def cos_fun(th, th0, a,b):
    return np.cos(th+th0)*a+b


def yaw_err_fun(yc,Va_b,Vg,q,ut,vt):
    qc = np.array([np.cos(yc/2),0,0,np.sin(yc/2)])
    q = bae.qprod(q,qc)
    wind = pm.wind_from_vab_vg_q(Va_b,Vg,q)
    return np.sqrt( (ut-wind[1])**2 + (vt-wind[0])**2 )

def find_yaw_offset(Va_b,Vg,q,ut,vt):
    res = minimize_scalar(yaw_err_fun,args=(Va_b,Vg,q,ut,vt))
    return res.x

def get_wind_correct_cir_data(data,tcirc,plot=False,fit_type=1):

    YC = np.array([])
    Y = np.array([])
    sf_tas = np.array([])

    for tr in tcirc:
        idx = lu.get_time_indeces(data['aptime'],tr)
        if fit_type == 1:
            wspd,wdir,ut,vt,sf = get_circle_wind(data['lat'][idx],data['lon'][idx],data['sog'][idx],data['tas'][idx],plot=plot)
        if fit_type == 2:
            wspd,wdir,ut,vt,sf = get_circle_wind2(data['course'][idx],data['sog'][idx],data['tas'][idx],plot=plot)
        tas = data['tas'][idx]*sf
        alpha = data['alpha'][idx]
        beta = data['beta'][idx]
        vg_x = data['vg_x'][idx]
        vg_y = data['vg_y'][idx]
        vg_z = data['vg_z'][idx]
        q = data['Q'][idx]

        Va_b = pm.body_frame_wind(tas,alpha,beta)
        Vg = np.transpose([vg_x,vg_y,vg_z])
        yc = tas*0

        for i,(va_b,vg,qm) in enumerate(zip(Va_b,Vg,q)):
            yc[i] = find_yaw_offset(va_b,vg,qm,ut,vt)


        YC = np.append(YC,yc)
        Y = np.append(Y,data['yaw'][idx])
        sf_tas = np.append(sf_tas,sf)
    return Y,YC,sf_tas


def wind_correct_cir_fit(data,tcirc,plot=False,fit_type=1):

    Y,YC,sf_tas = get_wind_correct_cir_data(data,tcirc,plot=plot,fit_type=fit_type)
    yawc_fit = np.poly1d(np.polyfit(Y, YC, 7))

    if plot:
        th = np.linspace(-pi,pi,200)
        fig, ax = plt.subplots(1, 1)
        ax.grid()
        ax.set_xlabel('Heading [deg]')
        ax.set_ylabel('Yaw Correction [deg]')
        ax.plot(Y*180/pi, YC*180/pi,'.')
        ax.plot(th*180/pi, yawc_fit(th)*180/pi,'--r',label='Fit',linewidth=3)

    return yawc_fit,np.mean(sf_tas)

def correct_q_cir(data,yawc_fit):
    Q2 = data['Q']*0
    for i,(yin,q) in enumerate(zip(data['yaw'],data['Q'])):
        yc = yawc_fit(yin)
        q_correct = np.array([np.cos(yc/2),0,0,np.sin(yc/2)])
        Q2[i] = bae.qprod(q_correct,q)
        data['yaw'][i] = bae.quat2yaw(Q2[i])
    data['Q'] = Q2
    return data

def wind_cir_correct(data_in,tcirc,plot=False,f_yc=None,fit_type=1):
    data = data_in.copy()
    if f_yc is None:
        yawc_fit,sf = wind_correct_cir_fit(data,tcirc,plot=plot,fit_type=fit_type)
    else:
        yawc_fit = f_yc[0]
        sf = f_yc[1]

    data['tas'] *= sf
    data = correct_q_cir(data,yawc_fit)
    W = pm.wind_from_tas_alpha_beta(data['tas'],data['alpha'],data['beta'],data['vg_x'],data['vg_y'],data['vg_z'],data['Q'])
    data['wind_u'] = W[:,1]
    data['wind_v'] = W[:,0]
    data['wind_w'] = W[:,2]
    wspd,wdir = pm.wind_uv_2_ws_dir(data['wind_u'],data['wind_v'])
    data['wind_speed'] = wspd
    data['wind_direction'] = wdir*180/pi
    return data,yawc_fit,sf

def find_toff_ap_mhp(apname,mhpname,tr=None,plot=False):
    df = pd.read_csv(mhpname)
    gyr,tgyr = lu.get_var(apname,'gyr')

    if tr is None:
        tstart,tstop = lu.flighttimes(apname)
        tr = np.array([tstart[0]+20,tstop[0]-20])

    idx = lu.get_time_indeces(gyr['system_time'],tr)
    ts = gyr['system_time'][idx]

    a = gyr['z'][idx]
    b = interp1d(df['IMU_TIME'].to_numpy(),
                    df['GYROSCOPE_Z'].to_numpy(),
                    fill_value='extrapolate')(ts)
    toff = find_toff(ts,a,b)

    ts = gyr['system_time']+toff
    idx = lu.get_time_indeces(ts,np.array([tr[0],tr[0]+20]))
    ts = ts[idx]
    a = gyr['z'][idx]
    b = interp1d(df['IMU_TIME'].to_numpy(),df['GYROSCOPE_Z'].to_numpy(),fill_value='extrapolate')(ts)

    toff += find_toff(ts,a,b)
    if plot:
      plt.figure()
      plt.plot(gyr['system_time'], gyr['z']*180/pi,label='AP')
      plt.plot(df['IMU_TIME'].to_numpy()-toff,df['GYROSCOPE_Z'].to_numpy()*180/pi,label='MHP')
      plt.legend()
      plt.grid()

    return toff

def find_toff(ts,a,b):
    A = fftpack.fft(a)
    B = fftpack.fft(b)
    Ar = -A.conjugate()
    Br = -B.conjugate()
    shifts = [np.argmax(np.abs(fftpack.ifft(Ar*B))),
              np.argmax(np.abs(fftpack.ifft(A*Br)))]
    shift = np.min(shifts)
    sign = np.argmin(shifts)
    toff = np.mean(np.diff(ts))*shift
    if sign:
        toff*=-1
    return toff

def plot_wind_telem(data,tr=None):
    if tr is None:
        idx = np.arange(0,len(data['aptime']))
    else:
        idx = lu.get_time_indeces(data['aptime'],tr)

    i=0
    fg,ax = plt.subplots(9,1,sharex=True)
    ax[i].plot(data['aptime'][idx],data['altitude'][idx]*1000,label='Alt')
    ax[i].grid()
    ax[i].legend()

    i+=1
    ax[i].plot(data['aptime'][idx],data['tas'][idx],label='TAS')
    ax[i].plot(data['aptime'][idx],data['sog'][idx],label='SOG')
    ax[i].grid()
    ax[i].legend()

    i+=1
    ax[i].plot(data['aptime'][idx],data['vg_x'][idx],label='Vx')
    ax[i].plot(data['aptime'][idx],data['vg_y'][idx],label='Vy')
    ax[i].plot(data['aptime'][idx],data['vg_z'][idx],label='Vz')
    ax[i].grid()
    ax[i].legend()

    i+=1
    ax[i].plot(data['aptime'][idx],data['roll'][idx]*180/pi,label='roll')
    ax[i].plot(data['aptime'][idx],data['pitch'][idx]*180/pi,label='pitch')
    ax[i].grid()
    ax[i].legend()

    i+=1
    ax[i].plot(data['aptime'][idx],data['yaw'][idx]*180/pi,label='yaw')
    ax[i].plot(data['aptime'][idx],data['course'][idx]*180/pi,label='course')
    ax[i].grid()
    ax[i].legend()

    i+=1
    ax[i].plot(data['aptime'][idx],data['alpha'][idx]*180/pi,label='alpha')
    ax[i].plot(data['aptime'][idx],data['beta'][idx]*180/pi,label='beta')
    ax[i].grid()
    ax[i].legend()

    i+=1
    ax[i].plot(data['aptime'][idx],data['temp'][idx],label='temp')
    ax[i].grid()
    ax[i].legend()

    i+=1
    ax[i].plot(data['aptime'][idx],data['rel_hum'][idx],label='RH')
    ax[i].grid()
    ax[i].legend()

    i+=1
    ax[i].plot(data['aptime'][idx],data['wind_u'][idx],label='wind_u')
    ax[i].plot(data['aptime'][idx],data['wind_v'][idx],label='wind_v')
    ax[i].plot(data['aptime'][idx],data['wind_w'][idx],label='wind_w')
    ax[i].grid()
    ax[i].legend()


def data2WMO_nc(data,fname = None,savedir='',processingLevel='raw',operatorID='025',airframeID='',flight_id='',platform_name='',datakey = 'wmo_key.xml',version=None):

    if fname is not None:
        savedir = os.path.dirname(fname) + '/'
        fname = os.path.basename(fname)

    fname_time_str = datetime.datetime.strptime(data['time_since_str'], "%Y-%m-%dT%H:%M:%SZ").strftime('%Y%m%d%H%M%SZ')
    if fname is None:
        fname = 'UASDC_'+operatorID+'_'+airframeID+'_'+fname_time_str+'.nc'

    if os.path.exists(savedir+fname):
        print('Deleting: '+savedir+fname)
        os.remove(savedir+fname)


    rootgrp = nc.Dataset(savedir+fname, 'w', format='NETCDF4')
    rootgrp.Conventions = 'CF-1.8, WMO-CF-1.0'
    rootgrp.wmo__cf_profile = 'FM 303- draft'
    rootgrp.featureType = 'trajectory'
    rootgrp.processing_level = processingLevel
    rootgrp.platform_name = platform_name
    rootgrp.flight_id = flight_id
    if version is not None:
      rootgrp.version = version
    obs = rootgrp.createDimension('obs', len(data['time']))
    #obs = rootgrp.createDimension('obs', None) # For appending variables

    nckey = xml2nckey(datakey)
    for value in zip(nckey['varname'],nckey['vartype'],nckey['units'],nckey['coordinates'],nckey['long_name'],nckey['processing_level'],nckey['ncvarname']):
        varname,vartype,units,coordinates,long_name,processing_level,ncvarname = value
        if varname in data:
            var = rootgrp.createVariable(ncvarname,vartype,('obs',),fill_value=np.nan)
            rootgrp.variables[ncvarname][:] = data[varname]
            if units is not None:
                var.units = units
            if coordinates is not None:
                var.coordinates = coordinates
            if long_name is not None:
                var.long_name = long_name
            if processing_level is not None:
                var.processing_level = processing_level
        else:
            print('WARNING [data2WMO_nc.py]: %s variable not found'%varname)

    print('Saving data to: '+fname)
    rootgrp.close()
    return savedir+fname

def WMO_nc2data(fname,datakey=None):
  data = {}
  rg = nc.Dataset(fname, 'r', format='NETCDF4')

  if datakey is None:
    for key in rg.variables.keys():
      data[key] = np.array(rg.variables[key][:])
  else:
    ncvars = rg.variables.keys()
    nckey = xml2nckey(datakey)
    for value in zip(nckey['varname'],nckey['vartype'],nckey['units'],nckey['coordinates'],nckey['long_name'],nckey['processing_level'],nckey['ncvarname']):
        varname,vartype,units,coordinates,long_name,processing_level,ncvarname = value
        if ncvarname in ncvars:
          data[varname] = np.array(rg.variables[ncvarname])
        else:
          print('WARNING (WMO_nc2data): %s not found in %s'%(ncvarname,fname))

  data['time_since_str'] = rg['time'].units[14:]
  data['datetime'] = lu.get_datetime_vec(data['time'],data['time_since_str'])
  data['fname'] = os.path.basename(fname)
  rg.close()
  return data

def reduce_wmo_file(fname,tsample='1000L',datakey = 'wmo_key.xml'):
    # tsample in milliseconds
    data = WMO_nc2data(fname)

    data_new = data.copy()
    del_array = []
    for k in data.keys():
        if np.shape(data['time']) != np.shape(data[k]):
            del_array.append(k)
            del data_new[k]

    df = pd.DataFrame.from_dict(data_new)

    dt = lu.get_datetime_vec(data['time'],data['time_since_str'])
    df['Datetime'] = pd.to_datetime(dt)
    df = df.set_index('Datetime')

    df2 = df.resample(tsample).mean().ffill(limit=1)
    df2 = df2.dropna()
    data_new = {'time':df2['time'].to_numpy()}
    for k in df2.keys():
        data_new[k] = df2[k].to_numpy()

    for var in del_array:
        data_new[var] = data[var]

    data_new['time'] = lu.get_seconds_from_datetime(df2.index.to_pydatetime(),data['time_since_str'])
    return data2WMO_nc(data_new, fname = fname,datakey=datakey)

def reduce_dict(data,tsample='1000L'):
    # tsample in milliseconds
    data_new = data.copy()
    del_array = []
    for k in data.keys():
        if np.shape(data['time']) != np.shape(data[k]):
            del_array.append(k)
            del data_new[k]

    df = pd.DataFrame.from_dict(data_new)

    dt = lu.get_datetime_vec(data['time'],data['time_since_str'])
    df['Datetime'] = pd.to_datetime(dt)
    df = df.set_index('Datetime')

    df2 = df.resample(tsample).mean().ffill(limit=1)
    data_new = {'time':df2['time'].to_numpy()}
    for k in df2.keys():
        data_new[k] = df2[k].to_numpy()

    for var in del_array:
        data_new[var] = data[var]

    data_new['time'] = lu.get_seconds_from_datetime(df2.index.to_pydatetime(),data['time_since_str'])
    return data_new


def plot_met(data,ax=None,useAPtime=False,pvars=['air_temperature','relative_humidity','pressure','dew_point_temperature','wind_speed','wind_direction','wind_w']):
  if useAPtime:
    dt = data['aptime']
  else:
    dt = lu.get_datetime_vec(data['time'],data['time_since_str'])
  if ax is None:
    fig,ax = plt.subplots(len(pvars),1,sharex=True)
    fig.tight_layout()

  for a,var in zip(ax,pvars):
     a.grid('on')
     a.plot(dt,data[var],'.-')
     a.set_ylabel(var)
  a.set_xlabel('Time')
  return ax

def check_circle_range(data,tcirc=None):
    fig,ax = plt.subplots(6,1,sharex=True)
    ax[0].grid()
    ax[0].set_ylabel('Roll')
    ax[1].grid()
    ax[1].set_ylabel('Yaw/Course')
    ax[2].grid()
    ax[2].set_ylabel('Speeds')
    ax[3].grid()
    ax[3].set_ylabel('Alt')
    ax[4].grid()
    ax[4].set_ylabel('Lat')
    ax[5].grid()
    ax[5].set_ylabel('Lon')

    ax[0].plot(data['aptime'], data['roll']*180/pi,'.',color='xkcd:blue',label='roll')
    ax[0].plot(data['aptime'], data['pitch']*180/pi,'.',color='xkcd:red',label='pitch')
    ax[0].legend()
    ax[1].plot(data['aptime'], data['yaw']*180/pi,color='gray',label='yaw')
    ax[1].plot(data['aptime'], data['course']*180/pi,color='green',label='Course')
    ax[1].legend()
    ax[2].plot(data['aptime'], data['tas'],color='gray',label='tas')
    ax[2].plot(data['aptime'], data['sog'],color='green',label='sog')
    ax[2].legend()
    ax[3].plot(data['aptime'], data['altitude'],color='gray')
    ax[4].plot(data['aptime'], data['lat'],color='gray')
    ax[5].plot(data['aptime'], data['lon'],color='gray')

    if tcirc is not None:
        for tr in tcirc:
            idx = lu.get_time_indeces(data['aptime'],tr)
            ax[0].plot(data['aptime'][idx], data['roll'][idx]*180/pi,'.')
            ax[1].plot(data['aptime'][idx], data['yaw'][idx]*180/pi,'.')
            ax[1].plot(data['aptime'][idx], data['course'][idx]*180/pi,'.')
            ax[2].plot(data['aptime'][idx], data['tas'][idx],'.')
            ax[2].plot(data['aptime'][idx], data['sog'][idx],'.')
            ax[3].plot(data['aptime'][idx], data['altitude'][idx],'.')
            ax[4].plot(data['aptime'][idx], data['lat'][idx],'.')
            ax[5].plot(data['aptime'][idx], data['lon'][idx],'.')

def ftutn2mhp(fname):
  df = pd.read_csv(fname)
  fname_out = fname[:-4]+'_mhp.csv'
  col1 = ['IMU_TIME',
          'STATIC_PRESSURE',
          'DYNAMIC_PRESSURE_0',
          'DYNAMIC_PRESSURE_1',
          'DYNAMIC_PRESSURE_2',
          'DYNAMIC_PRESSURE_3',
          'DYNAMIC_PRESSURE_4',
          'AIR_TEMPERATURE',
          'HUMIDITY',
          'GYROSCOPE_X',
          'GYROSCOPE_Y',
          'GYROSCOPE_Z',
          'ACCELEROMETER_X',
          'ACCELEROMETER_Y',
          'ACCELEROMETER_Z',
          'MAGNETOMETER_X',
          'MAGNETOMETER_Y',
          'MAGNETOMETER_Z',
          'ALPHA',
          'BETA',
          'U',
          'V',
          'W',
         ]

  table = np.transpose([df['MHP MEASUREMENT TIME [s]'].to_numpy(),
                        df['MHP STATIC PRESSURE [Pa]'].to_numpy(),
                        df['MHP DYNAMIC PRESSURE 0 [Pa]'].to_numpy(),
                        df['MHP DYNAMIC PRESSURE 1 [Pa]'].to_numpy(),
                        df['MHP DYNAMIC PRESSURE 2 [Pa]'].to_numpy(),
                        df['MHP DYNAMIC PRESSURE 3 [Pa]'].to_numpy(),
                        df['MHP DYNAMIC PRESSURE 4 [Pa]'].to_numpy(),
                        df['MHP AIR TEMP [deg C]'].to_numpy(),
                        df['MHP HUMIDITY [%]'].to_numpy(),
                        df['MHP GYROSCOPE X [rad/s]'].to_numpy(),
                        df['MHP GYROSCOPE Y [rad/s]'].to_numpy(),
                        df['MHP GYROSCOPE Z [rad/s]'].to_numpy(),
                        df['MHP ACCELEROMETER X [g]'].to_numpy(),
                        df['MHP ACCELEROMETER Y [g]'].to_numpy(),
                        df['MHP ACCELEROMETER Z [g]'].to_numpy(),
                        df['MHP MAGNETOMETER X [uT]'].to_numpy(),
                        df['MHP MAGNETOMETER Y [uT]'].to_numpy(),
                        df['MHP MAGNETOMETER Z [uT]'].to_numpy(),
                        df['MHP alpha [%]'].to_numpy(),
                        df['MHP beta [%]'].to_numpy(),
                        df['MHP beta [%]'].to_numpy()*0,
                        df['MHP beta [%]'].to_numpy()*0,
                        df['MHP beta [%]'].to_numpy()*0]
                      )

  mhp = pd.DataFrame(table,columns = col1)
  mhp.to_csv(fname_out,index=False)
  print('Saving to %s: '%fname_out)
  return fname_out

def xml2nckey(fname):
    tree = ET.parse(fname)
    root = tree.getroot()
    var_elems = []

    r = root.find('var')

    for v in r.iterchildren():
        var_elems.append(v.tag)

    nckey = {element: [] for element in var_elems}

    for idx,r in enumerate(root.findall('var')):
        for elem in var_elems:
            v = r.find(elem)
            if v is not None:
                nckey[elem].append(v.text)

    return nckey

def xml2summary(fname):
  tree = ET.parse(fname)
  root = tree.getroot()
  var_elems = []
  for v in root.iterchildren():
    var_elems.append(v.tag)

  var_elems

  varkey = {element: [] for element in var_elems}

  for elem in var_elems:
      v = root.find(elem)
      if v is not None:
          varkey[elem] = v.text
  return varkey

def recalc_wind(data_in,wind_w_offset = 0):
  data = data_in.copy()
  W = pm.wind_from_tas_alpha_beta(data['tas'],data['alpha'],data['beta'],data['vg_x'],data['vg_y'],data['vg_z'],data['Q'])
  data['wind_u'] = W[:,1]
  data['wind_v'] = W[:,0]
  data['wind_w'] = W[:,2] - wind_w_offset
  wspd,wdir = pm.wind_uv_2_ws_dir(data['wind_u'],data['wind_v'])
  data['wind_speed'] = wspd
  data['wind_direction'] = wdir*180/pi

  return data

def plot_profiles(datas,
                  #svars = ['relative_humidity','pressure','air_temperature','wind_u','wind_v'],
                  svars = ['relative_humidity','air_temperature','wind_speed','wind_direction','wind_w'],
                  colors = ['xkcd:black',
                            'xkcd:blue',
                            'xkcd:orange',
                            'xkcd:green',
                            'xkcd:red',
                            'xkcd:purple',
                            'xkcd:goldenrod',
                            'xkcd:grey',
                            'xkcd:sky blue',
                            'xkcd:lavender',
                            'xkcd:vomit',
                            'xkcd:dusty blue',
                            'xkcd:barbie pink',
                            'xkcd:silver',
                            'xkcd:brown',
                            'xkcd:white','xkcd:white','xkcd:white','xkcd:white','xkcd:white',
                            'xkcd:white','xkcd:white','xkcd:white','xkcd:white','xkcd:white',
                            'xkcd:white','xkcd:white','xkcd:white','xkcd:white','xkcd:white'],
                  dep_var = 'altitude',
                  print_dist = False,
                 ):
    fig = plt.figure(constrained_layout=True)
    gs = GridSpec(2, len(svars), figure=fig,height_ratios=[8,1])
    ax_time = fig.add_subplot(gs[1, :])
    ax = []
    for idx in np.arange(0,len(svars)):
        ax.append(fig.add_subplot(gs[0, idx]))

    data = datas[0]
    lat_s0 = np.nanmedian(data['lat'])
    lon_s0 = np.nanmedian(data['lon'])
    hgt = 0
    for i,data in enumerate(datas):
        for idx,var in enumerate(svars):
            ax[idx].plot(data[var],data[dep_var],'.',color=colors[i],label=data['fname'])
            ax[idx].grid('on')
            ax[idx].set_xlabel(var)
            if i == 0 and idx == 0:
                ax[idx].set_ylabel(dep_var)
#            if i == 0:
#                ax[idx].invert_yaxis()

        lat = np.nanmedian(data['lat'])
        lon = np.nanmedian(data['lon'])
        p = ax_time.plot([data['datetime'][0],data['datetime'][-1]],[hgt,hgt],linewidth=5,color=colors[i],label = '%.1f km'%(lu.lla2dist(lat_s0,lon_s0,lat,lon)/1000))
        hgt += 0.002
        ax_time.grid('on')

    ax_time.set_xlabel('Date/Time UTC')
    ax[0].legend()
    if print_dist:
      ax_time.legend()

def kml_p3_drops(datas,savedir = ''):
    cols = ['ff000000',
            'ff0343df',
            'fff97306',
            'ff15b01a',
            'ffe50000',
            'ff7e1e9c',
            'fffac205',
            'ff929591',
            'ff75bbfd',
            'ffc79fef',
            'ffa2a415',
            'ff5a86ad',
            'fffe46a5',
            'ffc5c9c7',
            'ff653700',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
            'ffffffff',
           ]

    for idx,data in enumerate(datas):
        data['lon'] = data['lon'][~np.isnan(data['lat'])]
        data['altitude'] = data['altitude'][~np.isnan(data['lat'])]
        data['lat'] = data['lat'][~np.isnan(data['lat'])]
        ind = data['fname'].rfind('.')
        fname = data['fname'][0:ind]+'.kml'
        lu.make_kml(data['lat'],data['lon'],data['altitude'],savedir+fname,color=cols[idx])

def dfile2data(dname):
    df = pd.read_csv(dname,
                     on_bad_lines='skip',
                     skiprows=[0,1,3,4,5],
                     delimiter='\t')

    df = df.replace(9999,np.nan)
    df = df.replace(999,np.nan)
    df = df.replace(99,np.nan)
    data = {'lat':df['Latitude'].to_numpy(),
            'lon':df['Longitude'].to_numpy(),
            'altitude':df['Altitude'].to_numpy(),
            'pressure':df['Press'].to_numpy(),
            'relative_humidity':df['Humid'].to_numpy(),
            'air_temperature':df['Temp'].to_numpy(),
            'wind_direction':df['Dir'].to_numpy(),
            'wind_speed':df['Spd'].to_numpy(),
           }
    u,v = pm.wind_ws_dir_2_uv(data['wind_speed'],data['wind_direction']*pi/180)
    data['wind_u'] = u
    data['wind_v'] = v
    data['fname'] = os.path.basename(dname)

    timesec = [float(val[0:2])*3600+float(val[2:4])*60+float(val[4:]) for val in df['Time'].apply(str)]
    basetime = datetime.datetime.strptime(str(df['Date'][0]),'%y%m%d')
    data['datetime'] = lu.get_datetime_vec(timesec,str(df['Date'][0]),datetime_format = '%y%m%d')
    return data

def remove_bad_wind(data,tbad):
  idx = lu.get_time_indeces(data['aptime'],tbad)
  data['wind_u'][idx] = np.nan
  data['wind_v'][idx] = np.nan
  data['wind_w'][idx] = np.nan
  data['wind_speed'][idx] = np.nan
  data['wind_direction'][idx] = np.nan
  return data

def print_s0_summary(fname):
  start,stop = lu.flighttimes(fname)
  print(os.path.basename(fname)+':')
  print('\tDate and Takeoff Time:\t%s (ZULU)'%lu.get_datetime_aplog(fname,t_start=start[0]))
  print('\tTotal TOF (min): \t%.2f min'%((stop[0]-start[0])/60))
  print('\tS0 Serial Number:\t%i'%lu.get_info_aplog(fname)[1])
  telem_pos,ttelem_pos = lu.get_var(fname,'telem_pos')
  telem_sys,ttelem_sys = lu.get_var(fname,'telem_sys')
  tlaunch_w_gps = ttelem_sys[np.where(( (ttelem_sys >= start[0]) & (telem_sys['pdop'] < 3) ))[0][0]]
  idx = np.where(ttelem_pos >= tlaunch_w_gps)[0][0]
  print('\tLaunch Altitude:\t%.1f m [MSL]'%telem_pos['gps_altitude'][idx])
  print('\tLaunch Latitude:\t%.6f deg'%telem_pos['latitude'][idx])
  print('\tLaunch Longitude:\t%.6f deg'%telem_pos['longitude'][idx])

  tlast_w_gps = ttelem_sys[np.where(( (ttelem_sys >= start[0]) & (telem_sys['pdop'] < 3) ))[0][-1]]
  if tlast_w_gps > ttelem_pos[-1]:
    tlast_w_gps = ttelem_pos[-1]
  idx = np.where(ttelem_pos >= tlast_w_gps)[0][0]
  print('\tTermination Latitude:\t%.6f'%telem_pos['latitude'][idx])
  print('\tTermination Longitude:\t%.6f'%telem_pos['longitude'][idx])
  print('\tEXTRA:')
  print('\tCruise Power: %.1f W'%lu.get_cruise_power(fname))
  print('\tFinal Batt: %.1f %%'%telem_sys['batt_percent'][-1])

def make_netcdf(fname,
                useGPStime = False,
                tbad = None,
                tcirc = None,
                datakey=f'{cur_path}/hurricane_key.xml',
                logtype = 's0_ap',
                flight_id='',
                processingLevel = 'a3',
                airframeID='BSTS0',
                savedir = '',
                p2w = None,
                tstart_buffer = 30,
                tstop_buffer = 0,
                tfull = None,
               ):

  tstart,tstop = lu.flighttimes(fname)
  if tfull is None:
    tfull = np.array([tstart[0]+tstart_buffer,tstop[0]-tstop_buffer])


  data = normalize_log_data(fname,
                            tfull = tfull,
                            logtype = logtype,
                            recompute_mhp=f'{cur_path}/mhp_coeff_2023_02_23.mat',
                            useGPStime = useGPStime,
                            recompute_yaw=f'{cur_path}/cal_blank.xml')

  if useGPStime:
    data = recalc_wind(data,wind_w_offset=0)
  if tbad is not None:
    data = remove_bad_wind(data,tbad)
  if p2w is not None:
    data['wind_w'] = data['wind_w'] - (p2w[0]*data['pitch']+p2w[1])

  ncname = data2WMO_nc(data,
                       savedir=savedir,
                       airframeID=airframeID,
                       datakey=datakey,
                       flight_id=flight_id,
                       processingLevel = processingLevel,
                       platform_name='')
  return ncname

def get_hurricane_summary(ncname):
    rg = nc.Dataset(ncname,'r')
    sg = rg['Summary']
    df = pd.DataFrame.from_dict({
                                'filename':[os.path.basename(ncname)],
                                'datetime':[sg.datetime_takeoff_zulu],
                                'ac_serial':[sg.ac_serial],
                                'drop_ac':[sg.drop_ac],
                                'storm_name':[sg.storm_name],
                                'mission_id':[sg.mission_id],
                                'mission_type':[sg.mission_type],
                                'launch_lat':[sg['launch_lat'][:].data],
                                'launch_lon':[sg['launch_lon'][:].data],
                                'launch_alt':[sg['launch_alt'][:].data],
                                'terminate_lat':[sg['terminate_lat'][:].data],
                                'terminate_lon':[sg['terminate_lon'][:].data],
                                'max_range':[sg['max_range'][:].data],
                                'time_of_flight':[sg['time_of_flight'][:].data],
                                'errors':[sg.errors],
                                'project':[sg.project],
                                'data_product':[sg.data_product],
                                'remarks':[sg.remarks],
                                })
    return df

def add_hurricane_sum(wmo_nc,
                      ac_nc,
                      ss_nc=None,
                      input_xml=None,
                     ):

  rg = nc.Dataset(wmo_nc, 'a')
  sum_grp = rg.createGroup("Summary")


  start,stop = lu.flighttimes(ac_nc)
  filename = os.path.basename(ac_nc)

  sum_grp.datetime_takeoff_zulu = lu.get_datetime_aplog(ac_nc,t_start=start[0])
  sum_grp.ac_serial = lu.get_info_aplog(ac_nc)[0]+'-'+str(lu.get_info_aplog(ac_nc)[1])

  var = sum_grp.createVariable('time_of_flight','f4')
  var[:] = (stop[0]-start[0])/60
  var.units = 'minutes'


  telem_pos,ttelem_pos = lu.get_var(ac_nc,'telem_pos')
  telem_sys,ttelem_sys = lu.get_var(ac_nc,'telem_sys')
  tlaunch_w_gps = ttelem_sys[np.where(( (ttelem_sys >= start[0]) & (telem_sys['pdop'] < 3) ))[0][0]]
  idx = np.where(ttelem_pos >= tlaunch_w_gps)[0][0]
  var = sum_grp.createVariable('launch_lat','f4')
  var.units = 'degrees_north'
  var[:] = telem_pos['latitude'][idx]
  var = sum_grp.createVariable('launch_lon','f4')
  var.units = 'degrees_east'
  var[:] = telem_pos['longitude'][idx]
  var = sum_grp.createVariable('launch_alt','f4')
  var.units = 'meters'
  var[:] = telem_pos['gps_altitude'][idx]

  tlast_w_gps = ttelem_sys[np.where(( (ttelem_sys >= start[0]) & (telem_sys['pdop'] < 3) ))[0][-1]]
  if tlast_w_gps > ttelem_pos[-1]:
    tlast_w_gps = ttelem_pos[-1]
  idx = np.where(ttelem_pos >= tlast_w_gps)[0][0]


  var = sum_grp.createVariable('terminate_lat','f4')
  var.units = 'degrees_north'
  var[:] = telem_pos['latitude'][idx]

  var = sum_grp.createVariable('terminate_lon','f4')
  var.units = 'degrees_east'
  var[:] = telem_pos['longitude'][idx]

  if ss_nc is not None:
    dist = lu.get_rssivrange(ac_nc,sname = ss_nc)[0]
    max_range = np.nanmax(dist)
  else:
    max_range = np.nan

  var = sum_grp.createVariable('max_range','f4')
  var.units = 'km'
  var[:] = max_range/1000

  if input_xml is not None:
    sum_vals = xml2summary(input_xml)
    for varname in sum_vals.keys():
      if sum_vals[varname] is None:
        exec('sum_grp.'+varname+' = \'\'')
      else:
        exec('sum_grp.'+varname+' = \''+sum_vals[varname]+'\'')

  rg.close()

def ncname2kml(ncname,color=simplekml.Color.white):
  data = WMO_nc2data(ncname)
  lu.make_kml(data['lat'],data['lon'],data['altitude'],ncname[:-2]+'kml',color=color)

def kolm_fit1(ts,u):
  ts = ts[~np.isnan(u)]
  u = u[~np.isnan(u)]

  dt = np.diff(ts)
  dt = dt[dt>0]
  f = np.linspace(1/((ts[-1]-ts[0])/2),1/(np.min(dt)*2),1000)
  Pxx_den = signal.lombscargle(ts,u,f)

  Pxx_den = Pxx_den[f > 0]
  f = f[f > 0]
  plt.loglog(f, Pxx_den,'.',label='Data',color='xkcd:dark gray')
  f_slope = np.linspace(np.min(f[1:]),np.max(f[1:]),num=100)
  plt.loglog(f_slope, (f_slope) **(-5/3),'--r',label='-5/3 Kolmogorovs Fit')
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


