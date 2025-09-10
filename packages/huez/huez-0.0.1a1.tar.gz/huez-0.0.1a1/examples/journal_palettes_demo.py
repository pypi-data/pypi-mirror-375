#!/usr/bin/env python3
"""
Journal palettes demonstration script for huez.

This script demonstrates all available journal color palettes and tests
different visualization libraries with each palette.
"""

import numpy as np
import os
from pathlib import Path

# Import huez
import huez as hz

# Optional: Import visualization libraries
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("matplotlib not available")

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("seaborn not available")

try:
    import plotly.graph_objects as go
    import plotly.io as pio
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("plotly not available")

try:
    import altair as alt
    HAS_ALTAIR = True
except ImportError:
    HAS_ALTAIR = False
    print("altair not available")

try:
    import plotnine as p9
    HAS_PLOTNINE = True
except ImportError:
    HAS_PLOTNINE = False
    print("plotnine not available")


def main():
    """Main demonstration function."""

    print("🎨 huez Journal Palettes Demo")
    print("=" * 60)

    # Available libraries
    libraries = []
    if HAS_MATPLOTLIB:
        libraries.append("matplotlib")
    if HAS_SEABORN:
        libraries.append("seaborn")
    if HAS_PLOTLY:
        libraries.append("plotly")
    if HAS_ALTAIR:
        libraries.append("altair")
    if HAS_PLOTNINE:
        libraries.append("plotnine")

    print(f"📚 Available libraries: {', '.join(libraries)}")

    # Load default configuration
    print("\n📋 Loading journal color schemes...")
    config = hz.load_config()
    print(f"   Found {len(config.schemes)} schemes:")
    for name, scheme in config.schemes.items():
        print(f"   • {name}: {scheme.title}")

    # Test each journal scheme
    journal_schemes = {
        "scheme-1": "Nature Journal Style",
        "scheme-2": "Science Journal Style",
        "scheme-3": "NEJM Style",
        "scheme-4": "Lancet Style",
        "scheme-5": "JAMA Style"
    }

    for scheme_name, scheme_title in journal_schemes.items():
        print(f"\n🎨 Testing {scheme_title} ({scheme_name})")
        print("-" * 50)

        try:
            # Apply scheme
            hz.use(scheme_name)
            print(f"✅ Applied {scheme_title}")

            # Get colors
            colors = hz.palette(None, kind="discrete", n=8)
            print(f"🎨 Color palette ({len(colors)} colors):")
            for i, color in enumerate(colors):
                print(f"   {i+1}. {color}")

            # Test each available library
            if HAS_MATPLOTLIB:
                print("\n📊 Testing matplotlib...")
                test_matplotlib(scheme_name, colors)

            if HAS_SEABORN:
                print("\n📊 Testing seaborn...")
                test_seaborn(scheme_name, colors)

            if HAS_PLOTLY:
                print("\n📊 Testing plotly...")
                test_plotly(scheme_name, colors)

            if HAS_ALTAIR:
                print("\n📊 Testing altair...")
                test_altair(scheme_name, colors)

            if HAS_PLOTNINE:
                print("\n📊 Testing plotnine...")
                test_plotnine(scheme_name, colors)

        except Exception as e:
            print(f"❌ Error testing {scheme_title}: {e}")
            continue

    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("📁 Generated files:")
    print("   - journal_*_matplotlib.png (matplotlib plots)")
    print("   - journal_*_seaborn.png (seaborn plots)")
    print("   - journal_*_plotly.html (plotly plots)")
    print("   - journal_*_altair.html (altair plots)")
    print("   - journal_*_plotnine.png (plotnine plots)")


