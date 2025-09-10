#!/usr/bin/env python3
"""
CLI demo script for huez.

This script demonstrates how to use huez from the command line.
Run this after installing huez.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display the result."""
    print(f"\n{description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.stdout:
            print("Output:")
            print(result.stdout)

        if result.stderr:
            print("Errors:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ Command completed successfully")
        else:
            print(f"❌ Command failed with return code {result.returncode}")

    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
    except FileNotFoundError:
        print("❌ Command not found (is huez installed?)")
    except Exception as e:
        print(f"❌ Error running command: {e}")


def main():
    """Main CLI demo function."""

    print("huez CLI Demo")
    print("=" * 30)
    print("This demo shows how to use huez from the command line.")
    print("Make sure huez is installed before running this script.")

    # Check if huez is available
    try:
        subprocess.run(["huez", "--help"], capture_output=True, check=True)
        print("✅ huez CLI is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ huez CLI is not available. Please install huez first:")
        print("   pip install -e .")
        return

    # Demo commands
    commands = [
        (["huez", "--help"], "Show help information"),

        (["huez", "list", "schemes"], "List available schemes"),

        (["huez", "list", "palettes"], "List available palettes"),

        (["huez", "current"], "Show current scheme (should be none initially)"),

        (["huez", "use", "scheme-1"], "Apply scheme-1"),

        (["huez", "current"], "Show current scheme (should be scheme-1 now)"),
    ]

    # Initialize config
    if not Path("demo_huez.yaml").exists():
        print("\n" + "=" * 50)
        print("First, let's initialize a configuration file...")
        run_command(["huez", "init", "--preset", "minimal", "--out", "demo_huez.yaml"],
                   "Initialize huez configuration")

        commands.extend([
            (["huez", "list", "schemes", "--config", "demo_huez.yaml"],
             "List schemes from custom config"),

            (["huez", "use", "scheme-1", "--config", "demo_huez.yaml"],
             "Use scheme with custom config"),
        ])

    # Export styles
    commands.extend([
        (["huez", "export", "styles", "--scheme", "scheme-1", "--out", "cli_styles"],
         "Export styles for scheme-1"),

        (["huez", "export", "styles", "--formats", "mpl", "--out", "cli_styles"],
         "Export only matplotlib style"),
    ])

    # Generate preview
    commands.extend([
        (["huez", "preview", "--scheme", "scheme-1", "--out", "cli_gallery"],
         "Generate preview gallery"),
    ])

    # Quality checks
    commands.extend([
        (["huez", "check", "palette", "--scheme", "scheme-1"],
         "Check palette quality"),
    ])

    # Run all commands
    print("\n" + "=" * 50)
    print("Running CLI commands...")

    for cmd, description in commands:
        run_command(cmd, description)

    # Check generated files
    print("\n" + "=" * 50)
    print("Checking generated files...")

    files_to_check = [
        "demo_huez.yaml",
        "cli_styles/",
        "cli_gallery/",
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                print(f"✅ Directory created: {file_path}")
                # List contents
                try:
                    contents = os.listdir(file_path)
                    if contents:
                        print(f"   Contents: {', '.join(contents[:5])}{'...' if len(contents) > 5 else ''}")
                except Exception:
                    pass
            else:
                size = os.path.getsize(file_path)
                print(f"✅ File created: {file_path} ({size} bytes)")
        else:
            print(f"❌ File/directory not found: {file_path}")

    print("\n" + "=" * 50)
    print("CLI demo completed!")
    print("\nYou can now:")
    print("- Open cli_gallery/gallery.html in your browser")
    print("- Use the exported styles in your projects")
    print("- Run individual huez commands as needed")


if __name__ == "__main__":
    main()


