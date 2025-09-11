from scipy.interpolate import interp1d
import h5py
import os
import matplotlib.pyplot as plt
import numpy as np
import bst_log_utils.log_utils as lu
import pandas as pd
from scipy import fftpack
from scipy.ndimage import shift
from matplotlib.gridspec import GridSpec
from scipy.optimize import curve_fit
from scipy.optimize import curve_fit
from scipy.stats import norm

pi = np.pi

#def add_row(fname, ignorefiles = 'master_qc_ignore.csv'):
def add_row(fname, ignorefiles = None):
    file_name = os.path.basename(fname)
    if ignorefiles is not None:
      ignore = pd.read_csv(ignorefiles)
      if ignore['ignore_files'].str.contains(file_name).sum() > 0:
          return None
    
    ac_type,ac_num,serial_num,num_flights,tof,sw_rev,hw_rev,svn_rev,comms_rev = lu.get_info_aplog(fname)
    start,stop = lu.flighttimes(fname)
    if ac_type == '':
        return None

    for i in range(num_flights):
      dfi = pd.DataFrame.from_dict({'filename': [file_name],
                                   'datetime':lu.get_datetime_aplog(fname),
                                   'Aircraft Type': [ac_type],
                                   'Aircraft Num': [ac_num],
                                   'Serial Num': [serial_num],
                                   'Software Rev': [sw_rev],
                                   'Hardware Rev': [hw_rev],
                                   'Git Hash': [svn_rev],
                                   'Comms Rev': [comms_rev],
                                   'Total TOF (min)': [tof/60],
                                   'Num Flights': [num_flights],
                                   'Flight Num': [i+1],
                                   'TOF (min)': [(stop[i]-start[i])/60],
                                   })
      dfi['datetime'] =  pd.to_datetime(dfi['datetime'], format='%Y-%m-%d %H:%M:%S')
      dfi = pd.concat([dfi,add_time_err(fname),add_useful_stats(fname,fn=i),add_control_err(fname,ac_type,fn=i)],axis=1)
      if i == 0:
        df = dfi
      else:
        df = pd.concat([df, dfi])        

    return df
        
def add_useful_stats(fname,fn=None):
    min_h,max_h,P,max_da,min_wind,max_wind,max_ias,max_speed,max_vz,min_vz,max_T,min_T = lu.get_useful_ap_stats(fname,fn=fn)
    rssi = rssi_at_d(fname,fn=fn)

    stats = {'Max Height (m MSL)':[min_h],
             'Min Height (m MSL)':[max_h],
             'Cruise Power (W)':[P],
             'Max Density Alt (m MSL)':[max_da],
             'Min Wind (m/s)':[min_wind],
             'Max Wind (m/s)':[max_wind],
             'Max IAS (m/s)':[max_ias],
             'Max Ground Speed (m/s)':[max_speed],
             'Max Climb Rate (m/s)':[max_vz],
             'Min Climb Rate (m/s)':[min_vz],
             'Max Temp (C)':[min_T],
             'Min Temp (C)':[max_T],
             'RSSI at 1km (dbm)':[rssi],
    }
    return pd.DataFrame.from_dict(stats)
    
def add_time_err(fname):
    # Variables to run
    tvars = ['gps','acc','gyr','mag','dyn_p','stat_p']
    name_key = ['gps_','acc_','gyr_','mag_','dynp_','statp_']
    for idx,(var,name) in enumerate(zip(tvars,name_key)):
        err_data = get_time_err(fname,var,name)
        if idx == 0:
            df = pd.DataFrame.from_dict(err_data)
        else:
            df = pd.concat([df,pd.DataFrame.from_dict(err_data)],axis=1)
    return df

def get_time_err(fname,var,key):
    var,t = lu.get_var(fname,var)
    t = t[t>0]
    if t is not None:
        if len(t) > 1:
            dt = np.diff(t)[1:]
            return {key+'dt_mean':[np.average(dt)],key+'dt_std':[np.std(dt)],key+'dt_max':[np.max(dt)]}
    return {key+'dt_mean':[np.nan],key+'dt_std':[np.nan],key+'dt_max':[np.nan]}

