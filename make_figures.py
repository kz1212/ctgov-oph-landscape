import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as mtick
import matplotlib as mpl

# ==============================

SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 16

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)    # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)


if not os.path.exists('outputs'):
    os.makedirs('outputs')


print("Loading data...")
df = pd.read_csv('outputs/oph_master_final_rebuild.csv')


# ==============================================================================
# HEATMAP VARIATIONS 
# ==============================================================================

df_heatmap = df.copy()
heatmap_data = pd.crosstab(df_heatmap['axisA_subspecialty'], df_heatmap['axisB_modality'])
heatmap_data['Total'] = heatmap_data.sum(axis=1)
heatmap_data = heatmap_data.sort_values('Total', ascending=False).drop(columns='Total')

heatmap_variations = [
    ('A_Standard_Viridis', 'viridis', 'Standard scientific (Green-Blue-Yellow)'),
    ('B_CVD_Safe_Cividis', 'cividis', 'Optimized for Colorblindness (Blue-Yellow)'),
    ('C_Cool_Tone_Mako', 'mako', 'Cool tones (Teal-Blueish)'),
    ('D_Warm_Tone_Magma', 'magma', 'Warm tones (Black-Red-Yellow)'),
]

for var_name, cmap_name, desc in heatmap_variations:
    plt.figure(figsize=(14, 10))
    # Use a slightly larger font for annotations in the heatmap cells
    sns.heatmap(heatmap_data, annot=True, fmt='d', cmap=cmap_name, 
                linewidths=.5, cbar_kws={'label': 'Number of Trials'},
                annot_kws={"size": 11}) 
    
    plt.title(f'Figure 1: Ophthalmic Clinical Trials by Subspecialty and Modality', pad=20)
    plt.ylabel('Subspecialty', fontweight='bold')
    plt.xlabel('Modality', fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    filename = f'outputs/Figure_1_Heatmap_{var_name}.png'
    plt.savefig(filename, dpi=300)
    print(f"  > Saved {filename} ({desc})")
    plt.close() # Close plot to free memory


# ==============================================================================
# BAR PLOT VARIATIONS
# ==============================================================================

sponsor_counts = df.groupby(['axisA_subspecialty', 'sponsor_class']).size().unstack(fill_value=0)
sponsor_counts['Total'] = sponsor_counts.sum(axis=1)
sponsor_counts['Industry_Pct'] = (sponsor_counts['Industry'] / sponsor_counts['Total']) * 100
sponsor_counts = sponsor_counts.sort_values('Industry_Pct', ascending=False)

# (inherently colorblind safe)
bar_variations = [
    ('A_Academic_Blue', 'Blues_r', 'Standard Academic Blue'),
    ('B_Neutral_Grey', 'Greys_r', 'Neutral Greyscale for print'),
    ('C_Teal_Green', 'YlGnBu_r', 'Teal-Green-Blue ramp'),
]

for var_name, palette_name, desc in bar_variations:
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(x=sponsor_counts['Industry_Pct'], y=sponsor_counts.index, 
                     palette=palette_name, edgecolor='black', linewidth=0.7)

    plt.title('Figure 2: Industry Sponsorship Share by Subspecialty', pad=20)
    plt.xlabel('Percentage of Trials Led by Industry (%)', fontweight='bold')
    plt.ylabel('Subspecialty', fontweight='bold')
    plt.xlim(0, 105) # Give space for labels
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.grid(axis='x', linestyle='--') # Add vertical gridlines for easier reading

    # Add text labels
    for i, v in enumerate(sponsor_counts['Industry_Pct']):
        ax.text(v + 1, i, f"{v:.1f}%", color='black', va='center', fontsize=11)

    plt.tight_layout()
    filename = f'outputs/Figure_2_Bar_{var_name}.png'
    plt.savefig(filename, dpi=300)
    print(f"  > Saved {filename} ({desc})")
    plt.close()


# ==============================================================================
# RETINA TRENDS VARIATIONS 
# ==============================================================================


retina_types = ['Medical Retina', 'Surgical Retina', 'Retina (Other/Unclear)']
df_retina = df[df['final_category'].isin(retina_types)]
trend_data = df_retina.groupby(['year', 'final_category']).size().reset_index(name='count')
trend_data = trend_data[(trend_data['year'] >= 1999) & (trend_data['year'] <= 2025)]

# --- Seaborn ---
plt.figure(figsize=(12, 8))
sns.lineplot(data=trend_data, x='year', y='count', hue='final_category', 
             style='final_category', # Vary style too, not just color
             markers=True, dashes=False, linewidth=3, markersize=10,
             palette='colorblind') # Use Seaborn's built-in CVD palette

plt.title('Figure 3 (Var A): Longitudinal Trends in Retina Research (1999-2025)', pad=20)
plt.ylabel('Number of New Trials Registered', fontweight='bold')
plt.xlabel('Year', fontweight='bold')
plt.legend(title='Retina Subtype', title_fontsize='13', fontsize='12')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig('outputs/Figure_3_Trends_A_ColorblindPalette.png', dpi=300)
print("  > Saved Figure_3_Trends_A_ColorblindPalette.png")
plt.close()

# --- High-Contrast---
# This is the most robust for black-and-white printing and severe colorblindness
custom_palette = {
    'Medical Retina': '#004488',      # Dark Blue (High contrast)
    'Surgical Retina': '#DDAA33',     # Dark Yellow/Gold (Distinct from blue)
    'Retina (Other/Unclear)': '#BB5566' # Muted Red/Rose (Distinct from others)
}
custom_styles = {
    'Medical Retina': (1, 0),        # Solid line
    'Surgical Retina': (4, 1.5),     # Dashed
    'Retina (Other/Unclear)': (1, 1) # Dotted
}
custom_markers = {
    'Medical Retina': 'o', # Circle
    'Surgical Retina': 's', # Square
    'Retina (Other/Unclear)': '^' # Triangle
}

plt.figure(figsize=(12, 8))
sns.lineplot(data=trend_data, x='year', y='count', hue='final_category', 
             style='final_category',
             markers=custom_markers, 
             dashes=custom_styles,
             linewidth=3, markersize=11,
             palette=custom_palette)

plt.title('Figure 3 (Var B): Longitudinal Trends (High Contrast/Accessible)', pad=20)
plt.ylabel('Number of New Trials Registered', fontweight='bold')
plt.xlabel('Year', fontweight='bold')
plt.legend(title='Retina Subtype', title_fontsize='13', fontsize='12')
plt.grid(True, which='major', linestyle='-', linewidth=0.7, color='lightgrey')
plt.tight_layout()
plt.savefig('outputs/Figure_3_Trends_B_HighContrast.png', dpi=300)
print("  > Saved Figure_3_Trends_B_HighContrast.png")
plt.close()


print("\nAll figure variations generated successfully.")