#!/usr/bin/env python3
"""
Comprehensive huez demo - generates all visualizations and creates HTML gallery.
"""

import numpy as np
import base64
from io import BytesIO

# Import huez
import huez as hz

# Optional: Import visualization libraries
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

try:
    import plotly.graph_objects as go
    import plotly.io as pio
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import altair as alt
    HAS_ALTAIR = True
except ImportError:
    HAS_ALTAIR = False

try:
    import plotnine as p9
    HAS_PLOTNINE = True
except ImportError:
    HAS_PLOTNINE = False

# Extended libraries
try:
    import bokeh.plotting as bkp
    from bokeh.models import ColumnDataSource
    HAS_BOKEH = True
except ImportError:
    HAS_BOKEH = False

try:
    import holoviews as hv
    HAS_HOLOVIEWS = True
except ImportError:
    HAS_HOLOVIEWS = False

try:
    import hvplot.pandas
    HAS_HVPLOT = True
except ImportError:
    HAS_HVPLOT = False

try:
    import pyvista as pv
    HAS_PYVISTA = True
except ImportError:
    HAS_PYVISTA = False

try:
    from pyecharts import options as opts
    from pyecharts.charts import Bar
    HAS_PYECHARTS = True
except ImportError:
    HAS_PYECHARTS = False


def create_matplotlib_demo(scheme_name, colors):
    """Create matplotlib demo and return base64 encoded image."""
    if not HAS_MATPLOTLIB:
        return None

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # Generate sample data
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    categories = ['A', 'B', 'C', 'D', 'E']
    values = np.random.randint(20, 80, len(categories))

    # Bar chart
    axes[0].bar(categories, values, color=colors[:len(categories)])
    axes[0].set_title('Bar Chart')
    axes[0].grid(True, alpha=0.3)

    # Line plot
    for i, cat in enumerate(categories[:3]):
        y = np.sin(x + i * np.pi/3) + np.random.normal(0, 0.1, len(x))
        axes[1].plot(x, y, color=colors[i], label=cat, linewidth=2)
    axes[1].set_title('Line Plot')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # Scatter plot
    for i, cat in enumerate(categories[:4]):
        mask = np.random.choice([True, False], len(x), p=[0.3, 0.7])
        x_scatter = x[mask] + np.random.normal(0, 0.5, sum(mask))
        y_scatter = np.sin(x_scatter) + np.random.normal(0, 0.2, sum(mask))
        axes[2].scatter(x_scatter, y_scatter, color=colors[i], label=cat, alpha=0.7, s=30)
    axes[2].set_title('Scatter Plot')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return image_base64


def create_seaborn_demo(scheme_name, colors):
    """Create seaborn demo and return base64 encoded image."""
    if not HAS_SEABORN:
        return None

    # Generate sample data
    np.random.seed(42)
    n = 100
    data = {
        'x': np.random.randn(n),
        'y': np.random.randn(n),
        'category': np.random.choice(['A', 'B', 'C', 'D'], n)
    }

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # Scatter plot
    sns.scatterplot(data=data, x='x', y='y', hue='category', ax=axes[0], palette=colors[:4])
    axes[0].set_title('Scatter Plot')

    # Box plot
    sns.boxplot(data=data, x='category', y='y', ax=axes[1], palette=colors[:4])
    axes[1].set_title('Box Plot')

    # Violin plot
    sns.violinplot(data=data, x='category', y='y', ax=axes[2], palette=colors[:4])
    axes[2].set_title('Violin Plot')

    plt.tight_layout()

    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return image_base64


def create_plotly_demo(scheme_name, colors):
    """Create plotly demo and return HTML."""
    if not HAS_PLOTLY:
        return None

    # Generate sample data
    categories = ['A', 'B', 'C', 'D']
    values = np.random.randint(20, 80, len(categories))

    fig = go.Figure()

    # Add bar chart
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors[:len(categories)],
        name='Bar Chart'
    ))

    fig.update_layout(
        title=f'{scheme_name.replace("-", " ").title()} - Plotly Demo',
        showlegend=False,
        height=300
    )

    # Convert to HTML
    html_content = pio.to_html(fig, include_plotlyjs=True, full_html=False)
    return html_content


