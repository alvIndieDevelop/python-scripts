#!/usr/bin/env python3

"""
Windows Performance Manager - System Performance Monitoring & Optimization
Monitor your computer's speed and optimize it for better performance.
Compatible with Windows 10 and Windows 11.
Part of Python Scripts Collection
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path
from datetime import datetime
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


def format_bar(value, max_value, width=30, warn_at=70, critical_at=90):
    """Create a visual bar with color indicators."""
    if max_value == 0:
        return "[" + "░" * width + "]"
    ratio = min(value / max_value, 1.0)
    percent = ratio * 100
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)

    if percent >= critical_at:
        emoji = "🔴"
    elif percent >= warn_at:
        emoji = "🟡"
    else:
        emoji = "🟢"

    return f"{emoji} [{bar}] {percent:.0f}%"


# ─── Banner ────────────────────────────────────────────────────────────────────

def show_startup_banner():
    """Display an attractive startup banner."""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    ⚡ WINDOWS PERFORMANCE MANAGER                           ║")
    print("║                     Monitor & Optimize Your Computer                       ║")
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

class WindowsPerformanceManager:
    def __init__(self):
        self.home_dir = Path.home()
        self.log_dir = Path(os.getenv('LOCALAPPDATA', self.home_dir / 'AppData' / 'Local')) / 'PerformanceManager'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "performance_manager.log"
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
                command, shell=True, capture_output=True, text=True, check=True, timeout=120
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
                self.log_action(description, success=False, details="Timed out")
            return False, "Operation timed out"
        except Exception as e:
            if description:
                self.log_action(description, success=False, details=str(e))
            return False, str(e)

    # ─── 1. System Overview Dashboard ───────────────────────────────────────

    def show_system_dashboard(self):
        """Show a comprehensive system performance dashboard."""
        print()
        print("=" * 65)
        print(f"⚡ HOW IS YOUR COMPUTER DOING?        {RISK_SAFE}")
        print("   A quick look at your computer's current performance.")
        print("   This only checks — nothing is changed.")
        print("=" * 65)
        print()

        # CPU Information
        print("  🖥️  PROCESSOR (CPU)")
        print("  ─" * 25)

        success, output = self.run_ps_command(
            "Get-CimInstance Win32_Processor | Select-Object -Property Name, NumberOfCores, "
            "NumberOfLogicalProcessors, MaxClockSpeed, LoadPercentage | Format-List",
            "Getting CPU info"
        )

        cpu_name = "Unknown"
        cpu_cores = 0
        cpu_threads = 0
        cpu_speed = 0
        cpu_load = 0

        if success and output:
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('Name'):
                    cpu_name = line.split(':', 1)[1].strip() if ':' in line else "Unknown"
                elif line.startswith('NumberOfCores'):
                    try:
                        cpu_cores = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('NumberOfLogicalProcessors'):
                    try:
                        cpu_threads = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('MaxClockSpeed'):
                    try:
                        cpu_speed = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('LoadPercentage'):
                    try:
                        cpu_load = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass

        print(f"  💻 Processor: {cpu_name}")
        if cpu_cores > 0:
            print(f"  ⚙️  Cores: {cpu_cores} cores, {cpu_threads} threads")
        if cpu_speed > 0:
            print(f"  ⚡ Speed: {cpu_speed / 1000:.1f} GHz")

        cpu_bar = format_bar(cpu_load, 100)
        print(f"  📊 Current usage: {cpu_bar}")

        if cpu_load >= 90:
            print("     🚨 Your processor is working very hard right now!")
            print("     💡 Some programs might be slow. Close programs you're not using.")
        elif cpu_load >= 70:
            print("     ⚠️  Your processor is moderately busy.")
        else:
            print("     ✅ Your processor is running smoothly.")

        print()

        # Memory (RAM) Information
        print("  💾 MEMORY (RAM)")
        print("  ─" * 25)

        success, output = self.run_ps_command(
            "$os = Get-CimInstance Win32_OperatingSystem; "
            "$total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1); "
            "$free = [math]::Round($os.FreePhysicalMemory / 1MB, 1); "
            "$used = [math]::Round($total - $free, 1); "
            "$percent = [math]::Round(($used / $total) * 100, 0); "
            "Write-Output \"$total|$used|$free|$percent\"",
            "Getting RAM info"
        )

        if success and output and '|' in output:
            parts = output.strip().split('|')
            try:
                total_ram = float(parts[0])
                used_ram = float(parts[1])
                free_ram = float(parts[2])
                ram_percent = int(parts[3])

                print(f"  📊 Total RAM: {total_ram:.1f} GB")
                ram_bar = format_bar(ram_percent, 100)
                print(f"  📊 Usage: {ram_bar}")
                print(f"     Used: {used_ram:.1f} GB  |  Free: {free_ram:.1f} GB")

                if ram_percent >= 90:
                    print("     🚨 Your memory is almost full!")
                    print("     💡 Close some programs or browser tabs to free up memory.")
                    print("     💡 If this happens often, your computer might need more RAM.")
                elif ram_percent >= 75:
                    print("     ⚠️  Memory usage is getting high.")
                    print("     💡 Consider closing programs you're not actively using.")
                else:
                    print("     ✅ Memory usage looks good.")
            except (ValueError, IndexError):
                print("  ⚠️  Could not read memory details.")
        else:
            print("  ⚠️  Could not read memory information.")

        print()

        # Disk I/O
        print("  💿 STORAGE")
        print("  ─" * 25)

        success, output = self.run_ps_command(
            "Get-CimInstance Win32_DiskDrive | Select-Object -Property Model, Size, MediaType | "
            "Format-List",
            "Getting disk info"
        )

        if success and output:
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('Model'):
                    disk_name = line.split(':', 1)[1].strip() if ':' in line else "Unknown"
                    print(f"  💿 Drive: {disk_name}")
                elif line.startswith('Size'):
                    try:
                        size_bytes = int(line.split(':')[1].strip())
                        print(f"     Capacity: {format_size(size_bytes)}")
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('MediaType'):
                    media = line.split(':', 1)[1].strip() if ':' in line else ""
                    if media:
                        is_ssd = 'ssd' in media.lower() or 'solid' in media.lower()
                        if is_ssd:
                            print(f"     Type: ⚡ SSD (fast storage)")
                        else:
                            print(f"     Type: 💿 HDD (standard storage)")
                            print(f"     💡 An SSD upgrade would make your computer much faster!")
                    print()
        else:
            print("  ⚠️  Could not read disk information.")

        print()

        # Network
        print("  🌐 NETWORK")
        print("  ─" * 25)

        success, output = self.run_ps_command(
            "Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet",
            "Testing network"
        )

        if success and 'true' in output.lower():
            print("  ✅ Internet connection: Working")

            # Check latency
            success2, output2 = self.run_ps_command(
                "(Test-Connection -ComputerName 8.8.8.8 -Count 3 | "
                "Measure-Object -Property Latency -Average).Average",
                "Measuring latency"
            )

            if success2 and output2.strip():
                try:
                    latency = float(output2.strip())
                    print(f"  📡 Response time: {latency:.0f} ms")
                    if latency < 50:
                        print("     ✅ Very fast connection!")
                    elif latency < 100:
                        print("     ✅ Good connection speed.")
                    elif latency < 200:
                        print("     ⚠️  Connection is a bit slow.")
                    else:
                        print("     🚨 Connection is slow. Check your network.")
                except (ValueError, TypeError):
                    pass
        else:
            print("  ❌ Internet connection: Not working")
            print("     💡 Check your Wi-Fi or network cable.")

        print()

        # Uptime
        print("  ⏱️  SYSTEM UPTIME")
        print("  ─" * 25)

        success, output = self.run_ps_command(
            "$uptime = (Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime; "
            "$days = $uptime.Days; $hours = $uptime.Hours; $mins = $uptime.Minutes; "
            "Write-Output \"$days|$hours|$mins\"",
            "Getting uptime"
        )

        if success and output and '|' in output:
            parts = output.strip().split('|')
            try:
                days = int(parts[0])
                hours = int(parts[1])
                minutes = int(parts[2])

                if days > 0:
                    uptime_str = f"{days} days, {hours} hours"
                elif hours > 0:
                    uptime_str = f"{hours} hours, {minutes} minutes"
                else:
                    uptime_str = f"{minutes} minutes"

                print(f"  ⏱️  Your computer has been on for: {uptime_str}")

                if days >= 7:
                    print("     ⚠️  Your computer hasn't been restarted in over a week.")
                    print("     💡 Restarting occasionally helps keep things running smoothly.")
                elif days >= 3:
                    print("     ℹ️  Consider restarting soon for best performance.")
                else:
                    print("     ✅ Recently restarted — that's good!")
            except (ValueError, IndexError):
                print("  ⚠️  Could not determine uptime.")
        else:
            print("  ⚠️  Could not determine uptime.")

        print()
        self.log_action("System dashboard displayed")

    # ─── 2. Startup Program Manager ─────────────────────────────────────────

    def manage_startup_programs(self):
        """List and manage programs that run at startup."""
        print()
        print("=" * 65)
        print(f"🚀 STARTUP PROGRAMS                   {RISK_SAFE}")
        print("   These programs start automatically when you turn on your computer.")
        print("   Too many can slow down how fast your computer starts up.")
        print("=" * 65)
        print()

        # Get startup items
        success, output = self.run_ps_command(
            "Get-CimInstance Win32_StartupCommand | "
            "Select-Object -Property Name, Command, Location | "
            "ConvertTo-Json",
            "Getting startup programs"
        )

        startup_items = []
        if success and output.strip():
            try:
                data = json.loads(output)
                if isinstance(data, dict):
                    data = [data]
                startup_items = data
            except json.JSONDecodeError:
                pass

        # Also check Task Manager startup (Win10+)
        success2, output2 = self.run_ps_command(
            "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -ErrorAction SilentlyContinue | "
            "Get-Member -MemberType NoteProperty | "
            "Where-Object { $_.Name -notin @('PSPath','PSParentPath','PSChildName','PSDrive','PSProvider') } | "
            "Select-Object -ExpandProperty Name",
            "Checking registry startup items"
        )

        registry_items = []
        if success2 and output2.strip():
            registry_items = [name.strip() for name in output2.strip().split('\n') if name.strip()]

        if not startup_items and not registry_items:
            print("  ✅ No startup programs found!")
            print("  💡 Your computer should start up quickly.")
            return

        total_items = len(startup_items) + len(registry_items)

        print(f"  📋 Found {total_items} programs that start with your computer:")
        print()

        # Show WMI startup items
        for i, item in enumerate(startup_items, 1):
            name = item.get('Name', 'Unknown')
            command = item.get('Command', 'Unknown')
            location = item.get('Location', 'Unknown')

            # Truncate long paths
            if len(command) > 60:
                command = command[:57] + "..."

            print(f"  {i:2d}. 📦 {name}")
            print(f"      📂 {command}")
            print(f"      📍 Source: {location}")
            print()

        # Show registry startup items
        offset = len(startup_items)
        for i, name in enumerate(registry_items, offset + 1):
            print(f"  {i:2d}. 📦 {name}")
            print(f"      📍 Source: User Registry (Run key)")
            print()

        # Performance assessment
        print("  ─" * 25)
        if total_items > 10:
            print(f"  ⚠️  You have {total_items} startup programs — that's quite a lot!")
            print("  💡 Having fewer startup programs makes your computer start faster.")
            print()
            print("  💡 How to manage startup programs:")
            print("     1. Press Ctrl + Shift + Esc to open Task Manager")
            print("     2. Click the 'Startup' tab")
            print("     3. Right-click programs you don't need and select 'Disable'")
            print()
            print("  ⚠️  Don't disable programs you don't recognize — some are important!")
            print("     When in doubt, search the program name online first.")
        elif total_items > 5:
            print(f"  ℹ️  You have {total_items} startup programs — that's a moderate amount.")
            print("  💡 You could disable a few to speed up startup slightly.")
        else:
            print(f"  ✅ Only {total_items} startup programs — that's great!")
            print("  💡 Your computer should start up reasonably fast.")

        print()
        self.log_action(f"Startup programs listed: {total_items} items")

    # ─── 3. Running Processes ───────────────────────────────────────────────

    def show_top_processes(self, top_n=15):
        """Show the programs using the most resources."""
        print()
        print("=" * 65)
        print(f"📊 PROGRAMS USING THE MOST RESOURCES  {RISK_SAFE}")
        print("   See which programs are using the most CPU and memory.")
        print("=" * 65)
        print()

        # Top CPU consumers
        print("  🖥️  TOP PROGRAMS BY CPU USAGE")
        print("  ─" * 25)

        success, output = self.run_ps_command(
            f"Get-Process | Sort-Object CPU -Descending | Select-Object -First {top_n} "
            "Name, @{{Name='CPU_Seconds';Expression={{[math]::Round($_.CPU, 1)}}}}, "
            "@{{Name='Memory_MB';Expression={{[math]::Round($_.WorkingSet64 / 1MB, 0)}}}} | "
            "ConvertTo-Json",
            "Getting top processes"
        )

        if success and output.strip():
            try:
                processes = json.loads(output)
                if isinstance(processes, dict):
                    processes = [processes]

                for i, proc in enumerate(processes, 1):
                    name = proc.get('Name', 'Unknown')
                    cpu = proc.get('CPU_Seconds', 0)
                    mem = proc.get('Memory_MB', 0)

                    # Make names user-friendly
                    friendly_names = {
                        'chrome': '🌐 Google Chrome',
                        'firefox': '🌐 Firefox',
                        'msedge': '🌐 Microsoft Edge',
                        'explorer': '📁 Windows Explorer',
                        'svchost': '⚙️ Windows Service',
                        'Code': '💻 Visual Studio Code',
                        'Teams': '💬 Microsoft Teams',
                        'Spotify': '🎵 Spotify',
                        'Discord': '💬 Discord',
                        'steam': '🎮 Steam',
                        'SearchHost': '🔍 Windows Search',
                        'RuntimeBroker': '⚙️ Windows Runtime',
                        'dwm': '🖥️ Desktop Window Manager',
                        'csrss': '⚙️ Windows System',
                        'lsass': '🔐 Windows Security',
                        'winlogon': '🔐 Windows Login',
                    }

                    display_name = friendly_names.get(name, f"📦 {name}")

                    # Memory bar
                    mem_bar = ""
                    if mem > 1000:
                        mem_bar = " ⚠️ Using a lot of memory"
                    elif mem > 500:
                        mem_bar = ""

                    print(f"  {i:2d}. {display_name:<35} CPU: {cpu:>8.1f}s  RAM: {mem:>5.0f} MB{mem_bar}")

                print()

                # Helpful tips
                total_mem = sum(p.get('Memory_MB', 0) for p in processes)
                if total_mem > 4000:
                    print("  💡 Your programs are using a lot of memory.")
                    print("     Consider closing browser tabs and programs you're not using.")
                else:
                    print("  ✅ Memory usage by programs looks reasonable.")

            except json.JSONDecodeError:
                print("  ⚠️  Could not read process information.")
        else:
            print("  ⚠️  Could not read process information.")

        print()
        self.log_action("Top processes displayed")

    # ─── 4. Service Manager ─────────────────────────────────────────────────

    def show_services_status(self):
        """Show important system services and their status."""
        print()
        print("=" * 65)
        print(f"⚙️  SYSTEM SERVICES STATUS             {RISK_SAFE}")
        print("   These are background programs that keep your computer working.")
        print("=" * 65)
        print()

        # Important services to check
        important_services = [
            ("wuauserv", "Windows Update", "Keeps your computer secure with the latest updates"),
            ("WinDefend", "Windows Defender", "Protects against viruses and malware"),
            ("Spooler", "Print Spooler", "Manages printing (needed for printers)"),
            ("BITS", "Background Transfer", "Downloads updates and files in the background"),
            ("Dhcp", "Network (DHCP)", "Gets your internet address automatically"),
            ("Dnscache", "DNS Cache", "Speeds up website loading"),
            ("EventLog", "Event Log", "Records system events for troubleshooting"),
            ("Schedule", "Task Scheduler", "Runs scheduled tasks automatically"),
            ("W32Time", "Windows Time", "Keeps your clock accurate"),
            ("Audiosrv", "Audio Service", "Manages sound on your computer"),
        ]

        print("  📋 Important Services:")
        print()

        running = 0
        stopped = 0

        for svc_name, friendly_name, description in important_services:
            success, output = self.run_ps_command(
                f"(Get-Service -Name '{svc_name}' -ErrorAction SilentlyContinue).Status",
                None  # Silent
            )

            if success and output.strip():
                status = output.strip()
                if status.lower() == 'running':
                    emoji = "✅"
                    status_text = "Running"
                    running += 1
                elif status.lower() == 'stopped':
                    emoji = "⏹️"
                    status_text = "Stopped"
                    stopped += 1
                else:
                    emoji = "⚠️"
                    status_text = status
            else:
                emoji = "❓"
                status_text = "Not found"

            print(f"  {emoji} {friendly_name:<25} {status_text}")
            print(f"     ℹ️  {description}")
            print()

        print("  ─" * 25)
        print(f"  📊 Summary: {running} running, {stopped} stopped")
        print()

        if stopped > 0:
            print("  ℹ️  Some stopped services are normal if you don't use those features.")
            print("     For example, Print Spooler can be off if you don't have a printer.")
        else:
            print("  ✅ All important services are running properly!")

        print()
        self.log_action(f"Services status: {running} running, {stopped} stopped")

    # ─── 5. Power Plan Manager ──────────────────────────────────────────────

    def show_power_plan(self):
        """Show and manage power plans."""
        print()
        print("=" * 65)
        print(f"🔋 POWER PLAN SETTINGS                {RISK_SAFE}")
        print("   Your power plan affects how fast your computer runs.")
        print("=" * 65)
        print()

        success, output = self.run_command(
            "powercfg /getactivescheme",
            "Getting active power plan"
        )

        if success and output:
            print(f"  ⚡ Current power plan: {output}")
            print()

            if 'balanced' in output.lower():
                print("  ℹ️  You're using the 'Balanced' plan.")
                print("     This is a good default — it balances speed with energy saving.")
                print()
                print("  💡 For better performance on a desktop computer:")
                print("     Switch to 'High Performance' plan.")
            elif 'high performance' in output.lower():
                print("  ⚡ You're using 'High Performance' — maximum speed!")
                print("     ℹ️  This uses more electricity but gives the best speed.")
            elif 'power saver' in output.lower():
                print("  🔋 You're using 'Power Saver' — this slows down your computer to save battery.")
                print("     💡 Switch to 'Balanced' for better speed while still saving some energy.")
        else:
            print("  ⚠️  Could not determine power plan.")

        # List available plans
        print()
        success2, output2 = self.run_command(
            "powercfg /list",
            "Listing power plans"
        )

        if success2 and output2:
            print("  📋 Available power plans:")
            for line in output2.split('\n'):
                line = line.strip()
                if 'GUID' in line or 'Power Scheme' in line:
                    if '*' in line:
                        print(f"     ⚡ {line}  ← ACTIVE")
                    else:
                        print(f"     📋 {line}")

        print()
        print("  💡 To change your power plan:")
        print("     1. Open Settings → System → Power & battery")
        print("     2. Or search for 'Power plan' in the Start menu")
        print()

        self.log_action("Power plan info displayed")

    # ─── 6. Disk Health Check ───────────────────────────────────────────────

    def check_disk_health(self):
        """Check disk health using available Windows tools."""
        print()
        print("=" * 65)
        print(f"💿 DISK HEALTH CHECK                  {RISK_SAFE}")
        print("   Checking if your storage drives are healthy.")
        print("=" * 65)
        print()

        # Get disk info
        success, output = self.run_ps_command(
            "Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, Size, "
            "@{Name='SizeGB';Expression={[math]::Round($_.Size / 1GB, 0)}} | ConvertTo-Json",
            "Checking disk health"
        )

        if success and output.strip():
            try:
                disks = json.loads(output)
                if isinstance(disks, dict):
                    disks = [disks]

                for disk in disks:
                    name = disk.get('FriendlyName', 'Unknown Disk')
                    media = disk.get('MediaType', 'Unknown')
                    health = disk.get('HealthStatus', 'Unknown')
                    size_gb = disk.get('SizeGB', 0)

                    # Disk type
                    if media == '4' or 'ssd' in str(media).lower():
                        type_emoji = "⚡"
                        type_name = "SSD (Solid State Drive)"
                    elif media == '3' or 'hdd' in str(media).lower():
                        type_emoji = "💿"
                        type_name = "HDD (Hard Disk Drive)"
                    else:
                        type_emoji = "💾"
                        type_name = f"Storage ({media})"

                    # Health status
                    if health.lower() == 'healthy' or health == '0':
                        health_emoji = "✅"
                        health_text = "Healthy"
                        health_explain = "Your drive is working perfectly!"
                    elif health.lower() in ('warning', '1'):
                        health_emoji = "⚠️"
                        health_text = "Warning"
                        health_explain = "Your drive might be having issues. Consider backing up your files."
                    elif health.lower() in ('unhealthy', '2'):
                        health_emoji = "🚨"
                        health_text = "Unhealthy"
                        health_explain = "Your drive has problems! Back up your files immediately!"
                    else:
                        health_emoji = "❓"
                        health_text = health
                        health_explain = "Could not determine health status."

                    print(f"  {type_emoji} {name}")
                    print(f"     Type: {type_name}")
                    print(f"     Size: {size_gb} GB")
                    print(f"     Health: {health_emoji} {health_text}")
                    print(f"     ℹ️  {health_explain}")
                    print()

            except json.JSONDecodeError:
                print("  ⚠️  Could not read disk health data.")
        else:
            # Fallback to wmic for Win10
            print("  ℹ️  Using alternative method to check disks...")
            success2, output2 = self.run_command(
                'wmic diskdrive get Model,Status,Size /format:list',
                "Checking disk status (wmic)"
            )
            if success2 and output2:
                print(f"  {output2}")
            else:
                print("  ⚠️  Could not check disk health. Try running as administrator.")

        # Check TRIM for SSDs
        print("  ⚡ SSD Optimization (TRIM):")
        success3, output3 = self.run_ps_command(
            "fsutil behavior query DisableDeleteNotify",
            "Checking TRIM status"
        )

        if success3 and output3:
            if '0' in output3:
                print("     ✅ TRIM is enabled — your SSD is being optimized automatically.")
                print("     ℹ️  TRIM helps your SSD stay fast over time.")
            elif '1' in output3:
                print("     ⚠️  TRIM is disabled.")
                print("     💡 Enabling TRIM can improve SSD performance and lifespan.")
        else:
            print("     ℹ️  Could not check TRIM status.")

        print()
        self.log_action("Disk health check completed")

    # ─── 7. System Integrity Check (Admin) ──────────────────────────────────

    def check_system_integrity(self):
        """Run Windows system file checker."""
        print()
        print("=" * 65)
        print(f"🛡️  SYSTEM FILE CHECK                  {RISK_MODERATE}")
        print("   Checks if Windows system files are intact and repairs them.")
        print("   This is like a doctor's checkup for your Windows installation.")
        print("=" * 65)
        print()

        if not require_admin("System integrity check"):
            return False

        print("  🟡 This operation:")
        print("     • Scans all Windows system files for problems")
        print("     • Automatically repairs any corrupted files")
        print("     • May take 10-30 minutes")
        print("     • Your computer will keep working during the scan")
        print()

        try:
            response = input("  Run the system check? (yes/no): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n  ❌ Cancelled.")
            return False

        if response not in ('yes', 'y', 'si', 'sí'):
            print("  ❌ Cancelled.")
            return False

        print()
        print("  🔍 Step 1: Scanning system files...")
        print("  ⏳ This may take 10-30 minutes. Please be patient...")
        print()

        success, output = self.run_command(
            "sfc /scannow",
            "System File Checker"
        )

        if success:
            if 'did not find any integrity violations' in output.lower():
                print("  ✅ Great news! All system files are intact!")
                print("  ℹ️  Your Windows installation is healthy.")
            elif 'successfully repaired' in output.lower():
                print("  ✅ Some files were damaged but have been repaired!")
                print("  💡 You may want to restart your computer.")
            elif 'could not' in output.lower() or 'unable' in output.lower():
                print("  ⚠️  Some files couldn't be repaired.")
                print("  💡 Try running DISM repair (option in the menu) first, then run this again.")
            else:
                print("  ℹ️  Scan completed. Results:")
                for line in output.split('\n')[-5:]:
                    if line.strip():
                        print(f"     {line.strip()}")
        else:
            print("  ❌ The system check encountered an error.")
            print()
            print("  💡 What to do:")
            print("     • Make sure you're running as administrator")
            print("     • Try restarting your computer and running again")
            if output:
                print(f"     🔍 Technical details: {output[:200]}")

        print()
        self.log_action("System integrity check", success=success)
        return success

    # ─── 8. Windows Update Status ───────────────────────────────────────────

    def check_windows_update(self):
        """Check Windows Update status."""
        print()
        print("=" * 65)
        print(f"🪟 WINDOWS UPDATE STATUS              {RISK_SAFE}")
        print("   Checking if your computer is up to date with the latest updates.")
        print("=" * 65)
        print()

        # Check last update time
        success, output = self.run_ps_command(
            "(Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1).InstalledOn.ToString('yyyy-MM-dd')",
            "Checking last update"
        )

        if success and output.strip():
            try:
                last_update = datetime.strptime(output.strip(), '%Y-%m-%d')
                days_since = (datetime.now() - last_update).days

                print(f"  📅 Last update installed: {output.strip()}")

                if days_since > 30:
                    print(f"     🚨 That was {days_since} days ago — your computer might be missing important security updates!")
                    print("     💡 Open Settings → Update & Security → Windows Update and check for updates.")
                elif days_since > 14:
                    print(f"     ⚠️  That was {days_since} days ago.")
                    print("     💡 Consider checking for updates soon.")
                else:
                    print(f"     ✅ Updated {days_since} days ago — that's recent!")
            except ValueError:
                print(f"  📅 Last update: {output.strip()}")
        else:
            print("  ⚠️  Could not determine last update date.")

        print()

        # List recent updates
        success2, output2 = self.run_ps_command(
            "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5 "
            "HotFixID, Description, InstalledOn | Format-Table -AutoSize",
            "Listing recent updates"
        )

        if success2 and output2.strip():
            print("  📋 Recent updates:")
            for line in output2.strip().split('\n'):
                print(f"     {line}")
        else:
            print("  ℹ️  Could not list recent updates.")

        print()
        print("  💡 To check for new updates:")
        print("     1. Open Settings (Windows key + I)")
        print("     2. Go to Update & Security (Win10) or Windows Update (Win11)")
        print("     3. Click 'Check for updates'")
        print()

        self.log_action("Windows Update status checked")

    # ─── Full Performance Check ─────────────────────────────────────────────

    def full_performance_check(self):
        """Run a comprehensive performance analysis."""
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              ⚡ FULL PERFORMANCE CHECK                      ║")
        print("║              A complete checkup of your computer's speed    ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

        self.show_system_dashboard()
        input("  ⏸️  Press Enter to continue...")

        self.show_top_processes()
        input("  ⏸️  Press Enter to continue...")

        self.manage_startup_programs()
        input("  ⏸️  Press Enter to continue...")

        self.check_disk_health()
        input("  ⏸️  Press Enter to continue...")

        self.check_windows_update()

        print()
        print("═" * 65)
        print("  🎉 Full performance check complete!")
        print()
        print("  💡 Quick recommendations:")
        print("     • Close browser tabs and programs you're not using")
        print("     • Restart your computer if it's been on for days")
        print("     • Keep Windows Update running to stay secure")
        print("     • Disable unnecessary startup programs for faster boot")
        print("═" * 65)
        print()

        self.log_action("Full performance check completed")


# ─── Interactive Menu ──────────────────────────────────────────────────────────

def show_interactive_menu():
    """Display the interactive menu for non-technical users."""
    manager = WindowsPerformanceManager()

    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception:
            pass

        show_startup_banner()

        print("🖥️  What would you like to do?")
        print("=" * 55)
        print()
        print("  📊 CHECK PERFORMANCE")
        print("  1. ⚡ See how your computer is performing right now")
        print("  2. 📊 See which programs are using the most resources")
        print("  3. 🚀 See what programs start with your computer")
        print("  4. ⚙️  Check system services status")
        print()
        print("  💿 HARDWARE & HEALTH")
        print("  5. 💿 Check if your storage drives are healthy")
        print("  6. 🔋 Check your power plan settings")
        print("  7. 🪟 Check if Windows is up to date")
        print()
        print("  🛠️  FIX & OPTIMIZE")
        print("  8. 🛡️  Check and repair Windows system files (admin)")
        print("  9. ⚡ Run a full performance check (all of the above)")
        print()
        print("  0. 🚪 Exit")
        print()
        print("=" * 55)

        try:
            choice = input("  🎯 Enter your choice (0-9): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  👋 Goodbye!")
            break

        if choice == '0':
            print("\n  👋 Thanks for using Performance Manager! Keep your computer running smoothly! 🎉")
            break

        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception:
            pass

        try:
            if choice == '1':
                manager.show_system_dashboard()
            elif choice == '2':
                manager.show_top_processes()
            elif choice == '3':
                manager.manage_startup_programs()
            elif choice == '4':
                manager.show_services_status()
            elif choice == '5':
                manager.check_disk_health()
            elif choice == '6':
                manager.show_power_plan()
            elif choice == '7':
                manager.check_windows_update()
            elif choice == '8':
                manager.check_system_integrity()
            elif choice == '9':
                manager.full_performance_check()
            else:
                print(f"  ❌ '{choice}' is not a valid option. Please enter a number from 0 to 9.")
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
        description="⚡ Windows Performance Manager — Monitor & optimize your computer (Win10 & Win11)",
        epilog="💡 Run without arguments for the interactive menu.\n🏠 Part of Python Scripts Collection",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    check_group = parser.add_argument_group("📊 Check Performance")
    check_group.add_argument("--dashboard", action="store_true", help="⚡ Show system performance dashboard")
    check_group.add_argument("--processes", action="store_true", help="📊 Show top resource-consuming programs")
    check_group.add_argument("--startup", action="store_true", help="🚀 List startup programs")
    check_group.add_argument("--services", action="store_true", help="⚙️ Check system services status")

    hw_group = parser.add_argument_group("💿 Hardware & Health")
    hw_group.add_argument("--disk-health", action="store_true", help="💿 Check storage drive health")
    hw_group.add_argument("--power", action="store_true", help="🔋 Show power plan info")
    hw_group.add_argument("--updates", action="store_true", help="🪟 Check Windows Update status")

    fix_group = parser.add_argument_group("🛠️ Fix & Optimize")
    fix_group.add_argument("--sfc", action="store_true", help="🛡️ Run system file checker (admin)")
    fix_group.add_argument("--full", action="store_true", help="⚡ Run full performance check")

    parser.add_argument("--version", action="version", version="Windows Performance Manager v1.0")

    args = parser.parse_args()

    has_args = any([
        args.dashboard, args.processes, args.startup, args.services,
        args.disk_health, args.power, args.updates,
        args.sfc, args.full
    ])

    if not has_args:
        show_interactive_menu()
        return

    # CLI mode
    show_startup_banner()
    manager = WindowsPerformanceManager()

    if args.full:
        manager.full_performance_check()
        return

    if args.dashboard:
        manager.show_system_dashboard()

    if args.processes:
        manager.show_top_processes()

    if args.startup:
        manager.manage_startup_programs()

    if args.services:
        manager.show_services_status()

    if args.disk_health:
        manager.check_disk_health()

    if args.power:
        manager.show_power_plan()

    if args.updates:
        manager.check_windows_update()

    if args.sfc:
        manager.check_system_integrity()


if __name__ == "__main__":
    main()