def test_matplotlib(scheme_name, colors):
    """Test matplotlib with journal colors."""
    if not HAS_MATPLOTLIB:
        return

    try:
        # Generate sample data
        np.random.seed(42)
        x = np.linspace(0, 10, 50)
        categories = ['Group A', 'Group B', 'Group C', 'Group D', 'Group E']
        values = np.random.randint(20, 80, len(categories))

        # Create figure with subplots
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        fig.suptitle(f'Matplotlib - {scheme_name.replace("-", " ").title()}', fontsize=12)

        # Bar chart
        axes[0].bar(categories, values, color=colors[:len(categories)])
        axes[0].set_title('Bar Chart', fontsize=10)
        axes[0].tick_params(axis='both', which='major', labelsize=8)
        axes[0].grid(True, alpha=0.3)

        # Line plot with different colors
        for i, cat in enumerate(categories[:3]):
            y = np.sin(x + i * np.pi/3) + np.random.normal(0, 0.1, len(x))
            axes[1].plot(x, y, color=colors[i], label=cat, linewidth=2)
        axes[1].set_title('Line Plot', fontsize=10)
        axes[1].legend(fontsize=8)
        axes[1].tick_params(axis='both', which='major', labelsize=8)
        axes[1].grid(True, alpha=0.3)

        # Scatter plot
        for i, cat in enumerate(categories[:4]):
            mask = np.random.choice([True, False], len(x), p=[0.3, 0.7])
            x_scatter = x[mask] + np.random.normal(0, 0.5, sum(mask))
            y_scatter = np.sin(x_scatter) + np.random.normal(0, 0.2, sum(mask))
            axes[2].scatter(x_scatter, y_scatter, color=colors[i], label=cat, alpha=0.7, s=30)
        axes[2].set_title('Scatter Plot', fontsize=10)
        axes[2].legend(fontsize=8)
        axes[2].tick_params(axis='both', which='major', labelsize=8)
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'journal_{scheme_name}_matplotlib.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved journal_{}_matplotlib.png".format(scheme_name))

    except Exception as e:
        print(f"   ❌ Matplotlib test failed: {e}")


def test_seaborn(scheme_name, colors):
    """Test seaborn with journal colors."""
    if not HAS_SEABORN:
        return

    try:
        # Generate sample data
        np.random.seed(42)
        n = 100
        data = {
            'x': np.random.randn(n),
            'y': np.random.randn(n),
            'category': np.random.choice(['A', 'B', 'C', 'D'], n),
            'value': np.random.randn(n)
        }

        # Create figure with subplots
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        fig.suptitle(f'Seaborn - {scheme_name.replace("-", " ").title()}', fontsize=12)

        # Scatter plot
        sns.scatterplot(data=data, x='x', y='y', hue='category', ax=axes[0], palette=colors[:4])
        axes[0].set_title('Scatter Plot', fontsize=10)
        axes[0].legend(fontsize=8)

        # Box plot
        sns.boxplot(data=data, x='category', y='value', ax=axes[1], palette=colors[:4])
        axes[1].set_title('Box Plot', fontsize=10)
        axes[1].tick_params(axis='both', which='major', labelsize=8)

        # Violin plot
        sns.violinplot(data=data, x='category', y='value', ax=axes[2], palette=colors[:4])
        axes[2].set_title('Violin Plot', fontsize=10)
        axes[2].tick_params(axis='both', which='major', labelsize=8)

        plt.tight_layout()
        plt.savefig(f'journal_{scheme_name}_seaborn.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved journal_{}_seaborn.png".format(scheme_name))

    except Exception as e:
        print(f"   ❌ Seaborn test failed: {e}")


def test_plotly(scheme_name, colors):
    """Test plotly with journal colors."""
    if not HAS_PLOTLY:
        return

    try:
        # Generate sample data
        np.random.seed(42)
        categories = ['Group A', 'Group B', 'Group C', 'Group D']
        values = np.random.randint(20, 80, len(categories))

        # Create subplots
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=['Bar Chart', 'Scatter Plot', 'Line Plot'],
            specs=[[{'type': 'bar'}, {'type': 'scatter'}, {'type': 'scatter'}]]
        )

        # Bar chart
        fig.add_trace(
            go.Bar(x=categories, y=values, marker_color=colors[:len(categories)]),
            row=1, col=1
        )

        # Scatter plot
        for i, cat in enumerate(categories[:3]):
            x_data = np.random.randn(30) + i
            y_data = np.random.randn(30) + i
            fig.add_trace(
                go.Scatter(
                    x=x_data, y=y_data, mode='markers',
                    name=cat, marker=dict(color=colors[i], size=8)
                ),
                row=1, col=2
            )

        # Line plot
        x_line = np.linspace(0, 10, 50)
        for i, cat in enumerate(categories[:3]):
            y_line = np.sin(x_line + i * np.pi/3) + np.random.normal(0, 0.1, len(x_line))
            fig.add_trace(
                go.Scatter(
                    x=x_line, y=y_line, mode='lines',
                    name=f'{cat} (line)', line=dict(color=colors[i], width=3)
                ),
                row=1, col=3
            )

        # Update layout
        fig.update_layout(
            title_text=f'Plotly - {scheme_name.replace("-", " ").title()}',
            showlegend=True,
            height=400
        )

        # Save as HTML
        fig.write_html(f'journal_{scheme_name}_plotly.html')
        print("   ✅ Saved journal_{}_plotly.html".format(scheme_name))

    except Exception as e:
        print(f"   ❌ Plotly test failed: {e}")


