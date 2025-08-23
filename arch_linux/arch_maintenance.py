#! /usr/bin/env python3

"""
Arch Linux maintenance script
automate the maintenance of the arch linux system
"""

import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import shutil
import stat


def show_startup_banner():
    """Display an attractive startup banner"""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    🚀 ARCH LINUX MAINTENANCE SCRIPT                        ║")
    print("║                     Professional System Maintenance Tool                    ║")
    print("║                              Version 2.0                                   ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()
    print("🔧 Comprehensive system maintenance for Arch Linux")
    print("📦 Package management, cleanup, health checks, and optimization")
    print("🛡️  Safe, secure, and user-friendly maintenance operations")
    print("=" * 80)
    print()


def show_system_info():
    """Display basic system information"""
    try:
        print("🖥️  SYSTEM INFORMATION")
        print("=" * 60)
        
        # OS info
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = {}
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_info[key] = value.strip('"')
            
            if 'PRETTY_NAME' in os_info:
                print(f"📋 OS: {os_info['PRETTY_NAME']}")
            if 'VERSION_ID' in os_info:
                print(f"📋 Version: {os_info['VERSION_ID']}")
        except:
            print("📋 OS: Arch Linux")
        
        # Kernel info
        try:
            kernel_result = subprocess.run("uname -r", shell=True, capture_output=True, text=True)
            if kernel_result.returncode == 0:
                print(f"🔧 Kernel: {kernel_result.stdout.strip()}")
        except:
            pass
        
        # Architecture
        try:
            arch_result = subprocess.run("uname -m", shell=True, capture_output=True, text=True)
            if arch_result.returncode == 0:
                print(f"🏗️  Architecture: {arch_result.stdout.strip()}")
        except:
            pass
        
        # User info
        print(f"👤 User: {os.getenv('USER', 'Unknown')}")
        print(f"🏠 Home: {Path.home()}")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"⚠️  Could not display system information: {e}")
        print()