def create_altair_demo(scheme_name, colors):
    """Create altair demo and return HTML."""
    if not HAS_ALTAIR:
        return None

    # Generate sample data
    np.random.seed(42)
    n = 50
    data = {
        'x': np.random.randn(n).tolist(),
        'y': np.random.randn(n).tolist(),
        'category': np.random.choice(['A', 'B', 'C'], n).tolist()
    }

    import pandas as pd
    df = pd.DataFrame(data)

    chart = alt.Chart(df).mark_circle(size=60).encode(
        x='x:Q',
        y='y:Q',
        color=alt.Color('category:N', scale=alt.Scale(range=colors[:3])),
        tooltip=['x', 'y', 'category']
    ).properties(
        width=300,
        height=200,
        title=f'{scheme_name.replace("-", " ").title()} - Altair'
    )

    html_content = chart.to_html()
    return html_content


def create_plotnine_demo(scheme_name, colors):
    """Create plotnine demo and return base64 encoded image."""
    if not HAS_PLOTNINE:
        return None

    # Generate sample data
    np.random.seed(42)
    n = 30
    data = {
        'x': np.random.randn(n),
        'y': np.random.randn(n),
        'category': np.random.choice(['A', 'B', 'C'], n)
    }

    import pandas as pd
    df = pd.DataFrame(data)

    plot = (
        p9.ggplot(df, p9.aes(x='x', y='y', color='category')) +
        p9.geom_point(size=3, alpha=0.7) +
        p9.scale_color_manual(values=colors[:3]) +
        p9.theme_minimal() +
        p9.labs(
            title=f'{scheme_name.replace("-", " ").title()} - plotnine',
            x='X Variable',
            y='Y Variable'
        ) +
        p9.theme(figure_size=(4, 3))
    )

    # Save to buffer
    buffer = BytesIO()
    plot.save(buffer, format='png', dpi=100, verbose=False)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return image_base64


def create_color_palette_demo():
    """Create color palette demonstration."""
    journal_palettes = {
        "npg": "Nature Publishing Group",
        "aaas": "Science Journal (AAAS)",
        "nejm": "New England Journal of Medicine",
        "lancet": "The Lancet",
        "jama": "Journal of the American Medical Association",
        "bmj": "British Medical Journal"
    }

    html_content = ""

    for palette_name, journal_name in journal_palettes.items():
        colors = hz.palette(palette_name, kind="discrete", n=10)

        html_content += f"""
        <div class="palette-section">
            <h3>{palette_name.upper()} - {journal_name}</h3>
            <div class="color-grid">
        """

        for i, color in enumerate(colors):
            html_content += f"""
                <div class="color-item">
                    <div class="color-swatch" style="background-color: {color};"></div>
                    <div class="color-code">{color}</div>
                    <div class="color-index">{i+1}</div>
                </div>
            """

        html_content += """
            </div>
        </div>
        """

    return html_content


def main():
    """Main function to create comprehensive demo."""
    print("🎨 Creating Comprehensive huez Demo Gallery")
    print("=" * 60)

    # Load configuration
    config = hz.load_config()
    print(f"✅ Loaded {len(config.schemes)} journal schemes")

    # Journal schemes
    journal_schemes = {
        "scheme-1": "Nature Journal Style",
        "scheme-2": "Science Journal Style",
        "scheme-3": "NEJM Style",
        "scheme-4": "Lancet Style",
        "scheme-5": "JAMA Style"
    }

    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>huez Journal Colors Demo</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
            color: #333;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .header h1 {{
            margin: 0;
            font-size: 3em;
            font-weight: 300;
        }}

        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.2em;
        }}

        .palette-section {{
            background: white;
            margin: 30px 0;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .palette-section h3 {{
            margin-top: 0;
            color: #2c3e50;
            font-size: 1.4em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}

        .color-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .color-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}

        .color-swatch {{
            width: 80px;
            height: 80px;
            border-radius: 8px;
            border: 2px solid #ddd;
            margin-bottom: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .color-code {{
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #666;
            text-align: center;
            word-break: break-all;
            margin-bottom: 5px;
        }}

        .color-index {{
            font-weight: bold;
            color: #2c3e50;
        }}

        .schemes-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }}

        .scheme-card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .scheme-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}

        .scheme-header h4 {{
            margin: 0;
            font-size: 1.3em;
            font-weight: 400;
        }}

        .scheme-content {{
            padding: 20px;
        }}

        .viz-tabs {{
            display: flex;
            border-bottom: 1px solid #e9ecef;
            margin-bottom: 20px;
        }}

        .viz-tab {{
            flex: 1;
            padding: 12px;
            text-align: center;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s;
        }}

        .viz-tab:hover {{
            background: #e9ecef;
        }}

        .viz-tab.active {{
            background: #3498db;
            color: white;
        }}

        .viz-content {{
            display: none;
        }}

        .viz-content.active {{
            display: block;
        }}

        .viz-placeholder {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }}

        .image-container {{
            text-align: center;
            padding: 20px;
        }}

        .image-container img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: #2c3e50;
            color: white;
            border-radius: 12px;
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 huez</h1>
        <p>Your all-in-one color solution in Python</p>
    </div>

    <div class="stats">
        <div class="stat">
            <div class="stat-number">{len(journal_schemes)}</div>
            <div class="stat-label">Journal Schemes</div>
        </div>
        <div class="stat">
            <div class="stat-number">6</div>
            <div class="stat-label">Palette Libraries</div>
        </div>
        <div class="stat">
            <div class="stat-number">10</div>
            <div class="stat-label">Visualization Tools</div>
        </div>
    </div>

    <h2>🎨 Journal Color Palettes</h2>