def test_altair(scheme_name, colors):
    """Test altair with journal colors."""
    if not HAS_ALTAIR:
        return

    try:
        # Generate sample data
        np.random.seed(42)
        n = 100
        data = {
            'x': np.random.randn(n).tolist(),
            'y': np.random.randn(n).tolist(),
            'category': np.random.choice(['A', 'B', 'C'], n).tolist(),
            'value': np.random.randn(n).tolist()
        }

        import pandas as pd
        df = pd.DataFrame(data)

        # Create charts
        base = alt.Chart(df).properties(width=200, height=150)

        # Scatter plot
        scatter = base.mark_circle(size=60).encode(
            x='x:Q',
            y='y:Q',
            color=alt.Color('category:N', scale=alt.Scale(range=colors[:3])),
            tooltip=['x', 'y', 'category']
        ).properties(title='Scatter Plot')

        # Bar chart
        bar = alt.Chart(df).mark_bar().encode(
            x='category:N',
            y='mean(value):Q',
            color=alt.Color('category:N', scale=alt.Scale(range=colors[:3]))
        ).properties(title='Bar Chart', width=200, height=150)

        # Combine charts
        chart = (scatter | bar).properties(
            title=f'Altair - {scheme_name.replace("-", " ").title()}'
        )

        # Save as HTML
        chart.save(f'journal_{scheme_name}_altair.html')
        print("   ✅ Saved journal_{}_altair.html".format(scheme_name))

    except Exception as e:
        print(f"   ❌ Altair test failed: {e}")


def test_plotnine(scheme_name, colors):
    """Test plotnine with journal colors."""
    if not HAS_PLOTNINE:
        return

    try:
        # Generate sample data
        np.random.seed(42)
        n = 50
        data = {
            'x': np.random.randn(n),
            'y': np.random.randn(n),
            'category': np.random.choice(['A', 'B', 'C'], n),
            'value': np.random.randn(n)
        }

        import pandas as pd
        df = pd.DataFrame(data)

        # Create plot
        plot = (
            p9.ggplot(df, p9.aes(x='x', y='y', color='category', size='value')) +
            p9.geom_point(alpha=0.7) +
            p9.scale_color_manual(values=colors[:3]) +
            p9.theme_minimal() +
            p9.labs(
                title=f'plotnine - {scheme_name.replace("-", " ").title()}',
                x='X Variable',
                y='Y Variable'
            )
        )

        # Save plot
        plot.save(f'journal_{scheme_name}_plotnine.png', dpi=150)
        print("   ✅ Saved journal_{}_plotnine.png".format(scheme_name))

    except Exception as e:
        print(f"   ❌ plotnine test failed: {e}")


if __name__ == "__main__":
    main()


