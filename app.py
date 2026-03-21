# ==========================================
# 📊 VIDEO GAME SALES DATA ANALYSIS API
# Stack: Flask, Pandas, Matplotlib, SciPy
# ==========================================

from flask import Flask, jsonify
import pandas as pd, io, base64, numpy as np; import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

# --- 1. CORE THEME (OLED Dark Mode DataViz) ---
plt.rcParams.update({'figure.facecolor':'#000000','axes.facecolor':'#000000','axes.edgecolor':'#444444','axes.labelcolor':'#ffffff','text.color':'#ffffff','xtick.color':'#cccccc','ytick.color':'#cccccc','grid.color':'#333333','legend.facecolor':'#111111','legend.edgecolor':'#333333','legend.labelcolor':'#ffffff'})
app = Flask(__name__, static_folder='.', static_url_path='')

# --- 2. FRONTEND ROUTING ---
@app.route('/')
def index(): return app.send_static_file('index.html')

# --- 3. DATA PROCESSING PIPELINE ---
@app.route('/api/analyze')
def analyze():
    # Load and clean primary dataset headers
    df, p, c_cols = pd.read_csv('vgsales.csv'), {}, ['Year','NA_Sales','EU_Sales','JP_Sales','Other_Sales','Global_Sales']
    df[c_cols], r = df[c_cols].apply(pd.to_numeric, errors='coerce'), ['NA_Sales','EU_Sales','JP_Sales','Other_Sales']
    t_df = df.dropna(subset=['Year'])[lambda x: x['Year'] <= 2016]

    # DRY Wrapper Interface for Rendering Charts to Memory
    def f(n, t, x, y, g='both'):
        plt.title(t, fontsize=14, pad=15); plt.xlabel(x); plt.ylabel(y); plt.grid(True, ls='--', alpha=0.3, axis=g)
        b = io.BytesIO(); plt.tight_layout(); plt.savefig(b, format='png', facecolor='#000000'); plt.close(); p[n] = base64.b64encode(b.getvalue()).decode()

    # --- 4. DATA VISUALIZATION GENERATORS ---
    
    # 1. Line Plot (Global Sales Trend Over Time)
    plt.figure(figsize=(10,6)); t_df.groupby('Year')['Global_Sales'].sum().plot(marker='o', color='#ec4899', lw=2); f('line_plot', 'Global Sales Trend Over Time (Line Plot)', 'Year', 'Global Sales (Millions)')
    
    # 2. Multi Line Plot (Regional Sales Over Time)
    plt.figure(figsize=(10,6)); [t_df.groupby('Year')[c_r].sum().plot(ls=s, c=c, lw=2.5, label=l) for c_r, s, c, l in zip(r, ['-','--','-.', ':'], ['#ef4444','#3b82f6','#10b981','#f59e0b'], ['North America','Europe','Japan','Other'])]
    plt.legend(fontsize=11); f('line_styles_plot', 'Regional Sales Over Time (Multi Line Plot)', 'Year', 'Sales (Millions)')
    
    # 3. Area Plot (Genre Market Share Over Time)
    plt.figure(figsize=(10,6)); t_df[t_df['Genre'].isin(df['Genre'].value_counts().nlargest(4).index)].groupby(['Year','Genre'])['Global_Sales'].sum().unstack().fillna(0).plot(kind='area', stacked=True, alpha=0.7, colormap='Spectral', ax=plt.gca()); f('area_plot', 'Genre Market Share Over Time (Area Plot)', 'Year', 'Global Sales (Millions)')

    # 4. Bar Plot (Global Sales by Genre)
    gs = df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False); plt.figure(figsize=(10,6)); gs.plot(kind='bar', color='#38bdf8', edgecolor='#222222'); plt.xticks(rotation=45, ha='right'); f('bar_plot', 'Global Sales by Genre (Bar Plot)', 'Genre', 'Global Sales (Millions)', 'y')
    
    # 5. Stacked Bar Plot (Regional Sales by Top Genres)
    t5 = gs.nlargest(5).index; plt.figure(figsize=(10,6)); df[df['Genre'].isin(t5)].groupby('Genre')[r].sum().plot(kind='bar', stacked=True, colormap='Set2', ax=plt.gca(), edgecolor='#222222'); plt.legend(['NA','EU','JP','Other'], title='Region'); plt.xticks(rotation=0); f('stacked_bar_plot', 'Regional Sales by Top Genres (Stacked Bar Plot)', 'Genre', 'Sales (Millions)', 'y')
    
    # 6. Histogram (Distribution of Games by Release Year)
    plt.figure(figsize=(10,6)); plt.hist(df['Year'].dropna(), bins=20, color='#f59e0b', edgecolor='#222222', alpha=0.85); f('histogram_plot', 'Distribution of Games by Release Year (Histogram)', 'Release Year', 'Number of Games')
    
    # 7. Scatter Plot (NA vs EU Sales Correlation)
    plt.figure(figsize=(10,6)); sc = plt.scatter(df['NA_Sales'], df['EU_Sales'], c=df['Global_Sales'], cmap='cool', s=40, alpha=0.5, edgecolors='none'); plt.xscale('symlog', linthresh=0.01); plt.yscale('symlog', linthresh=0.01); plt.colorbar(sc, label='Global Sales (M)'); f('scatter_plot', 'NA vs EU Sales Correlation (SymLog Scale Scatter)', 'NA Sales (Millions)', 'EU Sales (Millions)')
    
    # 8. Box Plot (Sales Distribution for Top Genres)
    plt.figure(figsize=(10,6)); plt.boxplot([df[df['Genre']==g]['Global_Sales'].dropna() for g in t5], patch_artist=True, showfliers=True, flierprops=dict(marker='o', markerfacecolor='#ef4444', markersize=4, alpha=0.5, markeredgewidth=0), boxprops=dict(facecolor='#8b5cf6', color='#cbd5e1'), whiskerprops=dict(color='#cbd5e1', lw=1.5), capprops=dict(color='#cbd5e1', lw=1.5), medianprops=dict(color='#fcd34d', lw=2)); plt.yscale('log'); plt.xticks(range(1, len(t5)+1), t5); f('box_plot', 'Sales Distribution for Top Genres (Log-Scale Box Plot)', 'Genre', 'Log Global Sales (Millions)', 'y')

    # 9. Hexbin Plot (NA vs EU Sales Density)
    from matplotlib.colors import LogNorm; plt.figure(figsize=(10,6)); hx = df[(df['NA_Sales']>0) & (df['EU_Sales']>0) & (df['NA_Sales']<10) & (df['EU_Sales']<10)]; plt.hexbin(hx['NA_Sales'], hx['EU_Sales'], gridsize=30, cmap='inferno', norm=LogNorm()); plt.colorbar(label='Count'); f('hexbin_plot', 'NA vs EU Sales Density (Hexbin Plot)', 'NA Sales (Millions)', 'EU Sales (Millions)')
    
    # 10. Log Scale KDE Plot (Global Sales Distribution)
    from scipy.stats import gaussian_kde; plt.figure(figsize=(10,6)); kd = np.log10(df['Global_Sales'].dropna()[lambda x: x>0]); x = np.linspace(kd.min(), kd.max(), 500); kde = gaussian_kde(kd, bw_method=0.25); plt.plot(x, kde(x), color='#10b981', lw=2.5); plt.fill_between(x, kde(x), color='#10b981', alpha=0.3); tk = [-2, -1, 0, 1, 2]; plt.xticks(tk, [f"{10**t:g}M" for t in tk]); f('kde_plot', 'Global Sales Distribution (Log Scale KDE)', 'Global Sales (Log Scale)', 'Density')

    # --- 5. API RESPONSE ---
    return jsonify({'plots': p})

    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
