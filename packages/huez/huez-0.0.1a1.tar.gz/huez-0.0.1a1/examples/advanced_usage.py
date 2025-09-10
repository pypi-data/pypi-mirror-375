#!/usr/bin/env python3
"""
Advanced usage example for huez.

This example demonstrates:
- Custom configuration files
- Quality checks and colorblind safety
- Figure linting
- Context managers for scheme switching
- Export functionality
"""

import numpy as np
import os
import json

# Import huez
import huez as hz

# Optional: Import visualization libraries
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def main():
    """Main advanced example function."""

    print("huez Advanced Usage Example")
    print("=" * 50)

    # 1. Create and load custom configuration
    print("\n1. Creating custom configuration...")
    custom_config = create_custom_config()
    print(f"   Created custom config with {len(custom_config.schemes)} schemes")

    # Save config
    hz.config.save_config_to_file(custom_config, "custom_huez.yaml")
    print("   Saved as 'custom_huez.yaml'")

    # Load custom config
    config = hz.load_config("custom_huez.yaml")
    print("   Loaded custom configuration")

    # 2. Use custom scheme
    print("\n2. Using custom scheme 'academic'...")
    hz.use("academic")
    print(f"   Current scheme: {hz.current_scheme()}")

    # 3. Quality checks
    print("\n3. Running quality checks...")
    quality_results = hz.check_palette("academic")
    print_quality_report(quality_results)

    # 4. Create publication-ready plots
    if HAS_MATPLOTLIB:
        print("\n4. Creating publication-ready plots...")
        create_publication_plots()
        print("   Plots saved with publication quality")

    # 5. Demonstrate context manager
    print("\n5. Demonstrating context manager...")
    demonstrate_context_manager()

    # 6. Export styles for different formats
    print("\n6. Exporting styles...")
    export_styles_for_formats()

    # 7. Figure linting
    if HAS_MATPLOTLIB:
        print("\n7. Running figure linting...")
        lint_results = hz.lint_figure("publication_plots.png")
        print_lint_report(lint_results)

    # 8. Generate comprehensive gallery
    print("\n8. Generating comprehensive gallery...")
    hz.preview_gallery("advanced_gallery", scheme="academic")
    print("   Gallery generated in 'advanced_gallery/'")

    print("\n" + "=" * 50)
    print("Advanced example completed!")
    print("\nGenerated files:")
    print("- custom_huez.yaml (custom configuration)")
    print("- publication_plots.png (publication-ready plots)")
    print("- academic.mplstyle (matplotlib style)")
    print("- academic_plotly.json (plotly template)")
    print("- advanced_gallery/ (complete preview gallery)")


def create_custom_config():
    """Create a custom configuration for academic publishing."""

    from huez.config import Config, Scheme, FontConfig, PalettesConfig, FigureConfig, StyleConfig

    # Academic scheme - optimized for papers
    academic_scheme = Scheme(
        title="Academic Publishing",
        fonts=FontConfig(family="DejaVu Sans", size=9),  # Small for papers
        palettes=PalettesConfig(
            discrete="okabe-ito",      # Colorblind-friendly
            sequential="viridis",      # Perceptually uniform
            diverging="vik",           # From Crameri, good for scientific data
            cyclic="twilight"          # Clean cyclic colormap
        ),
        figure=FigureConfig(size=[3.5, 2.5], dpi=300),  # Single column width
        style=StyleConfig(
            grid="y",                  # Only horizontal grid
            legend_loc="best",
            spine_top_right_off=True   # Clean look
        )
    )

    # Presentation scheme - optimized for slides
    presentation_scheme = Scheme(
        title="Presentation",
        fonts=FontConfig(family="DejaVu Sans", size=14),  # Larger for screens
        palettes=PalettesConfig(
            discrete="tableau-10",     # Bright and distinct
            sequential="plasma",       # High contrast
            diverging="coolwarm",      # Familiar diverging
            cyclic="hsv"              # Standard cyclic
        ),
        figure=FigureConfig(size=[8.0, 6.0], dpi=150),   # Larger for slides
        style=StyleConfig(
            grid="both",              # Full grid for clarity
            legend_loc="upper right",
            spine_top_right_off=False  # Keep all spines for definition
        )
    )

    # Create config
    config = Config()
    config.schemes = {
        "academic": academic_scheme,
        "presentation": presentation_scheme
    }
    config.default_scheme = "academic"

    return config


