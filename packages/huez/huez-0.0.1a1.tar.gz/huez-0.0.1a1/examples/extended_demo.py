#!/usr/bin/env python3
"""
Extended huez demo - showcases comprehensive library support and tokens export.
"""

import numpy as np
import json
from pathlib import Path

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


def main():
    """Main extended demo function."""

    print("🎨 Extended huez Demo - Comprehensive Library Support")
    print("=" * 70)

    # Show library availability
    libraries = check_library_availability()
    print("📚 Library Support Status:")
    for lib, available in libraries.items():
        status = "✅" if available else "❌"
        print(f"   {status} {lib}")

    # Load configuration
    config = hz.load_config()
    print(f"\n✅ Loaded {len(config.schemes)} journal schemes")

    # Show available palettes
    print(f"\n🎨 Available Palettes:")
    from huez.registry import list_available_palettes
    palettes = list_available_palettes()
    for kind, names in palettes.items():
        print(f"   {kind}: {len(names)} palettes")
        # Show first few examples
        examples = names[:3] if len(names) > 3 else names
        for name in examples:
            print(f"     • {name}")
        if len(names) > 3:
            print(f"     ... and {len(names)-3} more")

    # Test journal schemes
    journal_schemes = list(config.schemes.keys())

    for scheme_name in journal_schemes[:2]:  # Test first 2 schemes
        print(f"\n🎨 Testing {config.schemes[scheme_name].title}")
        print("-" * 50)

        try:
            # Apply scheme
            hz.use(scheme_name)
            print(f"✅ Applied {config.schemes[scheme_name].title}")

            # Get colors
            colors = hz.palette(None, kind="discrete", n=6)
            print(f"🎨 Discrete colors: {' '.join(colors)}")

            # Test available libraries
            test_available_libraries(scheme_name, colors, libraries)

        except Exception as e:
            print(f"❌ Error testing {scheme_name}: {e}")
            continue

    # Export tokens for web integration
    print("\n🔗 Exporting tokens for web integration...")
    try:
        from huez.export.tokens import export_tokens
        export_tokens(config.schemes["scheme-1"], "web_tokens")
        print("✅ Exported web tokens to web_tokens/")
    except Exception as e:
        print(f"❌ Token export failed: {e}")

    # Show export examples
    show_export_examples()

    print("\n" + "=" * 70)
    print("🎉 Extended demo completed!")
    print("📁 Generated files:")
    print("   - web_tokens/ (CSS, JSON, JS tokens for web integration)")
    print("   - Various visualization files for supported libraries")

    print("\n🌐 Web Integration:")
    print("   - CSS tokens: web_tokens/*_tokens.css")
    print("   - JSON tokens: web_tokens/*_tokens.json")
    print("   - JS module: web_tokens/*_tokens.js")


def check_library_availability():
    """Check which visualization libraries are available."""
    libraries = {
        "matplotlib": HAS_MATPLOTLIB,
        "seaborn": HAS_SEABORN,
        "plotnine": HAS_PLOTNINE,
        "altair": HAS_ALTAIR,
        "plotly": HAS_PLOTLY,
    }

    # Check additional libraries
    try:
        import bokeh
        libraries["bokeh"] = True
    except (ImportError, Exception):
        libraries["bokeh"] = False

    try:
        import holoviews
        libraries["holoviews"] = True
    except (ImportError, Exception):
        libraries["holoviews"] = False

    try:
        import hvplot
        libraries["hvplot"] = True
    except (ImportError, Exception):
        libraries["hvplot"] = False

    try:
        import pyvista
        libraries["pyvista"] = True
    except (ImportError, Exception):
        libraries["pyvista"] = False

    try:
        import geopandas
        libraries["geopandas"] = True
    except (ImportError, Exception):
        libraries["geopandas"] = False

    try:
        import pyecharts
        libraries["pyecharts"] = True
    except (ImportError, Exception):
        libraries["pyecharts"] = False

    return libraries


