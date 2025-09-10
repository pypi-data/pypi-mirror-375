#!/usr/bin/env python3
"""
Journal Colors Showcase - 显示所有期刊配色方案的颜色
"""

import matplotlib.pyplot as plt
import numpy as np

# Import huez
import huez as hz

def create_color_showcase():
    """创建颜色展示图"""
    print("🎨 Journal Colors Showcase")
    print("=" * 50)

    # 期刊配色方案
    journal_schemes = {
        "npg": "Nature Publishing Group",
        "aaas": "Science Journal (AAAS)",
        "nejm": "New England Journal of Medicine",
        "lancet": "The Lancet",
        "jama": "Journal of the American Medical Association",
        "bmj": "British Medical Journal"
    }

    # 创建大图
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Journal Color Palettes Showcase', fontsize=16, fontweight='bold')
    axes = axes.flatten()

    for i, (palette_name, journal_name) in enumerate(journal_schemes.items()):
        ax = axes[i]

        # 获取配色方案
        try:
            colors = hz.palette(palette_name, kind="discrete", n=10)
            print(f"\n{palette_name.upper()} ({journal_name}):")
            for j, color in enumerate(colors):
                print(f"  {j+1}. {color}")

            # 创建颜色条
            for j, color in enumerate(colors):
                ax.add_patch(plt.Rectangle((0, j), 1, 0.8, color=color))
                # 添加颜色代码标签
                ax.text(0.5, j + 0.4, color, ha='center', va='center',
                       fontsize=8, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.1", facecolor="white", alpha=0.8))

        except Exception as e:
            print(f"❌ Error loading {palette_name}: {e}")
            ax.text(0.5, 0.5, f"Error:\n{e}", ha='center', va='center', transform=ax.transAxes)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, len(colors))
        ax.set_title(f'{palette_name.upper()}\n{journal_name}', fontsize=10, fontweight='bold')
        ax.axis('off')

    plt.tight_layout()
    plt.savefig('journal_colors_showcase.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("\n✅ Saved journal_colors_showcase.png")
    print("\n📊 Color counts:")    for palette_name, journal_name in journal_schemes.items():
        try:
            colors = hz.palette(palette_name, kind="discrete", n=10)
            print(f"  {palette_name.upper()}: {len(colors)} colors")
        except:
            print(f"  {palette_name.upper()}: Error loading")


if __name__ == "__main__":
    create_color_showcase()
