# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 13:03:23 2026

@author: liuxi
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'mathtext.fontset': 'dejavusans',
    'axes.unicode_minus': False,
    'savefig.facecolor': 'white',
    'figure.facecolor': 'white'
})

mlr_base = '#2b6a99'
rf_base = '#f16c23'
rf_region_base = '#2ca02c'

df_pm = pd.read_excel('./AE_R2_PM25.xlsx')

df_o3 = pd.read_excel('./AE_R2_O3.xlsx')

regions = ['YRD', 'PRD', 'NEC', 'BTH']

def get_values(df, col):

    if 'Region' not in df.columns:
        raise ValueError('Excel文件中缺少 Region 列')

    if col not in df.columns:
        raise ValueError(f'Excel文件中缺少 {col} 列')

    region_names = df['Region'].astype(str).str.strip()

    values = []

    for region in regions:

        matched = df.loc[
            region_names == region, col
        ]

        if len(matched) != 1:
            raise ValueError(
                f'{region} 在 {col} 中应当对应一条记录，'
                f'实际找到 {len(matched)} 条'
            )

        value = pd.to_numeric(
            matched.iloc[0],
            errors='coerce'
        )

        if not np.isfinite(value):
            raise ValueError(
                f'{region} 的 {col} 存在缺失值或非数值'
            )

        values.append(float(value))

    values = np.array(values)

    if np.any(values < -1.0) or np.any(values > 1.0):
        raise ValueError(
            f'{col} 中存在超出 [-1, 1] 的相关系数'
        )

    return values


# PM2.5
pm_mlr = get_values(df_pm, 'MLR_r')
pm_rf = get_values(df_pm, 'RF_r')
pm_rf_region = get_values(df_pm, 'RF-region_r')

# O3
o3_mlr = get_values(df_o3, 'MLR_r')
o3_rf = get_values(df_o3, 'RF_r')
o3_rf_region = get_values(df_o3, 'RF-region_r')

angles = np.linspace(
    0,
    2 * np.pi,
    len(regions),
    endpoint=False
)

angles = np.concatenate([
    angles,
    [angles[0]]
])


def close(vals):

    vals = np.asarray(vals, dtype=float)

    return np.concatenate([
        vals,
        [vals[0]]
    ])



def to_radius(vals):

    vals = np.asarray(vals, dtype=float)

    return (vals + 1.0) / 2.0

def adjust_label_radii(
    radii,
    min_separation=0.08,
    label_gap=0.095
):

    radii = np.asarray(radii, dtype=float)

    adjusted = radii.copy()

    order = np.argsort(radii)

    groups = []

    current_group = [order[0]]

    for idx in order[1:]:

        if (
            radii[idx] - radii[current_group[-1]]
            < min_separation
        ):

            current_group.append(idx)

        else:

            groups.append(current_group)

            current_group = [idx]

    groups.append(current_group)

    for group in groups:

        if len(group) <= 1:
            continue

        group = np.asarray(group)

        center = np.mean(radii[group])

        n = len(group)

        offsets = (
            np.arange(n) - (n - 1) / 2
        ) * label_gap

        new_positions = center + offsets

        lower_limit = 0.035
        upper_limit = 0.965

        if new_positions.min() < lower_limit:

            new_positions += (
                lower_limit - new_positions.min()
            )

        if new_positions.max() > upper_limit:

            new_positions -= (
                new_positions.max() - upper_limit
            )

        adjusted[group] = new_positions

    return adjusted

def annotate_r_three(
    ax,
    values_dict,
    panel_name=None
):

    model_names = [
        'MLR',
        'RF',
        'RF-region'
    ]

    model_colors = [
        mlr_base,
        rf_base,
        rf_region_base
    ]

    text_effect = [
        path_effects.withStroke(
            linewidth=2.5,
            foreground='white'
        )
    ]

    for i, angle in enumerate(angles[:-1]):

        values = np.array([
            values_dict[name][i]
            for name in model_names
        ])

        radii = to_radius(values)

        label_radii = adjust_label_radii(radii)

        manual_offsets = [
            (0, 0),
            (0, 0),
            (0, 0)
        ]

        if panel_name == 'PM25' and i == 3:

            manual_offsets = [
                (0, 0), 
                (-4, 3), 
                (0, 0) 
            ]


        for j, (value, radius, color) in enumerate(
            zip(
                values,
                label_radii,
                model_colors
            )
        ):

            dx, dy = manual_offsets[j]

            ax.annotate(

                f'{value:.2f}',

                xy=(angle, radius),

                xytext=(dx, dy),

                textcoords='offset points',

                color=color,

                fontsize=8.5,

                fontweight='medium',

                ha='center',

                va='center',

                path_effects=text_effect,

                annotation_clip=False,

                zorder=10

            )

def add_center_ticks(ax):

    levels_true = [
        -1.0,
        -0.5,
        0.0,
        0.5,
        1.0
    ]

    levels_plot = to_radius(levels_true)

    tick_angle = -3 * np.pi / 4

    radial_factor = np.cos(np.pi / 4)

    text_effect = [
        path_effects.withStroke(
            linewidth=2.0,
            foreground='white'
        )
    ]

    for true_value, radius in zip(
        levels_true,
        levels_plot
    ):

        radius = radius * radial_factor

        radius = max(radius, 0.025)

        ax.text(
            tick_angle,
            radius,

            f'{true_value:.1f}',

            color='#666666',
            fontsize=8,

            ha='center',
            va='center',

            path_effects=text_effect,

            zorder=5
        )