def print_quality_report(results):
    """Print quality check results."""
    for palette_type, checks in results.items():
        if "error" in checks:
            print(f"   {palette_type}: ❌ {checks['error']}")
            continue

        print(f"   {palette_type}:")
        print(f"     Colors: {checks.get('n_colors', 'N/A')}")

        # Colorblind safety
        if "checks" in checks:
            cb_checks = checks["checks"]
            if "colorblind_safe" in cb_checks:
                cb_results = cb_checks["colorblind_safe"]
                if isinstance(cb_results, dict):
                    print("     Colorblind safety:")
                    for cb_type, result in cb_results.items():
                        if isinstance(result, bool):
                            status = "✅" if result else "⚠️"
                            print(f"       {cb_type}: {status}")
                        else:
                            print(f"       {cb_type}: {result}")

        # Contrast ratios
        if "contrast_ratios" in cb_checks:
            ratios = cb_checks["contrast_ratios"]
            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                print(".2f"
def create_publication_plots():
    """Create publication-ready plots."""
    if not HAS_MATPLOTLIB:
        return

    # Generate sample scientific data
    np.random.seed(42)
    n_samples = 100

    # Experiment data
    conditions = ['Control', 'Treatment A', 'Treatment B', 'Treatment C']
    measurements = [
        np.random.normal(1.0, 0.1, n_samples//4),
        np.random.normal(1.3, 0.15, n_samples//4),
        np.random.normal(1.1, 0.12, n_samples//4),
        np.random.normal(0.9, 0.08, n_samples//4)
    ]

    # Time series data
    time = np.linspace(0, 10, 50)
    signal1 = np.sin(time) + np.random.normal(0, 0.1, len(time))
    signal2 = np.cos(time) + np.random.normal(0, 0.1, len(time))

    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(7, 3))  # Single row for paper
    fig.suptitle('Scientific Data Analysis', fontsize=10, fontweight='bold')

    # Box plot
    axes[0].boxplot(measurements, labels=conditions)
    axes[0].set_ylabel('Measurement Value', fontsize=9)
    axes[0].set_title('Condition Comparison', fontsize=9)
    axes[0].tick_params(axis='both', which='major', labelsize=8)
    axes[0].grid(True, alpha=0.3)

    # Time series
    axes[1].plot(time, signal1, label='Signal 1', linewidth=1.5, marker='o', markersize=3)
    axes[1].plot(time, signal2, label='Signal 2', linewidth=1.5, marker='s', markersize=3)
    axes[1].set_xlabel('Time', fontsize=9)
    axes[1].set_ylabel('Signal Amplitude', fontsize=9)
    axes[1].set_title('Time Series Analysis', fontsize=9)
    axes[1].tick_params(axis='both', which='major', labelsize=8)
    axes[1].legend(fontsize=8, framealpha=0.9)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('publication_plots.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()


def demonstrate_context_manager():
    """Demonstrate context manager for scheme switching."""
    print("   Original scheme: academic")

    # Try to switch to presentation scheme temporarily
    try:
        with hz.using("presentation"):
            print("   Inside context: presentation")
            # Could create different plots here
        print("   Back to original: academic")
    except ValueError:
        print("   Presentation scheme not available in this config")


def export_styles_for_formats():
    """Export styles for different formats."""
    try:
        # Export matplotlib style
        hz.export_styles("styles_export", scheme="academic", formats=["matplotlib"])
        print("   Exported matplotlib style")

        # Export plotly template
        hz.export_styles("styles_export", scheme="academic", formats=["plotly"])
        print("   Exported plotly template")

    except Exception as e:
        print(f"   Style export failed: {e}")


def print_lint_report(results):
    """Print linting results."""
    if "error" in results:
        print(f"   ❌ Linting failed: {results['error']}")
        return

    summary = results.get("summary", {})
    issues = results.get("issues", [])

    print("   Linting summary:")
    print(f"     Total issues: {summary.get('total_issues', 0)}")
    print(f"     Errors: {summary.get('errors', 0)}")
    print(f"     Warnings: {summary.get('warnings', 0)}")
    print(f"     Info: {summary.get('info', 0)}")

    if issues:
        print("   Top issues:")
        for i, issue in enumerate(issues[:3]):  # Show first 3 issues
            severity = issue.get("severity", "info")
            icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(severity, "•")
            print(f"     {icon} {issue.get('message', 'Unknown issue')}")


if __name__ == "__main__":
    main()