"""

    # Add color palette demo
    html_content += create_color_palette_demo()

    html_content += """
    <h2>📊 Journal Schemes & Visualizations</h2>
    <div class="schemes-section">
"""

    for scheme_name, scheme_title in journal_schemes.items():
        print(f"\n🎨 Processing {scheme_title}...")

        # Apply scheme
        hz.use(scheme_name)
        colors = hz.palette(None, kind="discrete", n=8)

        # Generate visualizations
        matplotlib_img = create_matplotlib_demo(scheme_name, colors)
        seaborn_img = create_seaborn_demo(scheme_name, colors)
        plotly_html = create_plotly_demo(scheme_name, colors)
        altair_html = create_altair_demo(scheme_name, colors)
        plotnine_img = create_plotnine_demo(scheme_name, colors)

        # Extended visualizations
        bokeh_html = create_bokeh_demo(scheme_name, colors)
        holoviews_html = create_holoviews_demo(scheme_name, colors)
        hvplot_html = create_hvplot_demo(scheme_name, colors)
        pyvista_img = create_pyvista_demo(scheme_name, colors)
        pyecharts_html = create_pyecharts_demo(scheme_name, colors)

        html_content += f"""
        <div class="scheme-card">
            <div class="scheme-header">
                <h4>{scheme_title}</h4>
                <p>{len(colors)} colors from {scheme_name.replace('scheme-', '').upper()}</p>
            </div>
            <div class="scheme-content">
                <div class="viz-tabs">
                    <button class="viz-tab active" onclick="showViz(this, 'matplotlib-{scheme_name}')">Matplotlib</button>
                    <button class="viz-tab" onclick="showViz(this, 'seaborn-{scheme_name}')">Seaborn</button>
                    <button class="viz-tab" onclick="showViz(this, 'plotly-{scheme_name}')">Plotly</button>
                    <button class="viz-tab" onclick="showViz(this, 'altair-{scheme_name}')">Altair</button>
                    <button class="viz-tab" onclick="showViz(this, 'plotnine-{scheme_name}')">plotnine</button>
                    <button class="viz-tab" onclick="showViz(this, 'bokeh-{scheme_name}')">Bokeh</button>
                    <button class="viz-tab" onclick="showViz(this, 'holoviews-{scheme_name}')">HoloViews</button>
                    <button class="viz-tab" onclick="showViz(this, 'hvplot-{scheme_name}')">hvPlot</button>
                    <button class="viz-tab" onclick="showViz(this, 'pyvista-{scheme_name}')">PyVista</button>
                    <button class="viz-tab" onclick="showViz(this, 'pyecharts-{scheme_name}')">PyECharts</button>
                </div>

                <div id="matplotlib-{scheme_name}" class="viz-content active">
        """

        if matplotlib_img:
            html_content += f"""
                    <div class="image-container">
                        <img src="data:image/png;base64,{matplotlib_img}" alt="Matplotlib demo">
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">Matplotlib not available</div>
            """

        html_content += f"""
                </div>

                <div id="seaborn-{scheme_name}" class="viz-content">
        """

        if seaborn_img:
            html_content += f"""
                    <div class="image-container">
                        <img src="data:image/png;base64,{seaborn_img}" alt="Seaborn demo">
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">Seaborn not available</div>
            """

        html_content += f"""
                </div>

                <div id="plotly-{scheme_name}" class="viz-content">
        """

        if plotly_html:
            html_content += f"""
                    <div class="image-container">
                        {plotly_html}
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">Plotly not available</div>
            """

        html_content += f"""
                </div>

                <div id="altair-{scheme_name}" class="viz-content">
        """

        if altair_html:
            html_content += f"""
                    <div class="image-container">
                        {altair_html}
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">Altair not available</div>
            """

        html_content += f"""
                </div>

                <div id="plotnine-{scheme_name}" class="viz-content">
        """

        if plotnine_img:
            html_content += f"""
                    <div class="image-container">
                        <img src="data:image/png;base64,{plotnine_img}" alt="plotnine demo">
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">plotnine not available</div>
            """

        html_content += f"""
                </div>

                <div id="bokeh-{scheme_name}" class="viz-content">
        """

        if bokeh_html:
            html_content += f"""
                    <div class="image-container">
                        {bokeh_html}
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">Bokeh not available</div>
            """

        html_content += f"""
                </div>

                <div id="holoviews-{scheme_name}" class="viz-content">
        """

        if holoviews_html:
            html_content += f"""
                    <div class="image-container">
                        {holoviews_html}
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">HoloViews not available</div>
            """

        html_content += f"""
                </div>

                <div id="hvplot-{scheme_name}" class="viz-content">
        """

        if hvplot_html:
            html_content += f"""
                    <div class="image-container">
                        {hvplot_html}
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">hvPlot not available</div>
            """

        html_content += f"""
                </div>

                <div id="pyvista-{scheme_name}" class="viz-content">
        """

        if pyvista_img:
            html_content += f"""
                    <div class="image-container">
                        <img src="data:image/png;base64,{pyvista_img}" alt="PyVista demo">
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">PyVista not available</div>
            """

        html_content += f"""
                </div>

                <div id="pyecharts-{scheme_name}" class="viz-content">
        """

        if pyecharts_html:
            html_content += f"""
                    <div class="image-container">
                        {pyecharts_html}
                    </div>
            """
        else:
            html_content += """
                    <div class="viz-placeholder">PyECharts not available</div>
            """

        html_content += """
                </div>
            </div>
        </div>
        """

    html_content += """
    </div>

    <div class="footer">
        <h3>✨ huez - Your all-in-one color solution in Python</h3>
        <p>Generated with love for the scientific Python community</p>
    </div>

    <script>
        function showViz(button, vizId) {
            // Hide all viz contents in this card
            const card = button.closest('.scheme-card');
            const contents = card.querySelectorAll('.viz-content');
            const tabs = card.querySelectorAll('.viz-tab');

            contents.forEach(content => content.classList.remove('active'));
            tabs.forEach(tab => tab.classList.remove('active'));

            // Show selected viz
            document.getElementById(vizId).classList.add('active');
            button.classList.add('active');
        }
    </script>
