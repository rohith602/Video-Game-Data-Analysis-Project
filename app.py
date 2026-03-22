import os
import io
import base64
import numpy as np
import pandas as pd
from flask import Flask, jsonify
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- 1. CORE THEME & GLOBAL DATA ---
plt.rcParams.update({
    'figure.facecolor': '#000000',
    'axes.facecolor': '#000000',
    'axes.edgecolor': '#444444',
    'axes.labelcolor': '#ffffff',
    'text.color': '#ffffff',
    'xtick.color': '#cccccc',
    'ytick.color': '#cccccc',
    'grid.color': '#333333',
    'legend.facecolor': '#111111',
    'legend.edgecolor': '#333333',
    'legend.labelcolor': '#ffffff'
})

sales_columns = ['Year', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']
df = pd.read_csv('vgsales.csv')
df[sales_columns] = df[sales_columns].apply(pd.to_numeric, errors='coerce')

filtered_df = df.dropna(subset=['Year'])[lambda x: x['Year'] <= 2016]
regional_cols = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']

app = Flask(__name__, static_folder='.', static_url_path='')

# --- 2. FRONTEND ROUTING ---
@app.route('/')
def index():
    return app.send_static_file('index.html')

# --- 3. DATA PROCESSING PIPELINE ---
@app.route('/api/analyze')
def analyze():
    plots_dict = {}
    
    # Chart-to-Memory Wrapper Interface
    def generate_plot(plot_name, plot_title, x_label, y_label, grid_axis='both'):
        plt.title(plot_title, fontsize=14, pad=15)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True, ls='--', alpha=0.3, axis=grid_axis)
        img_buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='png', facecolor='#000000')
        plt.close('all')
        plots_dict[plot_name] = base64.b64encode(img_buffer.getvalue()).decode()
    
    # 1. Line Plot (Global Sales Trend)
    plt.figure(figsize=(10, 6))
    filtered_df.groupby('Year')['Global_Sales'].sum().plot(marker='o', color='#ec4899', lw=2)
    generate_plot('line_plot', 'Global Sales Trend Over Time', 'Year', 'Global Sales (Millions)')
    
    # 2. Multi Line Plot (Regional Sales)
    plt.figure(figsize=(10, 6))
    for region_col, line_style, line_color, region_label in zip(
        regional_cols, 
        ['-', '--', '-.', ':'], 
        ['#ef4444', '#3b82f6', '#10b981', '#f59e0b'], 
        ['North America', 'Europe', 'Japan', 'Other']
    ):
        filtered_df.groupby('Year')[region_col].sum().plot(ls=line_style, c=line_color, lw=2.5, label=region_label)
    plt.legend(fontsize=11)
    generate_plot('line_styles_plot', 'Regional Sales Over Time', 'Year', 'Sales (Millions)')
    
    # 3. Area Plot (Genre Market Share)
    plt.figure(figsize=(10, 6))
    top_4_genres = df['Genre'].value_counts().nlargest(4).index
    filtered_df[filtered_df['Genre'].isin(top_4_genres)] \
        .groupby(['Year', 'Genre'])['Global_Sales'].sum() \
        .unstack().fillna(0) \
        .plot(kind='area', stacked=True, alpha=0.7, colormap='Spectral', ax=plt.gca())
    generate_plot('area_plot', 'Genre Market Share Over Time', 'Year', 'Global Sales (Millions)')
    
    # 4. Bar Plot (Global Sales by Genre)
    genre_sales = df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    genre_sales.plot(kind='bar', color='#38bdf8', edgecolor='#222222')
    plt.xticks(rotation=45, ha='right')
    generate_plot('bar_plot', 'Global Sales by Genre', 'Genre', 'Global Sales (Millions)', 'y')
    
    # 5. Stacked Bar Plot (Top Genre Regional Sales)
    top_5_genres = genre_sales.nlargest(5).index
    plt.figure(figsize=(10, 6))
    df[df['Genre'].isin(top_5_genres)].groupby('Genre')[regional_cols].sum() \
        .plot(kind='bar', stacked=True, colormap='Set2', ax=plt.gca(), edgecolor='#222222')
    plt.legend(['NA', 'EU', 'JP', 'Other'], title='Region')
    plt.xticks(rotation=0)
    generate_plot('stacked_bar_plot', 'Regional Sales by Top Genres', 'Genre', 'Sales (Millions)', 'y')
    
    # 6. Histogram (Distribution by Release Year)
    plt.figure(figsize=(10, 6))
    plt.hist(df['Year'].dropna(), bins=20, color='#f59e0b', edgecolor='#222222', alpha=0.85)
    generate_plot('histogram_plot', 'Distribution of Games by Release Year', 'Release Year', 'Number of Games')
    
    # 7. Scatter Plot (NA vs EU Sales Correlation)
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        df['NA_Sales'], df['EU_Sales'], 
        c=df['Global_Sales'], 
        s=df['Global_Sales'] * 12 + 10, 
        cmap='cool', alpha=0.6, 
        edgecolors='#ffffff', linewidths=0.5
    )
    plt.plot([0, 45], [0, 45], color='#ffffff', ls='--', lw=1.5, alpha=0.5, zorder=0)
    plt.colorbar(scatter, label='Global Sales (M)')
    generate_plot('scatter_plot', 'NA vs EU Sales Correlation (Scatter Plot)', 'NA Sales (Millions)', 'EU Sales (Millions)')
    
    # 8. Box Plot (Sales Distribution for Top Genres)
    plt.figure(figsize=(10, 6))
    plt.boxplot(
        [df[df['Genre'] == genre]['Global_Sales'].dropna() for genre in top_5_genres], 
        patch_artist=True, 
        showfliers=True, 
        flierprops=dict(marker='o', markerfacecolor='#ef4444', markersize=4, alpha=0.5, markeredgewidth=0), 
        boxprops=dict(facecolor='#8b5cf6', color='#cbd5e1'), 
        whiskerprops=dict(color='#cbd5e1', lw=1.5), 
        capprops=dict(color='#cbd5e1', lw=1.5), 
        medianprops=dict(color='#fcd34d', lw=2)
    )
    plt.yscale('log')
    plt.xticks(range(1, len(top_5_genres) + 1), top_5_genres)
    generate_plot('box_plot', 'Sales Distribution for Top Genres', 'Genre', 'Log Global Sales (Millions)', 'y')
    
    # 9. Hexbin Plot (NA vs EU Sales Density)
    from matplotlib.colors import LogNorm
    plt.figure(figsize=(10, 6))
    # Filter out games with 0 sales and extreme outliers (>10M) to better visualize the dense cluster of typical sales
    hex_data = df[(df['NA_Sales'] > 0) & (df['EU_Sales'] > 0) & (df['NA_Sales'] < 10) & (df['EU_Sales'] < 10)]
    plt.hexbin(hex_data['NA_Sales'], hex_data['EU_Sales'], gridsize=30, cmap='inferno', norm=LogNorm())
    plt.colorbar(label='Count')
    generate_plot('hexbin_plot', 'NA vs EU Sales Density', 'NA Sales (Millions)', 'EU Sales (Millions)')
    
    # 10. Log Scale KDE Plot (Global Sales Distribution)
    from scipy.stats import gaussian_kde
    plt.figure(figsize=(10, 6))
    # Apply a log base 10 transformation to global sales to normalize the heavily right-skewed data distribution
    log_sales = np.log10(df['Global_Sales'].dropna()[lambda x: x > 0])
    # Generate 500 points for a smooth X-axis and fit a Gaussian Kernel Density Estimate (KDE) over the log data
    x_axis_values = np.linspace(log_sales.min(), log_sales.max(), 500)
    kde_model = gaussian_kde(log_sales, bw_method=0.25)
    plt.plot(x_axis_values, kde_model(x_axis_values), color='#10b981', lw=2.5)
    plt.fill_between(x_axis_values, kde_model(x_axis_values), color='#10b981', alpha=0.3)
    ticks = [-2, -1, 0, 1, 2]
    plt.xticks(ticks, [f"{10**t:g}M" for t in ticks])
    generate_plot('kde_plot', 'Global Sales Distribution (Log Scale KDE)', 'Global Sales (Log Scale)', 'Density')
    
    return jsonify({'plots': plots_dict})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