def test_available_libraries(scheme_name, colors, libraries):
    """Test all available visualization libraries."""
    tested_count = 0

    if libraries.get("matplotlib"):
        test_matplotlib_demo(scheme_name, colors)
        tested_count += 1

    if libraries.get("seaborn"):
        test_seaborn_demo(scheme_name, colors)
        tested_count += 1

    if libraries.get("plotly"):
        test_plotly_demo(scheme_name, colors)
        tested_count += 1

    if libraries.get("altair"):
        test_altair_demo(scheme_name, colors)
        tested_count += 1

    if libraries.get("plotnine"):
        test_plotnine_demo(scheme_name, colors)
        tested_count += 1

    print(f"   ✅ Tested {tested_count} libraries")


def test_matplotlib_demo(scheme_name, colors):
    """Create matplotlib demo plot."""
    try:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))

        # Generate sample data
        x = np.linspace(0, 10, 50)
        categories = ['A', 'B', 'C', 'D']

        # Bar chart
        axes[0].bar(categories, [20, 35, 30, 25], color=colors[:4])
        axes[0].set_title('Bar Chart')
        axes[0].set_ylabel('Values')

        # Line plot
        for i, cat in enumerate(categories[:3]):
            y = np.sin(x + i * np.pi/3) + np.random.normal(0, 0.1, len(x))
            axes[1].plot(x, y, color=colors[i], label=cat, linewidth=2)
        axes[1].set_title('Line Plot')
        axes[1].legend()

        plt.tight_layout()
        plt.savefig(f'extended_{scheme_name}_matplotlib.png', dpi=150, bbox_inches='tight')
        plt.close()

    except Exception as e:
        print(f"   ❌ Matplotlib test failed: {e}")


def test_seaborn_demo(scheme_name, colors):
    """Create seaborn demo plot."""
    try:
        # Generate sample data
        np.random.seed(42)
        n = 80
        data = {
            'x': np.random.randn(n),
            'y': np.random.randn(n),
            'category': np.random.choice(['A', 'B', 'C'], n)
        }

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))

        # Scatter plot
        sns.scatterplot(data=data, x='x', y='y', hue='category', ax=axes[0])
        axes[0].set_title('Scatter Plot')

        # Box plot
        sns.boxplot(data=data, x='category', y='y', ax=axes[1])
        axes[1].set_title('Box Plot')

        plt.tight_layout()
        plt.savefig(f'extended_{scheme_name}_seaborn.png', dpi=150, bbox_inches='tight')
        plt.close()

    except Exception as e:
        print(f"   ❌ Seaborn test failed: {e}")


def test_plotly_demo(scheme_name, colors):
    """Create plotly demo plot."""
    try:
        categories = ['A', 'B', 'C', 'D']
        values = [20, 35, 30, 25]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors[:len(categories)]
        ))

        fig.update_layout(
            title=f'{scheme_name.replace("-", " ").title()} - Plotly Demo',
            showlegend=False
        )

        fig.write_html(f'extended_{scheme_name}_plotly.html')

    except Exception as e:
        print(f"   ❌ Plotly test failed: {e}")


def test_altair_demo(scheme_name, colors):
    """Create altair demo plot."""
    try:
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
            width=400,
            height=300,
            title=f'{scheme_name.replace("-", " ").title()} - Altair'
        )

        chart.save(f'extended_{scheme_name}_altair.html')

    except Exception as e:
        print(f"   ❌ Altair test failed: {e}")


def test_plotnine_demo(scheme_name, colors):
    """Create plotnine demo plot."""
    try:
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

        plot.save(f'extended_{scheme_name}_plotnine.png', dpi=150, verbose=False)

    except Exception as e:
        print(f"   ❌ plotnine test failed: {e}")


def show_export_examples():
    """Show examples of exported tokens."""
    print("\n📄 Export Examples:")
    print("   CSS tokens can be used in web applications:")
    print("     @import url('nature_journal_style_tokens.css');")
    print("     .my-element { color: var(--huez-primary); }")

    print("\n   JSON tokens for JavaScript libraries:")
    print("     import tokens from './nature_journal_style_tokens.json';")
    print("     chart.color = tokens.colors.discrete;")

    print("\n   JS module for modern web development:")
    print("     import { getDiscreteColors } from './nature_journal_style_tokens.js';")
    print("     const colors = getDiscreteColors(5);")


if __name__ == "__main__":
    main()
