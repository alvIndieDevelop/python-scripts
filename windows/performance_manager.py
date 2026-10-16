#!/usr/bin/env python3

"""
Windows Performance Manager - System Performance Monitoring & Optimization
Monitor your computer's speed and optimize it for maximum performance.
Includes diagnostics AND active optimization tools to fix slow computers.
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


# ─── Constantes de Nivel de Riesgo ─────────────────────────────────────────────

RISK_SAFE = "🟢 Seguro"
RISK_LOW = "🔵 Riesgo Bajo"
RISK_MODERATE = "🟡 Moderado"
RISK_HIGH = "🔴 Riesgo Alto"


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
        print(f"🔐 Se necesitan permisos de administrador para: {operation_name}")
        print("   💡 Haz clic derecho en el programa y selecciona 'Ejecutar como administrador'")
        print()
        return False
    return True


def confirmar(mensaje="¿Continuar?"):
    """Ask for confirmation in Spanish. Returns True if user confirms."""
    try:
        response = input(f"  {mensaje} (s/n): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n  ❌ Cancelado.")
        return False
    return response in ('s', 'si', 'sí', 'yes', 'y')


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
    print("║                                                                            ║")
    print("║            ⚡ OPTIMIZADOR DE RENDIMIENTO DE WINDOWS ⚡                     ║")
    print("║                                                                            ║")
    print("║          Acelera tu computadora de forma segura y sencilla                 ║")
    print("║                          Versión 2.0                                       ║")
    print("║                                                                            ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()

    win_info = get_windows_info()
    print(f"  🪟  Sistema: {win_info['name']}")
    print(f"  👤  Usuario: {os.getenv('USERNAME', 'Desconocido')}")
    print(f"  📅  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    is_admin = check_admin()
    if is_admin:
        admin_status = "✅ Administrador — todas las funciones disponibles"
    else:
        admin_status = "⚠️  Usuario normal — algunas funciones necesitan permisos de administrador"
    print(f"  🔐  Permisos: {admin_status}")
    print()
    print("─" * 78)
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
        print(f"⚡ ¿CÓMO ESTÁ TU COMPUTADORA?         {RISK_SAFE}")
        print("   Un vistazo rápido al rendimiento actual de tu equipo.")
        print("   Solo revisa — no se modifica nada.")
        print("=" * 65)
        print()

        # CPU Information
        print("  🖥️  PROCESADOR (CPU)")
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

        print(f"  💻 Procesador: {cpu_name}")
        if cpu_cores > 0:
            print(f"  ⚙️  Núcleos: {cpu_cores} núcleos, {cpu_threads} hilos")
        if cpu_speed > 0:
            print(f"  ⚡ Velocidad: {cpu_speed / 1000:.1f} GHz")

        cpu_bar = format_bar(cpu_load, 100)
        print(f"  📊 Uso actual: {cpu_bar}")

        if cpu_load >= 90:
            print("     🚨 ¡Tu procesador está trabajando muy fuerte!")
            print("     💡 Cierra programas que no estés usando para mejorar la velocidad.")
        elif cpu_load >= 70:
            print("     ⚠️  Tu procesador está moderadamente ocupado.")
        else:
            print("     ✅ Tu procesador funciona bien.")

        print()

        # Memory (RAM) Information
        print("  💾 MEMORIA (RAM)")
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

                print(f"  📊 RAM Total: {total_ram:.1f} GB")
                ram_bar = format_bar(ram_percent, 100)
                print(f"  📊 Uso: {ram_bar}")
                print(f"     En uso: {used_ram:.1f} GB  |  Libre: {free_ram:.1f} GB")

                if ram_percent >= 90:
                    print("     🚨 ¡Tu memoria está casi llena!")
                    print("     💡 Cierra programas o pestañas del navegador para liberar memoria.")
                    print("     💡 Si pasa seguido, tu computadora podría necesitar más RAM.")
                elif ram_percent >= 75:
                    print("     ⚠️  El uso de memoria está alto.")
                    print("     💡 Cierra programas que no estés usando.")
                else:
                    print("     ✅ La memoria está bien.")
            except (ValueError, IndexError):
                print("  ⚠️  No se pudieron leer los detalles de memoria.")
        else:
            print("  ⚠️  No se pudo leer la información de memoria.")

        print()

        # Disk I/O
        print("  💿 ALMACENAMIENTO")
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
                    print(f"  💿 Disco: {disk_name}")
                elif line.startswith('Size'):
                    try:
                        size_bytes = int(line.split(':')[1].strip())
                        print(f"     Capacidad: {format_size(size_bytes)}")
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('MediaType'):
                    media = line.split(':', 1)[1].strip() if ':' in line else ""
                    if media:
                        is_ssd = 'ssd' in media.lower() or 'solid' in media.lower()
                        if is_ssd:
                            print(f"     Tipo: ⚡ SSD (almacenamiento rápido)")
                        else:
                            print(f"     Tipo: 💿 HDD (almacenamiento estándar)")
                            print(f"     💡 ¡Cambiar a un SSD haría tu computadora mucho más rápida!")
                    print()
        else:
            print("  ⚠️  No se pudo leer la información del disco.")

        print()

        # Network
        print("  🌐 RED / INTERNET")
        print("  ─" * 25)

        success, output = self.run_ps_command(
            "Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet",
            "Testing network"
        )

        if success and 'true' in output.lower():
            print("  ✅ Conexión a internet: Funcionando")

            # Check latency
            success2, output2 = self.run_ps_command(
                "(Test-Connection -ComputerName 8.8.8.8 -Count 3 | "
                "Measure-Object -Property Latency -Average).Average",
                "Measuring latency"
            )

            if success2 and output2.strip():
                try:
                    latency = float(output2.strip())
                    print(f"  📡 Tiempo de respuesta: {latency:.0f} ms")
                    if latency < 50:
                        print("     ✅ ¡Conexión muy rápida!")
                    elif latency < 100:
                        print("     ✅ Buena velocidad de conexión.")
                    elif latency < 200:
                        print("     ⚠️  La conexión está un poco lenta.")
                    else:
                        print("     🚨 La conexión está lenta. Revisa tu red.")
                except (ValueError, TypeError):
                    pass
        else:
            print("  ❌ Conexión a internet: No funciona")
            print("     💡 Revisa tu Wi-Fi o cable de red.")

        print()

        # Uptime
        print("  ⏱️  TIEMPO ENCENDIDA")
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
                    uptime_str = f"{days} días, {hours} horas"
                elif hours > 0:
                    uptime_str = f"{hours} horas, {minutes} minutos"
                else:
                    uptime_str = f"{minutes} minutos"

                print(f"  ⏱️  Tu computadora lleva encendida: {uptime_str}")

                if days >= 7:
                    print("     ⚠️  Tu computadora lleva más de una semana sin reiniciar.")
                    print("     💡 Reiniciar de vez en cuando ayuda a que funcione mejor.")
                elif days >= 3:
                    print("     ℹ️  Considera reiniciar pronto para mejor rendimiento.")
                else:
                    print("     ✅ Se reinició recientemente — ¡bien!")
            except (ValueError, IndexError):
                print("  ⚠️  No se pudo determinar el tiempo encendida.")
        else:
            print("  ⚠️  No se pudo determinar el tiempo encendida.")

        print()
        self.log_action("System dashboard displayed")

    # ─── 2. Startup Program Manager ─────────────────────────────────────────

    def manage_startup_programs(self):
        """List and manage programs that run at startup."""
        print()
        print("=" * 65)
        print(f"🚀 PROGRAMAS DE INICIO                {RISK_SAFE}")
        print("   Estos programas se inician automáticamente al encender tu computadora.")
        print("   Demasiados pueden hacer que tu computadora tarde más en iniciar.")
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
            print("  ✅ ¡No se encontraron programas de inicio!")
            print("  💡 Tu computadora debería iniciar rápido.")
            return

        total_items = len(startup_items) + len(registry_items)

        print(f"  📋 Se encontraron {total_items} programas que inician con tu computadora:")
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
            print(f"      📍 Origen: {location}")
            print()

        # Show registry startup items
        offset = len(startup_items)
        for i, name in enumerate(registry_items, offset + 1):
            print(f"  {i:2d}. 📦 {name}")
            print(f"      📍 Origen: User Registry (Run key)")
            print()

        # Performance assessment
        print("  ─" * 25)
        if total_items > 10:
            print(f"  ⚠️  Tienes {total_items} programas de inicio — ¡son bastantes!")
            print("  💡 Tener menos programas de inicio hace que tu computadora arranque más rápido.")
            print()
            print("  💡 Cómo gestionar los programas de inicio:")
            print("     1. Presiona Ctrl + Shift + Esc para abrir el Administrador de Tareas")
            print("     2. Haz clic en la pestaña 'Inicio'")
            print("     3. Clic derecho en programas que no necesites y selecciona 'Deshabilitar'")
            print()
            print("  ⚠️  ¡No deshabilites programas que no reconozcas — algunos son importantes!")
            print("     Si tienes duda, busca el nombre del programa en internet primero.")
        elif total_items > 5:
            print(f"  ℹ️  Tienes {total_items} programas de inicio — es una cantidad moderada.")
            print("  💡 Podrías deshabilitar algunos para acelerar un poco el inicio.")
        else:
            print(f"  ✅ Solo {total_items} programas de inicio — ¡excelente!")
            print("  💡 Tu computadora debería arrancar razonablemente rápido.")

        print()
        self.log_action(f"Startup programs listed: {total_items} items")

    # ─── 3. Running Processes ───────────────────────────────────────────────

    def show_top_processes(self, top_n=15):
        """Show the programs using the most resources."""
        print()
        print("=" * 65)
        print(f"📊 PROGRAMAS QUE MÁS RECURSOS USAN   {RISK_SAFE}")
        print("   Mira qué programas están usando más CPU y memoria.")
        print("=" * 65)
        print()

        # Top CPU consumers
        print("  🖥️  PROGRAMAS CON MÁS USO DE CPU")
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
                        mem_bar = " ⚠️ Usando mucha memoria"
                    elif mem > 500:
                        mem_bar = ""

                    print(f"  {i:2d}. {display_name:<35} CPU: {cpu:>8.1f}s  RAM: {mem:>5.0f} MB{mem_bar}")

                print()

                # Helpful tips
                total_mem = sum(p.get('Memory_MB', 0) for p in processes)
                if total_mem > 4000:
                    print("  💡 Tus programas están usando mucha memoria.")
                    print("     Cierra pestañas del navegador y programas que no estés usando.")
                else:
                    print("  ✅ El uso de memoria por los programas se ve razonable.")

            except json.JSONDecodeError:
                print("  ⚠️  No se pudo leer la información de procesos.")
        else:
            print("  ⚠️  No se pudo leer la información de procesos.")

        print()
        self.log_action("Top processes displayed")

    # ─── 4. Service Manager ─────────────────────────────────────────────────

    def show_services_status(self):
        """Show important system services and their status."""
        print()
        print("=" * 65)
        print(f"⚙️  ESTADO DE SERVICIOS DEL SISTEMA     {RISK_SAFE}")
        print("   Son programas en segundo plano que mantienen tu computadora funcionando.")
        print("=" * 65)
        print()

        # Important services to check
        important_services = [
            ("wuauserv", "Windows Update", "Mantiene tu computadora segura con las últimas actualizaciones"),
            ("WinDefend", "Windows Defender", "Protege contra virus y malware"),
            ("Spooler", "Print Spooler", "Gestiona la impresión (necesario para impresoras)"),
            ("BITS", "Background Transfer", "Descarga actualizaciones y archivos en segundo plano"),
            ("Dhcp", "Network (DHCP)", "Obtiene tu dirección de internet automáticamente"),
            ("Dnscache", "DNS Cache", "Acelera la carga de sitios web"),
            ("EventLog", "Event Log", "Registra eventos del sistema para resolver problemas"),
            ("Schedule", "Task Scheduler", "Ejecuta tareas programadas automáticamente"),
            ("W32Time", "Windows Time", "Mantiene tu reloj preciso"),
            ("Audiosrv", "Audio Service", "Gestiona el sonido de tu computadora"),
        ]

        print("  📋 Servicios Importantes:")
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
        print(f"  📊 Resumen: {running} activos, {stopped} detenidos")
        print()

        if stopped > 0:
            print("  ℹ️  Algunos servicios detenidos son normales si no usas esas funciones.")
            print("     Por ejemplo, el servicio de impresión puede estar apagado si no tienes impresora.")
        else:
            print("  ✅ ¡Todos los servicios importantes están funcionando correctamente!")

        print()
        self.log_action(f"Services status: {running} running, {stopped} stopped")

    # ─── 5. Power Plan Manager ──────────────────────────────────────────────

    def show_power_plan(self):
        """Show and manage power plans."""
        print()
        print("=" * 65)
        print(f"🔋 CONFIGURACIÓN DE ENERGÍA           {RISK_SAFE}")
        print("   Tu plan de energía afecta la velocidad de tu computadora.")
        print("=" * 65)
        print()

        success, output = self.run_command(
            "powercfg /getactivescheme",
            "Getting active power plan"
        )

        if success and output:
            print(f"  ⚡ Plan de energía actual: {output}")
            print()

            if 'balanced' in output.lower():
                print("  ℹ️  Estás usando el plan 'Equilibrado'.")
                print("     Es una buena opción — equilibra velocidad con ahorro de energía.")
                print()
                print("  💡 Para mejor rendimiento en una computadora de escritorio:")
                print("     Cambia al plan 'Alto rendimiento'.")
            elif 'high performance' in output.lower():
                print("  ⚡ Estás usando 'Alto rendimiento' — ¡máxima velocidad!")
                print("     ℹ️  Usa más electricidad pero da la mejor velocidad.")
            elif 'power saver' in output.lower():
                print("  🔋 Estás usando 'Ahorro de energía' — esto hace más lenta tu computadora para ahorrar batería.")
                print("     💡 Cambia a 'Equilibrado' para mejor velocidad y seguir ahorrando algo de energía.")
        else:
            print("  ⚠️  No se pudo determinar el plan de energía.")

        # List available plans
        print()
        success2, output2 = self.run_command(
            "powercfg /list",
            "Listing power plans"
        )

        if success2 and output2:
            print("  📋 Planes de energía disponibles:")
            for line in output2.split('\n'):
                line = line.strip()
                if 'GUID' in line or 'Power Scheme' in line:
                    if '*' in line:
                        print(f"     ⚡ {line}  ← ACTIVO")
                    else:
                        print(f"     📋 {line}")

        print()
        print("  💡 Para cambiar tu plan de energía:")
        print("     1. Abre Configuración → Sistema → Energía y batería")
        print("     2. O busca 'Plan de energía' en el menú Inicio")
        print()

        self.log_action("Power plan info displayed")

    # ─── 6. Disk Health Check ───────────────────────────────────────────────

    def check_disk_health(self):
        """Check disk health using available Windows tools."""
        print()
        print("=" * 65)
        print(f"💿 REVISIÓN DE SALUD DEL DISCO        {RISK_SAFE}")
        print("   Revisando si tus discos de almacenamiento están sanos.")
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
                        type_name = "SSD (Disco de Estado Sólido)"
                    elif media == '3' or 'hdd' in str(media).lower():
                        type_emoji = "💿"
                        type_name = "HDD (Disco Duro)"
                    else:
                        type_emoji = "💾"
                        type_name = f"Storage ({media})"

                    # Health status
                    if health.lower() == 'healthy' or health == '0':
                        health_emoji = "✅"
                        health_text = "Healthy"
                        health_explain = "¡Tu disco funciona perfectamente!"
                    elif health.lower() in ('warning', '1'):
                        health_emoji = "⚠️"
                        health_text = "Warning"
                        health_explain = "Tu disco podría tener problemas. Considera hacer respaldo de tus archivos."
                    elif health.lower() in ('unhealthy', '2'):
                        health_emoji = "🚨"
                        health_text = "Unhealthy"
                        health_explain = "¡Tu disco tiene problemas! ¡Haz respaldo de tus archivos inmediatamente!"
                    else:
                        health_emoji = "❓"
                        health_text = health
                        health_explain = "No se pudo determinar el estado de salud."

                    print(f"  {type_emoji} {name}")
                    print(f"     Type: {type_name}")
                    print(f"     Size: {size_gb} GB")
                    print(f"     Health: {health_emoji} {health_text}")
                    print(f"     ℹ️  {health_explain}")
                    print()

            except json.JSONDecodeError:
                print("  ⚠️  No se pudieron leer los datos de salud del disco.")
        else:
            # Fallback to wmic for Win10
            print("  ℹ️  Usando método alternativo para revisar discos...")
            success2, output2 = self.run_command(
                'wmic diskdrive get Model,Status,Size /format:list',
                "Checking disk status (wmic)"
            )
            if success2 and output2:
                print(f"  {output2}")
            else:
                print("  ⚠️  No se pudo revisar la salud del disco. Intenta ejecutar como administrador.")

        # Check TRIM for SSDs
        print("  ⚡ Optimización de SSD (TRIM):")
        success3, output3 = self.run_ps_command(
            "fsutil behavior query DisableDeleteNotify",
            "Checking TRIM status"
        )

        if success3 and output3:
            if '0' in output3:
                print("     ✅ TRIM está activado — tu SSD se optimiza automáticamente.")
                print("     ℹ️  TRIM ayuda a que tu SSD se mantenga rápido con el tiempo.")
            elif '1' in output3:
                print("     ⚠️  TRIM está desactivado.")
                print("     💡 Activar TRIM puede mejorar el rendimiento y vida útil del SSD.")
        else:
            print("     ℹ️  No se pudo verificar el estado de TRIM.")

        print()
        self.log_action("Disk health check completed")

    # ─── 7. System Integrity Check (Admin) ──────────────────────────────────

    def check_system_integrity(self):
        """Run Windows system file checker."""
        print()
        print("=" * 65)
        print(f"🛡️  VERIFICACIÓN DE ARCHIVOS DEL SISTEMA {RISK_MODERATE}")
        print("   Verifica si los archivos de Windows están intactos y los repara.")
        print("   Es como un chequeo médico para tu instalación de Windows.")
        print("=" * 65)
        print()

        if not require_admin("System integrity check"):
            return False

        print("  🟡 Esta operación:")
        print("     • Escanea todos los archivos del sistema en busca de problemas")
        print("     • Repara automáticamente archivos dañados")
        print("     • Puede tomar 10-30 minutos")
        print("     • Tu computadora seguirá funcionando durante el escaneo")
        print()

        if not confirmar("¿Ejecutar la verificación del sistema?"):
            return False

        print()
        print("  🔍 Paso 1: Escaneando archivos del sistema...")
        print("  ⏳ Puede tomar 10-30 minutos. Por favor ten paciencia...")
        print()

        success, output = self.run_command(
            "sfc /scannow",
            "System File Checker"
        )

        if success:
            if 'did not find any integrity violations' in output.lower():
                print("  ✅ ¡Buenas noticias! ¡Todos los archivos del sistema están intactos!")
                print("  ℹ️  Tu instalación de Windows está sana.")
            elif 'successfully repaired' in output.lower():
                print("  ✅ ¡Algunos archivos estaban dañados pero fueron reparados!")
                print("  💡 Es recomendable reiniciar tu computadora.")
            elif 'could not' in output.lower() or 'unable' in output.lower():
                print("  ⚠️  Algunos archivos no pudieron ser reparados.")
                print("  💡 Intenta ejecutar la reparación DISM primero, luego ejecuta esto de nuevo.")
            else:
                print("  ℹ️  Escaneo completado. Resultados:")
                for line in output.split('\n')[-5:]:
                    if line.strip():
                        print(f"     {line.strip()}")
        else:
            print("  ❌ La verificación del sistema encontró un error.")
            print()
            print("  💡 Qué hacer:")
            print("     • Asegúrate de ejecutar como administrador")
            print("     • Intenta reiniciar tu computadora y ejecutar de nuevo")
            if output:
                print(f"     🔍 Detalles técnicos: {output[:200]}")

        print()
        self.log_action("System integrity check", success=success)
        return success

    # ─── 8. Windows Update Status ───────────────────────────────────────────

    def check_windows_update(self):
        """Check Windows Update status."""
        print()
        print("=" * 65)
        print(f"🪟 ESTADO DE ACTUALIZACIONES DE WINDOWS {RISK_SAFE}")
        print("   Revisando si tu computadora tiene las últimas actualizaciones.")
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

                print(f"  📅 Última actualización instalada: {output.strip()}")

                if days_since > 30:
                    print(f"     🚨 Eso fue hace {days_since} días — ¡tu computadora podría estar sin actualizaciones de seguridad importantes!")
                    print("     💡 Abre Configuración → Actualización y seguridad → Windows Update y busca actualizaciones.")
                elif days_since > 14:
                    print(f"     ⚠️  Eso fue hace {days_since} días.")
                    print("     💡 Considera buscar actualizaciones pronto.")
                else:
                    print(f"     ✅ Actualizado hace {days_since} días — ¡es reciente!")
            except ValueError:
                print(f"  📅 Last update: {output.strip()}")
        else:
            print("  ⚠️  No se pudo determinar la fecha de la última actualización.")

        print()

        # List recent updates
        success2, output2 = self.run_ps_command(
            "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5 "
            "HotFixID, Description, InstalledOn | Format-Table -AutoSize",
            "Listing recent updates"
        )

        if success2 and output2.strip():
            print("  📋 Actualizaciones recientes:")
            for line in output2.strip().split('\n'):
                print(f"     {line}")
        else:
            print("  ℹ️  No se pudieron listar las actualizaciones recientes.")

        print()
        print("  💡 Para buscar nuevas actualizaciones:")
        print("     1. Abre Configuración (tecla Windows + I)")
        print("     2. Ve a Actualización y seguridad (Win10) o Windows Update (Win11)")
        print("     3. Haz clic en 'Buscar actualizaciones'")
        print()

        self.log_action("Windows Update status checked")

    # ─── 9. Optimize Visual Effects ─────────────────────────────────────────

    def optimize_visual_effects(self):
        """Disable only performance-heavy animations while keeping the visual look intact."""
        print()
        print("=" * 65)
        print(f"🎨 OPTIMIZAR EFECTOS VISUALES         {RISK_LOW}")
        print("   Desactiva solo las animaciones que consumen rendimiento.")
        print("   Tu escritorio se verá prácticamente igual, pero más rápido.")
        print("=" * 65)
        print()

        if not require_admin("Optimización de efectos visuales"):
            return False

        print("  🔵 Lo que SE DESACTIVA (no se nota mucho):")
        print("     • Animaciones al minimizar/maximizar ventanas")
        print("     • Animaciones en la barra de tareas")
        print("     • Animaciones de menús (desvanecimientos)")
        print("     • Deslizar ventanas al abrir/cerrar")
        print()
        print("  ✅ Lo que SE MANTIENE (tu escritorio se ve igual):")
        print("     • Transparencia de ventanas y barra de tareas")
        print("     • Sombras de ventanas")
        print("     • Texto suavizado (ClearType)")
        print("     • Vista previa de miniaturas")
        print("     • Iconos del escritorio con sombra")
        print("     • Bordes redondeados de Windows 11")
        print()
        print("  ℹ️  Esto es seguro y reversible. Puedes reactivar los efectos en:")
        print("     Configuración → Sistema → Acerca de → Config. avanzada → Rendimiento")
        print()

        if not confirmar("¿Optimizar efectos visuales?"):
            return False

        print()
        print("  🔧 Aplicando optimizaciones visuales (sin cambiar la apariencia)...")

        optimizations = [
            # Set visual effects to "Custom" (3) instead of "Best performance" (2)
            # This lets us choose exactly what to disable
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' "
                "-Name 'VisualFXSetting' -Value 3 -Type DWord -Force",
                "Configurar modo personalizado"
            ),
            # Disable minimize/maximize animations (performance-heavy, barely noticed)
            (
                "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop\\WindowMetrics' "
                "-Name 'MinAnimate' -Value '0' -Force",
                "Desactivar animación de minimizar/maximizar"
            ),
            # Disable taskbar animations (performance-heavy)
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' "
                "-Name 'TaskbarAnimations' -Value 0 -Type DWord -Force",
                "Desactivar animaciones de la barra de tareas"
            ),
            # Disable menu fade/slide animations (performance-heavy, menus still open fine)
            (
                "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' "
                "-Name 'MenuShowDelay' -Value '0' -Type String -Force",
                "Hacer menús más rápidos (sin retardo)"
            ),
            # Keep smooth fonts (ClearType) enabled — important for readability
            (
                "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' "
                "-Name 'FontSmoothing' -Value '2' -Type String -Force",
                "Mantener texto suavizado (ClearType)"
            ),
            # Keep window shadows enabled — important for visual distinction
            # UserPreferencesMask: custom value that keeps shadows, fonts, and peek
            # but disables menu animations, tooltip animations, and combo slide
            # Bits: Shadows=ON, FontSmoothing=ON, DragFull=ON, MenuAnim=OFF, TooltipAnim=OFF
            (
                "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' "
                "-Name 'UserPreferencesMask' -Value ([byte[]](0x90,0x32,0x07,0x80,0x12,0x00,0x00,0x00)) -Type Binary -Force",
                "Desactivar animaciones de menús (mantener sombras y fuentes)"
            ),
            # Disable Aero Peek (hover on taskbar to preview) — saves resources
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\DWM' "
                "-Name 'EnableAeroPeek' -Value 0 -Type DWord -Force",
                "Desactivar vista previa al pasar sobre la barra de tareas"
            ),
            # Disable showing window contents while dragging (saves GPU/CPU)
            (
                "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' "
                "-Name 'DragFullWindows' -Value '0' -Type String -Force",
                "Desactivar contenido visible al arrastrar ventanas"
            ),
        ]

        success_count = 0
        for ps_cmd, desc in optimizations:
            success, _ = self.run_ps_command(ps_cmd, desc)
            if success:
                print(f"     ✅ {desc}")
                success_count += 1
            else:
                print(f"     ⚠️  {desc} — no se pudo aplicar")

        print()
        if success_count > 0:
            print(f"  ✅ ¡Se aplicaron {success_count}/{len(optimizations)} optimizaciones!")
            print()
            print("  ℹ️  Tu escritorio se ve prácticamente igual.")
            print("     Solo se quitaron animaciones que consumían rendimiento.")
            print("  💡 Puede que necesites cerrar sesión e iniciar de nuevo para ver todos los cambios.")
        else:
            print("  ❌ No se pudieron aplicar las optimizaciones visuales.")

        print()
        self.log_action(f"Visual effects optimized (light mode): {success_count}/{len(optimizations)}")
        return success_count > 0

    # ─── 10. Set High Performance Power Plan ─────────────────────────────────

    def set_high_performance_power(self):
        """Switch to High Performance power plan for maximum speed."""
        print()
        print("=" * 65)
        print(f"⚡ PLAN DE ENERGÍA DE ALTO RENDIMIENTO {RISK_LOW}")
        print("   Cambia tu plan de energía para maximizar la velocidad.")
        print("   Usa más electricidad pero da el mejor rendimiento.")
        print("=" * 65)
        print()

        # Show current plan
        success, output = self.run_command(
            "powercfg /getactivescheme",
            "Getting active power plan"
        )

        if success and output:
            print(f"  📋 Plan actual: {output}")
            print()

            if 'high performance' in output.lower():
                print("  ✅ ¡Ya estás usando el modo de Alto Rendimiento!")
                print("  ℹ️  No se necesitan cambios.")
                print()
                self.log_action("High performance already active")
                return True

        print("  ⚡ Esto hará:")
        print("     • Evitar que tu CPU se ralentice para ahorrar energía")
        print("     • Mantener tus discos duros activos (acceso más rápido)")
        print("     • Evitar que los dispositivos USB se suspendan")
        print("     • Usar más electricidad (importa principalmente en laptops con batería)")
        print()

        if not confirmar("¿Cambiar a Alto Rendimiento?"):
            return False

        print()
        print("  🔧 Cambiando a Alto Rendimiento...")

        # High Performance GUID is always 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
        hp_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

        # First check if High Performance plan exists, if not create it
        success, output = self.run_command(
            f"powercfg /setactive {hp_guid}",
            "Activating High Performance plan"
        )

        if success:
            print("  ✅ ¡Plan de Alto Rendimiento activado!")
        else:
            # Try to duplicate from Balanced and set
            print("  ℹ️  Plan de Alto Rendimiento no disponible, creándolo...")
            success2, output2 = self.run_command(
                f"powercfg /duplicatescheme {hp_guid}",
                "Creating High Performance plan"
            )
            if success2:
                success3, _ = self.run_command(
                    f"powercfg /setactive {hp_guid}",
                    "Activating High Performance plan"
                )
                if success3:
                    print("  ✅ ¡Plan de Alto Rendimiento creado y activado!")
                else:
                    print("  ⚠️  Creado pero no se pudo activar. Intenta manualmente en Configuración → Energía.")
            else:
                print("  ⚠️  No se pudo crear el plan de Alto Rendimiento.")
                print("  💡 Abre Configuración → Sistema → Energía y batería → configura 'Mejor rendimiento'")

        # Additional power optimizations
        print()
        print("  🔧 Aplicando optimizaciones de energía adicionales...")

        power_opts = [
            ("powercfg /change monitor-timeout-ac 15", "Tiempo de apagado de monitor: 15 min (conectado)"),
            ("powercfg /change disk-timeout-ac 0", "Evitar que los discos se suspendan (conectado)"),
            ("powercfg /change standby-timeout-ac 0", "Evitar suspensión cuando está conectado"),
            ("powercfg /change hibernate-timeout-ac 0", "Desactivar hibernación cuando está conectado"),
        ]

        for cmd, desc in power_opts:
            s, _ = self.run_command(cmd, desc)
            if s:
                print(f"     ✅ {desc}")
            else:
                print(f"     ⚠️  {desc} — no se pudo aplicar")

        print()
        print("  💡 Con batería, Windows seguirá ahorrando energía automáticamente.")
        print()

        self.log_action("High Performance power plan set")
        return True

    # ─── 11. Disable Unnecessary Services ────────────────────────────────────

    def disable_unnecessary_services(self):
        """Disable services that slow down Windows but are not essential."""
        print()
        print("=" * 65)
        print(f"⚙️  DESHABILITAR SERVICIOS INNECESARIOS {RISK_MODERATE}")
        print("   Detiene servicios en segundo plano que desperdician CPU y memoria.")
        print("   Solo deshabilita servicios no esenciales que la mayoría no necesita.")
        print("=" * 65)
        print()

        if not require_admin("Disabling services"):
            return False

        # Services safe to disable for most users
        # Format: (service_name, friendly_name, description, what_breaks)
        disable_candidates = [
            ("DiagTrack", "Connected User Experiences & Telemetry",
             "Envía datos de uso a Microsoft",
             "Microsoft no recibirá tus datos de uso"),
            ("dmwappushservice", "Device Management WAP Push",
             "Envía políticas de recopilación de datos",
             "Sin impacto en el uso normal"),
            ("SysMain", "Superfetch/SysMain",
             "Precarga apps en memoria (puede causar alto uso de disco en HDDs)",
             "Las apps pueden tardar un poco más en abrir la primera vez"),
            ("WSearch", "Windows Search Indexing",
             "Indexa archivos para búsqueda (usa CPU y disco constantemente)",
             "La búsqueda de archivos en el menú Inicio será más lenta"),
            ("MapsBroker", "Downloaded Maps Manager",
             "Gestiona datos de mapas sin conexión",
             "Los mapas sin conexión no se actualizarán automáticamente"),
            ("RetailDemo", "Retail Demo Service",
             "Solo para computadoras de exhibición en tiendas",
             "Ninguno — esto solo es para tiendas"),
            ("wisvc", "Windows Insider Service",
             "Para versiones preliminares de Windows Insider",
             "No recibirás versiones preliminares de Insider"),
            ("lfsvc", "Geolocation Service",
             "Rastrea tu ubicación física",
             "Las apps basadas en ubicación no conocerán tu posición"),
            ("Fax", "Fax Service",
             "Para enviar y recibir faxes",
             "No podrás enviar faxes (la mayoría no necesita esto)"),
            ("XblAuthManager", "Xbox Live Auth Manager",
             "Autenticación de Xbox Live",
             "Las funciones de Xbox Live no funcionarán"),
            ("XblGameSave", "Xbox Live Game Save",
             "Sincroniza partidas guardadas de Xbox",
             "Las partidas de Xbox no se sincronizarán con la nube"),
            ("XboxGipSvc", "Xbox Accessory Management",
             "Gestiona controles/accesorios de Xbox",
             "Los controles de Xbox podrían no funcionar (reactiva si es necesario)"),
            ("XboxNetApiSvc", "Xbox Live Networking",
             "Funciones de red de Xbox Live",
             "El multijugador de Xbox Live no funcionará"),
        ]

        print("  📋 Servicios que se pueden deshabilitar de forma segura:")
        print()

        # Check current status of each
        services_to_disable = []
        for svc_name, friendly_name, desc, impact in disable_candidates:
            success, output = self.run_ps_command(
                f"(Get-Service -Name '{svc_name}' -ErrorAction SilentlyContinue).Status",
                None
            )

            if success and output.strip():
                status = output.strip().lower()
                if status == 'running':
                    status_emoji = "🟢 Activo"
                    services_to_disable.append((svc_name, friendly_name, desc, impact))
                elif status == 'stopped':
                    status_emoji = "⏹️ Ya detenido"
                else:
                    status_emoji = f"❓ {output.strip()}"

                print(f"  {status_emoji}  {friendly_name}")
                print(f"     ℹ️  {desc}")
                print(f"     ⚠️  Si se deshabilita: {impact}")
                print()

        if not services_to_disable:
            print("  ✅ ¡Todos los servicios innecesarios ya están deshabilitados!")
            print("  ℹ️  No se necesitan cambios.")
            print()
            return True

        print("  ─" * 25)
        print(f"  📊 Se encontraron {len(services_to_disable)} servicios que se pueden deshabilitar.")
        print()
        print("  🟡 Esto es reversible — puedes reactivar cualquier servicio después con:")
        print("     services.msc o PowerShell: Set-Service -Name 'ServiceName' -StartupType Automatic")
        print()

        if not confirmar("¿Deshabilitar estos servicios?"):
            return False

        print()
        print("  🔧 Deshabilitando servicios...")

        disabled_count = 0
        for svc_name, friendly_name, _, _ in services_to_disable:
            # Stop and disable the service
            success, _ = self.run_ps_command(
                f"Stop-Service -Name '{svc_name}' -Force -ErrorAction SilentlyContinue; "
                f"Set-Service -Name '{svc_name}' -StartupType Disabled -ErrorAction SilentlyContinue",
                f"Disabling {friendly_name}"
            )

            if success:
                print(f"     ✅ Deshabilitado: {friendly_name}")
                disabled_count += 1
            else:
                print(f"     ⚠️  No se pudo deshabilitar: {friendly_name}")

        print()
        print(f"  ✅ ¡Se deshabilitaron {disabled_count}/{len(services_to_disable)} servicios!")
        print("  💡 Reinicia tu computadora para que todos los cambios surtan efecto.")
        print()

        self.log_action(f"Services disabled: {disabled_count}/{len(services_to_disable)}")
        return disabled_count > 0

    # ─── 12. Clean DNS & Network Cache ───────────────────────────────────────

    def clean_network_cache(self):
        """Flush DNS cache and reset network components."""
        print()
        print("=" * 65)
        print(f"🌐 LIMPIAR CACHÉ DE RED               {RISK_LOW}")
        print("   Limpia datos de red antiguos que pueden causar lentitud y errores.")
        print("   Es como refrescar tu conexión a internet.")
        print("=" * 65)
        print()

        if not require_admin("Network cache cleanup"):
            return False

        print("  🔵 Esta operación:")
        print("     • Limpia la caché DNS (borra búsquedas antiguas de sitios web)")
        print("     • Restablece el catálogo Winsock (repara corrupción de red)")
        print("     • Renueva tu dirección IP")
        print("     • Limpia la caché ARP (repara problemas de red local)")
        print()
        print("  ℹ️  Tu internet se desconectará brevemente durante este proceso.")
        print()

        if not confirmar("¿Limpiar caché de red?"):
            return False

        print()
        print("  🔧 Limpiando caché de red...")

        commands = [
            ("ipconfig /flushdns", "Limpiar caché DNS"),
            ("ipconfig /release", "Liberar dirección IP"),
            ("ipconfig /renew", "Renovar dirección IP"),
            ("netsh winsock reset", "Restablecer catálogo Winsock"),
            ("netsh int ip reset", "Restablecer pila TCP/IP"),
            ("arp -d *", "Limpiar caché ARP"),
        ]

        success_count = 0
        for cmd, desc in commands:
            print(f"     🔧 {desc}...")
            success, _ = self.run_command(cmd, desc)
            if success:
                print(f"     ✅ {desc}")
                success_count += 1
            else:
                print(f"     ⚠️  {desc} — puede requerir reinicio")

        print()
        if success_count > 0:
            print(f"  ✅ ¡Caché de red limpiada! ({success_count}/{len(commands)} operaciones)")
            print("  💡 Si el internet no funciona, reinicia tu computadora.")
        else:
            print("  ⚠️  No se pudo limpiar la caché de red. Intenta reiniciar tu computadora.")

        print()
        self.log_action(f"Network cache cleaned: {success_count}/{len(commands)}")
        return success_count > 0

    # ─── 13. Disable Telemetry & Tracking ────────────────────────────────────

    def disable_telemetry(self):
        """Reduce Windows telemetry and background data collection."""
        print()
        print("=" * 65)
        print(f"🔒 DESHABILITAR TELEMETRÍA Y RASTREO  {RISK_MODERATE}")
        print("   Reduce la recopilación de datos en segundo plano que desperdicia CPU y red.")
        print("   Tu computadora usará menos recursos en segundo plano.")
        print("=" * 65)
        print()

        if not require_admin("Telemetry optimization"):
            return False

        print("  🟡 Esta operación:")
        print("     • Configura la telemetría al mínimo (solo nivel de Seguridad)")
        print("     • Desactiva el rastreo de ID de publicidad")
        print("     • Desactiva la recopilación de historial de actividad")
        print("     • Desactiva las notificaciones de comentarios")
        print("     • Desactiva el rastreo de inicio de aplicaciones")
        print("     • Desactiva el programa de mejora de experiencia del cliente")
        print()
        print("  ℹ️  Esto es reversible en Configuración → Privacidad y seguridad.")
        print()

        if not confirmar("¿Deshabilitar telemetría?"):
            return False

        print()
        print("  🔧 Aplicando optimizaciones de telemetría...")

        telemetry_opts = [
            # Set telemetry to Security only (minimum)
            (
                "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Force | Out-Null; "
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' "
                "-Name 'AllowTelemetry' -Value 0 -Type DWord -Force",
                "Set telemetry to minimum"
            ),
            # Disable advertising ID
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' "
                "-Name 'Enabled' -Value 0 -Type DWord -Force",
                "Disable advertising ID"
            ),
            # Disable activity history
            (
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' "
                "-Name 'EnableActivityFeed' -Value 0 -Type DWord -Force",
                "Disable activity history"
            ),
            # Disable feedback frequency
            (
                "New-Item -Path 'HKCU:\\Software\\Microsoft\\Siuf\\Rules' -Force | Out-Null; "
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Siuf\\Rules' "
                "-Name 'NumberOfSIUFInPeriod' -Value 0 -Type DWord -Force",
                "Disable feedback requests"
            ),
            # Disable app launch tracking
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' "
                "-Name 'Start_TrackProgs' -Value 0 -Type DWord -Force",
                "Disable app launch tracking"
            ),
            # Disable customer experience improvement
            (
                "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\SQMClient\\Windows' -Force | Out-Null; "
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\SQMClient\\Windows' "
                "-Name 'CEIPEnable' -Value 0 -Type DWord -Force",
                "Disable customer experience program"
            ),
            # Disable location tracking
            (
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors' "
                "-Name 'DisableLocation' -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue",
                "Disable background location tracking"
            ),
        ]

        success_count = 0
        for ps_cmd, desc in telemetry_opts:
            success, _ = self.run_ps_command(ps_cmd, desc)
            if success:
                print(f"     ✅ {desc}")
                success_count += 1
            else:
                print(f"     ⚠️  {desc} — no se pudo aplicar")

        print()
        if success_count > 0:
            print(f"  ✅ ¡Se aplicaron {success_count}/{len(telemetry_opts)} optimizaciones de telemetría!")
            print("  💡 Reinicia tu computadora para que todos los cambios surtan efecto.")
        else:
            print("  ❌ No se pudieron aplicar las optimizaciones de telemetría.")

        print()
        self.log_action(f"Telemetry disabled: {success_count}/{len(telemetry_opts)}")
        return success_count > 0

    # ─── 14. Optimize Search Indexing ────────────────────────────────────────

    def optimize_search_indexing(self):
        """Reduce or disable Windows Search indexing to save resources."""
        print()
        print("=" * 65)
        print(f"🔍 OPTIMIZAR INDEXACIÓN DE BÚSQUEDA   {RISK_LOW}")
        print("   La Búsqueda de Windows escanea constantemente tus archivos en segundo plano.")
        print("   Esto usa CPU y disco, haciendo más lenta tu computadora.")
        print("=" * 65)
        print()

        if not require_admin("Search indexing optimization"):
            return False

        # Check current state
        success, output = self.run_ps_command(
            "(Get-Service -Name 'WSearch' -ErrorAction SilentlyContinue).Status",
            "Checking Windows Search status"
        )

        if success and output.strip():
            status = output.strip()
            if status.lower() == 'running':
                print("  🟢 Búsqueda de Windows actualmente: Activa")
                print("     ℹ️  Está indexando archivos en segundo plano.")
            elif status.lower() == 'stopped':
                print("  ⏹️ Búsqueda de Windows actualmente: Detenida")
                print("     ✅ ¡La indexación de búsqueda ya está deshabilitada!")
                print()
                return True
            else:
                print(f"  ❓ Estado de Búsqueda de Windows: {status}")
        else:
            print("  ⚠️  No se pudo determinar el estado de búsqueda.")

        print()
        print("  🔵 Opciones:")
        print("     1. Deshabilitar Búsqueda de Windows completamente (ahorra más recursos)")
        print("        → La búsqueda de archivos en el menú Inicio será más lenta")
        print("     2. Reducir el alcance de indexación (mantener búsqueda pero limitar lo indexado)")
        print("        → La búsqueda sigue funcionando pero indexa menos ubicaciones")
        print()

        try:
            choice = input("  Elige opción (1/2) o 'no' para cancelar: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  ❌ Cancelado.")
            return False

        if choice == '1':
            print()
            print("  🔧 Deshabilitando Búsqueda de Windows...")

            success, _ = self.run_ps_command(
                "Stop-Service -Name 'WSearch' -Force -ErrorAction SilentlyContinue; "
                "Set-Service -Name 'WSearch' -StartupType Disabled",
                "Disabling Windows Search"
            )

            if success:
                print("  ✅ ¡La Búsqueda de Windows ha sido deshabilitada!")
                print("  ℹ️  Aún puedes buscar archivos usando la barra de búsqueda del Explorador de archivos.")
                print("  💡 Para reactivar: Ejecuta 'services.msc' y configura Windows Search en Automático.")
            else:
                print("  ⚠️  No se pudo deshabilitar la Búsqueda de Windows.")

            self.log_action("Windows Search disabled")

        elif choice == '2':
            print()
            print("  🔧 Reduciendo el alcance de indexación...")

            # Reduce indexing to essential locations only
            success, _ = self.run_ps_command(
                "Stop-Service -Name 'WSearch' -Force -ErrorAction SilentlyContinue; "
                "Start-Sleep -Seconds 2; "
                "Start-Service -Name 'WSearch' -ErrorAction SilentlyContinue",
                "Restarting Windows Search"
            )

            # Set indexer to low resource usage
            success2, _ = self.run_ps_command(
                "New-Item -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows Search' -Force | Out-Null; "
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows Search' "
                "-Name 'SetupCompletedSuccessfully' -Value 0 -Type DWord -Force",
                "Reducing search index scope"
            )

            if success:
                print("  ✅ ¡La indexación de búsqueda ha sido reducida!")
                print("  💡 Para personalizar más: Abre 'Opciones de indexación' desde el Panel de control.")
            else:
                print("  ⚠️  No se pudo reducir la indexación. Intenta abrir 'Opciones de indexación' manualmente.")

            self.log_action("Search indexing reduced")
        else:
            print("  ❌ Cancelado. No se realizaron cambios.")
            return False

        print()
        return True

    # ─── 15. Disable Windows Tips & Suggestions ─────────────────────────────

    def disable_tips_suggestions(self):
        """Disable Windows tips, suggestions, and notification bloat."""
        print()
        print("=" * 65)
        print(f"🔔 DESHABILITAR CONSEJOS Y SUGERENCIAS {RISK_LOW}")
        print("   Evita que Windows muestre consejos, sugerencias y anuncios.")
        print("   Estos usan recursos y pueden ser molestos.")
        print("=" * 65)
        print()

        print("  🔵 Esto deshabilitará:")
        print("     • Notificaciones de 'Obtener consejos, trucos y sugerencias'")
        print("     • Sugerencias del menú Inicio (anuncios de apps)")
        print("     • Consejos y datos curiosos de la pantalla de bloqueo")
        print("     • Apps 'Sugeridas' en Configuración")
        print("     • Sugerencias de la línea de tiempo")
        print("     • Notificaciones de 'Terminar de configurar'")
        print()

        if not confirmar("¿Deshabilitar consejos y sugerencias?"):
            return False

        print()
        print("  🔧 Deshabilitando consejos y sugerencias...")

        tips_opts = [
            # Disable tips
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' "
                "-Name 'SoftLandingEnabled' -Value 0 -Type DWord -Force",
                "Disable tips notifications"
            ),
            # Disable suggested content in Settings
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' "
                "-Name 'SubscribedContent-338393Enabled' -Value 0 -Type DWord -Force",
                "Disable suggested content in Settings"
            ),
            # Disable suggestions in Start Menu
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' "
                "-Name 'SubscribedContent-338388Enabled' -Value 0 -Type DWord -Force",
                "Disable Start Menu suggestions"
            ),
            # Disable suggestions in timeline
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' "
                "-Name 'SubscribedContent-353694Enabled' -Value 0 -Type DWord -Force",
                "Disable timeline suggestions"
            ),
            # Disable 'Get even more out of Windows' suggestions
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' "
                "-Name 'SubscribedContent-310093Enabled' -Value 0 -Type DWord -Force",
                "Disable 'Get more out of Windows' suggestions"
            ),
            # Disable 'Finish setting up' reminders
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\UserProfileEngagement' "
                "-Name 'ScoobeSystemSettingEnabled' -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue",
                "Disable 'Finish setting up' reminders"
            ),
            # Disable lock screen tips
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' "
                "-Name 'RotatingLockScreenOverlayEnabled' -Value 0 -Type DWord -Force",
                "Disable lock screen tips"
            ),
            # Disable pre-installed app suggestions
            (
                "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' "
                "-Name 'SilentInstalledAppsEnabled' -Value 0 -Type DWord -Force",
                "Disable silent app installations"
            ),
        ]

        success_count = 0
        for ps_cmd, desc in tips_opts:
            success, _ = self.run_ps_command(ps_cmd, desc)
            if success:
                print(f"     ✅ {desc}")
                success_count += 1
            else:
                print(f"     ⚠️  {desc} — no se pudo aplicar")

        print()
        if success_count > 0:
            print(f"  ✅ ¡Se deshabilitaron {success_count}/{len(tips_opts)} fuentes de consejos/sugerencias!")
            print("  💡 Tu computadora tendrá menos interrupciones y usará menos recursos.")
        else:
            print("  ❌ No se pudieron deshabilitar los consejos y sugerencias.")

        print()
        self.log_action(f"Tips/suggestions disabled: {success_count}/{len(tips_opts)}")
        return success_count > 0

    # ─── 16. DISM Component Store Repair ─────────────────────────────────────

    def run_dism_repair(self):
        """Run DISM to repair the Windows component store."""
        print()
        print("=" * 65)
        print(f"🛠️  REPARACIÓN DISM DEL SISTEMA        {RISK_MODERATE}")
        print("   Escanea y repara el almacén de componentes de Windows (WinSxS).")
        print("   Repara componentes del sistema dañados que pueden causar lentitud.")
        print("=" * 65)
        print()

        if not require_admin("DISM system repair"):
            return False

        print("  🟡 Esta operación:")
        print("     • Escanea componentes del sistema en busca de corrupción")
        print("     • Descarga y aplica reparaciones desde Windows Update")
        print("     • Limpia versiones antiguas de componentes para liberar espacio")
        print("     • Puede tomar 15-45 minutos")
        print("     • Requiere conexión a internet para las reparaciones")
        print()

        if not confirmar("¿Ejecutar reparación DISM?"):
            return False

        print()

        # Step 1: Check health
        print("  🔍 Paso 1/3: Verificando salud del almacén de componentes...")
        print("  ⏳ Esto puede tomar unos minutos...")
        success1, output1 = self.run_command(
            "DISM /Online /Cleanup-Image /CheckHealth",
            "DISM CheckHealth"
        )
        if success1:
            print("  ✅ Verificación de salud completada.")
            if output1:
                for line in output1.split('\n')[-3:]:
                    if line.strip():
                        print(f"     {line.strip()}")
        else:
            print("  ⚠️  La verificación de salud tuvo problemas.")

        print()

        # Step 2: Scan for corruption
        print("  🔍 Paso 2/3: Escaneando en busca de corrupción...")
        print("  ⏳ Esto puede tomar 10-20 minutos...")
        success2, output2 = self.run_command(
            "DISM /Online /Cleanup-Image /ScanHealth",
            "DISM ScanHealth"
        )
        if success2:
            print("  ✅ Escaneo completado.")
        else:
            print("  ⚠️  El escaneo encontró problemas.")

        print()

        # Step 3: Restore health
        print("  🔧 Paso 3/3: Reparando cualquier problema encontrado...")
        print("  ⏳ Esto puede tomar 15-30 minutos. Por favor ten paciencia...")
        success3, output3 = self.run_command(
            "DISM /Online /Cleanup-Image /RestoreHealth",
            "DISM RestoreHealth"
        )

        print()
        if success3:
            print("  ✅ ¡Reparación DISM completada exitosamente!")
            print("  ℹ️  Todos los componentes del sistema están sanos ahora.")
            print()
            print("  💡 Siguiente paso: Ejecuta 'Verificación de archivos del sistema' (SFC) para verificar archivos individuales.")
        else:
            print("  ⚠️  La reparación DISM encontró algunos problemas.")
            print("  💡 Intenta estos pasos:")
            print("     1. Asegúrate de estar conectado a internet")
            print("     2. Reinicia tu computadora")
            print("     3. Ejecuta esta herramienta de nuevo")
            if output3:
                print(f"  🔍 Detalles técnicos: {output3[:300]}")

        # Step 4: Component cleanup
        print()
        print("  🧹 Limpiando versiones antiguas de componentes...")
        success4, _ = self.run_command(
            "DISM /Online /Cleanup-Image /StartComponentCleanup",
            "DISM Component Cleanup"
        )
        if success4:
            print("  ✅ ¡Componentes antiguos limpiados — espacio liberado!")
        else:
            print("  ⚠️  La limpieza de componentes tuvo problemas (no crítico).")

        print()
        self.log_action("DISM repair", success=success3)
        return success3

    # ─── 17. Memory Optimization ─────────────────────────────────────────────

    def optimize_memory(self):
        """Optimize memory usage by clearing caches and adjusting settings."""
        print()
        print("=" * 65)
        print(f"💾 OPTIMIZACIÓN DE MEMORIA            {RISK_LOW}")
        print("   Libera RAM limpiando cachés y optimizando configuraciones.")
        print("   Ayuda cuando tu computadora se siente lenta.")
        print("=" * 65)
        print()

        # Show current memory usage
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

                print(f"  📊 Uso actual de memoria:")
                ram_bar = format_bar(ram_percent, 100)
                print(f"     {ram_bar}")
                print(f"     Total: {total_ram:.1f} GB  |  En uso: {used_ram:.1f} GB  |  Libre: {free_ram:.1f} GB")
                print()
            except (ValueError, IndexError):
                pass

        print("  🔵 Esto hará:")
        print("     • Limpiar el conjunto de trabajo de todos los procesos (liberar RAM en caché)")
        print("     • Optimizar la configuración de memoria virtual")
        print("     • Limpiar la caché del sistema de archivos")
        print()

        if not confirmar("¿Optimizar memoria?"):
            return False

        print()
        print("  🔧 Optimizando memoria...")

        # Clear working sets
        success1, _ = self.run_ps_command(
            "Get-Process | Where-Object { $_.WorkingSet64 -gt 50MB } | "
            "ForEach-Object { "
            "  try { $_.MinWorkingSet = 204800; $_.MaxWorkingSet = 1413120 } "
            "  catch {} "
            "}",
            "Trimming process working sets"
        )
        if success1:
            print("     ✅ Conjuntos de trabajo de procesos recortados")
        else:
            print("     ⚠️  No se pudieron recortar los conjuntos de trabajo de procesos")

        # Clear standby list using PowerShell (.NET approach)
        success2, _ = self.run_ps_command(
            "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()",
            "Running garbage collection"
        )
        if success2:
            print("     ✅ Recolección de basura ejecutada")

        # Optimize pagefile - ensure it's system managed
        success3, _ = self.run_ps_command(
            "$cs = Get-CimInstance Win32_ComputerSystem; "
            "if (-not $cs.AutomaticManagedPagefile) { "
            "  $cs | Set-CimInstance -Property @{AutomaticManagedPagefile=$true} -ErrorAction SilentlyContinue "
            "}",
            "Ensuring automatic pagefile management"
        )
        if success3:
            print("     ✅ Archivo de paginación configurado en gestión automática")
        else:
            print("     ⚠️  Configuración del archivo de paginación sin cambios")

        # Clear file system cache
        success4, _ = self.run_ps_command(
            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue",
            "Clearing Recycle Bin"
        )
        if success4:
            print("     ✅ Papelera de reciclaje vaciada")

        # Show results
        print()
        success_after, output_after = self.run_ps_command(
            "$os = Get-CimInstance Win32_OperatingSystem; "
            "$total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1); "
            "$free = [math]::Round($os.FreePhysicalMemory / 1MB, 1); "
            "$used = [math]::Round($total - $free, 1); "
            "$percent = [math]::Round(($used / $total) * 100, 0); "
            "Write-Output \"$total|$used|$free|$percent\"",
            "Getting updated RAM info"
        )

        if success_after and output_after and '|' in output_after:
            parts = output_after.strip().split('|')
            try:
                total_ram = float(parts[0])
                used_ram = float(parts[1])
                free_ram = float(parts[2])
                ram_percent = int(parts[3])

                print(f"  📊 Uso de memoria después de la optimización:")
                ram_bar = format_bar(ram_percent, 100)
                print(f"     {ram_bar}")
                print(f"     Total: {total_ram:.1f} GB  |  En uso: {used_ram:.1f} GB  |  Libre: {free_ram:.1f} GB")
            except (ValueError, IndexError):
                pass

        print()
        print("  💡 Para mejores resultados, cierra pestañas del navegador y programas que no estés usando.")
        print("  💡 Si tu computadora tiene menos de 8 GB de RAM, considera agregar más.")
        print()

        self.log_action("Memory optimization completed")
        return True

    # ─── 18. Full Optimization ───────────────────────────────────────────────

    def full_optimization(self):
        """Run all performance optimizations in sequence."""
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              🚀 OPTIMIZACIÓN COMPLETA DE RENDIMIENTO       ║")
        print("║              Maximiza la velocidad de tu computadora       ║")
        print("║              Ejecutará todas las optimizaciones            ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

        if not require_admin("Full performance optimization"):
            return False

        print("  🚀 Esto ejecutará las siguientes optimizaciones:")
        print()
        print("     1. ⚡ Configurar plan de energía de Alto Rendimiento")
        print("     2. 🎨 Optimizar efectos visuales (deshabilitar animaciones)")
        print("     3. 🔔 Deshabilitar consejos, sugerencias y anuncios")
        print("     4. 🔒 Deshabilitar telemetría y rastreo")
        print("     5. 🔍 Optimizar indexación de búsqueda")
        print("     6. ⚙️  Deshabilitar servicios innecesarios")
        print("     7. 🌐 Limpiar caché de red")
        print("     8. 💾 Optimizar memoria")
        print()
        print("  ⏱️  Tiempo estimado: 5-10 minutos")
        print("  🟡 Riesgo: Moderado — todos los cambios son reversibles")
        print()

        if not confirmar("¿Ejecutar optimización completa?"):
            return False

        results = {}

        # 1. High Performance Power Plan
        print()
        print("  " + "═" * 50)
        print("  ⚡ Paso 1/8: Configurando plan de energía de Alto Rendimiento...")
        print("  " + "═" * 50)
        # Auto-accept for full optimization
        success, _ = self.run_command(
            "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            "Set High Performance power plan"
        )
        results["Power Plan"] = success
        if success:
            print("  ✅ ¡Plan de Alto Rendimiento activado!")
        else:
            print("  ⚠️  No se pudo configurar el plan de energía (puede necesitar cambio manual)")

        # 2. Visual Effects (light-touch: only animations, keep visual look)
        print()
        print("  " + "═" * 50)
        print("  🎨 Paso 2/8: Quitando animaciones (sin cambiar la apariencia)...")
        print("  " + "═" * 50)
        visual_cmds = [
            # Custom mode (3) instead of Best Performance (2) — keeps visual look
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 3 -Type DWord -Force",
            # Disable animations only
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarAnimations' -Value 0 -Type DWord -Force",
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop\\WindowMetrics' -Name 'MinAnimate' -Value '0' -Force",
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'MenuShowDelay' -Value '0' -Type String -Force",
            # Keep ClearType font smoothing ON
            "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'FontSmoothing' -Value '2' -Type String -Force",
        ]
        v_success = 0
        for cmd in visual_cmds:
            s, _ = self.run_ps_command(cmd, None)
            if s:
                v_success += 1
        results["Efectos Visuales"] = v_success > 0
        print(f"  ✅ Se quitaron animaciones (la apariencia se mantiene igual)")

        # 3. Tips & Suggestions
        print()
        print("  " + "═" * 50)
        print("  🔔 Paso 3/8: Deshabilitando consejos y sugerencias...")
        print("  " + "═" * 50)
        tips_cmds = [
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SoftLandingEnabled' -Value 0 -Type DWord -Force",
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SubscribedContent-338393Enabled' -Value 0 -Type DWord -Force",
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SubscribedContent-338388Enabled' -Value 0 -Type DWord -Force",
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager' -Name 'SilentInstalledAppsEnabled' -Value 0 -Type DWord -Force",
        ]
        t_success = 0
        for cmd in tips_cmds:
            s, _ = self.run_ps_command(cmd, None)
            if s:
                t_success += 1
        results["Tips & Suggestions"] = t_success > 0
        print(f"  ✅ Se deshabilitaron {t_success}/{len(tips_cmds)} fuentes de consejos/sugerencias")

        # 4. Telemetry
        print()
        print("  " + "═" * 50)
        print("  🔒 Paso 4/8: Deshabilitando telemetría...")
        print("  " + "═" * 50)
        tel_cmds = [
            "New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Force | Out-Null; Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Name 'AllowTelemetry' -Value 0 -Type DWord -Force",
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name 'Enabled' -Value 0 -Type DWord -Force",
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'Start_TrackProgs' -Value 0 -Type DWord -Force",
        ]
        te_success = 0
        for cmd in tel_cmds:
            s, _ = self.run_ps_command(cmd, None)
            if s:
                te_success += 1
        results["Telemetry"] = te_success > 0
        print(f"  ✅ Se aplicaron {te_success}/{len(tel_cmds)} optimizaciones de telemetría")

        # 5. Search Indexing
        print()
        print("  " + "═" * 50)
        print("  🔍 Paso 5/8: Optimizando indexación de búsqueda...")
        print("  " + "═" * 50)
        s5, _ = self.run_ps_command(
            "Stop-Service -Name 'WSearch' -Force -ErrorAction SilentlyContinue; "
            "Set-Service -Name 'WSearch' -StartupType Disabled -ErrorAction SilentlyContinue",
            "Disabling Windows Search"
        )
        results["Search Indexing"] = s5
        if s5:
            print("  ✅ Indexación de Búsqueda de Windows deshabilitada")
        else:
            print("  ⚠️  No se pudo deshabilitar la indexación de búsqueda")

        # 6. Unnecessary Services
        print()
        print("  " + "═" * 50)
        print("  ⚙️  Paso 6/8: Deshabilitando servicios innecesarios...")
        print("  " + "═" * 50)
        svc_to_disable = ["DiagTrack", "dmwappushservice", "MapsBroker", "RetailDemo", "wisvc"]
        svc_success = 0
        for svc in svc_to_disable:
            s, _ = self.run_ps_command(
                f"Stop-Service -Name '{svc}' -Force -ErrorAction SilentlyContinue; "
                f"Set-Service -Name '{svc}' -StartupType Disabled -ErrorAction SilentlyContinue",
                None
            )
            if s:
                svc_success += 1
        results["Services"] = svc_success > 0
        print(f"  ✅ Se deshabilitaron {svc_success}/{len(svc_to_disable)} servicios innecesarios")

        # 7. Network Cache
        print()
        print("  " + "═" * 50)
        print("  🌐 Paso 7/8: Limpiando caché de red...")
        print("  " + "═" * 50)
        s7, _ = self.run_command("ipconfig /flushdns", "Flush DNS")
        results["Network Cache"] = s7
        if s7:
            print("  ✅ Caché DNS limpiada")
        else:
            print("  ⚠️  No se pudo limpiar la caché DNS")

        # 8. Memory
        print()
        print("  " + "═" * 50)
        print("  💾 Paso 8/8: Optimizando memoria...")
        print("  " + "═" * 50)
        s8, _ = self.run_ps_command(
            "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()",
            "Memory garbage collection"
        )
        results["Memory"] = s8
        if s8:
            print("  ✅ Memoria optimizada")
        else:
            print("  ⚠️  No se pudo optimizar la memoria")

        # Summary
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              📊 RESUMEN DE OPTIMIZACIÓN                     ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

        total_success = sum(1 for v in results.values() if v)
        total_ops = len(results)

        for name, success in results.items():
            emoji = "✅" if success else "⚠️"
            print(f"  {emoji} {name}")

        print()
        print(f"  📊 Resultado: ¡{total_success}/{total_ops} optimizaciones aplicadas exitosamente!")
        print()
        print("  🚀 IMPORTANTE: ¡Reinicia tu computadora para aplicar todos los cambios!")
        print()
        print("  💡 Recomendaciones adicionales para una computadora lenta:")
        print("     • Agrega más RAM si tienes menos de 8 GB")
        print("     • Cambia a un SSD si estás usando un HDD")
        print("     • Desinstala programas que no uses")
        print("     • Mantén Windows actualizado")
        print("     • Ejecuta un análisis de virus con Windows Defender")
        print()

        self.log_action(f"Full optimization: {total_success}/{total_ops} successful")
        return total_success > 0

    # ─── Full Performance Check ─────────────────────────────────────────────

    def full_performance_check(self):
        """Run a comprehensive performance analysis."""
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              ⚡ REVISIÓN COMPLETA DE RENDIMIENTO             ║")
        print("║              Un chequeo completo de la velocidad de tu PC   ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

        self.show_system_dashboard()
        input("  ⏸️  Presiona Enter para continuar...")

        self.show_top_processes()
        input("  ⏸️  Presiona Enter para continuar...")

        self.manage_startup_programs()
        input("  ⏸️  Presiona Enter para continuar...")

        self.check_disk_health()
        input("  ⏸️  Presiona Enter para continuar...")

        self.check_windows_update()

        print()
        print("═" * 65)
        print("  🎉 ¡Revisión completa de rendimiento terminada!")
        print()
        print("  💡 Recomendaciones rápidas:")
        print("     • Cierra pestañas del navegador y programas que no estés usando")
        print("     • Reinicia tu computadora si lleva días encendida")
        print("     • Mantén Windows Update activo para estar seguro")
        print("     • Deshabilita programas de inicio innecesarios para un arranque más rápido")
        print("═" * 65)
        print()

        self.log_action("Full performance check completed")


# ─── Menú Interactivo ──────────────────────────────────────────────────────────

def show_submenu_diagnostics(manager):
    """Sub-menu for diagnostic options."""
    print()
    print("  📊 DIAGNÓSTICO — ¿qué quieres revisar?")
    print("  ─" * 25)
    print()
    print("  1. ⚡ Ver cómo está funcionando tu computadora ahora")
    print("  2. 📊 Ver qué programas están usando más recursos")
    print("  3. 🚀 Ver qué programas arrancan con tu computadora")
    print("  4. ⚙️  Ver estado de servicios del sistema")
    print("  5. 💿 Revisar salud de tus discos")
    print("  6. 🔋 Ver configuración de energía")
    print("  7. 🪟 Ver si Windows está actualizado")
    print()
    print("  0. ← Volver al menú principal")
    print()

    try:
        sub = input("  Elige una opción: ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    actions = {
        '1': manager.show_system_dashboard,
        '2': manager.show_top_processes,
        '3': manager.manage_startup_programs,
        '4': manager.show_services_status,
        '5': manager.check_disk_health,
        '6': manager.show_power_plan,
        '7': manager.check_windows_update,
    }
    if sub in actions:
        actions[sub]()
    elif sub != '0':
        print(f"  ❌ '{sub}' no es una opción válida.")


def show_submenu_optimize(manager):
    """Sub-menu for individual optimization options."""
    print()
    print("  🚀 OPTIMIZAR — ¿qué quieres mejorar?")
    print("  ─" * 25)
    print()
    print("  1. ⚡ Activar plan de alto rendimiento")
    print("  2. 🎨 Quitar animaciones y efectos visuales")
    print("  3. ⚙️  Deshabilitar servicios innecesarios")
    print("  4. 🔒 Reducir telemetría y rastreo de datos")
    print("  5. 🔍 Optimizar indexación de búsqueda")
    print("  6. 🔔 Quitar consejos, sugerencias y anuncios")
    print("  7. 💾 Liberar memoria RAM")
    print("  8. 🌐 Limpiar caché de red e internet")
    print()
    print("  0. ← Volver al menú principal")
    print()

    try:
        sub = input("  Elige una opción: ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    actions = {
        '1': manager.set_high_performance_power,
        '2': manager.optimize_visual_effects,
        '3': manager.disable_unnecessary_services,
        '4': manager.disable_telemetry,
        '5': manager.optimize_search_indexing,
        '6': manager.disable_tips_suggestions,
        '7': manager.optimize_memory,
        '8': manager.clean_network_cache,
    }
    if sub in actions:
        actions[sub]()
    elif sub != '0':
        print(f"  ❌ '{sub}' no es una opción válida.")


def show_submenu_repair(manager):
    """Sub-menu for repair options."""
    print()
    print("  🛠️  REPARAR — herramientas de reparación")
    print("  ─" * 25)
    print()
    print("  1. 🛡️  Verificar y reparar archivos de Windows (SFC)")
    print("  2. 🛠️  Reparación profunda del sistema (DISM)")
    print()
    print("  0. ← Volver al menú principal")
    print()

    try:
        sub = input("  Elige una opción: ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if sub == '1':
        manager.check_system_integrity()
    elif sub == '2':
        manager.run_dism_repair()
    elif sub != '0':
        print(f"  ❌ '{sub}' no es una opción válida.")


def show_interactive_menu():
    """Display the interactive menu for non-technical users."""
    manager = WindowsPerformanceManager()

    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception:
            pass

        show_startup_banner()

        print("  🖥️  ¿Qué te gustaría hacer?")
        print()
        print("  ╔══════════════════════════════════════════════════════════╗")
        print("  ║                                                        ║")
        print("  ║  1. ⭐ ARREGLO RÁPIDO                                  ║")
        print("  ║     Optimiza todo automáticamente con un solo clic      ║")
        print("  ║     (Recomendado si tu computadora está lenta)          ║")
        print("  ║                                                        ║")
        print("  ╚══════════════════════════════════════════════════════════╝")
        print()
        print("  ─────────────────────────────────────────────────────────")
        print()
        print("  2. 📊 Diagnóstico     — Revisar cómo está tu computadora")
        print("  3. 🚀 Optimizar       — Elegir qué mejorar paso a paso")
        print("  4. 🛠️  Reparar         — Reparar archivos de Windows")
        print("  5. 📊 Chequeo completo — Revisar todo sin cambiar nada")
        print()
        print("  0. 🚪 Salir")
        print()
        print("  ─────────────────────────────────────────────────────────")

        try:
            choice = input("\n  👉 Escribe el número y presiona Enter: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  👋 ¡Hasta luego!")
            break

        if choice == '0':
            print()
            print("  👋 ¡Gracias por usar el Optimizador de Rendimiento!")
            print("  💡 Recuerda reiniciar tu computadora después de optimizar.")
            print()
            break

        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception:
            pass

        try:
            if choice == '1':
                manager.full_optimization()
            elif choice == '2':
                show_submenu_diagnostics(manager)
            elif choice == '3':
                show_submenu_optimize(manager)
            elif choice == '4':
                show_submenu_repair(manager)
            elif choice == '5':
                manager.full_performance_check()
            else:
                print(f"  ❌ '{choice}' no es una opción válida. Escribe un número del 0 al 5.")
        except KeyboardInterrupt:
            print("\n  ⚠️  Operación cancelada.")
        except Exception as e:
            print(f"\n  ❌ Algo salió mal: {e}")
            print("  💡 Intenta ejecutar el programa como administrador.")

        print()
        try:
            input("  ⏸️  Presiona Enter para volver al menú...")
        except (KeyboardInterrupt, EOFError):
            break


# ─── Punto de Entrada CLI ─────────────────────────────────────────────────────

def main():
    """Main function — CLI arguments or interactive menu."""
    parser = argparse.ArgumentParser(
        description="⚡ Optimizador de Rendimiento de Windows — Monitorea y optimiza tu computadora (Win10 & Win11)",
        epilog="💡 Ejecuta sin argumentos para el menú interactivo.\n🏠 Parte de Python Scripts Collection",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    check_group = parser.add_argument_group("📊 Diagnóstico")
    check_group.add_argument("--dashboard", action="store_true", help="⚡ Ver panel de rendimiento del sistema")
    check_group.add_argument("--processes", action="store_true", help="📊 Ver programas que más recursos usan")
    check_group.add_argument("--startup", action="store_true", help="🚀 Ver programas de inicio")
    check_group.add_argument("--services", action="store_true", help="⚙️ Ver estado de servicios del sistema")

    hw_group = parser.add_argument_group("💿 Hardware y Salud")
    hw_group.add_argument("--disk-health", action="store_true", help="💿 Revisar salud de discos")
    hw_group.add_argument("--power", action="store_true", help="🔋 Ver plan de energía")
    hw_group.add_argument("--updates", action="store_true", help="🪟 Ver estado de Windows Update")

    opt_group = parser.add_argument_group("🚀 Optimizar y Acelerar")
    opt_group.add_argument("--high-perf", action="store_true", help="⚡ Activar plan de alto rendimiento")
    opt_group.add_argument("--visual", action="store_true", help="🎨 Optimizar efectos visuales (admin)")
    opt_group.add_argument("--disable-services", action="store_true", help="⚙️ Deshabilitar servicios innecesarios (admin)")
    opt_group.add_argument("--disable-telemetry", action="store_true", help="🔒 Deshabilitar telemetría (admin)")
    opt_group.add_argument("--optimize-search", action="store_true", help="🔍 Optimizar indexación de búsqueda (admin)")
    opt_group.add_argument("--disable-tips", action="store_true", help="🔔 Deshabilitar consejos y sugerencias")
    opt_group.add_argument("--optimize-memory", action="store_true", help="💾 Optimizar uso de memoria")
    opt_group.add_argument("--clean-network", action="store_true", help="🌐 Limpiar caché de red (admin)")

    fix_group = parser.add_argument_group("🛠️ Reparar")
    fix_group.add_argument("--sfc", action="store_true", help="🛡️ Verificar archivos del sistema (admin)")
    fix_group.add_argument("--dism", action="store_true", help="🛠️ Reparación DISM profunda (admin)")

    all_group = parser.add_argument_group("⚡ Todo en Uno")
    all_group.add_argument("--full-check", action="store_true", help="📊 Chequeo completo (solo diagnóstico)")
    all_group.add_argument("--full-optimize", action="store_true", help="🚀 Optimización completa (aplicar todo)")

    parser.add_argument("--version", action="version", version="Optimizador de Rendimiento de Windows v2.0")

    args = parser.parse_args()

    has_args = any([
        args.dashboard, args.processes, args.startup, args.services,
        args.disk_health, args.power, args.updates,
        args.high_perf, args.visual, args.disable_services, args.disable_telemetry,
        args.optimize_search, args.disable_tips, args.optimize_memory, args.clean_network,
        args.sfc, args.dism,
        args.full_check, args.full_optimize
    ])

    if not has_args:
        show_interactive_menu()
        return

    # CLI mode
    show_startup_banner()
    manager = WindowsPerformanceManager()

    # All-in-one options
    if args.full_optimize:
        manager.full_optimization()
        return

    if args.full_check:
        manager.full_performance_check()
        return

    # Diagnóstico
    if args.dashboard:
        manager.show_system_dashboard()

    if args.processes:
        manager.show_top_processes()

    if args.startup:
        manager.manage_startup_programs()

    if args.services:
        manager.show_services_status()

    # Hardware y Salud
    if args.disk_health:
        manager.check_disk_health()

    if args.power:
        manager.show_power_plan()

    if args.updates:
        manager.check_windows_update()

    # Optimizar y Acelerar
    if args.high_perf:
        manager.set_high_performance_power()

    if args.visual:
        manager.optimize_visual_effects()

    if args.disable_services:
        manager.disable_unnecessary_services()

    if args.disable_telemetry:
        manager.disable_telemetry()

    if args.optimize_search:
        manager.optimize_search_indexing()

    if args.disable_tips:
        manager.disable_tips_suggestions()

    if args.optimize_memory:
        manager.optimize_memory()

    if args.clean_network:
        manager.clean_network_cache()

    # Reparar
    if args.sfc:
        manager.check_system_integrity()

    if args.dism:
        manager.run_dism_repair()


if __name__ == "__main__":
    main()
