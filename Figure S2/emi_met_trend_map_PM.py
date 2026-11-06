# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 10:29:36 2026

@author: liuxi
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import BoundaryNorm
import shapely.geometry as sgeom
import shapely.vectorized as sv
import pandas as pd
import os

def draw_screen_poly(lats, lons, m, ax):
    x, y = m(lons, lats)
    xy = list(zip(x, y))
    poly = plt.Polygon(
        xy,
        edgecolor="k",
        fc="none",
        lw=0.8,
        alpha=1
    )
    ax.add_patch(poly)


NEC = [123,128,41,48]
BTH = [114,118,37,41]
YRD = [118,122,30,33]
PRD = [112,115.5,21.5,24]

regions = [NEC,BTH,YRD,PRD]


nc = xr.open_dataset('result_GC.nc')
lon = nc['lon'].values
lat = nc['lat'].values
lons, lats = np.meshgrid(lon, lat)
print(lons.shape)

grid_df = pd.DataFrame({

    'lon': lons.flatten(),
    'lat': lats.flatten()

})


grid_df['lon'] = grid_df['lon'].astype(float)
grid_df['lat'] = grid_df['lat'].astype(float)

folder = '../Figure 1/pm'


files = {
    'GC': (folder, 'result_GC.xlsx'),
    'MLR-std': (folder, 'result_MLR_10_features.xlsx'),
    'RF-std': (folder, 'result_RF_month.xlsx'),
    'RF-region': (folder, 'result_RF_region.xlsx')
}

datasets = {}

for name, (data_folder, file) in files.items():

    filepath = os.path.join(data_folder, file)

    df = pd.read_excel(filepath)

    df['LON'] = df['LON'].astype(float)
    df['LAT'] = df['LAT'].astype(float)

    merge_df = pd.merge(
        grid_df,
        df,
        left_on=['lon','lat'],
        right_on=['LON','LAT'],
        how='left'
    )

    emis = merge_df[
        'PM25_Emis_diff_2014_slope'
    ].values.reshape(
        len(lat),
        len(lon)
    )


    met = merge_df[
        'PM25_Met_diff_2014_slope'
    ].values.reshape(
        len(lat),
        len(lon)
    )


    datasets[name] = {

        'lon': lon,
        'lat': lat,

        'lons': lons,
        'lats': lats,

        'EMIS': emis,
        'MET': met
    }


    print(name)

    print("EMIS shape:", emis.shape)
    print("MET shape:", met.shape)

    print(
        "NaN:",
        np.isnan(emis).sum()
    )

def region_mask(lons, lats):

    mask = np.zeros_like(lons,dtype=bool)

    for reg in regions:

        lon_min, lon_max, lat_min, lat_max = reg

        poly = sgeom.Polygon([
            (lon_min,lat_min),
            (lon_min,lat_max),
            (lon_max,lat_max),
            (lon_max,lat_min)
        ])

        inside = (
            sv.contains(poly,lons,lats)
            |
            sv.touches(poly,lons,lats)
        )

        mask |= inside

    return mask


def plot_panel(ax, data, lons, lats, title, vmax):


    mask = region_mask(lons,lats)

    data = np.where(mask,data,np.nan)


    m = Basemap(
        lat_0=lats.mean(),
        lon_0=lons.mean(),
        llcrnrlon=110,
        llcrnrlat=np.min(lats),
        urcrnrlon=np.max(lons)-3,
        urcrnrlat=np.max(lats),
        resolution='l',
        rsphere=(6370000,6370000),
        ax=ax
    )


    m.readshapefile(
        'Province/province_PolygonToLine',
        'ShapeT',
        linewidth=0.2,
        drawbounds=True
    )


    m.readshapefile(
        'China/China_10-dash_line',
        'Shape',
        linewidth=0.2,
        drawbounds=True
    )


    x,y=m(lons,lats)


    levels=np.linspace(-vmax, vmax, 21)


    mesh = m.contourf(
    x,
    y,
    data,
    cmap='RdBu_r',
    extend='both',
    levels=levels
    )

    for reg in regions:
    
        lat_box = [
            reg[2],
            reg[3],
            reg[3],
            reg[2]
        ]
    
        lon_box = [
            reg[0],
            reg[0],
            reg[1],
            reg[1]
        ]
    
        draw_screen_poly(
            lat_box,
            lon_box,
            m,
            ax
        )


    ax.set_title(
        title,
        fontsize=11
    )

    cbar = plt.colorbar(
        mesh,
        ax=ax,
        orientation='vertical',
        fraction=0.046,
        pad=0.04,
        extend='both'
    )

    cbar.ax.tick_params(
        direction='in',
        which='both'
    )


    return mesh


fig,axs=plt.subplots(
    2,
    4,
    figsize=(14,6.5)
)


methods = ['GC', 'MLR-std', 'RF-std', 'RF-region']

labels = ['(a)', '(b)', '(c)', '(d)',
          '(e)', '(f)', '(g)', '(h)']

mesh=None


for method in methods:
    print('\n========', method, '========')

    emis = datasets[method]['EMIS']
    met = datasets[method]['MET']

    print('PM25_EMIS_trend:')
    print('  min = ', np.nanmin(emis))
    print('  max = ', np.nanmax(emis))
    print('  abs max = ', np.nanmax(np.abs(emis)))

    print('PM25_MET_trend:')
    print('  min = ', np.nanmin(met))
    print('  max = ', np.nanmax(met))
    print('  abs max = ', np.nanmax(np.abs(met)))

for i,method in enumerate(methods):

    emis_max = 10

    d=datasets[method]

    mesh=plot_panel(
        axs[0,i],
        d['EMIS'],
        d['lons'],
        d['lats'],
        f"{labels[i]} {method}",
        emis_max
    )


    if i==0:
        axs[0,i].text(
            -0.25,
            0.5,
            r'PM$_{2.5}^{\mathrm{EMI}}$ (µg m$^{−3}$ yr$^{-1}$)',
            transform=axs[0,i].transAxes,
            fontsize=12,
            rotation=90,
            va='center'
        )



for i,method in enumerate(methods):

    d=datasets[method]

    met_max = 10
    mesh=plot_panel(
        axs[1,i],
        d['MET'],
        d['lons'],
        d['lats'],
        f"{labels[i+4]} {method}",
        met_max)


    if i==0:
        axs[1,i].text(
            -0.25,
            0.5,
            r'PM$_{2.5}^{\mathrm{MET}}$ (µg m$^{−3}$ yr$^{-1}$)',
            transform=axs[1,i].transAxes,
            fontsize=12,
            rotation=90,
            va='center'
        )




plt.subplots_adjust(
    wspace=-0.5

)


plt.savefig(
    'Figure_S2.tif',
    dpi=300,
    bbox_inches='tight'
)


plt.show()