class ArchLinuxMaintenance:
    def __init__(self):
        home_dir = Path.home()
        self.log_file = home_dir / ".arch_maintenance.log"
        self.install_dir = home_dir / ".local" / "bin"
        self.config_dir = home_dir / ".config" / "arch-maintenance"
        self.script_name = "archm-maintenance"
        self.short_command = "archm"

    def log_action(self, action, success=True):
        """Log the action to the log file with timestamp and success status"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp} - {action} - {status}\n")

    def run_command(self, command, description=None):
        """Run a command and handle errors with safety checks and enhanced visual feedback"""
        import threading
        import time
        import random
        
        # Lista de comandos peligrosos que requieren confirmación
        dangerous_patterns = [
            "rm -rf /", "rm -rf /*", "rm -rf /home", "rm -rf /etc",
            "dd if=", "mkfs", "fdisk", "parted", "wipefs",
            "chmod 777", "chown root", "chmod +s", "chmod +t"
        ]
        
        # Verificar si el comando contiene patrones peligrosos
        for pattern in dangerous_patterns:
            if pattern in command:
                print(f"⚠️  WARNING: Potentially dangerous command detected: {pattern}")
                print(f"Command: {command}")
                response = input("Are you sure you want to continue? (yes/no): ")
                if response.lower() != "yes":
                    print("Command cancelled by user")
                    self.log_action(f"CANCELLED: {description or command} (dangerous command)", success=False)
                    return False
        
        # Variables para la animación
        animation_running = True
        animation_thread = None
        
        def show_enhanced_animation():
            """Show an enhanced spinning animation with multiple effects"""
            # Diferentes tipos de spinners para variedad visual
            spinners = [
                ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],  # Braille
                ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],  # Circle
                ["◐", "◓", "◑", "◒"],  # Quarter circle
                ["◢", "◣", "◤", "◥"],  # Triangle
                ["▌", "▀", "▐", "▄"],  # Block
                ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],  # Braille again
            ]
            
            current_spinner = random.choice(spinners)
            i = 0
            frame_count = 0
            
            while animation_running:
                # Cambiar spinner cada 50 frames para variedad
                if frame_count % 50 == 0:
                    current_spinner = random.choice(spinners)
                
                # Mostrar spinner con descripción
                spinner_char = current_spinner[i % len(current_spinner)]
                print(f"\r{spinner_char} Running: {description or command}... ", end="", flush=True)
                
                time.sleep(0.1)
                i = (i + 1) % len(current_spinner)
                frame_count += 1
        
        try:
            # Mostrar inicio con efecto visual
            print(f"🚀 Starting: {command}")
            print("=" * 60)
            
            # Iniciar animación en un hilo separado
            animation_thread = threading.Thread(target=show_enhanced_animation)
            animation_thread.daemon = True
            animation_thread.start()
            
            # Ejecutar el comando
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            
            # Detener animación
            animation_running = False
            if animation_thread:
                animation_thread.join(timeout=0.5)
            
            # Limpiar línea de animación y mostrar resultado exitoso
            print(f"\r✅ Completed: {description or command}")
            print("🎉 Operation finished successfully!")
            print("=" * 60)
            
            self.log_action(description or command)
            return True
            
        except subprocess.CalledProcessError as e:
            # Detener animación
            animation_running = False
            if animation_thread:
                animation_thread.join(timeout=0.5)
            
            # Limpiar línea de animación y mostrar error detallado
            print(f"\r❌ Failed: {description or command} (exit code {e.returncode})")
            print("💥 Operation failed with errors:")
            print("=" * 60)
            print(f"🔍 Error details: {e}")
            
            if e.stdout:
                print(f"📤 Output: {e.stdout}")
            if e.stderr:
                print(f"📥 Error output: {e.stderr}")
            
            print("=" * 60)
            self.log_action(description or command, success=False)
            return False
            
        except FileNotFoundError as e:
            # Detener animación
            animation_running = False
            if animation_thread:
                animation_thread.join(timeout=0.5)
            
            print(f"\r❌ Command not found: {e}")
            print("🔍 The specified command is not available on this system")
            self.log_action(description or command, success=False)
            return False
            
        except PermissionError as e:
            # Detener animación
            animation_running = False
            if animation_thread:
                animation_thread.join(timeout=0.5)
            
            print(f"\r❌ Permission denied: {e}")
            print("🔐 This operation requires elevated privileges")
            print("💡 Try running with sudo or check file permissions")
            self.log_action(description or command, success=False)
            return False
            
        except KeyboardInterrupt:
            # Detener animación
            animation_running = False
            if animation_thread:
                animation_thread.join(timeout=0.5)
            
            print(f"\r⚠️  Interrupted: {description or command}")
            print("⏸️  Operation cancelled by user (Ctrl+C)")
            self.log_action(f"INTERRUPTED: {description or command}", success=False)
            return False
            
        except Exception as e:
            # Detener animación
            animation_running = False
            if animation_thread:
                animation_thread.join(timeout=0.5)
            
            print(f"\r❌ Unexpected error: {e}")
            print("💥 An unexpected error occurred during execution")
            print("🔍 Check system logs for more details")
            self.log_action(description or command, success=False)
            return False

    def update_system(self):
        """Update the system packages using pacman with best practices for Arch Linux"""
        print("🔄 Starting system update process...")
        print("=" * 60)
        print("📦 Arch Linux System Update")
        print("=" * 60)
        
        # Step 1: Sync package database first
        print("📦 Step 1: Synchronizing package database...")
        print("🔄 Syncing with official repositories...")
        success_sync = self.run_command("sudo pacman -Sy", "Synchronizing package database")
        if not success_sync:
            print("❌ Failed to sync package database. Aborting update.")
            print("💡 Check your internet connection and repository configuration.")
            return False
        
        # Step 2: Check for available updates
        print("🔍 Step 2: Checking for available updates...")
        print("🔍 Scanning for package updates...")
        try:
            result = subprocess.run("pacman -Qu", shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                update_count = len(result.stdout.strip().split('\n'))
                print(f"📊 Found {update_count} packages to update")
                print("📋 Packages that will be updated:")
                
                # Mostrar paquetes con formato mejorado
                packages = result.stdout.strip().split('\n')
                for i, pkg in enumerate(packages[:10], 1):  # Mostrar primeros 10
                    print(f"   {i:2d}. {pkg}")
                
                if update_count > 10:
                    print(f"   ... and {update_count - 10} more packages")
                
                print(f"\n💾 Estimated download size: Calculating...")
            else:
                print("✅ System is already up to date!")
                print("🎉 No updates available at this time.")
                return True
        except Exception as e:
            print(f"⚠️  Could not check update count: {e}")
        
        # Step 3: Update system packages
        print("\n🚀 Step 3: Updating system packages...")
        print("🚀 Installing updates from repositories...")
        success_update = self.run_command("sudo pacman -Syu --noconfirm", "Updating system packages")
        
        if success_update:
            print("✅ System packages updated successfully")
            print("🎉 System update completed!")
            
            # Step 4: Check if kernel was updated (common in Arch)
            print("\n🔍 Step 4: Checking for kernel updates...")
            try:
                kernel_check = subprocess.run("pacman -Q linux", shell=True, capture_output=True, text=True)
                if kernel_check.returncode == 0:
                    print("⚠️  Kernel update detected!")
                    print("💡 A new kernel version has been installed.")
                    print("💡 Consider rebooting when convenient for the new kernel to take effect.")
            except:
                pass
            
            # Step 5: Update package database again after update
            print("\n🔄 Step 5: Final database sync...")
            print("🔄 Updating package database after installation...")
            self.run_command("sudo pacman -Sy", "Final database sync after update")
            
            print("\n" + "=" * 60)
            print("🎉 System Update Summary")
            print("=" * 60)
            print("✅ Package database synchronized")
            print("✅ System packages updated")
            print("✅ Package database re-synchronized")
            print("🎉 System update completed successfully!")
            print("=" * 60)
            print()
            return True
        else:
            print("❌ Failed to update system packages")
            print("💥 Update process encountered errors")
            print("\n💡 Troubleshooting suggestions:")
            print("   • Check your internet connection")
            print("   • Verify repository configuration: sudo pacman -Syy")
            print("   • Try running without --noconfirm: sudo pacman -Syu")
            print("   • Check for package conflicts: sudo pacman -Syu --print-uris")
            print("   • Review system logs for detailed error information")
            print("\n" + "=" * 60)
            print()
            return False
        
    def clean_packages_cache(self):
        """Clean the packages cache with enhanced visual feedback and detailed information"""
        print("🧹 Starting package cache cleanup process...")
        print("=" * 60)
        print("🗑️  Arch Linux Package Cache Cleanup")
        print("=" * 60)
        
        # Step 1: Check current cache size
        print("📊 Step 1: Analyzing current package cache...")
        try:
            cache_info = subprocess.run("pacman -Sc --print-format '%n %s'", shell=True, capture_output=True, text=True)
            if cache_info.returncode == 0 and cache_info.stdout.strip():
                cache_lines = cache_info.stdout.strip().split('\n')
                total_packages = len(cache_lines)
                print(f"📦 Found {total_packages} cached packages")
                
                # Calcular tamaño total aproximado
                total_size = 0
                for line in cache_lines:
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            size_str = parts[-1]
                            if size_str.isdigit():
                                total_size += int(size_str)
                    except:
                        pass
                
                if total_size > 0:
                    size_mb = total_size / (1024 * 1024)
                    print(f"💾 Estimated cache size: {size_mb:.1f} MB")
            else:
                print("✅ Package cache is already clean")
                return True
        except Exception as e:
            print(f"⚠️  Could not analyze cache: {e}")
        
        # Step 2: Clean package cache
        print("\n🗑️  Step 2: Cleaning package cache...")
        print("🧹 Removing old package files...")
        success_1 = self.run_command("sudo pacman -Sc --noconfirm", "Cleaning packages cache")
        
        if not success_1:
            print("❌ Failed to clean package cache")
            print("💡 Try running manually: sudo pacman -Sc")
            return False
        
        # Step 3: Remove orphaned packages
        print("\n🧹 Step 3: Checking for orphaned packages...")
        print("🔍 Scanning for packages with no dependencies...")
        
        try:
            # Check for orphaned packages first
            orphan_check = subprocess.run("pacman -Qtd", shell=True, capture_output=True, text=True)
            if orphan_check.returncode == 0 and orphan_check.stdout.strip():
                orphan_count = len(orphan_check.stdout.strip().split('\n'))
                print(f"📦 Found {orphan_count} orphaned packages")
                
                if orphan_count > 0:
                    print("📋 Orphaned packages found:")
                    packages = orphan_check.stdout.strip().split('\n')
                    for i, pkg in enumerate(packages[:10], 1):  # Show first 10
                        print(f"   {i:2d}. {pkg}")
                    
                    if orphan_count > 10:
                        print(f"   ... and {orphan_count - 10} more")
                    
                    print("\n💡 Orphaned packages are packages that are no longer needed by any other package")
                    print("💡 Removing them can free up disk space and reduce system clutter")
                    
                    # Remove orphaned packages
                    success_2 = self.run_command("sudo pacman -Rns $(pacman -Qtdq)", "Removing orphaned packages")
                    
                    if success_2:
                        print("✅ Orphaned packages removed successfully")
                    else:
                        print("⚠️  Failed to remove some orphaned packages")
                        print("💡 Some packages may be protected or have dependencies")
                else:
                    print("✅ No orphaned packages found")
                    success_2 = True
            else:
                print("✅ No orphaned packages found")
                success_2 = True
        except Exception as e:
            print(f"⚠️  Could not check for orphaned packages: {e}")
            success_2 = False
        
        # Step 4: Clean AUR cache if yay is available
        print("\n📦 Step 4: Checking AUR package cache...")
        try:
            have_yay = subprocess.run("which yay", shell=True, capture_output=True, text=True).returncode == 0
            if have_yay:
                print("🔍 Found yay, checking AUR cache...")
                
                # Check yay cache size
                yay_cache_check = subprocess.run("yay -Sc --print-format '%n %s'", shell=True, capture_output=True, text=True)
                if yay_cache_check.returncode == 0 and yay_cache_check.stdout.strip():
                    yay_packages = len(yay_cache_check.stdout.strip().split('\n'))
                    print(f"📦 Found {yay_packages} cached AUR packages")
                    
                    if yay_packages > 0:
                        print("🧹 Cleaning AUR package cache...")
                        yay_cleanup = self.run_command("yay -Sc --noconfirm", "Cleaning AUR packages cache")
                        if yay_cleanup:
                            print("✅ AUR package cache cleaned successfully")
                        else:
                            print("⚠️  Failed to clean AUR package cache")
                    else:
                        print("✅ AUR package cache is already clean")
                else:
                    print("✅ AUR package cache is already clean")
            else:
                print("ℹ️  yay not found, skipping AUR cache cleanup")
        except Exception as e:
            print(f"⚠️  Could not check AUR cache: {e}")
        
        # Step 5: Show final results
        print("\n" + "=" * 60)
        print("🎉 Package Cache Cleanup Summary")
        print("=" * 60)
        
        if success_1 and success_2:
            print("✅ Package cache cleaned successfully")
            print("✅ Orphaned packages removed")
            print("✅ AUR cache checked and cleaned")
            print("🎉 Cache cleanup completed successfully!")
            
            # Show disk space freed (approximate)
            try:
                df_before = subprocess.run("df -h /var/cache/pacman/pkg", shell=True, capture_output=True, text=True)
                if df_before.returncode == 0:
                    print("\n💾 Disk space information:")
                    print(df_before.stdout.strip())
            except:
                pass
        else:
            print("⚠️  Cache cleanup completed with some issues")
            if not success_1:
                print("❌ Failed to clean package cache")
            if not success_2:
                print("❌ Failed to remove orphaned packages")
            print("💡 Check logs for detailed error information")
        
        print("=" * 60)
        print()
        return success_1 and success_2
        
    def update_aur_packages(self):
        """Update AUR packages using yay with comprehensive package management"""
        print("🔄 Starting AUR package update process...")
        print("=" * 40)
        
        # Step 1: Check if yay is installed
        print("🔍 Step 1: Checking for yay package manager...")
        have_yay = subprocess.run("which yay", shell=True, capture_output=True, text=True).returncode == 0
        
        if not have_yay:
            print("❌ yay is not installed")
            print("💡 To install yay, run: sudo pacman -S yay")
            print("💡 Alternative AUR helpers: paru, aura, or manual git clone")
            self.log_action("AUR Update: yay not installed", success=False)
            return False
        
        print("✅ yay is installed and available")
        
        # Step 2: Check yay version and configuration
        print("📋 Step 2: Checking yay configuration...")
        try:
            yay_version = subprocess.run("yay --version", shell=True, capture_output=True, text=True)
            if yay_version.returncode == 0:
                version_line = yay_version.stdout.strip().split('\n')[0]
                print(f"📦 yay version: {version_line}")
        except Exception as e:
            print(f"⚠️  Could not determine yay version: {e}")
        
        # Step 3: Check for available AUR updates
        print("🔍 Step 3: Checking for available AUR updates...")
        try:
            check_updates = subprocess.run("yay -Qua", shell=True, capture_output=True, text=True)
            if check_updates.returncode == 0 and check_updates.stdout.strip():
                update_count = len(check_updates.stdout.strip().split('\n'))
                print(f"📊 Found {update_count} AUR packages to update")
                
                # Show some package names for transparency
                packages = check_updates.stdout.strip().split('\n')[:5]  # Show first 5
                print("📋 Packages to update:")
                for pkg in packages:
                    print(f"   • {pkg}")
                if update_count > 5:
                    print(f"   ... and {update_count - 5} more")
            else:
                print("✅ All AUR packages are up to date!")
                self.log_action("AUR Update: No updates available", success=True)
                return True
        except Exception as e:
            print(f"⚠️  Could not check for updates: {e}")
        
        # Step 4: Update AUR packages
        print("🚀 Step 4: Updating AUR packages...")
        success_update = self.run_command("yay -Syu --noconfirm", "Updating AUR packages")
        
        if success_update:
            print("✅ AUR packages updated successfully")
            
            # Step 5: Clean up orphaned AUR packages
            print("🧹 Step 5: Cleaning up orphaned AUR packages...")
            try:
                # Check for orphaned packages
                orphan_check = subprocess.run("yay -Qtd", shell=True, capture_output=True, text=True)
                if orphan_check.returncode == 0 and orphan_check.stdout.strip():
                    orphan_count = len(orphan_check.stdout.strip().split('\n'))
                    print(f"📦 Found {orphan_count} orphaned packages")
                    
                    # Ask user if they want to remove them
                    print("💡 Orphaned packages are packages that are no longer needed by any other package")
                    response = input("Do you want to remove orphaned packages? (yes/no): ")
                    if response.lower() == "yes":
                        success_cleanup = self.run_command("yay -Rns $(yay -Qtdq)", "Removing orphaned AUR packages")
                        if success_cleanup:
                            print("✅ Orphaned packages removed successfully")
                        else:
                            print("⚠️  Failed to remove some orphaned packages")
                    else:
                        print("⏭️  Skipping orphaned package removal")
                else:
                    print("✅ No orphaned packages found")
            except Exception as e:
                print(f"⚠️  Could not check for orphaned packages: {e}")
            
            # Step 6: Update yay itself if needed
            print("🔄 Step 6: Checking if yay needs updating...")
            try:
                yay_update_check = subprocess.run("yay -Qu yay", shell=True, capture_output=True, text=True)
                if yay_update_check.returncode == 0 and yay_update_check.stdout.strip():
                    print("📦 yay has an update available")
                    response = input("Do you want to update yay? (yes/no): ")
                    if response.lower() == "yes":
                        success_yay_update = self.run_command("yay -S yay --noconfirm", "Updating yay package manager")
                        if success_yay_update:
                            print("✅ yay updated successfully")
                        else:
                            print("⚠️  Failed to update yay")
                    else:
                        print("⏭️  Skipping yay update")
                else:
                    print("✅ yay is up to date")
            except Exception as e:
                print(f"⚠️  Could not check yay update status: {e}")
            
            print("=" * 40)
            print("🎉 AUR package update completed successfully!")
            self.log_action("AUR Update: All packages updated successfully", success=True)
            return True
            
        else:
            print("❌ Failed to update AUR packages")
            print("💡 Common issues and solutions:")
            print("   • Check internet connection")
            print("   • Verify AUR repository access")
            print("   • Try running: yay -Syu (without --noconfirm) to see detailed errors")
            print("   • Check: yay -Ps for package status")
            print("=" * 40)
            self.log_action("AUR Update: Failed to update packages", success=False)
            return False

    def clean_systemd_logs(self):
        """Clean the systemd journal logs"""
        print("Cleaning systemd logs...")
        success_1 = self.run_command("sudo journalctl --vacuum-time=2w", "Clean systemd logs (2 weeks)")
        if success_1:
            print("Systemd journal logs cleaned successfully")
            print()
        else:
            print("Failed to clean systemd journal logs")
            print()

    def update_locate_database(self):
        """Update the locate database"""
        print("Updating locate database...")
        success_1 = self.run_command("sudo updatedb", "Updating locate database")
        if success_1:
            print("Locate database updated successfully")
            print()
        else:
            print("Failed to update locate database")
            print()
        
    def check_system_health(self):
        """Check the system health with comprehensive analysis and enhanced visual feedback"""
        print("🏥 Starting system health check...")
        print("=" * 60)
        print("🔍 Arch Linux System Health Check")
        print("=" * 60)
        
        # Contador de problemas encontrados
        issues_found = 0
        total_checks = 0
        
        # Step 1: Check for failed services
        print("🔍 Step 1: Checking systemd services status...")
        total_checks += 1
        
        try:
            result = subprocess.run("systemctl --failed --no-legend", shell=True, capture_output=True, text=True)
            
            if result.stdout.strip():
                failed_services = result.stdout.strip().split('\n')
                failed_count = len(failed_services)
                issues_found += 1
                
                print(f"❌ Found {failed_count} failed services:")
                print("=" * 60)
                
                for i, service in enumerate(failed_services, 1):
                    print(f"   {i:2d}. {service}")
                
                print("=" * 60)
                print("💡 Failed services can indicate system problems")
                print("💡 Consider investigating these services manually")
                
                self.log_action("System health check: Failed services found", success=False)
            else:
                print("✅ No failed services found")
                print("🎉 All systemd services are running properly")
                self.log_action("System health check: No failed services found", success=True)
        except Exception as e:
            print(f"⚠️  Could not check systemd services: {e}")
        
        # Step 2: Check system load
        print("\n📊 Step 2: Checking system load...")
        total_checks += 1
        
        try:
            load_result = subprocess.run("uptime", shell=True, capture_output=True, text=True)
            if load_result.returncode == 0:
                print("📈 System load information:")
                print(f"   {load_result.stdout.strip()}")
                
                # Parse load average
                load_line = load_result.stdout.strip()
                if "load average:" in load_line:
                    load_parts = load_line.split("load average:")
                    if len(load_parts) > 1:
                        load_values = load_parts[1].strip().split(", ")
                        if len(load_values) >= 3:
                            load_1min = float(load_values[0])
                            load_5min = float(load_values[1])
                            load_15min = float(load_values[2])
                            
                            print("📊 Load average analysis:")
                            print(f"   1 minute:  {load_1min:.2f}")
                            print(f"   5 minutes: {load_5min:.2f}")
                            print(f"   15 minutes: {load_15min:.2f}")
                            
                            # Evaluar carga del sistema
                            cpu_cores = os.cpu_count() or 1
                            if load_1min > cpu_cores * 2:
                                print("⚠️  High system load detected")
                                issues_found += 1
                            elif load_1min > cpu_cores:
                                print("⚠️  Moderate system load detected")
                            else:
                                print("✅ System load is normal")
            else:
                print("⚠️  Could not get system load information")
        except Exception as e:
            print(f"⚠️  Could not check system load: {e}")
        
        # Step 3: Check memory usage
        print("\n💾 Step 3: Checking memory usage...")
        total_checks += 1
        
        try:
            mem_result = subprocess.run("free -h", shell=True, capture_output=True, text=True)
            if mem_result.returncode == 0:
                print("💾 Memory usage:")
                print(mem_result.stdout.strip())
                
                # Parse memory info for analysis
                mem_lines = mem_result.stdout.strip().split('\n')
                if len(mem_lines) >= 2:
                    mem_parts = mem_lines[1].split()
                    if len(mem_parts) >= 3:
                        try:
                            total_mem = mem_parts[1]
                            used_mem = mem_parts[2]
                            print(f"📊 Total memory: {total_mem}")
                            print(f"📊 Used memory: {used_mem}")
                        except:
                            pass
            else:
                print("⚠️  Could not get memory information")
        except Exception as e:
            print(f"⚠️  Could not check memory usage: {e}")
        
        # Step 4: Check disk space
        print("\n💿 Step 4: Checking disk space...")
        total_checks += 1
        
        try:
            disk_result = subprocess.run("df -h /", shell=True, capture_output=True, text=True)
            if disk_result.returncode == 0:
                print("💿 Root filesystem disk usage:")
                print(disk_result.stdout.strip())
                
                # Parse disk usage for analysis
                disk_lines = disk_result.stdout.strip().split('\n')
                if len(disk_lines) >= 2:
                    disk_parts = disk_lines[1].split()
                    if len(disk_parts) >= 5:
                        try:
                            usage_percent = disk_parts[4].replace('%', '')
                            usage_int = int(usage_percent)
                            
                            print(f"📊 Disk usage: {usage_percent}%")
                            if usage_int > 90:
                                print("🚨 CRITICAL: Disk space is critically low!")
                                issues_found += 1
                            elif usage_int > 80:
                                print("⚠️  WARNING: Disk space is getting low")
                                issues_found += 1
                            elif usage_int > 70:
                                print("⚠️  NOTICE: Disk space usage is moderate")
                            else:
                                print("✅ Disk space usage is normal")
                        except:
                            pass
            else:
                print("⚠️  Could not get disk space information")
        except Exception as e:
            print(f"⚠️  Could not check disk space: {e}")
        
        # Step 5: Check for system errors in logs
        print("\n📋 Step 5: Checking recent system errors...")
        total_checks += 1
        
        try:
            # Check journal for recent errors
            error_result = subprocess.run("journalctl -p err --since '1 hour ago' --no-pager | head -10", 
                                        shell=True, capture_output=True, text=True)
            if error_result.returncode == 0 and error_result.stdout.strip():
                error_lines = error_result.stdout.strip().split('\n')
                error_count = len(error_lines)
                
                if error_count > 0:
                    print(f"⚠️  Found {error_count} recent error messages:")
                    print("=" * 60)
                    
                    for i, error in enumerate(error_lines[:5], 1):  # Show first 5
                        print(f"   {i:2d}. {error[:100]}...")
                    
                    if error_count > 5:
                        print(f"   ... and {error_count - 5} more errors")
                    
                    print("=" * 60)
                    issues_found += 1
                else:
                    print("✅ No recent error messages found")
            else:
                print("✅ No recent error messages found")
        except Exception as e:
            print(f"⚠️  Could not check system logs: {e}")
        
        # Step 6: Check network connectivity
        print("\n🌐 Step 6: Checking network connectivity...")
        total_checks += 1
        
        try:
            # Test basic connectivity
            ping_result = subprocess.run("ping -c 1 -W 3 8.8.8.8", shell=True, capture_output=True, text=True)
            if ping_result.returncode == 0:
                print("✅ Network connectivity: OK")
                print("🌐 Internet connection is working")
            else:
                print("❌ Network connectivity: FAILED")
                print("🌐 Internet connection is not working")
                issues_found += 1
        except Exception as e:
            print(f"⚠️  Could not check network connectivity: {e}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🏥 SYSTEM HEALTH CHECK SUMMARY")
        print("=" * 60)
        
        if issues_found == 0:
            print("🎉 EXCELLENT! All health checks passed")
            print("✅ Your system is in optimal condition")
            print("💡 Continue with regular maintenance schedule")
        elif issues_found <= 2:
            print("⚠️  GOOD with minor issues detected")
            print(f"📊 Issues found: {issues_found}/{total_checks}")
            print("💡 Some issues were detected but they're not critical")
            print("💡 Consider investigating the issues above")
        else:
            print("🚨 ATTENTION REQUIRED! Multiple issues detected")
            print(f"📊 Issues found: {issues_found}/{total_checks}")
            print("💡 Several system issues were detected")
            print("💡 Review the issues above and take appropriate action")
        
        print("=" * 60)
        print()
        
        # Log the overall result
        overall_success = issues_found == 0
        self.log_action(f"System health check: {issues_found} issues found", success=overall_success)
        
        return overall_success

    def check_disk_usage(self):
        """Check disk usage with comprehensive analysis and enhanced visual feedback"""
        print("💾 Starting disk usage analysis...")
        print("=" * 60)
        print("💿 Arch Linux Disk Usage Analysis")
        print("=" * 60)
        
        # Step 1: Check overall disk usage
        print("💿 Step 1: Checking overall disk usage...")
        print("🔍 Analyzing filesystem space...")
        
        try:
            df_result = subprocess.run("df -h", shell=True, capture_output=True, text=True)
            if df_result.returncode == 0:
                print("📊 Filesystem disk usage:")
                print(df_result.stdout.strip())
                
                # Parse and analyze disk usage
                df_lines = df_result.stdout.strip().split('\n')
                critical_partitions = []
                
                for line in df_lines[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 6:
                        filesystem = parts[0]
                        size = parts[1]
                        used = parts[2]
                        available = parts[3]
                        usage_percent = parts[4]
                        mount_point = parts[5]
                        
                        # Check for critical usage
                        try:
                            usage_int = int(usage_percent.replace('%', ''))
                            if usage_int > 90:
                                critical_partitions.append((mount_point, usage_percent, "CRITICAL"))
                            elif usage_int > 80:
                                critical_partitions.append((mount_point, usage_percent, "WARNING"))
                        except:
                            pass
                
                if critical_partitions:
                    print("\n⚠️  Disk space alerts:")
                    for partition, usage, level in critical_partitions:
                        icon = "🚨" if level == "CRITICAL" else "⚠️"
                        print(f"   {icon} {partition}: {usage} ({level})")
                else:
                    print("✅ All filesystems have adequate space")
            else:
                print("⚠️  Could not get disk usage information")
        except Exception as e:
            print(f"⚠️  Could not check disk usage: {e}")
        
        # Step 2: Check home directory usage
        print("\n🏠 Step 2: Checking home directory usage...")
        print("🔍 Analyzing user files and directories...")
        
        try:
            home_dir = Path.home()
            print(f"🏠 Home directory: {home_dir}")
            
            # Get home directory size
            du_result = subprocess.run(f"du -sh {home_dir}", shell=True, capture_output=True, text=True)
            if du_result.returncode == 0:
                home_size = du_result.stdout.strip().split()[0]
                print(f"💾 Total home directory size: {home_size}")
            
            # Check large directories in home
            print("\n📁 Large directories in home:")
            large_dirs_result = subprocess.run(f"du -sh {home_dir}/* 2>/dev/null | sort -hr | head -10", 
                                            shell=True, capture_output=True, text=True)
            if large_dirs_result.returncode == 0 and large_dirs_result.stdout.strip():
                large_dirs = large_dirs_result.stdout.strip().split('\n')
                for i, dir_info in enumerate(large_dirs, 1):
                    if dir_info.strip():
                        print(f"   {i:2d}. {dir_info}")
            else:
                print("   No large directories found")
                
        except Exception as e:
            print(f"⚠️  Could not check home directory: {e}")
        
        # Step 3: Check package cache size
        print("\n📦 Step 3: Checking package cache size...")
        print("🔍 Analyzing pacman cache...")
        
        try:
            cache_result = subprocess.run("du -sh /var/cache/pacman/pkg", shell=True, capture_output=True, text=True)
            if cache_result.returncode == 0:
                cache_size = cache_result.stdout.strip().split()[0]
                print(f"📦 Package cache size: {cache_size}")
                
                # Check if cache is large
                try:
                    if 'G' in cache_size:
                        size_gb = float(cache_size.replace('G', ''))
                        if size_gb > 5:
                            print("⚠️  Package cache is quite large")
                            print("💡 Consider running: sudo pacman -Sc")
                        elif size_gb > 2:
                            print("⚠️  Package cache is moderately large")
                        else:
                            print("✅ Package cache size is reasonable")
                    elif 'M' in cache_size:
                        size_mb = float(cache_size.replace('M', ''))
                        if size_mb > 500:
                            print("⚠️  Package cache is moderately large")
                        else:
                            print("✅ Package cache size is reasonable")
                except:
                    pass
            else:
                print("⚠️  Could not check package cache size")
        except Exception as e:
            print(f"⚠️  Could not check package cache: {e}")
        
        # Step 4: Check log files size
        print("\n📋 Step 4: Checking log files size...")
        print("🔍 Analyzing system logs...")
        
        try:
            # Check systemd journal size
            journal_result = subprocess.run("journalctl --disk-usage", shell=True, capture_output=True, text=True)
            if journal_result.returncode == 0:
                print("📋 Systemd journal disk usage:")
                print(journal_result.stdout.strip())
                
                # Parse journal size
                journal_output = journal_result.stdout.strip()
                if "Archived and active journals take up" in journal_output:
                    try:
                        size_part = journal_output.split("Archived and active journals take up")[1].split()[0]
                        print(f"📊 Journal size: {size_part}")
                        
                        # Check if logs are large
                        if 'G' in size_part:
                            size_gb = float(size_part.replace('G', ''))
                            if size_gb > 1:
                                print("⚠️  System logs are quite large")
                                print("💡 Consider running: sudo journalctl --vacuum-time=1w")
                            else:
                                print("✅ System logs size is reasonable")
                    except:
                        pass
            else:
                print("⚠️  Could not check systemd journal size")
        except Exception as e:
            print(f"⚠️  Could not check log files: {e}")
        
        # Step 5: Check temporary files
        print("\n🗂️  Step 5: Checking temporary files...")
        print("🔍 Analyzing /tmp and /var/tmp...")
        
        try:
            # Check /tmp size
            tmp_result = subprocess.run("du -sh /tmp", shell=True, capture_output=True, text=True)
            if tmp_result.returncode == 0:
                tmp_size = tmp_result.stdout.strip().split()[0]
                print(f"🗂️  /tmp directory size: {tmp_size}")
            
            # Check /var/tmp size
            var_tmp_result = subprocess.run("du -sh /var/tmp", shell=True, capture_output=True, text=True)
            if var_tmp_result.returncode == 0:
                var_tmp_size = var_tmp_result.stdout.strip().split()[0]
                print(f"🗂️  /var/tmp directory size: {var_tmp_size}")
                
        except Exception as e:
            print(f"⚠️  Could not check temporary files: {e}")
        
        # Step 6: Generate recommendations
        print("\n💡 Step 6: Disk usage recommendations...")
        print("🔍 Analyzing and providing suggestions...")
        
        recommendations = []
        
        # Check if we have critical partitions
        if 'critical_partitions' in locals() and critical_partitions:
            recommendations.append("🚨 Free up space on critical partitions immediately")
        
        # Check package cache
        if 'cache_size' in locals():
            try:
                if 'G' in cache_size and float(cache_size.replace('G', '')) > 2:
                    recommendations.append("📦 Clean package cache: sudo pacman -Sc")
            except:
                pass
        
        # Check logs
        if 'journal_output' in locals() and 'G' in journal_output:
            try:
                size_part = journal_output.split("Archived and active journals take up")[1].split()[0]
                if 'G' in size_part and float(size_part.replace('G', '')) > 1:
                    recommendations.append("📋 Clean system logs: sudo journalctl --vacuum-time=1w")
            except:
                pass
        
        if recommendations:
            print("💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("✅ No immediate actions required")
            print("💡 Your disk usage is well managed")
        
        # Final summary
        print("\n" + "=" * 60)
        print("💾 DISK USAGE ANALYSIS SUMMARY")
        print("=" * 60)
        
        if 'critical_partitions' in locals() and critical_partitions:
            critical_count = sum(1 for _, _, level in critical_partitions if level == "CRITICAL")
            warning_count = sum(1 for _, _, level in critical_partitions if level == "WARNING")
            
            if critical_count > 0:
                print("🚨 CRITICAL: Immediate action required")
                print(f"📊 Critical partitions: {critical_count}")
                print(f"📊 Warning partitions: {warning_count}")
            elif warning_count > 0:
                print("⚠️  WARNING: Monitor disk space")
                print(f"📊 Warning partitions: {warning_count}")
            else:
                print("✅ GOOD: Disk space is adequate")
        else:
            print("✅ EXCELLENT: All filesystems have adequate space")
        
        print("=" * 60)
        print()
        
        return True

    def full_maintenance(self):
        """Run full maintenance tasks with comprehensive progress tracking and error handling"""
        import time
        from datetime import datetime
        
        start_time = time.time()
        
        # Banner principal
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                    🚀 ARCH LINUX FULL MAINTENANCE                          ║")
        print("║                     Comprehensive System Maintenance                       ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print()
        
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  System: Arch Linux")
        print(f"👤 User: {os.getenv('USER', 'Unknown')}")
        print("=" * 80)
        print()

        # Definir tareas con información detallada
        tasks = [
            {
                "name": "System Update",
                "func": self.update_system,
                "description": "Update system packages and sync databases",
                "critical": True,
                "icon": "📦"
            },
            {
                "name": "Clean Packages Cache",
                "func": self.clean_packages_cache,
                "description": "Remove old packages and orphaned dependencies",
                "critical": False,
                "icon": "🧹"
            },
            {
                "name": "Update AUR Packages",
                "func": self.update_aur_packages,
                "description": "Update packages from AUR repositories",
                "critical": False,
                "icon": "📦"
            },
            {
                "name": "Clean Systemd Logs",
                "func": self.clean_systemd_logs,
                "description": "Clean old systemd journal logs",
                "critical": False,
                "icon": "📋"
            },
            {
                "name": "Update Locate Database",
                "func": self.update_locate_database,
                "description": "Update file location database",
                "critical": False,
                "icon": "🔍"
            },
            {
                "name": "Check System Health",
                "func": self.check_system_health,
                "description": "Verify system services and overall health",
                "critical": True,
                "icon": "🏥"
            }
        ]

        success_count = 0
        failed_tasks = []
        warnings = []
        
        # Mostrar resumen de tareas
        print("📋 MAINTENANCE TASKS OVERVIEW")
        print("=" * 80)
        for i, task in enumerate(tasks, 1):
            critical_mark = "🔴" if task["critical"] else "🟡"
            status_icon = "⚡" if task["critical"] else "📝"
            print(f"  {i:2d}. {critical_mark} {task['icon']} {task['name']}")
            print(f"      {status_icon} {task['description']}")
            print()
        
        print("🔴 Critical tasks (must succeed for system stability)")
        print("🟡 Optional tasks (can fail without affecting core functionality)")
        print("=" * 80)
        print()

        # Ejecutar tareas
        for i, task in enumerate(tasks, 1):
            task_name = task["name"]
            task_func = task["func"]
            is_critical = task["critical"]
            task_icon = task["icon"]
            
            # Header de la tarea
            print(f"🔄 TASK {i}/{len(tasks)}: {task_icon} {task_name}")
            print(f"📝 {task['description']}")
            print(f"🔴 Critical: {'Yes' if is_critical else 'No'}")
            print("-" * 80)
            
            try:
                task_start = time.time()
                result = task_func()
                task_duration = time.time() - task_start
                
                if result:
                    success_count += 1
                    print(f"✅ {task_icon} {task_name} completed successfully in {task_duration:.1f}s")
                    self.log_action(f"FULL_MAINTENANCE: {task_name} - SUCCESS", success=True)
                else:
                    print(f"❌ {task_icon} {task_name} failed after {task_duration:.1f}s")
                    failed_tasks.append(task_name)
                    self.log_action(f"FULL_MAINTENANCE: {task_name} - FAILED", success=False)
                    
                    if is_critical:
                        print(f"⚠️  {task_name} is a critical task. Consider reviewing the error.")
                        warnings.append(f"Critical task '{task_name}' failed")
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  Maintenance interrupted by user during {task_name}")
                self.log_action(f"FULL_MAINTENANCE: INTERRUPTED during {task_name}", success=False)
                print("\n🔄 You can resume maintenance later or run individual tasks.")
                return False
                
            except Exception as e:
                print(f"❌ Unexpected error in {task_name}: {e}")
                failed_tasks.append(task_name)
                self.log_action(f"FULL_MAINTENANCE: {task_name} - ERROR: {e}", success=False)
                
            print()

        # Calcular estadísticas
        total_time = time.time() - start_time
        success_rate = (success_count / len(tasks)) * 100
        
        # Mostrar resumen final con diseño mejorado
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                           📊 MAINTENANCE SUMMARY                           ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print()
        
        # Barra de progreso visual
        progress_bar_length = 50
        filled_length = int(progress_bar_length * success_rate / 100)
        progress_bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
        
        print(f"📈 Overall Progress: [{progress_bar}] {success_rate:.1f}%")
        print()
        
        # Estadísticas detalladas
        print("📊 EXECUTION STATISTICS")
        print("=" * 60)
        print(f"⏱️  Total execution time: {total_time:.1f} seconds")
        print(f"📋 Total tasks: {len(tasks)}")
        print(f"✅ Successful tasks: {success_count}")
        print(f"❌ Failed tasks: {len(failed_tasks)}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        print()
        
        # Estado de tareas críticas
        critical_tasks = [t for t in tasks if t["critical"]]
        critical_success = sum(1 for t in critical_tasks if t["name"] not in failed_tasks)
        print("🔴 CRITICAL TASKS STATUS")
        print("=" * 60)
        print(f"📋 Critical tasks: {len(critical_tasks)}")
        print(f"✅ Successful: {critical_success}")
        print(f"❌ Failed: {len(critical_tasks) - critical_success}")
        print()
        
        if failed_tasks:
            print("🔴 FAILED TASKS")
            print("=" * 60)
            for task in failed_tasks:
                print(f"   • {task}")
            print()
            
        if warnings:
            print("⚠️  WARNINGS")
            print("=" * 60)
            for warning in warnings:
                print(f"   • {warning}")
            print()
        
        # Recomendaciones basadas en resultados
        print("💡 RECOMMENDATIONS")
        print("=" * 60)
        if success_rate == 100:
            print("   🎉 EXCELLENT! All maintenance tasks completed successfully.")
            print("   💡 Your system is in optimal condition.")
            print("   💡 Continue with regular maintenance schedule.")
        elif success_rate >= 80:
            print("   ✅ GOOD! Most maintenance tasks completed successfully.")
            print("   🔍 Review failed tasks to ensure system stability.")
            print("   💡 Consider running failed tasks individually.")
        elif success_rate >= 60:
            print("   ⚠️  FAIR. Some critical tasks may need attention.")
            print("   🔧 Consider running failed tasks individually.")
            print("   💡 Check system logs for error details.")
        else:
            print("   ❌ POOR. Multiple critical tasks failed.")
            print("   🚨 Review system logs and consider manual intervention.")
            print("   💡 Some tasks may require administrator attention.")
        
        print("=" * 60)
        
        # Mostrar información del sistema
        if success_count > 0:
            print("\n🔍 SYSTEM INFORMATION")
            print("=" * 60)
            self.check_disk_usage()
            print()
            
            print("📁 LOG FILE INFORMATION")
            print("=" * 60)
            print(f"📁 Location: {self.log_file}")
            
            # Mostrar tamaño del log
            try:
                log_size = os.path.getsize(self.log_file)
                print(f"📊 Size: {log_size / 1024:.1f} KB")
                
                # Mostrar estadísticas del log
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        success_logs = sum(1 for line in lines if "SUCCESS" in line)
                        failed_logs = sum(1 for line in lines if "FAILED" in line)
                        print(f"📝 Total entries: {len(lines)}")
                        print(f"✅ Success entries: {success_logs}")
                        print(f"❌ Failed entries: {failed_logs}")
            except:
                pass
        
        print("\n" + "=" * 80)
        print("🎉 FULL MAINTENANCE PROCESS COMPLETED!")
        print("=" * 80)
        return success_count == len(tasks)

    def install_script(self):
        """Install the maintenance script to the system with comprehensive setup"""
        print("🚀 Starting Arch Linux Maintenance Script installation...")
        print("=" * 60)
        print("📦 Installation and Setup Process")
        print("=" * 60)
        
        # Step 1: Check if running as root
        if os.geteuid() == 0:
            print("❌ This script should not be run as root")
            print("💡 Please run as a regular user with sudo privileges")
            return False
        
        # Step 2: Check dependencies
        print("🔍 Step 1: Checking system dependencies...")
        dependencies = ["python3", "sudo"]
        missing_deps = []
        
        for dep in dependencies:
            if not shutil.which(dep):
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
            print("📦 Installing missing dependencies...")
            
            try:
                install_cmd = f"sudo pacman -S --noconfirm {' '.join(missing_deps)}"
                success = self.run_command(install_cmd, f"Installing dependencies: {', '.join(missing_deps)}")
                if not success:
                    print("❌ Failed to install dependencies")
                    return False
            except Exception as e:
                print(f"❌ Error installing dependencies: {e}")
                return False
        else:
            print("✅ All dependencies are available")
        
        # Step 3: Create installation directories
        print("\n📁 Step 2: Creating installation directories...")
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.config_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {self.install_dir}")
            print(f"✅ Created: {self.config_dir}")
        except Exception as e:
            print(f"❌ Failed to create directories: {e}")
            return False
        
        # Step 4: Copy main script
        print("\n📋 Step 3: Installing main script...")
        try:
            current_script = Path(__file__).resolve()
            target_script = self.install_dir / self.script_name
            
            shutil.copy2(current_script, target_script)
            
            # Make executable
            target_script.chmod(target_script.stat().st_mode | stat.S_IEXEC)
            
            print(f"✅ Script installed: {target_script}")
            print(f"✅ Made executable")
        except Exception as e:
            print(f"❌ Failed to install script: {e}")
            return False
        
        # Step 5: Create short command symlink
        print("\n🔗 Step 4: Creating short command link...")
        try:
            short_link = self.install_dir / self.short_command
            if short_link.exists():
                short_link.unlink()
            
            short_link.symlink_to(target_script)
            print(f"✅ Short command created: {short_link}")
        except Exception as e:
            print(f"⚠️  Failed to create short command: {e}")
        
        # Step 6: Add to PATH
        print("\n🌐 Step 5: Adding to system PATH...")
        try:
            shell_rc = self._get_shell_rc()
            if shell_rc and shell_rc.exists():
                self._add_to_path(shell_rc)
                print(f"✅ PATH updated in: {shell_rc}")
            else:
                print("⚠️  Could not determine shell configuration file")
        except Exception as e:
            print(f"⚠️  Failed to update PATH: {e}")
        
        # Step 7: Configure automatic reminders
        print("\n⏰ Step 6: Configuring automatic reminders...")
        reminder_choice = self._configure_reminders()
        if reminder_choice:
            self._setup_reminders(reminder_choice)
        
        # Step 8: Installation summary
        print("\n" + "=" * 60)
        print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("📁 Installation locations:")
        print(f"   🚀 Main script: {self.install_dir / self.script_name}")
        print(f"   🔗 Short command: {self.install_dir / self.short_command}")
        print(f"   ⚙️  Configuration: {self.config_dir}")
        print()
        print("💻 Available commands:")
        print(f"   {self.script_name} --help     (Show help)")
        print(f"   {self.script_name} --full     (Complete maintenance)")
        print(f"   {self.script_name}            (Interactive menu)")
        print(f"   {self.short_command} --help    (Short command)")
        print()
        print("⏰ Reminder configured: {reminder_choice}")
        print()
        print("💡 To complete installation:")
        print("   • Restart your terminal")
        print("   • Or run: source ~/.zshrc (or ~/.bashrc)")
        print()
        
        self.log_action("Script installation completed successfully", success=True)
        return True

    def uninstall_script(self):
        """Uninstall the maintenance script from the system"""
        print("🗑️  Starting Arch Linux Maintenance Script uninstallation...")
        print("=" * 60)
        print("🧹 Uninstallation and Cleanup Process")
        print("=" * 60)
        
        # Step 1: Confirm uninstallation
        print("⚠️  This will remove the Arch Linux Maintenance Script from your system")
        print("📁 All configuration files and reminders will be deleted")
        print()
        
        try:
            response = input("Are you sure you want to uninstall? (y/N): ").strip()
            if response.lower() != 'y':
                print("❌ Uninstallation cancelled")
                return False
        except KeyboardInterrupt:
            print("\n❌ Uninstallation cancelled")
            return False
        
        # Step 2: Remove main script
        print("\n🗑️  Step 1: Removing main script...")
        try:
            main_script = self.install_dir / self.script_name
            if main_script.exists():
                main_script.unlink()
                print(f"✅ Removed: {main_script}")
            else:
                print("ℹ️  Main script not found")
        except Exception as e:
            print(f"⚠️  Failed to remove main script: {e}")
        
        # Step 3: Remove short command
        print("\n🔗 Step 2: Removing short command...")
        try:
            short_link = self.install_dir / self.short_command
            if short_link.exists():
                short_link.unlink()
                print(f"✅ Removed: {short_link}")
            else:
                print("ℹ️  Short command not found")
        except Exception as e:
            print(f"⚠️  Failed to remove short command: {e}")
        
        # Step 4: Remove configuration
        print("\n⚙️  Step 3: Removing configuration...")
        try:
            if self.config_dir.exists():
                shutil.rmtree(self.config_dir)
                print(f"✅ Removed: {self.config_dir}")
            else:
                print("ℹ️  Configuration directory not found")
        except Exception as e:
            print(f"⚠️  Failed to remove configuration: {e}")
        
        # Step 5: Remove reminder file
        print("\n⏰ Step 4: Removing reminder file...")
        try:
            reminder_file = Path.home() / ".arch_maintenance_reminder"
            if reminder_file.exists():
                reminder_file.unlink()
                print(f"✅ Removed: {reminder_file}")
            else:
                print("ℹ️  Reminder file not found")
        except Exception as e:
            print(f"⚠️  Failed to remove reminder file: {e}")
        
        # Step 6: Clean shell configuration
        print("\n🐚 Step 5: Cleaning shell configuration...")
        try:
            shell_rc = self._get_shell_rc()
            if shell_rc and shell_rc.exists():
                self._clean_shell_config(shell_rc)
                print(f"✅ Cleaned: {shell_rc}")
            else:
                print("ℹ️  Shell configuration file not found")
        except Exception as e:
            print(f"⚠️  Failed to clean shell configuration: {e}")
        
        # Step 7: Uninstallation summary
        print("\n" + "=" * 60)
        print("🎉 UNINSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ All files and configurations have been removed")
        print()
        print("💡 To complete uninstallation:")
        print("   • Restart your terminal")
        print("   • Or run: source ~/.zshrc (or ~/.bashrc)")
        print()
        print("👋 Thank you for using Arch Linux Maintenance Script!")
        print()
        
        self.log_action("Script uninstallation completed successfully", success=True)
        return True

    def _get_shell_rc(self):
        """Get the appropriate shell configuration file path"""
        shell = os.getenv('SHELL', '')
        home = Path.home()
        
        if 'zsh' in shell:
            return home / '.zshrc'
        elif 'bash' in shell:
            return home / '.bashrc'
        else:
            return home / '.profile'

    def _add_to_path(self, shell_rc):
        """Add the installation directory to PATH in shell configuration"""
        try:
            with open(shell_rc, 'r') as f:
                content = f.read()
            
            # Check if already added
            if str(self.install_dir) in content:
                return
            
            # Add to PATH
            path_line = f'\n# Arch Linux Maintenance Script\nexport PATH="{self.install_dir}:$PATH"\n'
            
            with open(shell_rc, 'a') as f:
                f.write(path_line)
                
        except Exception as e:
            print(f"⚠️  Failed to update PATH: {e}")

    def _clean_shell_config(self, shell_rc):
        """Clean shell configuration file from maintenance script entries"""
        try:
            with open(shell_rc, 'r') as f:
                lines = f.readlines()
            
            # Remove maintenance script related lines
            cleaned_lines = []
            skip_next = 0
            
            for line in lines:
                if '# Arch Linux Maintenance Script' in line:
                    skip_next = 2
                    continue
                elif '# Arch Linux Maintenance Reminder' in line:
                    skip_next = 4
                    continue
                elif skip_next > 0:
                    skip_next -= 1
                    continue
                else:
                    cleaned_lines.append(line)
            
            # Write cleaned content
            with open(shell_rc, 'w') as f:
                f.writelines(cleaned_lines)
                
        except Exception as e:
            print(f"⚠️  Failed to clean shell configuration: {e}")

    def _configure_reminders(self):
        """Configure automatic maintenance reminders"""
        print("⏰ Configure automatic maintenance reminders:")
        print("1. Weekly (recommended)")
        print("2. Bi-weekly (every 2 weeks)")
        print("3. Monthly (every 4 weeks)")
        print("4. Custom (specify days)")
        print("5. No automatic reminders")
        print()
        
        try:
            choice = input("Select an option (1-5): ").strip()
            
            if choice == '1':
                return "Weekly (7 days)"
            elif choice == '2':
                return "Bi-weekly (14 days)"
            elif choice == '3':
                return "Monthly (28 days)"
            elif choice == '4':
                try:
                    days = input("Specify number of days between reminders: ").strip()
                    days_int = int(days)
                    return f"Custom ({days_int} days)"
                except ValueError:
                    print("⚠️  Invalid input, using weekly reminders")
                    return "Weekly (7 days)"
            elif choice == '5':
                return "Disabled"
            else:
                print("⚠️  Invalid option, using weekly reminders")
                return "Weekly (7 days)"
        except KeyboardInterrupt:
            print("\n⚠️  Using default weekly reminders")
            return "Weekly (7 days)"

    def _setup_reminders(self, reminder_type):
        """Setup automatic maintenance reminders"""
        if reminder_type == "Disabled":
            print("ℹ️  Automatic reminders disabled")
            return
        
        try:
            # Parse reminder type to get days
            if "Weekly" in reminder_type:
                days = 7
            elif "Bi-weekly" in reminder_type:
                days = 14
            elif "Monthly" in reminder_type:
                days = 28
            elif "Custom" in reminder_type:
                days = int(reminder_type.split('(')[1].split()[0])
            else:
                days = 7
            
            # Create reminder script
            reminder_script = self.config_dir / "maintenance-reminder.sh"
            
            reminder_content = f'''#!/bin/bash
# Arch Linux Maintenance Reminder
# Generated by installer

MAINTENANCE_LOG="$HOME/.arch_maintenance.log"
REMINDER_FILE="$HOME/.arch_maintenance_reminder"
REMINDER_DAYS={days}

# Check if reminder should be shown
should_show_reminder() {{
    if [ ! -f "$MAINTENANCE_LOG" ]; then
        return 1
    fi
    
    if [ -f "$REMINDER_FILE" ]; then
        LAST_REMINDER=$(cat "$REMINDER_FILE")
        CURRENT_DATE=$(date +%Y-%m-%d)
        
        LAST_TIMESTAMP=$(date -d "$LAST_REMINDER" +%s 2>/dev/null)
        CURRENT_TIMESTAMP=$(date +%s)
        DAYS_DIFF=$(( (CURRENT_TIMESTAMP - LAST_TIMESTAMP) / 86400 ))
        
        if [ $DAYS_DIFF -lt $REMINDER_DAYS ]; then
            return 1
        fi
    fi
    
    return 0
}}

# Show reminder
show_reminder() {{
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    MAINTENANCE REMINDER                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "⏰ It's time for your {reminder_type} Arch Linux maintenance!"
    echo "💡 This helps keep your system secure and optimized."
    echo ""
    echo "Options:"
    echo "   🚀 archm-maintenance --full     (Complete maintenance)"
    echo "   📋 archm-maintenance            (Interactive menu)"
    echo "   📊 archm-maintenance --status  (Check system status)"
    echo ""
    
    read -p "🔄 Run maintenance now? (Y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "⏰ No problem! You can run it later with: archm-maintenance --full"
        echo "💡 Reminder will appear again in $REMINDER_DAYS days."
    else
        echo "🚀 Starting maintenance..."
        archm-maintenance --full
    fi
    
    echo ""
}}

# Update reminder timestamp
update_reminder_timestamp() {{
    date +%Y-%m-%d > "$REMINDER_FILE"
}}

# Main function
main() {{
    if should_show_reminder; then
        show_reminder
        update_reminder_timestamp
    fi
}}

# Execute only if called directly
if [[ "${{BASH_SOURCE[0]}}" == "${{0}}" ]]; then
    main
fi
'''
            
            with open(reminder_script, 'w') as f:
                f.write(reminder_content)
            
            # Make executable
            reminder_script.chmod(reminder_script.stat().st_mode | stat.S_IEXEC)
            
            # Add to shell configuration
            shell_rc = self._get_shell_rc()
            if shell_rc and shell_rc.exists():
                self._add_reminder_to_shell(shell_rc)
            
            print(f"✅ Reminders configured: {reminder_type}")
            
        except Exception as e:
            print(f"⚠️  Failed to setup reminders: {e}")

    def _add_reminder_to_shell(self, shell_rc):
        """Add reminder script to shell configuration"""
        try:
            with open(shell_rc, 'r') as f:
                content = f.read()
            
            # Check if already added
            if "maintenance-reminder.sh" in content:
                return
            
            # Add reminder configuration
            reminder_config = f'''
# Arch Linux Maintenance Reminder
if [ -f ~/.config/arch-maintenance/maintenance-reminder.sh ]; then
    source ~/.config/arch-maintenance/maintenance-reminder.sh
fi
'''
            
            with open(shell_rc, 'a') as f:
                f.write(reminder_config)
                
        except Exception as e:
            print(f"⚠️  Failed to add reminder to shell: {e}")

    def is_installed(self):
        """Check if the maintenance script is installed in the system"""
        main_script = self.install_dir / self.script_name
        short_command = self.install_dir / self.short_command
        config_exists = self.config_dir.exists()
        
        return {
            "installed": main_script.exists(),
            "main_script": str(main_script) if main_script.exists() else None,
            "short_command": str(short_command) if short_command.exists() else None,
            "config_dir": str(self.config_dir) if config_exists else None,
            "in_path": str(self.install_dir) in os.getenv('PATH', '')
        }

    def get_installation_status(self):
        """Get detailed installation status information"""
        status = self.is_installed()
        
        print("🔧 Installation Status")
        print("=" * 50)
        
        if status["installed"]:
            print("✅ Script is installed")
            print(f"   📁 Main script: {status['main_script']}")
            
            if status["short_command"]:
                print(f"   🔗 Short command: {status['short_command']}")
            else:
                print("   ❌ Short command: Not found")
            
            if status["config_dir"]:
                print(f"   ⚙️  Configuration: {status['config_dir']}")
            else:
                print("   ❌ Configuration: Not found")
            
            if status["in_path"]:
                print("   🌐 PATH: Updated")
            else:
                print("   ⚠️  PATH: Not updated (restart terminal or source shell config)")
            
            # Check reminder configuration
            reminder_script = self.config_dir / "maintenance-reminder.sh"
            if reminder_script.exists():
                print("   ⏰ Reminders: Configured")
            else:
                print("   ⏰ Reminders: Not configured")
                
        else:
            print("❌ Script is not installed")
            print("💡 Use --install to install the script")
        
        print("=" * 50)
        return status


def main():
    """Main function to run the Arch Linux maintenance script with enhanced features and interactive CLI menu"""
    import sys
    from pathlib import Path
    
    # Configurar el parser de argumentos con más opciones y mejor descripción
    parser = argparse.ArgumentParser(
        description="🚀 Arch Linux Maintenance Script - Comprehensive system maintenance tool",
        epilog="💡 Use --full for complete system maintenance or combine specific tasks as needed.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Argumentos principales
    parser.add_argument(
        "--full", 
        action="store_true", 
        help="🚀 Perform complete system maintenance (recommended for regular maintenance)"
    )
    
    # Argumentos de actualización
    update_group = parser.add_argument_group("📦 Update Operations")
    update_group.add_argument(
        "--update", 
        action="store_true", 
        help="🔄 Update system packages using pacman"
    )
    update_group.add_argument(
        "--aur", 
        action="store_true", 
        help="📦 Update AUR packages using yay"
    )
    update_group.add_argument(
        "--force", 
        action="store_true", 
        help="⚠️  Force updates even if there are potential conflicts (use with caution)"
    )
    
    # Argumentos de limpieza
    clean_group = parser.add_argument_group("🧹 Cleanup Operations")
    clean_group.add_argument(
        "--clean", 
        action="store_true", 
        help="🗑️  Clean package cache and remove orphaned packages"
    )
    clean_group.add_argument(
        "--logs", 
        action="store_true", 
        help="📋 Clean systemd journal logs"
    )
    clean_group.add_argument(
        "--aggressive", 
        action="store_true", 
        help="🔥 Aggressive cleanup (removes more old packages and logs)"
    )
    
    # Argumentos de verificación
    check_group = parser.add_argument_group("🔍 System Check Operations")
    check_group.add_argument(
        "--health", 
        action="store_true", 
        help="🏥 Check system health and failed services"
    )
    check_group.add_argument(
        "--disk", 
        action="store_true", 
        help="💾 Check disk usage and large files"
    )
    check_group.add_argument(
        "--locate", 
        action="store_true", 
        help="🔍 Update locate database"
    )
    
    # Argumentos de configuración
    config_group = parser.add_argument_group("⚙️ Configuration Options")
    config_group.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="📝 Enable verbose output with detailed information"
    )
    config_group.add_argument(
        "--dry-run", 
        action="store_true", 
        help="🧪 Show what would be done without actually doing it"
    )
    config_group.add_argument(
        "--log-level", 
        choices=["info", "warning", "error"], 
        default="info",
        help="📊 Set logging level (default: info)"
    )
    
    # Argumentos de información
    info_group = parser.add_argument_group("ℹ️ Information Options")
    info_group.add_argument(
        "--version", 
        action="version", 
        version="Arch Linux Maintenance Script v2.0"
    )
    info_group.add_argument(
        "--status", 
        action="store_true", 
        help="📊 Show current system status and maintenance history"
    )
    
    # Argumentos de instalación
    install_group = parser.add_argument_group("🔧 Installation Options")
    install_group.add_argument(
        "--install", 
        action="store_true", 
        help="🚀 Install the maintenance script to the system"
    )
    install_group.add_argument(
        "--uninstall", 
        action="store_true", 
        help="🗑️  Uninstall the maintenance script from the system"
    )
    install_group.add_argument(
        "--check-install", 
        action="store_true", 
        help="🔍 Check if the script is installed and show installation status"
    )
    
    # Parsear argumentos
    try:
        args = parser.parse_args()
    except SystemExit:
        # Si hay error en argumentos, mostrar ayuda y salir
        parser.print_help()
        sys.exit(1)
    
    # Si no hay argumentos, mostrar menú interactivo
    if not any([args.full, args.update, args.clean, args.aur, args.logs, 
                args.health, args.disk, args.locate, args.status, args.install, args.uninstall, args.check_install]):
        show_interactive_menu()
        return
    
    # Validar argumentos
    if not any([args.full, args.update, args.clean, args.aur, args.logs, 
                args.health, args.disk, args.locate, args.status, args.install, args.uninstall, args.check_install]):
        print("❌ No maintenance operation specified!")
        print("💡 Use --help to see available options")
        print("💡 Use --full for complete maintenance")
        sys.exit(1)
    
    # Crear instancia de mantenimiento
    try:
        maintenance = ArchLinuxMaintenance()
    except Exception as e:
        print(f"❌ Failed to initialize maintenance system: {e}")
        sys.exit(1)
    
    # Configurar logging si se especifica
    if hasattr(maintenance, 'set_log_level'):
        maintenance.set_log_level(args.log_level)
    
    # Mostrar información del sistema si se solicita
    if args.status:
        show_system_status(maintenance)
        return
    
    # Verificar estado de instalación si se solicita
    if args.check_install:
        maintenance.get_installation_status()
        return
    
    # Ejecutar operaciones de instalación/desinstalación
    if args.install:
        success = run_operation("Script Installation", maintenance.install_script)
        if success:
            print("🎉 Installation completed successfully!")
        else:
            print("❌ Installation failed. Check the logs for details.")
        return
    
    if args.uninstall:
        success = run_operation("Script Uninstallation", maintenance.uninstall_script)
        if success:
            print("🎉 Uninstallation completed successfully!")
        else:
            print("❌ Uninstallation failed. Check the logs for details.")
        return
    
    # Ejecutar operaciones de mantenimiento
    show_startup_banner()
    show_system_info()
    
    print("🚀 Arch Linux Maintenance Script")
    print("=" * 50)
    
    # Contador de operaciones exitosas
    success_count = 0
    total_operations = 0
    
    # Función helper para ejecutar operaciones
    def run_operation(operation_name, operation_func, *args, **kwargs):
        nonlocal success_count, total_operations
        total_operations += 1
        
        # Acceder a la variable dry_run del scope externo
        dry_run_mode = getattr(args, 'dry_run', False)
        
        if dry_run_mode:
            print(f"🧪 [DRY RUN] Would execute: {operation_name}")
            return True
        
        try:
            print(f"🔄 Executing: {operation_name}")
            result = operation_func(*args, **kwargs)
            if result:
                success_count += 1
                print(f"✅ {operation_name} completed successfully")
            else:
                print(f"❌ {operation_name} failed")
            return result
        except KeyboardInterrupt:
            print(f"\n⚠️  Operation interrupted: {operation_name}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error in {operation_name}: {e}")
            return False
    
    # Ejecutar operaciones según los argumentos
    try:
        if args.full:
            print("🚀 Starting full maintenance process...")
            success = run_operation("Full Maintenance", maintenance.full_maintenance)
            if success:
                print("🎉 Full maintenance completed successfully!")
            else:
                print("⚠️  Full maintenance completed with some issues")
        else:
            # Ejecutar operaciones individuales
            if args.update:
                run_operation("System Update", maintenance.update_system)
            
            if args.clean:
                run_operation("Package Cache Cleanup", maintenance.clean_packages_cache)
            
            if args.aur:
                run_operation("AUR Package Update", maintenance.update_aur_packages)
            
            if args.logs:
                run_operation("Systemd Logs Cleanup", maintenance.clean_systemd_logs)
            
            if args.locate:
                run_operation("Locate Database Update", maintenance.update_locate_database)
            
            if args.health:
                run_operation("System Health Check", maintenance.check_system_health)
            
            if args.disk:
                run_operation("Disk Usage Check", maintenance.check_disk_usage)
        
        # Mostrar resumen final
        dry_run_mode = getattr(args, 'dry_run', False)
        if not dry_run_mode and total_operations > 0:
            show_final_summary(success_count, total_operations)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Maintenance interrupted by user")
        print("💡 You can resume maintenance later or run individual tasks")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during maintenance: {e}")
        print("💡 Check the logs for more details")
        sys.exit(1)
    
    print("\n🎉 Maintenance script completed!")
    print(f"📁 Log file: {maintenance.log_file}")


def show_interactive_menu():
    """Display an interactive CLI menu for maintenance operations"""
    import os
    import sys
    
    def clear_screen():
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_menu():
        print("📋 Available Maintenance Operations:")
        print("=" * 50)
        print("🚀 1. Full System Maintenance (Recommended)")
        print("📦 2. System Update Only")
        print("📦 3. AUR Packages Update")
        print("🧹 4. Clean Package Cache")
        print("📋 5. Clean Systemd Logs")
        print("🔍 6. Update Locate Database")
        print("🏥 7. Check System Health")
        print("💾 8. Check Disk Usage")
        print("📊 9. Show System Status")
        print("🔧 10. Install Script to System")
        print("🗑️  11. Uninstall Script from System")
        print("🔍 12. Check Installation Status")
        print("❌ 0. Exit")
        print("=" * 50)
    
    def get_user_choice():
        while True:
            try:
                choice = input("🎯 Select an option (0-12): ").strip()
                if choice in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
                    return int(choice)
                else:
                    print("❌ Invalid option. Please select 0-12.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
    
    def execute_choice(choice):
        maintenance = ArchLinuxMaintenance()
        
        if choice == 1:
            print("🚀 Starting full system maintenance...")
            maintenance.full_maintenance()
        elif choice == 2:
            print("📦 Starting system update...")
            maintenance.update_system()
        elif choice == 3:
            print("📦 Starting AUR packages update...")
            maintenance.update_aur_packages()
        elif choice == 4:
            print("🧹 Starting package cache cleanup...")
            maintenance.clean_packages_cache()
        elif choice == 5:
            print("📋 Starting systemd logs cleanup...")
            maintenance.clean_systemd_logs()
        elif choice == 6:
            print("🔍 Starting locate database update...")
            maintenance.update_locate_database()
        elif choice == 7:
            print("🏥 Starting system health check...")
            maintenance.check_system_health()
        elif choice == 8:
            print("💾 Starting disk usage check...")
            maintenance.check_disk_usage()
        elif choice == 9:
            show_system_status(maintenance)
        elif choice == 10:
            print("🔧 Starting script installation...")
            maintenance.install_script()
        elif choice == 11:
            print("🗑️  Starting script uninstallation...")
            maintenance.uninstall_script()
        elif choice == 12:
            print("🔍 Checking installation status...")
            maintenance.get_installation_status()
    
    # Main menu loop
    while True:
        clear_screen()
        show_startup_banner()
        show_system_info()
        print_menu()
        
        choice = get_user_choice()
        
        if choice == 0:
            print("👋 Thank you for using Arch Linux Maintenance!")
            print("💡 Remember to run maintenance regularly for optimal system performance.")
            break
        
        clear_screen()
        print_menu()
        print(f"🔄 Executing option {choice}...")
        print("=" * 50)
        
        try:
            execute_choice(choice)
        except KeyboardInterrupt:
            print("\n⚠️  Operation interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during operation: {e}")
        
        input("\n⏸️  Press Enter to continue...")
    
    print("👋 Goodbye!")


def show_system_status(maintenance):
    """Display system status information"""
    from pathlib import Path
    
    print("📊 System Status Information")
    print("=" * 50)
    print(f"🏠 Home directory: {Path.home()}")
    print(f"📁 Log file: {maintenance.log_file}")
    
    # Verificar si el log existe y mostrar información
    if maintenance.log_file.exists():
        try:
            log_size = maintenance.log_file.stat().st_size
            print(f"📊 Log size: {log_size / 1024:.1f} KB")
            
            # Mostrar últimas entradas del log
            with open(maintenance.log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"📝 Last {min(5, len(lines))} log entries:")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
        except Exception as e:
            print(f"⚠️  Could not read log file: {e}")
    else:
        print("📝 No log file found (first run)")
    
    print("=" * 50)
    
    # Mostrar estado de instalación
    print()
    maintenance.get_installation_status()


def show_final_summary(success_count, total_operations):
    """Display final maintenance summary"""
    print("\n" + "=" * 50)
    print("📊 Maintenance Summary")
    print("=" * 50)
    print(f"✅ Successful operations: {success_count}")
    print(f"❌ Failed operations: {total_operations - success_count}")
    print(f"📈 Success rate: {(success_count / total_operations) * 100:.1f}%")
    
    if success_count == total_operations:
        print("🎉 All operations completed successfully!")
    elif success_count > 0:
        print("⚠️  Some operations failed. Check logs for details.")
    else:
        print("❌ All operations failed. Please review the errors above.")

if __name__ == "__main__":
    main()
        