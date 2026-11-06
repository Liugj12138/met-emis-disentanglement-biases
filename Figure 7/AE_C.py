# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 16:10:29 2026

@author: liuxi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df_pm = pd.read_excel(
    'AE_C_PM.xlsx'
)

df_o3 = pd.read_excel(
    'AE_C_O3.xlsx'
)

regions_order = ['BTH', 'YRD', 'NEC', 'PRD']

mlr_base = '#2b6a99'
rf_base = '#f16c23'
rf_region_base = '#2ca02c' 


def finite_xy(df, xcol, ycol):
    sub = df[[xcol, ycol]].copy()
    sub = sub.replace([np.inf, -np.inf], np.nan).dropna()
    return sub

r_pm = []
r_o3 = []


fig, axes = plt.subplots(2, 4, figsize=(15, 7), dpi=150)
axes = axes.ravel()
label_id = 0

for i, region in enumerate(regions_order):
    ax = axes[i]

    sub = df_pm.loc[df_pm['region'] == region].copy()

    sub['SYNC_GC_abs'] = np.abs(sub['SYNC_GC'])

    mlr_xy = finite_xy(
        sub, 'SYNC_GC_abs', 'MLR_MET_AE'
    )

    rf_xy = finite_xy(
        sub, 'SYNC_GC_abs', 'RF_MET_AE'
    )

    rf_region_xy = finite_xy(
        sub, 'SYNC_GC_abs', 'RF-region_MET_AE'
    )

    r_mlr = np.nan
    r_rf = np.nan
    r_rf_region = np.nan

    if len(mlr_xy) > 1:
        r_mlr = np.corrcoef(
            mlr_xy['SYNC_GC_abs'],
            mlr_xy['MLR_MET_AE']
        )[0, 1]

    if len(rf_xy) > 1:
        r_rf = np.corrcoef(
            rf_xy['SYNC_GC_abs'],
            rf_xy['RF_MET_AE']
        )[0, 1]

    if len(rf_region_xy) > 1:
        r_rf_region = np.corrcoef(
            rf_region_xy['SYNC_GC_abs'],
            rf_region_xy['RF-region_MET_AE']
        )[0, 1]

    r_pm.append({
        'Region': region,
        'MLR_r': r_mlr,
        'RF_r': r_rf,
        'RF-region_r': r_rf_region
    })

    ax.scatter(
        mlr_xy['SYNC_GC_abs'],
        mlr_xy['MLR_MET_AE'],
        s=22,
        alpha=0.8,
        edgecolors=mlr_base,
        color='none'
    )

    ax.scatter(
        rf_xy['SYNC_GC_abs'],
        rf_xy['RF_MET_AE'],
        s=22,
        alpha=0.8,
        edgecolors=rf_base,
        color='none'
    )

    ax.scatter(
        rf_region_xy['SYNC_GC_abs'],
        rf_region_xy['RF-region_MET_AE'],
        s=22,
        alpha=0.8,
        edgecolors=rf_region_base,
        color='none'
    )

    if len(mlr_xy) > 1:
        k, b = np.polyfit(
            mlr_xy['SYNC_GC_abs'],
            mlr_xy['MLR_MET_AE'],
            1
        )

        x_line = np.linspace(
            mlr_xy['SYNC_GC_abs'].min(),
            mlr_xy['SYNC_GC_abs'].max(),
            100
        )

        ax.plot(
            x_line,
            k * x_line + b,
            color=mlr_base,
            linewidth=1
        )

        r = np.corrcoef(
            mlr_xy['SYNC_GC_abs'],
            mlr_xy['MLR_MET_AE']
        )[0, 1]

        ax.text(
            0.6, 0.98,
            f'r = {r:.2f}',
            transform=ax.transAxes,
            color=mlr_base,
            fontsize=14,
            ha='left',
            va='top'
        )

    if len(rf_xy) > 1:
        k, b = np.polyfit(
            rf_xy['SYNC_GC_abs'],
            rf_xy['RF_MET_AE'],
            1
        )

        x_line = np.linspace(
            rf_xy['SYNC_GC_abs'].min(),
            rf_xy['SYNC_GC_abs'].max(),
            100
        )

        ax.plot(
            x_line,
            k * x_line + b,
            color=rf_base,
            linewidth=1
        )

        r = np.corrcoef(
            rf_xy['SYNC_GC_abs'],
            rf_xy['RF_MET_AE']
        )[0, 1]

        ax.text(
            0.6, 0.90,
            f'r = {r:.2f}',
            transform=ax.transAxes,
            color=rf_base,
            fontsize=14,
            ha='left',
            va='top'
        )

    if len(rf_region_xy) > 1:
        k, b = np.polyfit(
            rf_region_xy['SYNC_GC_abs'],
            rf_region_xy['RF-region_MET_AE'],
            1
        )

        x_line = np.linspace(
            rf_region_xy['SYNC_GC_abs'].min(),
            rf_region_xy['SYNC_GC_abs'].max(),
            100
        )

        ax.plot(
            x_line,
            k * x_line + b,
            color=rf_region_base,
            linewidth=1
        )

        r = np.corrcoef(
            rf_region_xy['SYNC_GC_abs'],
            rf_region_xy['RF-region_MET_AE']
        )[0, 1]

        ax.text(
            0.6, 0.82,
            f'r = {r:.2f}',
            transform=ax.transAxes,
            color=rf_region_base,
            fontsize=14,
            ha='left',
            va='top'
        )

    ax.text(
        0.02, 0.98,
        f'({chr(97 + label_id)})',
        transform=ax.transAxes,
        fontsize=16,
        va='top'
    )

    label_id += 1

    ax.set_title(region, fontsize=15)

    if i == 0:
        ax.set_ylabel(
            'AE$_{att}$ PM$_{2.5}^{\\mathrm{MET}}$ '
            '(µg m$^{-3}$ yr$^{-1}$)',
            fontsize=13
        )
    else:
        ax.set_ylabel('')

    ax.set_xlabel('')
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.tick_params(direction='in')

