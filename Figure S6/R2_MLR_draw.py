# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 14:35:34 2025

@author: liuxi
"""

import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap, cm
import matplotlib.colors as colors
import netCDF4 as nc
from matplotlib.colors import ListedColormap
from matplotlib.cm import ScalarMappable
import cmaps
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import BoundaryNorm

import shapely.geometry as sgeom
import shapely.vectorized as sv

def draw_screen_poly(lats, lons, m):
    x, y = m(lons, lats)
    xy = list(zip(x, y))
    poly = plt.Polygon(xy, edgecolor="k", fc="none", lw=0.8, alpha=1)
    plt.gca().add_patch(poly)



csv_obs = pd.read_excel('./R2_MLR_PM.xlsx')
print(csv_obs.columns)
csv_obs['lat'] = csv_obs['LAT_NC'].values
csv_obs['lon'] = csv_obs['LON_NC'].values

mean_value = np.nanmean(csv_obs['R']**2)  
std_value = np.nanstd(csv_obs['R']**2, ddof=0) 

csv_file = r'lonlat_only.csv'

grid_df = pd.read_csv(csv_file)


lon = np.sort(grid_df['lon'].unique())
lat = np.sort(grid_df['lat'].unique())


lons, lats = np.meshgrid(lon, lat)

print(lons.shape)
print(lats.shape)
print(lon[:5], lon[-5:])
print(lat[:5], lat[-5:])
print(lons.shape)
grid_df = pd.DataFrame()
grid_df["lon"] = lons.flatten()
grid_df["lat"] = lats.flatten()
print(grid_df)
grid_df['lon'] = grid_df['lon'].astype(np.float64)
grid_df['lat'] = grid_df['lat'].astype(np.float64)
print(grid_df['lon'].dtype)
print(grid_df['lat'].dtype)
array_1 = pd.merge(grid_df, csv_obs,how='left')
print(array_1)

R = array_1['R'].values.reshape(160, 224)
R2 = R**2


result = f"{mean_value:.2f} ± {std_value:.2f}"



fig, ax = plt.subplots(1, 1, figsize=(2.5, 4))
NEC = [123, 128, 41, 48]
BTH = [114, 118, 37, 41]
YRD = [118, 122, 30, 33]
PRD = [112, 115.5, 21.5, 24]
regions = [NEC, BTH, YRD, PRD]


polygons = []
for reg in regions:
    lon_min, lon_max, lat_min, lat_max = reg
    poly = sgeom.Polygon([
        (lon_min, lat_min),
        (lon_min, lat_max),
        (lon_max, lat_max),
        (lon_max, lat_min)
    ])
    polygons.append(poly)

mask = np.zeros_like(R2, dtype=bool)
for poly in polygons:
    inside = sv.contains(poly, lons, lats) | sv.touches(poly, lons, lats)  
    mask = mask | inside

aim_value_masked = np.where(mask, R2, np.nan)

cmap = plt.cm.get_cmap('jet')


plt.subplot(1, 1, 1)

lon_0 = lons.mean()
lat_0 = lats.mean()

m = Basemap(lat_0=lat_0, lon_0=lon_0, llcrnrlon=110, llcrnrlat=np.min(lat), urcrnrlon=np.max(lon)-3,
            urcrnrlat=np.max(lat), resolution='l', rsphere=(6370000.0, 6370000.0),ax=ax)
m.readshapefile('../Figure S2/Province/province_PolygonToLine', 'ShapeT', linewidth=0.2, drawbounds=True)
m.readshapefile('../Figure S2/China/China_10-dash_line', 'Shape', linewidth=0.2, drawbounds=True)
x, y = m(lons, lats)

print(np.max(lon))
levels = np.linspace(0, 0.9, 19)
norm = BoundaryNorm(levels, ncolors=cmap.N, clip=False)
mesh =  m.pcolormesh(x, y,aim_value_masked, cmap=cmap, norm=norm)

parallels = np.arange(0, 60, 5)

meridians = np.arange(0, 180, 10)

for reg in regions:
    lat_box = [reg[2], reg[3], reg[3], reg[2]]
    lon_box = [reg[0], reg[0], reg[1], reg[1]]
    draw_screen_poly(lat_box, lon_box, m)
size = 13

plt.title('MLR–std',fontsize=12)
plt.text(-0.25, 0.5, r'PM$_{2.5}$', fontsize=12, 
         transform=plt.gca().transAxes, va='center', ha='center')
plt.text(
    0.98, 0.95, "(a)",        
    transform=ax.transAxes,   
    fontsize=10, fontweight='bold',
    ha='right', va='top'     
)


c2 =  plt.colorbar(mesh, extend='both', aspect=30,  shrink=0.75)


c2.ax.tick_params(axis='y', direction='in', which='major')

c2.ax.tick_params(axis='y', direction='in', which='minor')
plt.savefig("domain.tif", dpi=300, bbox_inches='tight')
plt.show()