def remove_outliers(var,max_sigma=3):
    var = var[~np.isnan(var)]
    run = True
    i = 0
    last_std = np.std(var)
    while(run):
        idx = np.where(( (var-np.nanmean(var) <=  max_sigma*np.std(var)) &
                     (var-np.nanmean(var) >= -max_sigma*np.std(var)) ))
        var = var[idx]
        i += 1
        if (last_std - np.std(var))/last_std < 0.01:
            run = False
        last_std = np.std(var)
    return var,np.mean(var),np.std(var)

def plot_hist_comp(df_big,df_single,key,ax,scale=1.0):
    var = df_big[key].to_numpy()*scale
    var,mu_var,std_var = remove_outliers(var,max_sigma=3)

    counts, bins = np.histogram(var,20)
    ax.stairs(counts, bins,fill=True,color='xkcd:light grey')

    val = float(df_single[key])*scale
    if np.abs(val - mu_var) < 1*std_var:
        col = 'xkcd:green'
    elif np.abs(val - mu_var) < 3*std_var:
        col = 'xkcd:dark yellow'
    else:
        col = 'xkcd:red'
    ax.plot([val,val],[0,np.max(counts)*1],color=col,linewidth=3)
    ax.text(val,np.max(counts)*1.01,'%.3f'%val,color=col,fontsize=14,weight='bold')
    ax.spines[['right', 'top']].set_visible(False)
    ax.grid()   

    # Plot the PDF (probability density function)
    xmin, xmax = ax.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu_var, std_var)
    
    scale_factor=(bins[1]-bins[0])* len(var)
    
    ax.plot(x,p*scale_factor,color='xkcd:red',linewidth=3)
    idx = np.where(np.abs(x-mu_var) < 3*std_var)
    ax.plot(x[idx],p[idx]*scale_factor,color='xkcd:dark yellow',linewidth=3)
    idx = np.where(np.abs(x-mu_var) < std_var)
    ax.plot(x[idx],p[idx]*scale_factor,color='xkcd:green',linewidth=3)
    
               
def performance_plot(DF=None, df = None,repo_ncname=None,fromFile=None,fdir = '/home/stachura/usb/flight_testing/'):
    if df is None:
      if repo_ncname is not None:
          df = DF[DF['filename'] == repo_ncname]
      elif fromFile is not None:
          df = add_row(fromFile)

    # Only compare against similar type
    
    DF = DF[DF['Aircraft Type'] == df['Aircraft Type'].item()]
    fsize = 14
    
    #fig,ax = plt.subplots(4,3)
    fig = plt.figure()
    gs = fig.add_gridspec(4,3)
    
    ax = fig.add_subplot(gs[0,0])
    plot_hist_comp(DF,df,'roll_rms',ax,scale=180/pi)
    ax.set_xlabel('RMS [deg]',fontsize=fsize)
    ax.set_ylabel('Roll',fontsize=fsize)
    ax = fig.add_subplot(gs[0,1])
    ax.set_title('%s-%s on %s with TOF %.1f min'%(df['Aircraft Type'].item(),df['Aircraft Num'].item(),df['datetime'].item(),df['TOF (min)'].item()),fontsize=16)
    plot_hist_comp(DF,df,'roll_max',ax,scale=180/pi)
    ax.set_xlabel('Max Error [deg]',fontsize=fsize)
    ax = fig.add_subplot(gs[0,2])
    plot_hist_comp(DF,df,'roll_delay',ax)
    ax.set_xlabel('Delay [s]',fontsize=fsize)
    
    ax = fig.add_subplot(gs[1,0])
    plot_hist_comp(DF,df,'pitch_rms',ax,scale=180/pi)
    ax.set_xlabel('RMS [deg]',fontsize=fsize)
    ax.set_ylabel('Pitch',fontsize=fsize)
    
    ax = fig.add_subplot(gs[1,1])
    plot_hist_comp(DF,df,'pitch_max',ax,scale=180/pi)
    ax.set_xlabel('Max Error [deg]',fontsize=fsize)
    
    ax = fig.add_subplot(gs[1,2])
    plot_hist_comp(DF,df,'pitch_delay',ax)
    ax.set_xlabel('Delay [s]',fontsize=fsize)
    
    ax = fig.add_subplot(gs[2,0])
    plot_hist_comp(DF,df,'ias_rms',ax)
    ax.set_ylabel('IAS',fontsize=fsize)
    ax = fig.add_subplot(gs[2,1])
    plot_hist_comp(DF,df,'ias_max',ax)
    ax.set_xlabel('Max Error [m/s]',fontsize=fsize)
    
    
    ax = fig.add_subplot(gs[3,0])
    plot_hist_comp(DF,df,'Cruise Power (W)',ax)
    ax.set_xlabel('Cruise Power [W]',fontsize=fsize)
    ax = fig.add_subplot(gs[3,1])
    plot_hist_comp(DF,df,'RSSI at 1km (dbm)',ax)
    ax.set_xlabel('RSSI fit at 1km [dBm]',fontsize=fsize)
    
    ax = fig.add_subplot(gs[2:4,2])
    lu.plot_traj(fdir+df['filename'].item(),ax=ax,bmap=False)