for i, region in enumerate(regions_order):
    ax = axes[i + 4]

    sub = df_o3.loc[df_o3['region'] == region].copy()

    sub['SYNC_GC_abs'] = np.abs(sub['SYNC_GC'])

    mlr_xy = finite_xy(
        sub, 'SYNC_GC_abs', 'MLR_MET_AE'
    )

    rf_xy = finite_xy(
        sub, 'SYNC_GC_abs', 'RF_MET_AE'
    )

    rf_region_xy = finite_xy(
        sub, 'SYNC_GC_abs', 'RF-region_MET_AE'
    )

    r_mlr = np.nan
    r_rf = np.nan
    r_rf_region = np.nan

    if len(mlr_xy) > 1:
        r_mlr = np.corrcoef(
            mlr_xy['SYNC_GC_abs'],
            mlr_xy['MLR_MET_AE']
        )[0, 1]

    if len(rf_xy) > 1:
        r_rf = np.corrcoef(
            rf_xy['SYNC_GC_abs'],
            rf_xy['RF_MET_AE']
        )[0, 1]

    if len(rf_region_xy) > 1:
        r_rf_region = np.corrcoef(
            rf_region_xy['SYNC_GC_abs'],
            rf_region_xy['RF-region_MET_AE']
        )[0, 1]

    r_o3.append({
        'Region': region,
        'MLR_r': r_mlr,
        'RF_r': r_rf,
        'RF-region_r': r_rf_region
    })

    ax.scatter(
        mlr_xy['SYNC_GC_abs'],
        mlr_xy['MLR_MET_AE'],
        s=22,
        alpha=0.8,
        edgecolors=mlr_base,
        color='none'
    )

    ax.scatter(
        rf_xy['SYNC_GC_abs'],
        rf_xy['RF_MET_AE'],
        s=22,
        alpha=0.8,
        edgecolors=rf_base,
        color='none'
    )

    ax.scatter(
        rf_region_xy['SYNC_GC_abs'],
        rf_region_xy['RF-region_MET_AE'],
        s=22,
        alpha=0.8,
        edgecolors=rf_region_base,
        color='none'
    )

    if len(mlr_xy) > 1:
        k, b = np.polyfit(
            mlr_xy['SYNC_GC_abs'],
            mlr_xy['MLR_MET_AE'],
            1
        )

        x_line = np.linspace(
            mlr_xy['SYNC_GC_abs'].min(),
            mlr_xy['SYNC_GC_abs'].max(),
            100
        )

        ax.plot(
            x_line,
            k * x_line + b,
            color=mlr_base,
            linewidth=1
        )

        r = np.corrcoef(
            mlr_xy['SYNC_GC_abs'],
            mlr_xy['MLR_MET_AE']
        )[0, 1]

        ax.text(
            0.6, 0.98,
            f'r = {r:.2f}',
            transform=ax.transAxes,
            color=mlr_base,
            fontsize=14,
            ha='left',
            va='top'
        )

    if len(rf_xy) > 1:
        k, b = np.polyfit(
            rf_xy['SYNC_GC_abs'],
            rf_xy['RF_MET_AE'],
            1
        )

        x_line = np.linspace(
            rf_xy['SYNC_GC_abs'].min(),
            rf_xy['SYNC_GC_abs'].max(),
            100
        )

        ax.plot(
            x_line,
            k * x_line + b,
            color=rf_base,
            linewidth=1
        )

        r = np.corrcoef(
            rf_xy['SYNC_GC_abs'],
            rf_xy['RF_MET_AE']
        )[0, 1]

        ax.text(
            0.6, 0.90,
            f'r = {r:.2f}',
            transform=ax.transAxes,
            color=rf_base,
            fontsize=14,
            ha='left',
            va='top'
        )

    if len(rf_region_xy) > 1:
        k, b = np.polyfit(
            rf_region_xy['SYNC_GC_abs'],
            rf_region_xy['RF-region_MET_AE'],
            1
        )

        x_line = np.linspace(
            rf_region_xy['SYNC_GC_abs'].min(),
            rf_region_xy['SYNC_GC_abs'].max(),
            100
        )

        ax.plot(
            x_line,
            k * x_line + b,
            color=rf_region_base,
            linewidth=1
        )

        r = np.corrcoef(
            rf_region_xy['SYNC_GC_abs'],
            rf_region_xy['RF-region_MET_AE']
        )[0, 1]

        ax.text(
            0.6, 0.82,
            f'r = {r:.2f}',
            transform=ax.transAxes,
            color=rf_region_base,
            fontsize=14,
            ha='left',
            va='top'
        )

    ax.text(
        0.02, 0.98,
        f'({chr(97 + label_id)})',
        transform=ax.transAxes,
        fontsize=16,
        va='top'
    )

    label_id += 1

    if i == 0:
        ax.set_ylabel(
            'AE$_{att}$ O$_{3}^{\\mathrm{MET}}$ '
            '(ppbv yr$^{-1}$)',
            fontsize=13
        )
    else:
        ax.set_ylabel('')

    ax.set_xlabel('C$_{GC}$', fontsize=13)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.tick_params(direction='in')


plt.tight_layout()
fig.subplots_adjust(bottom=0.08)

out_path = Path('.') / 'AE_C.tif'

plt.savefig(
    out_path,
    dpi=300,
    bbox_inches='tight'
)

plt.show()

print(f'图像已保存: {out_path.resolve()}')


pd.DataFrame(r_pm).to_excel(
    'PM25_AE_C.xlsx',
    index=False
)

pd.DataFrame(r_o3).to_excel(
    'O3_AE_C.xlsx',
    index=False
)

print('r 已保存完成')