#!/usr/bin/env python3
"""
Working huez demo - shows all currently working features.
"""

import numpy as np

# Import huez
import huez as hz

# Check available libraries
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
    """Main demo function."""
    print("🎨 Working huez Demo - Core Features")
    print("=" * 50)

    # Show available libraries
    print("📚 Available Libraries:")
    libs = []
    if HAS_MATPLOTLIB: libs.append("matplotlib")
    if HAS_SEABORN: libs.append("seaborn")
    if HAS_PLOTLY: libs.append("plotly")
    if HAS_ALTAIR: libs.append("altair")
    if HAS_PLOTNINE: libs.append("plotnine")
    print(f"   {', '.join(libs)}")

    # Load configuration
    print("\n📋 Loading journal color schemes...")
    config = hz.load_config()
    print(f"✅ Loaded {len(config.schemes)} schemes")

    # Show all journal palettes
    print("\n🎨 Journal Color Palettes:")
    journal_palettes = ["npg", "aaas", "nejm", "lancet", "jama", "bmj"]

    for palette in journal_palettes:
        try:
            colors = hz.palette(palette, kind="discrete", n=6)
            print(f"   {palette.upper()}: {len(colors)} colors")
            print(f"     {colors}")
        except Exception as e:
            print(f"   {palette.upper()}: Error - {e}")

    # Test Nature Journal Style
    print("\n🎨 Testing Nature Journal Style (NPG)...")
    try:
        hz.use("scheme-1")
        colors = hz.palette(None, kind="discrete", n=6)
        print(f"✅ Applied NPG colors: {colors}")

        # Test each available library
        test_libraries(colors)

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test CLI commands
    print("\n🔧 Testing CLI Commands...")
    test_cli_commands()

    # Export tokens
    print("\n🔗 Exporting Web Tokens...")
    try:
        from huez.export import export_tokens
        export_tokens(config.schemes["scheme-1"], "demo_tokens")
        print("✅ Exported tokens to demo_tokens/")
    except Exception as e:
        print(f"❌ Token export failed: {e}")

    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n📁 Generated files:")
    if HAS_MATPLOTLIB: print("   - demo_npg_matplotlib.png")
    if HAS_SEABORN: print("   - demo_npg_seaborn.png")
    if HAS_PLOTLY: print("   - demo_npg_plotly.html")
    if HAS_ALTAIR: print("   - demo_npg_altair.html")
    if HAS_PLOTNINE: print("   - demo_npg_plotnine.png")
    print("   - demo_tokens/ (CSS, JSON, JS)")


def test_libraries(colors):
    """Test available visualization libraries."""
    count = 0

    if HAS_MATPLOTLIB:
        test_matplotlib(colors)
        count += 1

    if HAS_SEABORN:
        test_seaborn(colors)
        count += 1

    if HAS_PLOTLY:
        test_plotly(colors)
        count += 1

    if HAS_ALTAIR:
        test_altair(colors)
        count += 1

    if HAS_PLOTNINE:
        test_plotnine(colors)
        count += 1

    print(f"✅ Tested {count} visualization libraries")


def test_matplotlib(colors):
    """Test matplotlib."""
    fig, ax = plt.subplots(figsize=(8, 5))

    categories = ['A', 'B', 'C', 'D', 'E']
    values = [20, 35, 30, 25, 40]

    bars = ax.bar(categories, values, color=colors[:len(categories)])
    ax.set_title('Matplotlib - NPG Colors')
    ax.set_ylabel('Values')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('demo_npg_matplotlib.png', dpi=150, bbox_inches='tight')
    plt.close()


def test_seaborn(colors):
    """Test seaborn."""
    np.random.seed(42)
    data = {
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    }

    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=data, x='x', y='y', hue='category')
    plt.title('Seaborn - NPG Colors')
    plt.grid(True, alpha=0.3)

    plt.savefig('demo_npg_seaborn.png', dpi=150, bbox_inches='tight')
    plt.close()


def test_plotly(colors):
    """Test plotly."""
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [20, 35, 30, 25, 40]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors[:len(categories)]
    ))

    fig.update_layout(
        title='Plotly - NPG Colors',
        showlegend=False
    )

    fig.write_html('demo_npg_plotly.html')


def test_altair(colors):
    """Test altair."""
    np.random.seed(42)
    data = {
        'x': np.random.randn(50).tolist(),
        'y': np.random.randn(50).tolist(),
        'category': np.random.choice(['A', 'B', 'C'], 50).tolist()
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
        title='Altair - NPG Colors'
    )

    chart.save('demo_npg_altair.html')


def test_plotnine(colors):
    """Test plotnine."""
    np.random.seed(42)
    data = {
        'x': np.random.randn(30),
        'y': np.random.randn(30),
        'category': np.random.choice(['A', 'B', 'C'], 30)
    }

    import pandas as pd
    df = pd.DataFrame(data)

    plot = (
        p9.ggplot(df, p9.aes(x='x', y='y', color='category')) +
        p9.geom_point(size=3, alpha=0.7) +
        p9.scale_color_manual(values=colors[:3]) +
        p9.theme_minimal() +
        p9.labs(
            title='plotnine - NPG Colors',
            x='X Variable',
            y='Y Variable'
        ) +
        p9.theme(figure_size=(4, 3))
    )

    plot.save('demo_npg_plotnine.png', dpi=150, verbose=False)


def test_cli_commands():
    """Test basic CLI commands."""
    import subprocess
    import sys

    commands = [
        ["huez", "list", "schemes"],
        ["huez", "list", "palettes"],
        ["huez", "current"]
    ]

    for cmd in commands:
        try:
            result = subprocess.run([sys.executable, "-m", "huez.cli"] + cmd[1:],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd)}")
            else:
                print(f"❌ {' '.join(cmd)} - {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ {' '.join(cmd)} - {e}")


if __name__ == "__main__":
    main()