def timing_plot(DF = None, repo_ncname=None,fromFile=None):
    
    if repo_ncname is not None:
        df = DF[DF['filename'] == repo_ncname]
    elif fromFile is not None:
        df = add_row(fromFile)

    ac_type = df['Aircraft Type'].item()

    if ac_type == 'S0' or ac_type == 'S1' or ac_type == 'S2':
        name_key = ['gps_','acc_','gyr_','statp_','dynp_']
    else:
        name_key = ['gps_','acc_','gyr_','mag_','statp_']
    name_type = ['dt_mean','dt_std','dt_max']
    fig = plt.figure()
    gs = fig.add_gridspec(nrows=len(name_key),ncols=len(name_type))
    for rowID,key in enumerate(name_key):
        for colID,ntype in enumerate(name_type):
            ax = fig.add_subplot(gs[rowID,colID])
            plot_hist_comp(DF,df,key+ntype,ax)
            if rowID == 0 and colID ==1:
              ax.set_title('%s-%s on %s with TOF %.1f min'%(df['Aircraft Type'].item(),df['Aircraft Num'].item(),df['datetime'].item(),df['TOF (min)'].item()),fontsize=16)
            if colID == 0:
                ax.set_ylabel(key[0:-1])
            if rowID == len(name_key)-1:
                ax.set_xlabel(ntype)

def get_rmse_delay(t,val,val_c):
    idx = np.where(np.isfinite(val))
    val = val[idx]
    val_c = val_c[idx]
    idx = np.where(np.isfinite(val_c))
    val = val[idx]
    val_c = val_c[idx]
    
    A = fftpack.fft(val)
    B = fftpack.fft(val_c)
    Ar = -A.conjugate()
    Br = -B.conjugate()
    fft_res = np.abs(fftpack.ifft(A*Br))
    delay_ind = np.argmax(fft_res[0:int(len(fft_res)/2)])
#delay_ind = np.argmax(np.abs(fftpack.ifft(A*Br)))
    val_shift = shift(val,-delay_ind, cval=np.nan)
    err,max_err = err_calc(val_c,val_shift)
    delay = np.mean(np.diff(t))*delay_ind
    return delay,err,max_err

def err_calc(Y1,Y2):
    rms = 0
    
    idx = np.where(np.isfinite(Y1))
    Y1 = Y1[idx]
    Y2 = Y2[idx]
    idx = np.where(np.isfinite(Y2))
    Y1 = Y1[idx]
    Y2 = Y2[idx]
    
    for y1,y2 in zip(Y1,Y2):
        rms += (y1-y2)**2
        
    return np.sqrt(rms/len(Y1)),np.max(np.abs(Y1-Y2))
    
