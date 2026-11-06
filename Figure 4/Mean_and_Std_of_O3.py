import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


files_info = {
    'ERA5_MLR_10': './o3/result_MLR_10_features_era5.xlsx',
    'ERA5_RF_month': './o3/result_RF_month_era5.xlsx',
    
    'GC': './o3/result_GC.xlsx',
    'GC_MLR_10': './o3/result_MLR_10_features.xlsx',
    'GC_RF_month': './o3/result_RF_month.xlsx'
}


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
            if lon_min <= row['LON'] <= lon_max and lat_min <= row['LAT'] <= lat_max:
                return region
        return 'OTHER'
    df['region'] = df.apply(get_region, axis=1)
    return df


data_dict = {}
for key, path in files_info.items():
    df = pd.read_excel(path)
    need_cols = ['O3_Met_diff_2013_slope', 'LON', 'LAT']
    if all(c in df.columns for c in need_cols):
        df = assign_region(df)
        region_data = {
            r: df.loc[df['region'] == r, 'O3_Met_diff_2013_slope'].dropna().values
            for r in region_order
        }
        data_dict[key] = region_data
    else:
        print(f"⚠️ 缺少必要列 in {key}: {set(need_cols) - set(df.columns)}")


series = [
    ("GC",          "GC"),           
    ("MLR GEOS-FP", "GC_MLR_10"),    
    ("MLR ERA5",    "ERA5_MLR_10"),  
    ("RF GEOS-FP",  "GC_RF_month"),   
    ("RF ERA5",     "ERA5_RF_month"),  
]

series_style = {
    "GC":          dict(color="red",   marker="o"),
    "MLR GEOS-FP": dict(color="blue",  marker="o"),
    "MLR ERA5":    dict(color="blue",  marker="s"),
    "RF GEOS-FP":  dict(color="green", marker="o"),
    "RF ERA5":     dict(color="green", marker="s"),
}


mean_map = {name: [] for name, _ in series}
std_map  = {name: [] for name, _ in series}

for region in region_order:
    for name, key in series:
        vals = data_dict.get(key, {}).get(region, np.array([np.nan], dtype=float))
        m = np.nanmean(vals)
        s = np.nanstd(vals, ddof=0)
        mean_map[name].append(m)
        std_map[name].append(s)


fig, ax = plt.subplots(figsize=(6, 4))

x = np.arange(len(region_order))  


offsets = [-0.32, -0.16, 0.00, 0.16, 0.32]
capsize = 4

for (name, _), dx in zip(series, offsets):
    style = series_style[name]
    ax.errorbar(
        x + dx,
        mean_map[name],
        yerr=std_map[name],
        fmt=style["marker"],
        color=style["color"],        
        ecolor=style["color"],     
        markersize=6,
        capsize=capsize,
        elinewidth=1.2,
        linewidth=0,
        label=name
    )

xtick_positions = np.arange(len(region_order))


ax.axhline(y=0, linestyle="--", color="black", linewidth=1)

ax.set_xticks(x)
ax.set_xticklabels(region_order)
ax.set_ylabel(r'O$_{3}^{\mathrm{MET}}$ (ppbv yr$^{-1}$)', fontsize=16)


ax.text(
    0.1, 0.95, "(b)",
    transform=ax.transAxes,
    fontsize=18, fontweight='bold',
    ha='right', va='top'
)


for i, xv in enumerate(xtick_positions):
    if i % 2 == 0:
        ax.axvspan(
            xv - 0.5, xv + 0.5,
            color='lightgray',
            alpha=0.3,
            zorder=0
        )

ax.grid(axis='y', linestyle='--', alpha=0.4)
plt.xlabel("Region", fontsize=16)


ax.tick_params(axis='both', direction='in', labelsize=14)


ax.set_xlim(min(xtick_positions) - 0.5, max(xtick_positions) + 0.5)
ax.set_ylim(-0.7, 1.8)

plt.tight_layout()

out_fig = './o3_effect_5methods_allregions.tif'
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.show()

print(f"✅ 完成：单图（所有区域）+ 5种方法（含GC）已保存：{out_fig}")


rows = []
for region in region_order:
    for name, _ in series:
        idx = region_order.index(region)
        m = mean_map[name][idx]
        s = std_map[name][idx]
        rows.append({
            "Region": region,
            "Method": name,
            "Mean": m,
            "Std": s,
            "Mean ± Std": f"{m:.2f} ± {s:.2f}"
        })

formatted_df = pd.DataFrame(rows)
output_path = './o3_effect_summary_5methods_allregions.xlsx'
formatted_df.to_excel(output_path, index=False)
print(f"✅ 统计表已保存：{output_path}")
