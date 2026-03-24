#!/usr/bin/env python3

"""
Windows Space Manager - Disk Space Analysis & Cleanup
Find where your storage is being used and free up space safely.
Compatible with Windows 10 and Windows 11.
Part of Python Scripts Collection
"""

import os
import sys
import subprocess
import argparse
import platform
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import json


# ─── Risk Level Constants ──────────────────────────────────────────────────────

RISK_SAFE = "🟢 Safe"
RISK_LOW = "🔵 Low Risk"
RISK_MODERATE = "🟡 Moderate"
RISK_HIGH = "🔴 High Risk"


# ─── Windows Version Detection ─────────────────────────────────────────────────

def get_windows_info():
    """Detect Windows version and build number."""
    version = platform.version()
    release = platform.release()
    try:
        build = int(version.split('.')[2])
    except (IndexError, ValueError):
        build = 0

    is_win11 = build >= 22000
    return {
        "version": version,
        "release": release,
        "build": build,
        "is_win11": is_win11,
        "name": "Windows 11" if is_win11 else "Windows 10"
    }


def check_admin():
    """Check if running with administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def require_admin(operation_name):
    """Warn if not running as admin for operations that need it."""
    if not check_admin():
        print()
        print(f"🔐 Administrator privileges needed for: {operation_name}")
        print("   💡 Right-click this script and select 'Run as administrator'")
        print()
        return False
    return True


# ─── Utility Functions ──────────────────────────────────────────────────────────

def format_size(size_bytes):
    """Convert bytes to a human-friendly string."""
    if size_bytes < 0:
        return "Unknown"
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.1f} {units[unit_index]}"


def format_bar(used, total, width=30):
    """Create a visual progress bar for disk usage."""
    if total == 0:
        return "[" + "░" * width + "]"
    ratio = min(used / total, 1.0)
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def get_usage_emoji(percent):
    """Return emoji based on usage percentage."""
    if percent < 50:
        return "🟢"
    elif percent < 75:
        return "🟡"
    elif percent < 90:
        return "🟠"
    else:
        return "🔴"


# ─── Banner ────────────────────────────────────────────────────────────────────

def show_startup_banner():
    """Display an attractive startup banner"""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    💾 WINDOWS SPACE MANAGER                                ║")
    print("║                     Find & Free Up Disk Space                              ║")
    print("║                              Version 1.0                                   ║")
    print("║                    Part of Python Scripts Collection                       ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()

    win_info = get_windows_info()
    print(f"🪟  Running on: {win_info['name']} (Build {win_info['build']})")
    print(f"👤  User: {os.getenv('USERNAME', 'Unknown')}")
    print(f"📅  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    is_admin = check_admin()
    admin_status = "✅ Administrator" if is_admin else "⚠️  Standard User (some features need admin)"
    print(f"🔐  Privileges: {admin_status}")
    print("=" * 80)
    print()


# ─── Main Class ────────────────────────────────────────────────────────────────

class WindowsSpaceManager:
    def __init__(self):
        self.home_dir = Path.home()
        self.log_dir = Path(os.getenv('LOCALAPPDATA', self.home_dir / 'AppData' / 'Local')) / 'SpaceManager'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "space_manager.log"
        self.win_info = get_windows_info()

    def log_action(self, action, success=True, details=""):
        """Log the action to the log file with timestamp and success status."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        log_entry = f"{timestamp} - {action} - {status}"
        if details:
            log_entry += f" - {details}"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass

    def run_ps_command(self, ps_script, description=None):
        """Execute a PowerShell command and return (success, output)."""
        command = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{ps_script}"'
        return self._run(command, description)

    def run_command(self, command, description=None):
        """Execute a shell command and return (success, output)."""
        return self._run(command, description)

    def _run(self, command, description=None):
        """Internal: execute command with error handling."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True, timeout=300
            )
            if description:
                self.log_action(description)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if description:
                self.log_action(description, success=False, details=str(e))
            return False, e.stderr.strip() if e.stderr else str(e)
        except subprocess.TimeoutExpired:
            if description:
                self.log_action(description, success=False, details="Timed out after 5 minutes")
            return False, "Operation timed out"
        except Exception as e:
            if description:
                self.log_action(description, success=False, details=str(e))
            return False, str(e)

    # ─── 1. Drive Overview ──────────────────────────────────────────────────

    def show_drive_overview(self):
        """Show all drives with space usage in a friendly format."""
        print()
        print("=" * 60)
        print(f"📊 YOUR DISK SPACE OVERVIEW          {RISK_SAFE}")
        print("   This only looks at your drives — nothing is changed.")
        print("=" * 60)
        print()

        drives_found = []

        # Use shutil.disk_usage for each drive letter
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    usage = shutil.disk_usage(drive)
                    total = usage.total
                    used = usage.used
                    free = usage.free
                    percent = (used / total * 100) if total > 0 else 0

                    emoji = get_usage_emoji(percent)
                    bar = format_bar(used, total)

                    drives_found.append({
                        "letter": letter,
                        "total": total,
                        "used": used,
                        "free": free,
                        "percent": percent
                    })

                    print(f"  {emoji} Drive {letter}: {bar} {percent:.0f}% used")
                    print(f"      Total: {format_size(total)}  |  Used: {format_size(used)}  |  Free: {format_size(free)}")

                    if percent >= 90:
                        print(f"      🚨 This drive is almost full! You should free up space soon.")
                    elif percent >= 75:
                        print(f"      ⚠️  Getting full — consider cleaning up some files.")
                    else:
                        print(f"      ✅ Plenty of space available.")
                    print()

                except PermissionError:
                    print(f"  🔒 Drive {letter}: Cannot read (access denied)")
                    print()
                except Exception:
                    pass

        if not drives_found:
            print("  ❌ No drives found. This is unusual — please check your system.")
        else:
            # Summary
            total_space = sum(d["total"] for d in drives_found)
            total_used = sum(d["used"] for d in drives_found)
            total_free = sum(d["free"] for d in drives_found)

            print("─" * 60)
            print(f"  📊 Total across all drives:")
            print(f"      💾 Total: {format_size(total_space)}  |  Used: {format_size(total_used)}  |  Free: {format_size(total_free)}")
            print()

        self.log_action("Drive overview displayed")
        return drives_found

    # ─── 2. Folder Size Scanner ─────────────────────────────────────────────

    def scan_folder_sizes(self, target_path=None, top_n=15):
        """Scan a directory and show the largest folders."""
        if target_path is None:
            target_path = self.home_dir

        target = Path(target_path)

        print()
        print("=" * 60)
        print(f"📁 WHAT'S TAKING UP SPACE?           {RISK_SAFE}")
        print("   Scanning your folders to find the biggest ones.")
        print("   This only looks — it won't delete anything.")
        print("=" * 60)
        print(f"   📂 Scanning: {target}")
        print("   ⏳ This may take a minute or two...")
        print()

        folder_sizes = []

        try:
            for item in target.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    try:
                        total_size = 0
                        file_count = 0
                        for root, dirs, files in os.walk(item):
                            # Skip hidden and system directories
                            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('$Recycle.Bin', 'System Volume Information')]
                            for f in files:
                                try:
                                    fp = os.path.join(root, f)
                                    if not os.path.islink(fp):
                                        total_size += os.path.getsize(fp)
                                        file_count += 1
                                except (OSError, PermissionError):
                                    pass
                        folder_sizes.append((item.name, total_size, file_count))
                    except PermissionError:
                        folder_sizes.append((item.name, -1, 0))

        except PermissionError:
            print("  🔒 Cannot access this folder. Try running as administrator.")
            return

        # Sort by size descending
        folder_sizes.sort(key=lambda x: x[1], reverse=True)

        if not folder_sizes:
            print("  📂 No folders found in this location.")
            return

        # Find max size for bar scaling
        max_size = folder_sizes[0][1] if folder_sizes[0][1] > 0 else 1

        print(f"  📊 Top {min(top_n, len(folder_sizes))} largest folders in {target.name or target}:")
        print()

        for i, (name, size, count) in enumerate(folder_sizes[:top_n], 1):
            if size < 0:
                print(f"  {i:2d}. 🔒 {name:<30}  (access denied)")
            else:
                bar_width = 20
                ratio = size / max_size if max_size > 0 else 0
                filled = int(bar_width * ratio)
                bar = "█" * filled + "░" * (bar_width - filled)
                print(f"  {i:2d}. [{bar}] {format_size(size):>10}  📁 {name}  ({count:,} files)")

        print()
        total_scanned = sum(s for _, s, _ in folder_sizes if s > 0)
        print(f"  📊 Total scanned: {format_size(total_scanned)}")
        print()
        print("  💡 Tip: Large folders like 'AppData' or 'Downloads' often have files")
        print("     you can safely delete. Use option 3 to find specific large files.")
        print()

        self.log_action(f"Folder scan completed: {target}")

    # ─── 3. Large File Finder ───────────────────────────────────────────────

    def find_large_files(self, target_path=None, min_size_mb=100, top_n=20):
        """Find the largest files on the system."""
        if target_path is None:
            target_path = self.home_dir

        target = Path(target_path)

        print()
        print("=" * 60)
        print(f"🔍 FINDING LARGE FILES               {RISK_SAFE}")
        print(f"   Looking for files larger than {min_size_mb} MB.")
        print("   This only finds them — it won't delete anything.")
        print("=" * 60)
        print(f"   📂 Searching in: {target}")
        print("   ⏳ This may take a few minutes for large drives...")
        print()

        min_size_bytes = min_size_mb * 1024 * 1024
        large_files = []

        try:
            for root, dirs, files in os.walk(target):
                # Skip system directories
                dirs[:] = [d for d in dirs if d not in ('$Recycle.Bin', 'System Volume Information', 'Windows', 'ProgramData')]
                for f in files:
                    try:
                        fp = Path(root) / f
                        if not fp.is_symlink():
                            size = fp.stat().st_size
                            if size >= min_size_bytes:
                                large_files.append((str(fp), size, fp.suffix.lower()))
                    except (OSError, PermissionError):
                        pass

        except PermissionError:
            print("  🔒 Cannot access some folders. Try running as administrator.")

        # Sort by size descending
        large_files.sort(key=lambda x: x[1], reverse=True)

        if not large_files:
            print(f"  ✅ No files larger than {min_size_mb} MB found!")
            print("  💡 Your files are well managed. No action needed.")
            return

        print(f"  🔍 Found {len(large_files)} files larger than {min_size_mb} MB:")
        print()

        # Group by file type for friendliness
        type_names = {
            '.iso': '💿 Disk Image',
            '.zip': '📦 Archive',
            '.rar': '📦 Archive',
            '.7z': '📦 Archive',
            '.tar': '📦 Archive',
            '.gz': '📦 Archive',
            '.mp4': '🎬 Video',
            '.mkv': '🎬 Video',
            '.avi': '🎬 Video',
            '.mov': '🎬 Video',
            '.wmv': '🎬 Video',
            '.mp3': '🎵 Audio',
            '.flac': '🎵 Audio',
            '.wav': '🎵 Audio',
            '.exe': '⚙️ Program',
            '.msi': '⚙️ Installer',
            '.vhdx': '💿 Virtual Disk',
            '.vmdk': '💿 Virtual Disk',
            '.bak': '💾 Backup',
            '.log': '📋 Log File',
            '.tmp': '🗑️ Temporary',
        }

        for i, (path, size, ext) in enumerate(large_files[:top_n], 1):
            type_label = type_names.get(ext, '📄 File')
            print(f"  {i:2d}. {type_label:<18} {format_size(size):>10}  {path}")

        if len(large_files) > top_n:
            print(f"  ... and {len(large_files) - top_n} more files")

        total_size = sum(s for _, s, _ in large_files)
        print()
        print(f"  📊 Total size of large files: {format_size(total_size)}")
        print()
        print("  💡 Tips:")
        print("     • 💿 Disk images (.iso) can often be deleted after use")
        print("     • 📦 Archives (.zip, .rar) may have already been extracted")
        print("     • 🗑️ Temporary files (.tmp) are safe to delete")
        print("     • 🎬 Videos take the most space — move them to external storage")
        print()

        self.log_action(f"Large file scan: found {len(large_files)} files over {min_size_mb}MB")

    # ─── 4. Duplicate File Finder ───────────────────────────────────────────

    def find_duplicates(self, target_path=None, min_size_mb=1):
        """Find duplicate files using hash comparison."""
        if target_path is None:
            target_path = self.home_dir

        target = Path(target_path)
        min_size_bytes = min_size_mb * 1024 * 1024

        print()
        print("=" * 60)
        print(f"🔍 FINDING DUPLICATE FILES            {RISK_SAFE}")
        print("   Looking for identical files that waste space.")
        print("   This only finds them — it won't delete anything.")
        print("=" * 60)
        print(f"   📂 Searching in: {target}")
        print(f"   📏 Minimum file size: {min_size_mb} MB")
        print("   ⏳ This may take several minutes...")
        print()

        # Phase 1: Group files by size
        print("   🔍 Step 1/2: Grouping files by size...")
        size_groups = {}

        try:
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in ('$Recycle.Bin', 'System Volume Information', '.git')]
                for f in files:
                    try:
                        fp = Path(root) / f
                        if not fp.is_symlink():
                            size = fp.stat().st_size
                            if size >= min_size_bytes:
                                size_groups.setdefault(size, []).append(str(fp))
                    except (OSError, PermissionError):
                        pass
        except PermissionError:
            pass

        # Keep only sizes with multiple files
        potential_dupes = {s: paths for s, paths in size_groups.items() if len(paths) > 1}

        if not potential_dupes:
            print()
            print("  ✅ No duplicate files found!")
            print("  💡 Your files look well organized. No action needed.")
            return

        # Phase 2: Hash comparison
        print(f"   🔍 Step 2/2: Comparing {sum(len(v) for v in potential_dupes.values())} files...")

        hash_groups = {}
        for size, paths in potential_dupes.items():
            for path in paths:
                try:
                    file_hash = self._hash_file(path)
                    if file_hash:
                        hash_groups.setdefault(file_hash, []).append((path, size))
                except Exception:
                    pass

        # Keep only actual duplicates
        duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}

        if not duplicates:
            print()
            print("  ✅ No duplicate files found!")
            print("  💡 Files with the same size turned out to be different.")
            return

        # Display results
        total_wasted = 0
        dup_count = 0

        print()
        print(f"  🔍 Found {len(duplicates)} groups of duplicate files:")
        print()

        for i, (file_hash, files) in enumerate(sorted(duplicates.items(), key=lambda x: x[1][0][1], reverse=True), 1):
            if i > 10:
                remaining = len(duplicates) - 10
                print(f"  ... and {remaining} more groups of duplicates")
                break

            file_size = files[0][1]
            wasted = file_size * (len(files) - 1)
            total_wasted += wasted
            dup_count += len(files) - 1

            print(f"  Group {i}: {format_size(file_size)} each — {len(files)} identical copies")
            for path, _ in files:
                print(f"     📄 {path}")
            print(f"     💡 You could save {format_size(wasted)} by keeping just one copy.")
            print()

        print("─" * 60)
        print(f"  📊 Summary:")
        print(f"     🔍 Duplicate groups found: {len(duplicates)}")
        print(f"     📄 Extra copies: {dup_count}")
        print(f"     💾 Space you could free: {format_size(total_wasted)}")
        print()
        print("  ⚠️  Before deleting duplicates, make sure you keep the copy")
        print("     in the location you want. Don't delete files you're unsure about.")
        print()

        self.log_action(f"Duplicate scan: {len(duplicates)} groups, {format_size(total_wasted)} reclaimable")

    def _hash_file(self, filepath, block_size=65536):
        """Compute SHA-256 hash of a file (first 1MB for speed)."""
        hasher = hashlib.sha256()
        max_read = 1024 * 1024  # 1MB for quick comparison
        bytes_read = 0
        try:
            with open(filepath, 'rb') as f:
                while bytes_read < max_read:
                    data = f.read(block_size)
                    if not data:
                        break
                    hasher.update(data)
                    bytes_read += len(data)
            return hasher.hexdigest()
        except Exception:
            return None

    # ─── 5. Temp Files Cleanup ──────────────────────────────────────────────

    def cleanup_temp_files(self):
        """Clean up temporary files and caches."""
        print()
        print("=" * 60)
        print(f"🧹 CLEAN UP TEMPORARY FILES           {RISK_LOW}")
        print("   Removes junk files that your computer doesn't need.")
        print("   This frees up space without affecting your programs.")
        print("=" * 60)
        print()

        # Define cleanup targets with user-friendly descriptions
        cleanup_targets = []

        # Windows Temp
        temp_dir = os.getenv('TEMP', '')
        if temp_dir and os.path.exists(temp_dir):
            cleanup_targets.append({
                "name": "Windows temporary files",
                "path": temp_dir,
                "description": "Files programs create temporarily while running",
                "risk": RISK_LOW
            })

        # User Temp
        user_temp = self.home_dir / 'AppData' / 'Local' / 'Temp'
        if user_temp.exists() and str(user_temp) != temp_dir:
            cleanup_targets.append({
                "name": "Your temporary files",
                "path": str(user_temp),
                "description": "Temporary files from programs you've used",
                "risk": RISK_LOW
            })

        # Recycle Bin
        cleanup_targets.append({
            "name": "Recycle Bin",
            "path": "RECYCLE_BIN",
            "description": "Files you've already deleted (they're in the trash)",
            "risk": RISK_LOW
        })

        # Windows Prefetch
        prefetch = Path("C:\\Windows\\Prefetch")
        if prefetch.exists():
            cleanup_targets.append({
                "name": "Windows Prefetch cache",
                "path": str(prefetch),
                "description": "Old startup optimization data (Windows will rebuild it)",
                "risk": RISK_LOW
            })

        # Thumbnails
        thumb_cache = self.home_dir / 'AppData' / 'Local' / 'Microsoft' / 'Windows' / 'Explorer'
        if thumb_cache.exists():
            cleanup_targets.append({
                "name": "Thumbnail cache",
                "path": str(thumb_cache),
                "description": "Preview images of your files (will be recreated automatically)",
                "risk": RISK_LOW
            })

        # Scan sizes first
        print("  🔍 Checking what can be cleaned up...")
        print()

        total_reclaimable = 0
        valid_targets = []

        for target in cleanup_targets:
            if target["path"] == "RECYCLE_BIN":
                # Estimate recycle bin size
                size = self._estimate_recycle_bin_size()
                if size > 0:
                    valid_targets.append({**target, "size": size})
                    total_reclaimable += size
            else:
                size = self._get_dir_size(target["path"])
                if size > 0:
                    valid_targets.append({**target, "size": size})
                    total_reclaimable += size

        if not valid_targets:
            print("  ✅ Your computer is already clean! No temporary files to remove.")
            return True

        # Show what we found
        for i, target in enumerate(valid_targets, 1):
            print(f"  {i}. {target['risk']}  {target['name']}")
            print(f"     📝 {target['description']}")
            print(f"     💾 Space to free: {format_size(target['size'])}")
            print()

        print(f"  📊 Total space you can free: {format_size(total_reclaimable)}")
        print()

        # Ask for confirmation
        print("  Would you like to clean up these files?")
        print("  🔵 This is low risk — your programs will keep working normally.")
        print()

        try:
            response = input("  Clean up now? (yes/no): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n  ❌ Cancelled.")
            return False

        if response not in ('yes', 'y', 'si', 'sí'):
            print("  ❌ Cancelled. No files were deleted.")
            return False

        # Execute cleanup
        print()
        print("  🧹 Cleaning up...")
        cleaned = 0

        for target in valid_targets:
            print(f"  🧹 Cleaning: {target['name']}...")

            if target["path"] == "RECYCLE_BIN":
                success = self._empty_recycle_bin()
            else:
                success = self._clean_directory(target["path"])

            if success:
                cleaned += target["size"]
                print(f"     ✅ Done — freed {format_size(target['size'])}")
            else:
                print(f"     ⚠️  Some files couldn't be removed (they may be in use)")

        print()
        print("─" * 60)
        print(f"  ✅ Cleanup complete!")
        print(f"  💾 Space freed: approximately {format_size(cleaned)}")
        print()
        print("  💡 Tip: Run this once a month to keep your computer tidy.")
        print()

        self.log_action(f"Temp cleanup: freed approximately {format_size(cleaned)}")
        return True

    def _get_dir_size(self, path):
        """Calculate total size of a directory."""
        total = 0
        try:
            for root, dirs, files in os.walk(path):
                for f in files:
                    try:
                        total += os.path.getsize(os.path.join(root, f))
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total

    def _estimate_recycle_bin_size(self):
        """Estimate recycle bin size via PowerShell."""
        success, output = self.run_ps_command(
            "(New-Object -ComObject Shell.Application).NameSpace(10).Items() | "
            "ForEach-Object { $_.Size } | Measure-Object -Sum | "
            "Select-Object -ExpandProperty Sum",
            "Estimating Recycle Bin size"
        )
        if success and output.strip():
            try:
                return int(float(output.strip()))
            except (ValueError, TypeError):
                pass
        return 0

    def _empty_recycle_bin(self):
        """Empty the recycle bin."""
        success, _ = self.run_ps_command(
            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue",
            "Emptying Recycle Bin"
        )
        return success

    def _clean_directory(self, path):
        """Delete contents of a directory safely."""
        success_count = 0
        fail_count = 0

        try:
            for item in Path(path).iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    else:
                        item.unlink()
                    success_count += 1
                except (OSError, PermissionError):
                    fail_count += 1
        except (OSError, PermissionError):
            return False

        return success_count > 0

    # ─── 6. Old Downloads Scanner ───────────────────────────────────────────

    def scan_old_downloads(self, days_old=90):
        """Find old files in the Downloads folder."""
        downloads = self.home_dir / 'Downloads'

        if not downloads.exists():
            print("  ❌ Downloads folder not found.")
            return

        print()
        print("=" * 60)
        print(f"📥 OLD DOWNLOADS SCANNER              {RISK_SAFE}")
        print(f"   Finding files in your Downloads folder older than {days_old} days.")
        print("   This only shows them — nothing is deleted.")
        print("=" * 60)
        print()

        cutoff = datetime.now() - timedelta(days=days_old)
        old_files = []

        try:
            for item in downloads.iterdir():
                try:
                    if item.is_file():
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        if mtime < cutoff:
                            old_files.append((str(item.name), item.stat().st_size, mtime))
                except (OSError, PermissionError):
                    pass
        except (OSError, PermissionError):
            print("  🔒 Cannot access Downloads folder.")
            return

        if not old_files:
            print(f"  ✅ No files older than {days_old} days in your Downloads folder!")
            print("  💡 Your Downloads folder is well maintained.")
            return

        # Sort by size
        old_files.sort(key=lambda x: x[1], reverse=True)

        total_size = sum(s for _, s, _ in old_files)

        print(f"  📥 Found {len(old_files)} files older than {days_old} days:")
        print(f"  💾 Total size: {format_size(total_size)}")
        print()

        for i, (name, size, mtime) in enumerate(old_files[:20], 1):
            age_days = (datetime.now() - mtime).days
            print(f"  {i:2d}. {format_size(size):>10}  📄 {name}")
            print(f"      📅 Last used: {mtime.strftime('%Y-%m-%d')} ({age_days} days ago)")

        if len(old_files) > 20:
            print(f"  ... and {len(old_files) - 20} more files")

        print()
        print("  💡 Tips:")
        print("     • Installers (.exe, .msi) can usually be deleted after installing")
        print("     • Old documents might need to be moved to a better folder")
        print("     • You can delete these files manually from your Downloads folder")
        print()

        self.log_action(f"Old downloads scan: {len(old_files)} files, {format_size(total_size)}")

    # ─── 7. Windows Update Cleanup (Admin) ──────────────────────────────────

    def cleanup_windows_update(self):
        """Clean up old Windows Update files using DISM."""
        print()
        print("=" * 60)
        print(f"🪟 WINDOWS UPDATE CLEANUP             {RISK_MODERATE}")
        print("   Removes old Windows Update files that are no longer needed.")
        print("   This is an official Windows maintenance operation.")
        print("=" * 60)
        print()

        if not require_admin("Windows Update cleanup"):
            return False

        # Show WinSxS size first
        print("  🔍 Checking Windows component store size...")
        success, output = self.run_ps_command(
            "(Get-ChildItem -Path 'C:\\Windows\\WinSxS' -Recurse -ErrorAction SilentlyContinue | "
            "Measure-Object -Property Length -Sum).Sum",
            "Checking WinSxS size"
        )

        if success and output.strip():
            try:
                winsxs_size = int(float(output.strip()))
                print(f"  📦 Windows component store: {format_size(winsxs_size)}")
                print("     ℹ️  This is where Windows keeps backup copies of system files.")
                print("     ℹ️  Some of this space can be reclaimed safely.")
            except (ValueError, TypeError):
                print("  📦 Windows component store: Unable to determine size")

        print()
        print("  🟡 This is a moderate operation:")
        print("     • It removes old Windows update files")
        print("     • It may take 5-15 minutes")
        print("     • Your computer may need to restart afterward")
        print("     • This is the same as running 'Disk Cleanup' → 'Clean up system files'")
        print()

        try:
            response = input("  Continue with cleanup? (yes/no): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n  ❌ Cancelled.")
            return False

        if response not in ('yes', 'y', 'si', 'sí'):
            print("  ❌ Cancelled. No changes were made.")
            return False

        print()
        print("  🧹 Cleaning up Windows Update files...")
        print("  ⏳ This may take 5-15 minutes. Please be patient...")
        print()

        success, output = self.run_command(
            "DISM /Online /Cleanup-Image /StartComponentCleanup",
            "DISM Component Cleanup"
        )

        if success:
            print("  ✅ Windows Update cleanup complete!")
            print("  💾 Old update files have been removed.")
            print()
            print("  💡 You may need to restart your computer for all changes to take effect.")
        else:
            print("  ❌ Something went wrong during cleanup.")
            print()
            print("  This can happen when:")
            print("  • Windows Update is currently installing updates")
            print("  • Another cleanup is already running")
            print("  • System files need to be repaired first")
            print()
            print("  💡 Try restarting your computer and running this again.")
            if output:
                print(f"  🔍 Technical details: {output[:200]}")

        self.log_action("Windows Update cleanup", success=success)
        return success

    # ─── 8. Pagefile & Hibernation Info ─────────────────────────────────────

    def show_system_files_info(self):
        """Show info about pagefile.sys and hiberfil.sys."""
        print()
        print("=" * 60)
        print(f"📊 SYSTEM FILES INFO                  {RISK_SAFE}")
        print("   Information about special Windows files that use space.")
        print("=" * 60)
        print()

        # Pagefile
        pagefile = Path("C:\\pagefile.sys")
        if pagefile.exists():
            try:
                size = pagefile.stat().st_size
                print(f"  💾 Pagefile (pagefile.sys): {format_size(size)}")
                print("     ℹ️  What is this? Windows uses this as extra memory when your RAM is full.")
                print("     ℹ️  This file is normal and important for your computer to work well.")
                print("     ℹ️  Windows manages this automatically — you usually don't need to change it.")
            except (OSError, PermissionError):
                print("  💾 Pagefile (pagefile.sys): Exists but cannot determine size")
                print("     ℹ️  Run as administrator to see the size.")
        else:
            print("  💾 Pagefile: Not found on C: drive (may be on another drive)")

        print()

        # Hibernation file
        hiberfil = Path("C:\\hiberfil.sys")
        if hiberfil.exists():
            try:
                size = hiberfil.stat().st_size
                print(f"  😴 Hibernation file (hiberfil.sys): {format_size(size)}")
                print("     ℹ️  What is this? This lets your computer hibernate (sleep with no power).")
                print("     ℹ️  If you never use 'Hibernate', you can disable it to save space.")
                print(f"     💡 To disable: Open Command Prompt as admin and run: powercfg /h off")
                print(f"     💡 This would free up {format_size(size)}.")
            except (OSError, PermissionError):
                print("  😴 Hibernation file (hiberfil.sys): Exists but cannot determine size")
        else:
            print("  😴 Hibernation file: Not present (hibernation is disabled)")
            print("     ℹ️  This is fine — your computer uses normal sleep instead.")

        print()

        # Swap file (Windows 10+)
        swapfile = Path("C:\\swapfile.sys")
        if swapfile.exists():
            try:
                size = swapfile.stat().st_size
                print(f"  📊 Swap file (swapfile.sys): {format_size(size)}")
                print("     ℹ️  What is this? Windows uses this for modern apps' memory management.")
                print("     ℹ️  This is small and managed automatically — leave it alone.")
            except (OSError, PermissionError):
                print("  📊 Swap file (swapfile.sys): Exists but cannot determine size")

        print()
        self.log_action("System files info displayed")

    # ─── 9. Export Report ───────────────────────────────────────────────────

    def export_report(self):
        """Generate a space usage report."""
        print()
        print("=" * 60)
        print(f"📋 GENERATING SPACE REPORT            {RISK_SAFE}")
        print("   Creating a file with all your disk space information.")
        print("=" * 60)
        print()

        report = {
            "generated": datetime.now().isoformat(),
            "system": {
                "os": self.win_info["name"],
                "build": self.win_info["build"],
                "user": os.getenv("USERNAME", "Unknown")
            },
            "drives": []
        }

        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    usage = shutil.disk_usage(drive)
                    report["drives"].append({
                        "letter": letter,
                        "total_bytes": usage.total,
                        "used_bytes": usage.used,
                        "free_bytes": usage.free,
                        "total_human": format_size(usage.total),
                        "used_human": format_size(usage.used),
                        "free_human": format_size(usage.free),
                        "percent_used": round(usage.used / usage.total * 100, 1) if usage.total > 0 else 0
                    })
                except Exception:
                    pass

        # Save report
        report_path = self.home_dir / "Desktop" / f"space_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"  ✅ Report saved to your Desktop!")
            print(f"  📄 File: {report_path}")
            print()
            print("  💡 You can share this file if someone is helping you with your computer.")

        except Exception as e:
            # Fallback to log directory
            report_path = self.log_dir / f"space_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"  ✅ Report saved to: {report_path}")
            except Exception as e2:
                print(f"  ❌ Could not save report: {e2}")

        print()
        self.log_action("Space report exported")

    # ─── Full Analysis ──────────────────────────────────────────────────────

    def full_analysis(self):
        """Run a complete space analysis."""
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              🔍 FULL SPACE ANALYSIS                        ║")
        print("║              Checking everything about your disk space      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

        self.show_drive_overview()
        input("  ⏸️  Press Enter to continue...")

        self.scan_folder_sizes()
        input("  ⏸️  Press Enter to continue...")

        self.find_large_files()
        input("  ⏸️  Press Enter to continue...")

        self.scan_old_downloads()
        input("  ⏸️  Press Enter to continue...")

        self.show_system_files_info()

        print()
        print("═" * 60)
        print("  🎉 Full analysis complete!")
        print()
        print("  💡 What to do next:")
        print("     • Use option 5 to clean up temporary files")
        print("     • Delete old downloads you no longer need")
        print("     • Move large videos/photos to external storage")
        print("     • Use option 7 to clean old Windows Update files (admin)")
        print("═" * 60)
        print()

        self.log_action("Full space analysis completed")


# ─── Interactive Menu ──────────────────────────────────────────────────────────

def show_interactive_menu():
    """Display the interactive menu for non-technical users."""
    manager = WindowsSpaceManager()

    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception:
            pass

        show_startup_banner()

        print("🖥️  What would you like to do?")
        print("=" * 55)
        print()
        print("  📊 CHECK YOUR SPACE")
        print("  1. 🔍 See how full your drives are")
        print("  2. 📁 Find which folders are using the most space")
        print("  3. 📄 Find your biggest files")
        print("  4. 🔍 Find duplicate files (wasting space)")
        print("  5. 📥 Find old files in Downloads")
        print()
        print("  🧹 FREE UP SPACE")
        print("  6. 🗑️  Clean up temporary files (junk files)")
        print("  7. 🪟 Clean up old Windows Update files (admin)")
        print()
        print("  📋 INFORMATION")
        print("  8. 📊 Show system files info (pagefile, hibernation)")
        print("  9. 📋 Export a space report")
        print(" 10. 🔍 Run a full analysis (all of the above)")
        print()
        print("  0. 🚪 Exit")
        print()
        print("=" * 55)

        try:
            choice = input("  🎯 Enter your choice (0-10): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  👋 Goodbye!")
            break

        if choice == '0':
            print("\n  👋 Thanks for using Space Manager! Your computer thanks you too! 🎉")
            break

        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception:
            pass

        try:
            if choice == '1':
                manager.show_drive_overview()
            elif choice == '2':
                print()
                print("  📂 Where would you like to scan?")
                print("  1. Your home folder (recommended)")
                print("  2. The entire C: drive")
                print("  3. A specific folder")
                print()
                sub = input("  Choose (1/2/3): ").strip()
                if sub == '2':
                    manager.scan_folder_sizes("C:\\")
                elif sub == '3':
                    path = input("  Enter folder path: ").strip()
                    if os.path.exists(path):
                        manager.scan_folder_sizes(path)
                    else:
                        print(f"  ❌ Folder not found: {path}")
                else:
                    manager.scan_folder_sizes()
            elif choice == '3':
                print()
                print("  📏 What's the minimum file size to look for?")
                print("  1. 100 MB (recommended)")
                print("  2. 500 MB (only very large files)")
                print("  3. 50 MB (more results)")
                print()
                sub = input("  Choose (1/2/3): ").strip()
                size_map = {'1': 100, '2': 500, '3': 50}
                min_size = size_map.get(sub, 100)
                manager.find_large_files(min_size_mb=min_size)
            elif choice == '4':
                manager.find_duplicates()
            elif choice == '5':
                print()
                print("  📅 How old should files be?")
                print("  1. 90 days (recommended)")
                print("  2. 30 days")
                print("  3. 180 days (6 months)")
                print()
                sub = input("  Choose (1/2/3): ").strip()
                days_map = {'1': 90, '2': 30, '3': 180}
                days = days_map.get(sub, 90)
                manager.scan_old_downloads(days_old=days)
            elif choice == '6':
                manager.cleanup_temp_files()
            elif choice == '7':
                manager.cleanup_windows_update()
            elif choice == '8':
                manager.show_system_files_info()
            elif choice == '9':
                manager.export_report()
            elif choice == '10':
                manager.full_analysis()
            else:
                print(f"  ❌ '{choice}' is not a valid option. Please enter a number from 0 to 10.")
        except KeyboardInterrupt:
            print("\n  ⚠️  Operation cancelled.")
        except Exception as e:
            print(f"\n  ❌ Something went wrong: {e}")
            print("  💡 Try running the script as administrator if this keeps happening.")

        print()
        try:
            input("  ⏸️  Press Enter to go back to the menu...")
        except (KeyboardInterrupt, EOFError):
            break


# ─── CLI Entry Point ───────────────────────────────────────────────────────────

def main():
    """Main function — CLI arguments or interactive menu."""
    parser = argparse.ArgumentParser(
        description="💾 Windows Space Manager — Find and free up disk space (Win10 & Win11)",
        epilog="💡 Run without arguments for the interactive menu.\n🏠 Part of Python Scripts Collection",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    check_group = parser.add_argument_group("📊 Check Space")
    check_group.add_argument("--drives", action="store_true", help="🔍 Show all drives and their space usage")
    check_group.add_argument("--folders", type=str, nargs='?', const=str(Path.home()), help="📁 Scan folder sizes (default: home directory)")
    check_group.add_argument("--large-files", type=int, nargs='?', const=100, metavar="MB", help="📄 Find files larger than N MB (default: 100)")
    check_group.add_argument("--duplicates", type=str, nargs='?', const=str(Path.home()), help="🔍 Find duplicate files")
    check_group.add_argument("--old-downloads", type=int, nargs='?', const=90, metavar="DAYS", help="📥 Find downloads older than N days (default: 90)")

    clean_group = parser.add_argument_group("🧹 Cleanup")
    clean_group.add_argument("--clean-temp", action="store_true", help="🗑️ Clean up temporary files")
    clean_group.add_argument("--clean-updates", action="store_true", help="🪟 Clean old Windows Update files (admin)")

    info_group = parser.add_argument_group("📋 Information")
    info_group.add_argument("--system-files", action="store_true", help="📊 Show pagefile and hibernation info")
    info_group.add_argument("--report", action="store_true", help="📋 Export a space usage report")
    info_group.add_argument("--full", action="store_true", help="🔍 Run full space analysis")

    parser.add_argument("--version", action="version", version="Windows Space Manager v1.0")

    args = parser.parse_args()

    # Check if any CLI args were provided
    has_args = any([
        args.drives, args.folders is not None, args.large_files is not None,
        args.duplicates is not None, args.old_downloads is not None,
        args.clean_temp, args.clean_updates, args.system_files,
        args.report, args.full
    ])

    if not has_args:
        show_interactive_menu()
        return

    # CLI mode
    show_startup_banner()
    manager = WindowsSpaceManager()

    if args.full:
        manager.full_analysis()
        return

    if args.drives:
        manager.show_drive_overview()

    if args.folders is not None:
        manager.scan_folder_sizes(args.folders)

    if args.large_files is not None:
        manager.find_large_files(min_size_mb=args.large_files)

    if args.duplicates is not None:
        manager.find_duplicates(args.duplicates)

    if args.old_downloads is not None:
        manager.scan_old_downloads(days_old=args.old_downloads)

    if args.clean_temp:
        manager.cleanup_temp_files()

    if args.clean_updates:
        manager.cleanup_windows_update()

    if args.system_files:
        manager.show_system_files_info()

    if args.report:
        manager.export_report()


if __name__ == "__main__":
    main()
