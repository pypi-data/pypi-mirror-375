import os
import netCDF4

def list_group_details(group, group_name="root", indent=0):
    """Recursively prints details for a netCDF group."""
    prefix = " " * indent
    print(f"{prefix}Group: {group_name}")
    for var_name, var in group.variables.items():
        print(f"{prefix}  Variable: {var_name}, shape: {var.shape}")
    for sub_group_name, sub_group in group.groups.items():
        list_group_details(sub_group, sub_group_name, indent + 2)

def list_netcdf_details(directory_path):
    """
    Finds all netCDF files in the given directory (and subdirectories)
    and prints all groups, variable names, and their sizes (shapes).
    """
    # Walk through the directory and find .nc files
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.nc'):
                file_path = os.path.join(root, file)
                print(f"File: {file_path}")
                try:
                    ds = netCDF4.Dataset(file_path, "r")
                    # Print the details of the root group and any subgroups recursively
                    list_group_details(ds)
                    ds.close()
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                print()  # Blank line for clarity between files

import shutil
import importlib
import numpy as np
from datetime import datetime
from bst_helper_functions.gnss_utils import gps_week_hours_to_datetime
from bst_python_sdk.bstpacket import BSTPacket
from bst_python_sdk.comm_packets.comm_packets import VehicleType, PacketTypes

#import bst_python_sdk.comm_versions.ver_3210.comm_packets as bst_cp

def reimport_comms(new_rev: int):
    #print(f'-- Using comms rev: {new_rev}')

    comm_packets_import = f'bst_python_sdk.comm_versions.ver_{new_rev}.comm_packets'

    globals()['bstpkt'] = importlib.import_module(comm_packets_import)

def process_flight_files(input_dir, output_dir):
    # Make sure output directory exists.
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.nc'):
                file_path = os.path.join(root, file)
                try:
                    ds = netCDF4.Dataset(file_path, 'r')
                except Exception as e:
                    print(f"Error opening file {file_path}: {e}")
                    continue

                # Check for the SYSTEM_INITIALIZE group
                if "SYSTEM_INITIALIZE" not in ds.groups:
                    print(f"SYSTEM_INITIALIZE group not found in {file_path}")
                    ds.close()
                    continue

                system_grp = ds.groups["SYSTEM_INITIALIZE"]
                try:
                    new_rev = system_grp.variables["comms_rev"][0]
                except Exception as e:
                    print(f"Error reading SYSTEM_INITIALIZE variables in {file_path}: {e}")

                reimport_comms(new_rev)

                # Check for the TELEMETRY_SYSTEM group
                if "TELEMETRY_SYSTEM" not in ds.groups:
                    print(f"TELEMETRY_SYSTEM group not found in {file_path}")
                    ds.close()
                    continue

                telem_grp = ds.groups["TELEMETRY_SYSTEM"]
                try:
                    flight_modes  = telem_grp.variables["flight_mode"][:]
                    weeks         = telem_grp.variables["week"][:]
                    hours         = telem_grp.variables["hour"][:]
                    minutes       = telem_grp.variables["minute"][:]
                except Exception as e:
                    print(f"Error reading TELEMETRY_SYSTEM variables in {file_path}: {e}")
                    ds.close()
                    continue

                try:
                    msecs         = telem_grp.variables["milliseconds"][:]  # assumed in milliseconds
                except Exception as e:
                    try:
                        msecs         = telem_grp.variables["seconds"][:] * 1000.0
                    except Exception as e:
                        print(f"Error reading TELEMETRY_SYSTEM system time in {file_path}: {e}")
                        ds.close()
                        continue

                flying_indices = np.where(flight_modes >= bstpkt.FlightMode.FLIGHT_MODE_CLIMBOUT.value)[0]
                if flying_indices.size == 0:
                    print(f"No valid flight modes found in {file_path}")
                    ds.close()
                    continue

                start_idx = flying_indices[0]
                end_idx   = flying_indices[-1]

                # Get GPS time components at flight start
                start_week   = weeks[start_idx]
                start_hour   = hours[start_idx]
                start_minute = minutes[start_idx]
                start_sec    = msecs[start_idx] / 1000.0
                try:
                    start_dt = gps_week_hours_to_datetime(int(start_week), start_hour, start_minute, start_sec)
                except Exception as e:
                    print(f"Error converting start time in {file_path}: {e}")
                    ds.close()
                    continue

                # Get GPS time components at flight end
                end_week   = weeks[end_idx]
                end_hour   = hours[end_idx]
                end_minute = minutes[end_idx]
                end_sec    = msecs[end_idx] / 1000.0
                try:
                    end_dt = gps_week_hours_to_datetime(int(end_week), end_hour, end_minute, end_sec)
                except Exception as e:
                    print(f"Error converting end time in {file_path}: {e}")
                    ds.close()
                    continue

                duration = end_dt - start_dt

                # Now get aircraft name from VEHICLE_PARAMS group
                if "VEHICLE_PARAMS" not in ds.groups:
                    print(f"VEHICLE_PARAMS group not found in {file_path}")
                    ds.close()
                    continue

                veh_grp = ds.groups["VEHICLE_PARAMS"]
                try:
                    veh_sys_times = veh_grp.variables["system_time"][:]  # assumed to be in seconds (epoch time)
                    names         = veh_grp.variables["name"][:]          # might be stored as byte strings
                except Exception as e:
                    print(f"Error reading VEHICLE_PARAMS variables in {file_path}: {e}")
                    ds.close()
                    continue

                # Convert the flight start datetime to a comparable timestamp (in seconds)
                start_timestamp = start_dt.timestamp()
                # Find indices where vehicle system_time is <= start_timestamp.
                valid_idx = np.where(veh_sys_times <= start_timestamp)[0]
                if valid_idx.size == 0:
                    ac_name = "UNKNOWN"
                else:
                    # Choose the index with the maximum system_time that is still <= start_timestamp
                    idx2 = valid_idx[np.argmax(veh_sys_times[valid_idx])]
                    ac_name = names[idx2]
                    ac_name = ac_name[ac_name != 0]
                    ac_name = ''.join(chr(i) for i in ac_name)

                    if isinstance(ac_name, bytes):
                        ac_name = ac_name.decode('utf-8').strip()
                    else:
                        ac_name = str(ac_name).strip()

                ds.close()

                # Format the new filename as "YYYY-MM-DD HH:MM:SS  AC_NAME.nc"
                new_filename = f"{start_dt.strftime('%Y-%m-%d_%H:%M:%S')}_{ac_name}.nc"
                out_path = os.path.join(output_dir, new_filename)

                try:
                    shutil.copy2(file_path, out_path)
                except Exception as e:
                    print(f"Error copying {file_path} to {out_path}: {e}")
                    continue

                # Format duration as HH:MM:SS (assuming duration is a timedelta)
                total_seconds = int(duration.total_seconds())
                hrs = total_seconds // 3600
                mins = (total_seconds % 3600) // 60
                secs = total_seconds % 60
                duration_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

                print(f"Found flight on {start_dt.strftime('%Y-%m-%d')} at {start_dt.strftime('%H:%M:%S')} name {ac_name} of duration {duration_str}")
