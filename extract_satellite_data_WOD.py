#!/usr/bin/env python
# coding: utf-8

# # Extract satellite data at time and location for WOD data
# Created by Ivan Lima on Tue Mar 30 2021 13:09:11 -0400

# **There are 195745 observational data points and it will take several hours to extract the satellite data. Use Python script in this directory to extract the data instead of this notebook.**

import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import datetime, os, glob
from tqdm import tnrange, notebook
from ccsm_utils import find_stn, find_stn_idx, find_closest_pt, extract_loc
from cesm_utils import da2ma
print('Last updated on {}'.format(datetime.datetime.now().ctime()))


# ## Read observational data

# df_obs = pd.read_csv('data/WOD_metadata.csv', index_col=1, parse_dates={'Date':['Year','Month','Day']})
df_obs = pd.read_csv('data/metadata_2012topresent.csv', index_col=1, parse_dates={'Date':['Year','Month','Day']})
# df_obs[:25]


# ## Extract satellite data at observation dates & locations

ssh_dir = '/bali/data/ilima/Satellite_Data/AVISO/daily/'
sst_dir = '/bali/data/ilima/Satellite_Data/SST/NOAA_OI/'
sst_hr_dir = '/bali/data/ilima/Satellite_Data/SST/PO.DAAC/'
chl_dir = '/bali/data/ilima/Satellite_Data/Ocean_Color/Chl/daily/'
kd490_dir = '/bali/data/ilima/Satellite_Data/Ocean_Color/KD490/daily/'

for i in notebook.tqdm(df_obs.index):
    year, month, day = df_obs.loc[i,'Date'].year, df_obs.loc[i,'Date'].month, df_obs.loc[i,'Date'].day
    doy = df_obs.loc[i,'Date'].day_of_year
    
    # extract AVISO SSH data
    ssh_file = glob.glob(ssh_dir + '{}/{:02}/dt_global_allsat_phy_l4_{}{:02}{:02}_????????.nc'.format(year,month,year,month,day))
    if ssh_file:
        with xr.open_dataset(ssh_file[0]) as ds:
            lon_sat, lat_sat = np.meshgrid(ds.longitude, ds.latitude)
            lon_obs, lat_obs = df_obs.loc[i,['Longitude','Latitude']]
            lon_obs = lon_obs + 360.
            for var in ['adt','ugos','vgos','sla','ugosa','vgosa']:
                df_obs.loc[i,var.upper()] = extract_loc(lon_obs, lat_obs, lon_sat, lat_sat, da2ma(ds[var]))
    else:
        print('SSH i={} ({}-{:02}-{:02})'.format(i, year, month, day), end=', ')
    
    # extract SST (0.25 x 0.25 degree) data
    sst_file = glob.glob(sst_dir + '{}/{:03d}/{}*AVHRR_OI*.nc'.format(year,doy,year))
    if sst_file:
        with xr.open_dataset(sst_file[0]) as ds:
            lon_sat, lat_sat = np.meshgrid(ds.lon, ds.lat)
            lon_obs, lat_obs = df_obs.loc[i,['Longitude','Latitude']]
            data = da2ma(ds['analysed_sst'].squeeze() - 273.15) # Kelvin -> Celsius
            df_obs.loc[i,'SST'] = extract_loc(lon_obs, lat_obs, lon_sat, lat_sat, data)
    else:
        print('SST1 i={} ({}-{:02}-{:02})'.format(i, year, month, day), end=', ')
    
    # extract high res SST (0.01 x 0.01 degree) data
    # sst_hr_file = sst_hr_dir + '{}/{:03d}/{}{:02}{:02}090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc'.format(year,doy,year,month,day)
    sst_hr_file = '/home/ivan/Data/Postproc/PO.DAAC/' + 'subset_{}{:02}{:02}090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc'.format(year,month,day)
    if os.path.isfile(sst_hr_file):
        with xr.open_dataset(sst_hr_file) as ds:
            lon_sat, lat_sat = np.meshgrid(ds.lon, ds.lat)
            lon_obs, lat_obs = df_obs.loc[i,['Longitude','Latitude']]
            data = da2ma(ds['analysed_sst'].squeeze() - 273.15) # Kelvin -> Celsius
            df_obs.loc[i,'SST_hires'] = extract_loc(lon_obs, lat_obs, lon_sat, lat_sat, data)
    else:
        print('SST2 i={} ({}-{:02}-{:02})'.format(i, year, month, day), end=', ')
        
    # extract surface Chl (~4.64 Km resolution)
    chl_file = chl_dir + '{}/{:02}/{}{:02}{:02}_d-ACRI-L4-CHL-MULTI_4KM-GLO-REP.nc'.format(year,month,year,month,day)
    if os.path.isfile(chl_file):
        with xr.open_dataset(chl_file) as ds:
            lon_sat, lat_sat = np.meshgrid(ds.lon, ds.lat)
            lon_obs, lat_obs = df_obs.loc[i,['Longitude','Latitude']]
            data = da2ma(ds['CHL'].squeeze())
            df_obs.loc[i,'Chl'] = extract_loc(lon_obs, lat_obs, lon_sat, lat_sat, data)
    else:
        print('Chl i={} ({}-{:02}-{:02})'.format(i, year, month, day), end=', ')
        
    # extract surface KD490 (~4.64 Km resolution)
    kd490_file = kd490_dir + '{}/{:02}/{}{:02}{:02}_d-ACRI-L4-KD490-MULTI_4KM-GLO-REP.nc'.format(year,month,year,month,day)
    if os.path.isfile(kd490_file):
        with xr.open_dataset(kd490_file) as ds:
            lon_sat, lat_sat = np.meshgrid(ds.lon, ds.lat)
            lon_obs, lat_obs = df_obs.loc[i,['Longitude','Latitude']]
            data = da2ma(ds['KD490'].squeeze())
            df_obs.loc[i,'KD490'] = extract_loc(lon_obs, lat_obs, lon_sat, lat_sat, data)
    else:
        print('KD490 i={} ({}-{:02}-{:02})'.format(i, year, month, day), end=' | ')        


# ## Write data to CSV file

df_obs['Year'] = df_obs.Date.dt.year
df_obs['Month'] = df_obs.Date.dt.month
df_obs['Day'] = df_obs.Date.dt.day
cols = ['Latitude', 'Longitude', 'Year', 'Month', 'Day', 'Cast',
        'ADT', 'UGOS', 'VGOS', 'SLA', 'UGOSA', 'VGOSA', 'SST',
        'SST_hires', 'Chl', 'KD490']
df_out = df_obs[cols]
df_out = df_out.fillna('NA')
df_out.to_csv('data/metadata_2012topresent_satellite.csv')
