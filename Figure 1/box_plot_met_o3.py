# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 14:48:29 2026

@author: liuxi
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.patches import Patch
from matplotlib import colors
import matplotlib.colors as mcolors


# ---------- 区域设置 ----------
regions = {
    'NEC': [123, 128, 41, 48],
    'BTH': [114, 118, 37, 41],
    'YRD': [118, 122, 30, 33],
    'PRD': [112, 115.5, 21.5, 24],
}

region_order = ['BTH', 'YRD', 'NEC', 'PRD']


def assign_region(df):

    def get_region(row):

        for region, bounds in regions.items():

            lon_min, lon_max, lat_min, lat_max = bounds

            if (
                lon_min <= row['LON'] <= lon_max
                and lat_min <= row['LAT'] <= lat_max
            ):
                return region

        return 'OTHER'

    df['region'] = df.apply(get_region, axis=1)

    return df



files = {
    'GC': './o3/result_GC.xlsx',
    'MLR-std': './o3/result_MLR_10_features.xlsx',
    'MLR-5var': './o3/result_MLR_5_features.xlsx',
    'MLR-stp': './o3/result_MLR_5_choice.xlsx',
    'RF-std': './o3/result_RF_month.xlsx',
    'RF-day': './o3/result_RF_day.xlsx',
    'RF-region':'./o3/result_RF_region.xlsx'
}



# ---------- 读取数据 ----------
all_data = []


for model_name, path in files.items():

    if not os.path.exists(path):

        print(f"跳过未找到文件: {path}")

        continue


    df = pd.read_excel(path)


    df = assign_region(df)


    df = df[
        df['region'].isin(region_order)
    ]


    if 'O3_Met_diff_2013_slope' not in df.columns:

        print(
            f"{model_name} 缺少 O3_Met_diff_2013_slope"
        )

        continue


    df_model = df[
        [
            'region',
            'O3_Met_diff_2013_slope'
        ]
    ].copy()


    df_model['Model'] = model_name


    all_data.append(df_model)



df_long = pd.concat(
    all_data,
    ignore_index=True
)



# ---------- 颜色函数 ----------
def adjust_lightness(color, amount=1.2):

    try:
        c = colors.cnames[color]

    except:

        c = color


    c = colors.to_rgb(c)


    return colors.to_hex(
        [
            min(1, c[0] * amount),
            min(1, c[1] * amount),
            min(1, c[2] * amount)
        ]
    )



def adjust_alpha(color, alpha=0.5):

    rgba = mcolors.to_rgba(color)

    return (
        rgba[0],
        rgba[1],
        rgba[2],
        alpha
    )



mlr_base = '#3F698E'

rf_base = '#5CB85C'



box_colors = {

    'GC':
    '#F9A7A7',

    'MLR-std':
    mlr_base,

    'MLR-5var':
    adjust_lightness(
        mlr_base,
        1.5
    ),

    'MLR-stp':
    adjust_lightness(
        mlr_base,
        2
    ),

    'RF-std':
    rf_base,

    'RF-day':
    adjust_alpha(
        rf_base,
        0.5
    ),

    'RF-region':
    adjust_alpha(
        rf_base,
        0.2
    )

}



edge_colors = {

    'GC':
    'darkred',

    'MLR-std':
    'darkblue',

    'MLR-5var':
    'darkblue',

    'MLR-stp':
    'darkblue',

    'RF-std':
    'darkgreen',

    'RF-day':
    'darkgreen',

    'RF-region':
    'darkgreen'

}



# ---------- 模型顺序 ----------
models = [

    'GC',
    'MLR-std',
    'MLR-5var',
    'MLR-stp',
    'RF-std',
    'RF-day',
    'RF-region'

]



# 7个箱子均匀分布
offsets = np.linspace(
    -0.4,
    0.4,
    len(models)
)


hue_offsets = dict(
    zip(models, offsets)
)


box_width = 0.1



# ---------- 绘图 ----------
plt.figure(
    figsize=(8,4)
)

ax = plt.gca()



xtick_positions = np.arange(
    len(region_order)
)


region_pos_map = dict(
    zip(
        region_order,
        xtick_positions
    )
)



for model in models:


    y_data = []

    positions = []


    for region in region_order:


        values = df_long[
            (df_long['region']==region)
            &
            (df_long['Model']==model)
        ]['O3_Met_diff_2013_slope'].values



        if len(values)>0:


            y_data.append(values)


            pos = (
                region_pos_map[region]
                +
                hue_offsets[model]
            )


            positions.append(pos)



            mean_val = np.mean(values)


            ax.plot(

                pos,

                mean_val,

                marker="*",

                markersize=8,

                markerfacecolor="none",

                markeredgecolor=edge_colors[model],

                markeredgewidth=1.2,

                zorder=5
            )



    if len(y_data)>0:


        ax.boxplot(

            y_data,

            positions=positions,

            widths=box_width,

            patch_artist=True,


            boxprops=dict(
                facecolor=box_colors[model],
                color=edge_colors[model],
                linewidth=1.2
            ),


            medianprops=dict(
                color=edge_colors[model],
                linewidth=1.2
            ),


            whiskerprops=dict(
                color=edge_colors[model],
                linewidth=1.2
            ),


            capprops=dict(
                color=edge_colors[model],
                linewidth=1.2
            ),


            flierprops=dict(
                marker='o',
                markersize=3,
                markerfacecolor=box_colors[model],
                markeredgecolor=edge_colors[model]
            )

        )



# ---------- 背景 ----------
for i,x in enumerate(xtick_positions):

    if i%2==0:

        ax.axvspan(
            x-0.5,
            x+0.5,
            color='lightgray',
            alpha=0.3,
            zorder=0
        )



ax.set_xlim(
    -0.5,
    len(region_order)-0.5
)



ax.set_xticks(
    xtick_positions
)

ax.set_xticklabels(
    region_order
)


plt.xlabel(
    "Region",
    fontsize=16
)


plt.ylabel(
    r'O$_{3}^{\mathrm{MET}}$ (ppbv yr$^{-1}$)',
    fontsize=16
)



ax.axhline(
    y=0,
    linestyle="--",
    color="black",
    linewidth=1
)



# ---------- legend ----------
legend_elements = [

    Patch(
        facecolor=box_colors[m],
        edgecolor=edge_colors[m],
        label=m
    )

    for m in models

]


# plt.legend(
#     handles=legend_elements,
#     loc='best',
#     frameon=True,
#     ncols=2
# )



for spine in ax.spines.values():

    spine.set_visible(True)

    spine.set_color("black")

    spine.set_linewidth(1)



ax.tick_params(

    axis='both',

    which='both',

    direction='in',

    length=5,

    width=1,

    labelsize=14

)



ax.grid(False)



ax.text(

    0.98,
    0.95,

    "(d)",

    transform=ax.transAxes,

    fontsize=18,

    fontweight='bold',

    ha='right',

    va='top'

)



output_path = (
    'boxplot_O3_Met_diff_2013_slope_all_models'
)



plt.tight_layout()


plt.savefig(
    output_path,
    dpi=300,
    bbox_inches='tight'
)


print(
    f"图像已保存: {output_path}"
)


plt.show()