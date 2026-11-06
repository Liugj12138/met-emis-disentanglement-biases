# -*- coding: utf-8 -*-
"""
Created on Sun May 17 21:18:34 2026

@author: liuxi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.lines import Line2D

regions = ['BTH', 'YRD', 'NEC', 'PRD']


winter_dir = 'METE_zl_PM25/'


colors = {'Geos-FP': 'blue', 'ERA5': 'red'}
labels = {'Geos-FP': 'GEOS-FP', 'ERA5': 'ERA5'}

custom_vars_MLR = {
    'BTH': ['RH', 'PBLH'],
    'NEC': ['PRECTOT', 'V850'],
    'PRD': ['V', 'PRECTOT'],
    'YRD': ['RH', 'V850'],
}

custom_vars_RF = {
    'BTH': ['RH', 'PBLH'],
    'NEC': ['RH', 'U'],
    'PRD': ['V', 'SWGDN'],
    'YRD': ['PBLH', 'U'],
}

var_units = {
    'T': 'T2M (℃)',
    'SLP': 'SLP (hPa)',
    'U': 'U10 (m s$^{-1}$)',
    'V': 'V10 (m s$^{-1}$)',
    'RH': 'RH (%)',
    'PRECTOT': 'PRECTOT (kg m$^{-2}$ s$^{-1}$, log)',
    'PBLH': 'PBLH (m)',
    'CLDTOT': 'CLDTOT (log)',
    'SWGDN': 'SWGDN (W m$^{-2}$)',
    'V850': 'V850 (m s$^{-1}$)',
}


xlims_winter = {
    'T': (-40, 30),
    'SLP': (990, 1050),
    'U': (-7.5, 10),
    'V': (-7.5, 7.5),
    'RH': (0, 100),
    'PRECTOT': (-50, 0),
    'PBLH': (-20, 2000),
    'CLDTOT': (-10, 0.5),
    'SWGDN': (0, 300),
    'V850': (-20, 15),
}


fig, axes = plt.subplots(4, 4, figsize=(18, 10))

plot_idx = 0

for r, region in enumerate(regions):

    winter_df = {
        src: pd.read_pickle(os.path.join(winter_dir, f'{src}_{region}_data.pkl'))
        for src in ['Geos-FP', 'ERA5']
    }

    vars_for_region = custom_vars_MLR[region][:2] + custom_vars_RF[region][:2]

    for c, var in enumerate(vars_for_region):

        ax = axes[r, c]
        winter_data = {}

        for src in ['Geos-FP', 'ERA5']:
            if var not in winter_df[src].columns:
                continue

            series = winter_df[src][var].dropna()

            if len(series) > 0:
                sns.kdeplot(series, color=colors[src], ax=ax)
                ax.axvline(series.median(), color=colors[src], linestyle='dashed')
                winter_data[src] = series

        ax.text(
            0.02, 0.95, f"({chr(97 + plot_idx)})",
            transform=ax.transAxes,
            ha='left',
            va='top',
            fontsize=12,
            fontweight='bold'
        )
        plot_idx += 1

        if var in ['PRECTOT', 'CLDTOT']:
            min_log = -50 if var == 'PRECTOT' else -10
            max_val = np.ceil(max([d.max() for d in winter_data.values()])) if winter_data else 0
            step = 10 if var == 'PRECTOT' else 2
            ticks = np.arange(min_log, max_val + step, step)

            ax.set_xticks(ticks)
            ax.set_xticklabels([f"$e^{{{int(t)}}}$" for t in ticks])

        if var in xlims_winter:
            ax.set_xlim(xlims_winter[var])


        if c == 0:
            ax.set_ylabel('Density', fontsize=12)
        else:
            ax.set_ylabel('')


        if c == 0:
            ax.text(
                -0.30, 0.5, region,
                va='center',
                ha='right',
                fontsize=18,
                transform=ax.transAxes
            )


        ax.set_xlabel(var_units.get(var, var), fontsize=12)


        if r == 0 and c == 0:
            legend_elements = [
                Line2D([0], [0], color=colors['Geos-FP'], lw=2, label=labels['Geos-FP']),
                Line2D([0], [0], color=colors['ERA5'], lw=2, label=labels['ERA5'])
            ]
            ax.legend(handles=legend_elements, fontsize=12, frameon=False)
        else:
            if ax.get_legend() is not None:
                ax.get_legend().remove()

        ax.tick_params(axis='both', direction='in', labelsize=10)


fig.text(
    0.285, 0.965, 'MLR',
    ha='center',
    va='center',
    fontsize=18,

)

fig.text(
    0.735, 0.965, 'RF',
    ha='center',
    va='center',
    fontsize=18,

)


plt.tight_layout(rect=[0, 0, 1, 0.94])

plt.savefig(
    os.path.join(winter_dir, 'ALLREGIONS_top2_MLR_RF_winter_4x4.jpg'),
    dpi=600,
    bbox_inches='tight'
)

plt.close()

print("Saved ALLREGIONS_top2_MLR_RF_winter_4x4.jpg")