def add_control_err(fname,ac_type,fn=None):
    ctrl_err = {'roll_rms':[np.nan],
                'roll_delay':[np.nan],
                'roll_max':[np.nan],
                'pitch_rms':[np.nan],
                'pitch_delay':[np.nan],
                'pitch_max':[np.nan],
                'yaw_rms':[np.nan],
                'yaw_delay':[np.nan],
                'yaw_max':[np.nan],
                'height_rms':[np.nan],
                'height_max':[np.nan],
                'ias_rms':[np.nan],
                'ias_max':[np.nan],
                'vx_rms':[np.nan],
                'vx_max':[np.nan],
                'vy_rms':[np.nan],
                'vy_max':[np.nan],
                'vz_rms':[np.nan],
                'vz_max':[np.nan]}
    fw_list = ['S0','S1','S2']
    mr_list = ['FW','E2']
    
    start,stop = lu.flighttimes(fname,fn=fn)
    start +=20
    stop -= 20
    state,tstate = lu.get_var(fname,'state')
    command = lu.get_log_command(fname)

    # Angles
    roll,pitch,yaw = lu.log2ang(fname)
   
    # FIXME  - tmp
    if stop-start > 20:
      if ac_type in fw_list:
        tvar,var,var_c = get_control_data(command['t_ALTITUDE'],command['ALTITUDE'],tstate,state['altitude'],start,stop)
        tvar,var,var_c = get_control_data_mode(tvar,var,var_c,command['t_AUTOPILOT_MODE'],command['AUTOPILOT_MODE'],1)
        tvar,var,var_c = get_control_data_mode(tvar,var,var_c,command['t_ALT_MODE'],command['ALT_MODE'],3)
        if (len(tvar) > 0):
          ctrl_err['height_rms'],ctrl_err['height_max'] = err_calc(var,var_c)


        tvar,var,var_c = get_control_data(command['t_SPEED'],command['SPEED'],tstate,state['ias'],start,stop)
        tvar,var,var_c = get_control_data_mode(tvar,var,var_c,command['t_AUTOPILOT_MODE'],command['AUTOPILOT_MODE'],1)
        if (len(tvar) > 0):
          ctrl_err['ias_rms'],ctrl_err['ias_max'] = err_calc(var,var_c)

        tvar,var,var_c = get_control_data(command['t_ROLL'],command['ROLL'],tstate,roll,start,stop)
        tvar,var,var_c = get_control_data_mode(tvar,var,var_c,command['t_AUTOPILOT_MODE'],command['AUTOPILOT_MODE'],1)
        if (len(tvar) > 0):
          ctrl_err['roll_delay'],ctrl_err['roll_rms'],ctrl_err['roll_max'] = get_rmse_delay(tvar,var,var_c)
        
        tvar,var,var_c = get_control_data(command['t_PITCH'],command['PITCH'],tstate,pitch,start,stop)
        tvar,var,var_c = get_control_data_mode(tvar,var,var_c,command['t_AUTOPILOT_MODE'],command['AUTOPILOT_MODE'],1)
        if (len(tvar) > 0):
          ctrl_err['pitch_delay'],ctrl_err['pitch_rms'],ctrl_err['pitch_max'] = get_rmse_delay(tvar,var,var_c)

 
      if ac_type in mr_list:
        tvar,var,var_c = get_control_data(command['t_ALTITUDE'],command['ALTITUDE'],tstate,state['altitude'],start,stop)
        tvar,var,var_c = get_control_data_mode(tvar,var,var_c,command['t_AUTOPILOT_MODE'],command['AUTOPILOT_MODE'],1)
        tvar,var,var_c = get_control_data_mode(tvar,var,var_c,command['t_ALT_MODE'],command['ALT_MODE'],3)
        if (len(tvar) > 0):
          ctrl_err['height_rms'],ctrl_err['height_max'] = err_calc(var,var_c)
    
        tvar,var,var_c = get_control_data(command['t_ROLL'],command['ROLL'],tstate,roll,start,stop)
        if (len(tvar) > 0):
          ctrl_err['roll_delay'],ctrl_err['roll_rms'],ctrl_err['roll_max'] = get_rmse_delay(tvar,var,var_c)
        
        tvar,var,var_c = get_control_data(command['t_PITCH'],command['PITCH'],tstate,pitch,start,stop)
        if (len(tvar) > 0):
          ctrl_err['pitch_delay'],ctrl_err['pitch_rms'],ctrl_err['pitch_max'] = get_rmse_delay(tvar,var,var_c)
     
        tvar,var,var_c = get_control_data(command['t_YAW'],command['YAW'],tstate,yaw,start,stop)
        if (len(tvar) > 0):
          ctrl_err['yaw_delay'],ctrl_err['yaw_rms'],ctrl_err['yaw_max'] = get_rmse_delay(tvar,var,var_c)
        
    df = pd.DataFrame.from_dict(ctrl_err)    
    return df
     
