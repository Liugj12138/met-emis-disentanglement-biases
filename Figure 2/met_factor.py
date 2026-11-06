# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 15:06:07 2026

@author: liuxi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import spearmanr

data_paths = {
    "PM25": {
        "mlr": "./pm/MLR.csv",
        "rf":  "./pm/RF.xlsx",
        "label": r"PM$_{2.5}$"
    },
    "O3": {
        "mlr": "./o3/MLR.csv",
        "rf":  "./o3/RF.xlsx",
        "label": r"O$_3$"
    }
}

regions = ["BTH", "YRD", "NEC", "PRD"]

fixed_order = [
    "T", "PRECTOT", "RH", "PBLH", "CLDTOT",
    "SLP", "SWGDN", "U", "V", "V850"
]

color_map = {
    "positive": "red",
    "negative": "#0072B2"
}

sign_map = {
    "+": "positive",
    "-": "negative",
    "positive": "positive",
    "negative": "negative"
}

offset = 0.15


def read_merge_data(mlr_path, rf_path):
    df_mlr = pd.read_csv(mlr_path)
    df_rf = pd.read_excel(rf_path)

    df_mlr.columns = df_mlr.columns.str.strip()
    df_rf.columns = df_rf.columns.str.strip()

    cols = ["Region", "Rank", "Variable", "Sign"]

    df_mlr = df_mlr[cols].copy()
    df_rf = df_rf[cols].copy()

    df_mlr["Sign"] = df_mlr["Sign"].map(sign_map)
    df_rf["Sign"] = df_rf["Sign"].map(sign_map)


    df = pd.merge(
        df_mlr,
        df_rf,
        on=["Region", "Variable"],
        suffixes=("_MLR", "_RF")
    )

    df = df.rename(columns={
        "Rank_MLR": "MLR_rank",
        "Rank_RF": "RF_rank",
        "Sign_MLR": "MLR_sign",
        "Sign_RF": "RF_sign"
    })

    df["d"] = df["MLR_rank"] - df["RF_rank"]

    return df


all_data = {
    pollutant: read_merge_data(paths["mlr"], paths["rf"])
    for pollutant, paths in data_paths.items()
}


fig, axes = plt.subplots(
    2, 4,
    figsize=(18, 9),
    sharex=True,
    sharey=True
)

rho_results = []

for row_idx, pollutant in enumerate(["PM25", "O3"]):

    df = all_data[pollutant]

    for col_idx, region in enumerate(regions):

        ax = axes[row_idx, col_idx]

        sub = df[df["Region"] == region].copy()

        sub["Variable"] = pd.Categorical(
            sub["Variable"],
            categories=fixed_order,
            ordered=True
        )

        sub = sub.sort_values("Variable").reset_index(drop=True)

        y_pos = np.arange(len(sub))

        mlr_x = sub["MLR_rank"] - offset
        rf_x = sub["RF_rank"] + offset

        size = 80 + np.abs(sub["d"]) * 45

        rho, p = spearmanr(sub["MLR_rank"], sub["RF_rank"])

        rho_results.append({
            "Pollutant": pollutant,
            "Region": region,
            "Spearman_rho": rho,
            "p_value": p
        })


        ax.scatter(
            mlr_x,
            y_pos,
            s=size,
            c=sub["MLR_sign"].map(color_map),
            edgecolor=sub["MLR_sign"].map(color_map),
            marker="o",
            linewidth=1.6,
            zorder=3
        )


        ax.scatter(
            rf_x,
            y_pos,
            s=size,
            facecolors="none",
            edgecolors=sub["RF_sign"].map(color_map),
            marker="o",
            linewidth=1.8,
            zorder=3
        )


        for i, row in sub.iterrows():
            ax.plot(
                [row["MLR_rank"] - offset, row["RF_rank"] + offset],
                [i, i],
                color="gray",
                linewidth=0.8,
                alpha=0.6,
                zorder=1
            )


        ax.set_title(rf"$\rho$ = {rho:.2f}", fontsize=16, pad=8)
        ax.set_xlim(0.2, 10.8)
        ax.set_xticks(range(1, 11))
        
        ax.set_ylim(len(fixed_order) -0.3, -0.7)
        ax.grid(axis="x", linestyle="--", alpha=0.35)

        ax.tick_params(
            axis="both",
            direction="in",
            length=5,
            width=1,
            labelbottom=True
        )


for col_idx, region in enumerate(regions):
    axes[0, col_idx].text(
        0.5, 1.18,
        region,
        transform=axes[0, col_idx].transAxes,
        ha="center",
        va="bottom",
        fontsize=18,
    )


axes[0, 0].set_yticks(np.arange(len(fixed_order)))
axes[0, 0].set_yticklabels(fixed_order, fontsize=11)
axes[0, 0].invert_yaxis()

for ax in axes[0, :]:
    ax.set_xlabel("")

for ax in axes[1, :]:
    ax.set_xlabel("Importance rank", fontsize=16)

axes[0, 0].set_ylabel("Meteorological variable", fontsize=16)
axes[1, 0].set_ylabel("Meteorological variable", fontsize=16)


fig.text(
    0.025, 0.72,
    r"PM$_{2.5}$",
    fontsize=18,
    va="center",
    ha="center",
    rotation=90
)

fig.text(
    0.025, 0.30,
    r"O$_3$",
    fontsize=18,
    va="center",
    ha="center",
    rotation=90
)


method_legend = [
    Line2D(
        [0], [0],
        marker="o",
        color="black",
        label="MLR",
        markerfacecolor="gray",
        markeredgecolor="gray",
        markersize=10,
        linestyle="None"
    ),
    Line2D(
        [0], [0],
        marker="o",
        color="black",
        label="RF",
        markerfacecolor="none",
        markeredgecolor="gray",
        markersize=10,
        linestyle="None"
    ),
]

sign_legend = [
    Line2D(
        [0], [0],
        marker="o",
        color="red",
        label="Positive effect",
        markerfacecolor="red",
        markeredgecolor="red",
        markersize=10,
        linestyle="None"
    ),
    Line2D(
        [0], [0],
        marker="o",
        color="#0072B2",
        label="Negative effect",
        markerfacecolor="#0072B2",
        markeredgecolor="#0072B2",
        markersize=10,
        linestyle="None"
    ),
]

legend1 = fig.legend(
    handles=method_legend,
    title="Method",
    loc="center left",
    bbox_to_anchor=(0.91, 0.62),
    frameon=False,
    fontsize=12,       
    title_fontsize=13  
)

legend2 = fig.legend(
    handles=sign_legend,
    title="Effect direction",
    loc="center left",
    bbox_to_anchor=(0.91, 0.42),
    frameon=False,
    fontsize=12,       
    title_fontsize=13   
)


plt.tight_layout(rect=[0.06, 0.05, 0.89, 0.95])

output_path = 'Fig2.tif'

plt.savefig(output_path, dpi=300, bbox_inches='tight')