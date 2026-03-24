#!/usr/bin/env python3
"""
🔨 Windows Scripts - EXE Builder
=================================
Builds standalone .exe files for Space Manager and Performance Manager
using PyInstaller. The resulting executables run on any Windows machine
without requiring Python to be installed.

Usage:
    python build_exe.py              # Build both scripts
    python build_exe.py --space      # Build Space Manager only
    python build_exe.py --perf       # Build Performance Manager only
    python build_exe.py --clean      # Remove build artifacts

Requirements:
    pip install pyinstaller
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPTS = {
    "space": {
        "source": "space_manager.py",
        "name": "SpaceManager",
        "icon": None,  # Set to .ico path if you have an icon
        "description": "Windows Space Manager - Disk space analysis and cleanup",
    },
    "perf": {
        "source": "performance_manager.py",
        "name": "PerformanceManager",
        "icon": None,
        "description": "Windows Performance Manager - System monitoring and optimization",
    },
}

DIST_DIR = Path("dist")
BUILD_DIR = Path("build")


# ─── Helpers ─────────────────────────────────────────────────────────────────


def check_pyinstaller():
    """Verify PyInstaller is installed."""
    try:
        import PyInstaller  # noqa: F401

        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller via pip."""
    print("📦 Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✅ PyInstaller installed successfully\n")


def build_exe(key: str):
    """Build a single script into a standalone .exe."""
    config = SCRIPTS[key]
    source = Path(config["source"])

    if not source.exists():
        print(f"❌ Source file not found: {source}")
        return False

    print(f"🔨 Building {config['name']}...")
    print(f"   Source: {source}")
    print(f"   Output: {DIST_DIR / config['name']}.exe\n")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",           # Single .exe file
        "--console",           # Console application (not windowed)
        "--clean",             # Clean cache before building
        f"--name={config['name']}",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        "--specpath=build",
    ]

    # Add icon if available
    if config["icon"] and Path(config["icon"]).exists():
        cmd.append(f"--icon={config['icon']}")

    # Add version info
    cmd.extend([
        f"--add-data={source};.",  # Include source as data (Windows separator)
    ])

    cmd.append(str(source))

    try:
        subprocess.check_call(cmd)
        exe_path = DIST_DIR / f"{config['name']}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ {config['name']}.exe built successfully ({size_mb:.1f} MB)")
            print(f"   Location: {exe_path.resolve()}\n")
            return True
        else:
            print(f"\n❌ Build completed but .exe not found at {exe_path}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed for {config['name']}: {e}")
        return False


def clean_build():
    """Remove all build artifacts."""
    print("🧹 Cleaning build artifacts...")
    removed = []
    for d in [BUILD_DIR, DIST_DIR]:
        if d.exists():
            shutil.rmtree(d)
            removed.append(str(d))

    # Remove .spec files
    for spec in Path(".").glob("*.spec"):
        spec.unlink()
        removed.append(str(spec))

    if removed:
        print(f"   Removed: {', '.join(removed)}")
    else:
        print("   Nothing to clean")
    print("✅ Clean complete\n")


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="🔨 Build standalone .exe files for Windows Scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--space", action="store_true", help="Build Space Manager only")
    parser.add_argument("--perf", action="store_true", help="Build Performance Manager only")
    parser.add_argument("--clean", action="store_true", help="Remove build artifacts")
    args = parser.parse_args()

    print("=" * 60)
    print("🔨 Windows Scripts - EXE Builder")
    print("=" * 60)
    print()

    if args.clean:
        clean_build()
        return

    # Check / install PyInstaller
    if not check_pyinstaller():
        print("⚠️  PyInstaller is not installed.")
        try:
            install_pyinstaller()
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller. Install manually:")
            print("   pip install pyinstaller")
            sys.exit(1)

    # Determine what to build
    build_space = args.space or (not args.space and not args.perf)
    build_perf = args.perf or (not args.space and not args.perf)

    results = {}

    if build_space:
        results["SpaceManager"] = build_exe("space")

    if build_perf:
        results["PerformanceManager"] = build_exe("perf")

    # Summary
    print("=" * 60)
    print("📊 Build Summary")
    print("=" * 60)
    for name, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"   {name}: {status}")

    if all(results.values()):
        print(f"\n🎉 All executables are in the '{DIST_DIR}/' folder.")
        print("   Copy the .exe files to any Windows machine to use them.")
        print("   No Python installation required!\n")
    else:
        print("\n⚠️  Some builds failed. Check the output above for details.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