def get_control_data(tcommand,command,tstate,var,start,stop):
    idc = lu.get_time_indeces(tcommand,start,stop)
    ids = lu.get_time_indeces(tstate,start,stop)
    
#   var = interp1d(tstate[ids],var[ids],fill_value='extrapolate')(tcommand[idc])
#   return tcommand[idc],var,command[idc]
    var_c = interp1d(tcommand[idc],command[idc],fill_value='extrapolate')(tstate[ids])
    return tstate[ids],var[ids],var_c
    
def get_control_data_mode(tvar,var,var_c,tmode,mode,imode):
    com_auto = interp1d(tmode,mode,fill_value='extrapolate')(tvar)
    idx = np.where(com_auto == imode)
    return tvar[idx],var[idx],var_c[idx]

def generate_qc_database(new_db, log_dir, existing_db=None,ignorefiles = 'master_qc_ignore.csv'):
  # new_db is the CSV you'd like to save to
  # log_dir is the folder with all the AP netCDF files
  # existing_db is if you already have one you just want to append to
  # - leaving it as None is SLOW
  # ignorefiles is a file with netCDF files with known issues
  
  start = True
  if existing_db is not None:
    DF_old = pd.read_csv(existing_db)
  else:
    DF_old = pd.DataFrame.from_dict({'filename': ['']})
  
  for fname in sorted(os.listdir(log_dir)):
    print('Checking %s'%fname)
    if DF_old['filename'].str.contains(fname).sum() == 0:
      f = os.path.join(log_dir, fname)
      if os.path.isfile(f):
#try:
        df = add_row(f,ignorefiles=ignorefiles)
#except:
#          df = None
        if df is not None:
          print('\tAdding to database!')
          if start:
            DF = df
            start = False
          else:
            DF = pd.concat([DF, df])        
        else:
          print('\tFAILED: Issue with file, add_row() function, or on ignore list')
    else:
      print('\tFile already in database')
              
  if existing_db is not None:
    DF = pd.concat([DF_old,DF])        
  DF2 = DF.reset_index()
  DF2.drop('index', axis=1, inplace=True)
  DF2 = DF2.sort_values(by=['filename'])
  DF2.to_csv(new_db,index=False)

def reduce_repo(master_qc_repo='master_qc_repo.csv',ac_type=None, ac_num=None,
                   date_start=None, date_stop=None, firstNfiles=None, lastNfiles=None):
    df = pd.read_csv(master_qc_repo)
    if ac_type is not None:
        idx = np.where(df['Aircraft Type'] == ac_type)[0]
        df = df.iloc[idx,:].reset_index(drop=True)
    if ac_num is not None:
        idx = np.where(df['Aircraft Num'] == ac_num)[0]
        df = df.iloc[idx,:].reset_index(drop=True)
    if date_start is not None:
        print('Warning: date_start not implemented!')
    if date_stop is not None:
        print('Warning: date_stop not implemented!')
    if firstNfiles is not None:
        df = df.iloc[:firstNfiles,:].reset_index(drop=True)
    if lastNfiles is not None:
        df = df.iloc[-lastNfiles:,:].reset_index(drop=True)

    return df

def rssi_at_d(fname, d_normal = 1000,min_d=100,fn=None):
  d, rssi = lu.get_rssivrange(fname,fn=fn)
  if d is None:
    return np.nan
  rssi = rssi[d>min_d]
  d = d[d>min_d]
  if len(d) < 60:
    return np.nan
  v = curve_fit(lu.rssi_fun, d, rssi)[0]
  n,C = v
  return -n*np.log10(d_normal) + C

