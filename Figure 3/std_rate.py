# -*- coding: utf-8 -*-
"""
Created on Thu May 14 18:42:29 2026

@author: liuxi
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


pm25_diff = {
    'BTH': {'Emis_diff': -37, 'Met_diff': 37},
    'NEC': {'Emis_diff': 51, 'Met_diff': -51},
    'PRD': {'Emis_diff': -123, 'Met_diff': 123},
    'YRD': {'Emis_diff': 61, 'Met_diff': -61}
}

o3_diff = {
    'BTH': {'Emis_diff': 25, 'Met_diff': -25},
    'NEC': {'Emis_diff': 12, 'Met_diff': -12},
    'PRD': {'Emis_diff': 9, 'Met_diff': -9},
    'YRD': {'Emis_diff': 30, 'Met_diff': -30}
}

pm25_rho = {
    'BTH': 0.31,
    'YRD': -0.10,
    'NEC': 0.08,
    'PRD': 0.12
}

o3_rho = {
    'BTH': 0.50,
    'YRD': 0.41,
    'NEC': 0.42,
    'PRD': 0.81
}

regions = ['BTH', 'YRD', 'NEC', 'PRD']



def draw_panel(ax1, diff_dict, rho_dict, title, show_legend=False):

    x = np.arange(len(regions))

    emis_diff = np.array([diff_dict[r]['Met_diff'] for r in regions])
    abs_diff = np.abs(emis_diff)

    rho = np.array([rho_dict[r] for r in regions])

    colors = ['#d62728' if v > 0 else '#1f77b4'
              for v in emis_diff]



    bars = ax1.bar(
        x,
        abs_diff,
        color=colors,
        width=0.6,
        alpha=0.85
    )

    ax1.set_xticks(x)
    ax1.set_xticklabels(regions, fontsize=12)

    ax1.set_xlabel(
        'Region',
        fontsize=16
    )

    ax1.set_ylabel(
        r'$|\Delta \mathrm{RC}^{\mathrm{MET}}|$ (%)',
        fontsize=16
    )

    ax1.tick_params(
        axis='both',
        direction='in',
        labelsize=12
    )

    ax1.set_ylim(0, max(abs_diff) * 1.28)

    for i, v in enumerate(emis_diff):

        ax1.text(
            x[i],
            abs(v) + max(abs_diff) * 0.03,
            f'{abs(v):.0f}',
            ha='center',
            fontsize=12,
            color=colors[i],
        )



    ax2 = ax1.twinx()

    ax2.plot(
        x,
        rho,
        color='black',
        marker='o',
        linewidth=1.8,
        markersize=6
    )

    ax2.set_ylabel(
        "Spearman's ρ",
        fontsize=16
    )

    ax2.tick_params(
        axis='y',
        direction='in',
        labelsize=12
    )

    ax2.set_ylim(-0.2, 1.0)


    for i, r in enumerate(rho):

        ax2.text(
            x[i],
            r + 0.04,
            f'{r:.2f}',
            ha='center',
            fontsize=12
        )


    ax1.set_title(
        title,
        fontsize=18,
    )


    ax1.grid(
        axis='y',
        linestyle='--',
        alpha=0.3
    )


    if show_legend:

        legend_elements = [

            Patch(
                facecolor='#d62728',
                label='MLR > RF'
            ),

            Patch(
                facecolor='#1f77b4',
                label='RF > MLR'
            ),

            Line2D(
                [0], [0],
                color='black',
                marker='o',
                label="Spearman's ρ"
            )
        ]

        ax1.legend(
            handles=legend_elements,
            loc='upper left',
            frameon=False,
            fontsize=12
        )



fig, axes = plt.subplots(
    1, 2,
    figsize=(11, 4.5)
)


draw_panel(
    axes[0],
    pm25_diff,
    pm25_rho,
    r'(a) PM$_{2.5}$',
    show_legend=True
)


draw_panel(
    axes[1],
    o3_diff,
    o3_rho,
    r'(b) O$_3$'
)



plt.tight_layout()

plt.savefig(
    'Contribution_difference_vs_rho_combined.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()