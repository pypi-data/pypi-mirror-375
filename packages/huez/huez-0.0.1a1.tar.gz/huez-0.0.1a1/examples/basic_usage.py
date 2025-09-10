#!/usr/bin/env python3
"""
Basic usage example for huez.

This example demonstrates the core functionality of huez:
- Loading and using color schemes
- Creating plots with consistent styling
- Working with different visualization libraries
"""

import numpy as np

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
    import plotnine as p9
    HAS_PLOTNINE = True
except ImportError:
    HAS_PLOTNINE = False
    print("plotnine not available")


def main():
    """Main example function."""

    print("huez Basic Usage Example")
    print("=" * 40)

    # 1. Load default configuration
    print("\n1. Loading default configuration...")
    config = hz.load_config()
    print(f"   Loaded {len(config.schemes)} schemes")
    print(f"   Available schemes: {', '.join(config.schemes.keys())}")

    # 2. Use a color scheme
    print("\n2. Applying color scheme 'scheme-1'...")
    hz.use("scheme-1")
    print(f"   Current scheme: {hz.current_scheme()}")

    # 3. Get color palettes
    print("\n3. Getting color palettes...")
    discrete_colors = hz.palette(None, kind="discrete", n=6)
    print(f"   Discrete colors ({len(discrete_colors)}): {discrete_colors}")

    sequential_cmap = hz.cmap(None, kind="sequential")
    print(f"   Sequential colormap: {sequential_cmap}")

    # 4. Create sample plots
    if HAS_MATPLOTLIB:
        print("\n4. Creating sample matplotlib plots...")
        create_matplotlib_plots()
        print("   Plots saved as 'example_plots.png'")

    if HAS_SEABORN:
        print("\n5. Creating sample seaborn plots...")
        create_seaborn_plots()
        print("   Seaborn plot saved as 'seaborn_example.png'")

    if HAS_PLOTNINE:
        print("\n6. Creating sample plotnine plots...")
        create_plotnine_plots()
        print("   Plotnine plot saved as 'plotnine_example.png'")

    # 7. Export styles
    print("\n7. Exporting styles...")
    try:
        hz.export_styles("exported_styles", scheme="scheme-1")
        print("   Styles exported to 'exported_styles/' directory")
    except Exception as e:
        print(f"   Failed to export styles: {e}")

    # 8. Generate preview gallery
    print("\n8. Generating preview gallery...")
    try:
        hz.preview_gallery("gallery", scheme="scheme-1")
        print("   Gallery generated in 'gallery/' directory")
        print("   Open 'gallery/gallery.html' in your browser")
    except Exception as e:
        print(f"   Failed to generate gallery: {e}")

    print("\n" + "=" * 40)
    print("Example completed!")


def create_matplotlib_plots():
    """Create sample matplotlib plots."""
    if not HAS_MATPLOTLIB:
        return

    # Generate sample data
    np.random.seed(42)
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x + np.pi/4)

    scatter_x = np.random.randn(50)
    scatter_y = np.random.randn(50)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('huez Matplotlib Example', fontsize=16)

    # Line plot
    axes[0, 0].plot(x, y1, label='sin(x)', linewidth=2)
    axes[0, 0].plot(x, y2, label='cos(x)', linewidth=2)
    axes[0, 0].plot(x, y3, label='sin(x+π/4)', linewidth=2)
    axes[0, 0].set_title('Line Plot')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Scatter plot
    colors = np.random.randint(0, len(hz.palette(None, kind="discrete", n=6)), 50)
    axes[0, 1].scatter(scatter_x, scatter_y, c=colors, alpha=0.7, cmap=hz.cmap(None, kind="sequential"))
    axes[0, 1].set_title('Scatter Plot')
    axes[0, 1].grid(True, alpha=0.3)

    # Bar chart
    categories = ['A', 'B', 'C', 'D', 'E']
    values = np.random.randint(10, 50, 5)
    axes[1, 0].bar(categories, values)
    axes[1, 0].set_title('Bar Chart')
    axes[1, 0].grid(True, alpha=0.3)

    # Heatmap
    data = np.random.randn(10, 10)
    im = axes[1, 1].imshow(data, cmap=hz.cmap(None, kind="sequential"))
    axes[1, 1].set_title('Heatmap')
    plt.colorbar(im, ax=axes[1, 1])

    plt.subplots_adjust(hspace=0.3, wspace=0.3)
    plt.savefig('example_plots.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_seaborn_plots():
    """Create sample seaborn plots."""
    if not HAS_SEABORN:
        return

    # Generate sample data
    np.random.seed(42)
    data = {
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'value': np.random.randn(100)
    }

    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=data, x='x', y='y', hue='category', style='category')
    plt.title('huez Seaborn Example')
    plt.grid(True, alpha=0.3)
    plt.savefig('seaborn_example.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_plotnine_plots():
    """Create sample plotnine plots."""
    if not HAS_PLOTNINE:
        return

    # Generate sample data
    np.random.seed(42)
    n = 50
    data = {
        'x': np.random.randn(n),
        'y': np.random.randn(n),
        'category': np.random.choice(['A', 'B', 'C'], n),
        'size': np.random.randint(10, 50, n)
    }

    # Create plotnine plot with huez scales
    plot = (
        p9.ggplot(data, p9.aes(x='x', y='y', color='category', size='size')) +
        p9.geom_point(alpha=0.7) +
        p9.theme_minimal() +
        p9.labs(title='huez plotnine Example') +
        hz.gg_scales()  # Add huez scales
    )

    plot.save('plotnine_example.png', dpi=150)


if __name__ == "__main__":
    main()