def radar_style(
    ax,
    show_scale_labels=True
):

    ax.grid(False)

    ax.spines['polar'].set_visible(False)

    ax.set_theta_offset(np.pi / 4)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])

    ax.set_xticklabels(
        regions,
        fontsize=10,
        fontweight='medium',
        color='#333333'
    )

    ax.tick_params(
        axis='x',
        pad=10
    )

    ax.set_ylim(0, 1)

    ax.set_yticks([])

    zero_radius = to_radius(0.0)  # r = 0 对应半径 0.5
    
    ax.fill(
        angles,
        np.repeat(zero_radius, len(angles)),
        facecolor='#E8E8E8',
        alpha=0.40,
        edgecolor='none',
        zorder=-1
    )

    levels_true = [
        -1.0,
        -0.5,
        0.0,
        0.5,
        1.0
    ]
    
    levels_plot = to_radius(levels_true)
    
    for true_value, radius in zip(
        levels_true,
        levels_plot
    ):
    
        vals = close(
            np.repeat(radius, len(regions))
        )

        if np.isclose(true_value, 0.0):
    
            ax.plot(
                angles,
                vals,
                color='#555555',
                linewidth=1.2,
                alpha=0.95,
                linestyle='--',
                zorder=2
            )

        elif np.isclose(true_value, 1.0):
    
            ax.plot(
                angles,
                vals,
                color='#888888',
                linewidth=0.9,
                alpha=0.9,
                linestyle='-',
                zorder=1
            )

        else:
    
            ax.plot(
                angles,
                vals,
                color='#D5D5D5',
                linewidth=0.55,
                alpha=0.8,
                linestyle='-',
                zorder=0
            )

        
        for angle in angles[:-1]:
        
            ax.plot(
                [angle, angle],
                [0, 1],
        
                color='#D5D5D5',
                linewidth=0.55,
                alpha=0.8,
        
                zorder=0
            )

    if show_scale_labels:

        add_center_ticks(ax)

def draw_radar_panel(
    ax,
    values_dict,
    title,
    show_scale_labels=True,
    panel_name=None
):

    radar_style(
        ax,
        show_scale_labels=show_scale_labels
    )

    model_styles = [

        {
            'name': 'MLR',
            'color': mlr_base,
            'linestyle': '-',
            'marker': 'o'
        },

        {
            'name': 'RF',
            'color': rf_base,
            'linestyle': '--',
            'marker': 's'
        },

        {
            'name': 'RF-region',
            'color': rf_region_base,
            'linestyle': '-.',
            'marker': '^'
        }

    ]

    line_handles = []

    for style in model_styles:

        name = style['name']
        color = style['color']

        values = values_dict[name]

        radii = close(
            to_radius(values)
        )

        line, = ax.plot(

            angles,
            radii,

            color=color,

            linewidth=1.7,

            linestyle=style['linestyle'],

            marker=style['marker'],

            markersize=4.5,

            markerfacecolor=color,

            markeredgecolor='white',

            markeredgewidth=0.8,

            label=name,

            zorder=4

        )

        line_handles.append(line)

    annotate_r_three(
        ax,
        values_dict,
        panel_name=panel_name
    )

    ax.set_title(
        title,

        fontsize=13.5,

        fontweight='semibold',

        color='#222222',

        pad=18
    )

    return line_handles

fig, axes = plt.subplots(

    1,
    2,

    subplot_kw=dict(polar=True),

    figsize=(9, 5.5)

)

fig.patch.set_facecolor('white')

pm_values = {

    'MLR': pm_mlr,

    'RF': pm_rf,

    'RF-region': pm_rf_region

}

legend_handles = draw_radar_panel(

    axes[0],

    pm_values,

    title='(a) PM$_{2.5}$',

    show_scale_labels=True,
    panel_name='PM25'

)

o3_values = {

    'MLR': o3_mlr,

    'RF': o3_rf,

    'RF-region': o3_rf_region

}

draw_radar_panel(

    axes[1],

    o3_values,

    title='(b) O$_3$',

    show_scale_labels=True,
    panel_name='O3'

)

fig.text(

    0.055,
    0.50,

    r'R$_{fit}^{2}$-AE$_{att}$',

    fontsize=11.5,

    rotation=90,

    ha='center',
    va='center',

    color='#333333'

)

axes[0].legend(

    handles=legend_handles,

    labels=[
        'MLR',
        'RF',
        'RF-region'
    ],

    loc='upper right',

    bbox_to_anchor=(0.98, 0.99),

    ncol=3,

    frameon=False,

    fontsize=10,

    handlelength=1.8,

    handletextpad=0.5,

    labelspacing=0.5,

    borderaxespad=0.2

)

fig.subplots_adjust(
    left=0.09,
    right=0.985,
    top=0.88,
    bottom=0.10,
    wspace=-0.1
)

output_file = 'AE_R2.tif'

fig.savefig(

    output_file,

    dpi=600,

    format='tiff',

    bbox_inches='tight',

    facecolor='white'

)


print(f'图片已保存：{output_file}')

plt.show()