</body>
</html>"""

    # Save HTML file
    with open('huez_comprehensive_demo.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("\n" + "=" * 60)
    print("🎉 Comprehensive demo gallery created!")
    print("📁 File: huez_comprehensive_demo.html")
    print("🌐 Open in browser to view all visualizations")


def create_bokeh_demo(scheme_name, colors):
    """Create Bokeh demo and return HTML."""
    if not HAS_BOKEH:
        return None

    try:
        # Generate sample data
        categories = ['A', 'B', 'C', 'D', 'E']
        values = [20, 35, 30, 25, 40]

        # Create Bokeh plot
        source = ColumnDataSource(data=dict(categories=categories, values=values))

        p = bkp.figure(x_range=categories, title=f"{scheme_name.replace('-', ' ').title()} - Bokeh Demo",
                      toolbar_location=None, tools="")

        p.vbar(x='categories', top='values', width=0.9, source=source,
               color=colors[:len(categories)], legend_field="categories")

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.y_range.end = max(values) * 1.1

        # Save as HTML
        from bokeh.resources import CDN
        from bokeh.embed import file_html

        html_content = file_html(p, CDN, f"{scheme_name} Bokeh Demo")
        return html_content

    except Exception as e:
        print(f"   ❌ Bokeh test failed: {e}")
        return None


def create_holoviews_demo(scheme_name, colors):
    """Create HoloViews demo and return HTML."""
    if not HAS_HOLOVIEWS:
        return None

    try:
        import holoviews as hv
        hv.extension('bokeh')

        # Generate sample data
        data = {'x': [1, 2, 3, 4, 5], 'y': [2, 5, 3, 8, 7], 'category': ['A', 'B', 'C', 'D', 'E']}

        # Create scatter plot
        scatter = hv.Scatter(data, 'x', 'y').opts(
            color=colors[0],
            size=10,
            title=f"{scheme_name.replace('-', ' ').title()} - HoloViews"
        )

        # Convert to HTML
        from holoviews import renderer
        bokeh_renderer = renderer('bokeh')
        plot = bokeh_renderer.get_plot(scatter)

        from bokeh.resources import CDN
        from bokeh.embed import file_html
        html_content = file_html(plot.state, CDN, f"{scheme_name} HoloViews Demo")

        return html_content

    except Exception as e:
        print(f"   ❌ HoloViews test failed: {e}")
        return None


def create_hvplot_demo(scheme_name, colors):
    """Create hvPlot demo and return HTML."""
    if not HAS_HVPLOT:
        return None

    try:
        import pandas as pd

        # Generate sample data
        data = {
            'x': [1, 2, 3, 4, 5],
            'y': [2, 5, 3, 8, 7],
            'category': ['A', 'B', 'C', 'D', 'E']
        }
        df = pd.DataFrame(data)

        # Create hvPlot
        plot = df.hvplot.scatter(
            x='x',
            y='y',
            c=colors[0],
            title=f"{scheme_name.replace('-', ' ').title()} - hvPlot"
        )

        # Convert to HTML
        html_content = hvplot.save(plot, f'temp_{scheme_name}_hvplot.html')
        with open(f'temp_{scheme_name}_hvplot.html', 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Clean up temp file
        import os
        os.remove(f'temp_{scheme_name}_hvplot.html')

        return html_content

    except Exception as e:
        print(f"   ❌ hvPlot test failed: {e}")
        return None


def create_pyvista_demo(scheme_name, colors):
    """Create PyVista demo and return base64 encoded image."""
    if not HAS_PYVISTA:
        return None

    try:
        # Create a simple 3D plot
        sphere = pv.Sphere(radius=0.5, center=(0, 0, 0))
        cube = pv.Cube(center=(1, 1, 1))

        # Create plotter
        plotter = pv.Plotter(off_screen=True, window_size=(800, 600))
        plotter.background_color = 'white'

        # Add meshes with colors
        plotter.add_mesh(sphere, color=colors[0], show_edges=True)
        plotter.add_mesh(cube, color=colors[1], show_edges=True)

        plotter.add_text(f"{scheme_name.replace('-', ' ').title()} - PyVista",
                        position='upper_left', font_size=12)

        # Save screenshot
        import numpy as np
        screenshot = plotter.screenshot(None, return_img=True)
        buffer = BytesIO()
        plt.imsave(buffer, screenshot, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        plotter.close()
        return image_base64

    except Exception as e:
        print(f"   ❌ PyVista test failed: {e}")
        return None


def create_pyecharts_demo(scheme_name, colors):
    """Create PyECharts demo and return HTML."""
    if not HAS_PYECHARTS:
        return None

    try:
        # Generate sample data
        categories = ['A', 'B', 'C', 'D', 'E']
        values = [20, 35, 30, 25, 40]

        # Create bar chart
        bar = (
            Bar()
            .add_xaxis(categories)
            .add_yaxis("Data", values, color=colors[0])
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"{scheme_name.replace('-', ' ').title()} - PyECharts"),
                toolbox_opts=opts.ToolboxOpts(),
            )
        )

        # Generate HTML
        html_content = bar.render_embed()

        return html_content

    except Exception as e:
        print(f"   ❌ PyECharts test failed: {e}")
        return None


if __name__ == "__main__":
    main()
