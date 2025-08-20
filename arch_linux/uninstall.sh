#!/bin/bash

# Arch Linux Maintenance Script Uninstaller
# Version 1.0

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Banner de inicio
print_header "🗑️  ARCH LINUX MAINTENANCE SCRIPT UNINSTALLER"
echo ""
echo "⚠️  This will remove the Arch Linux Maintenance Script from your system"
echo "📁 All configuration files and reminders will be deleted"
echo ""

# Confirmar desinstalación
read -p "¿Estás seguro de que quieres desinstalar? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Desinstalación cancelada"
    exit 0
fi

# Directorios
INSTALL_DIR="$HOME/.local/bin"
SCRIPT_NAME="archm-maintenance"
CONFIG_DIR="$HOME/.config/arch-maintenance"
REMINDER_FILE="$HOME/.arch_maintenance_reminder"

print_status "Starting uninstallation..."

# Remover scripts
if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    rm -f "$INSTALL_DIR/$SCRIPT_NAME"
    print_status "Main script removed"
fi

if [ -L "$INSTALL_DIR/archm" ]; then
    rm -f "$INSTALL_DIR/archm"
    print_status "Short command link removed"
fi

# Remover configuración
if [ -d "$CONFIG_DIR" ]; then
    rm -rf "$CONFIG_DIR"
    print_status "Configuration directory removed"
fi

# Remover archivo de recordatorio
if [ -f "$REMINDER_FILE" ]; then
    rm -f "$REMINDER_FILE"
    print_status "Reminder file removed"
fi

# Limpiar shell RC
SHELL_RC=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

if [ -f "$SHELL_RC" ]; then
    # Remover líneas relacionadas con el script
    sed -i '/# Arch Linux Maintenance Script/,+2d' "$SHELL_RC"
    sed -i '/# Arch Linux Maintenance Reminder/,+4d' "$SHELL_RC"
    print_status "Shell configuration cleaned"
fi

print_header "🎉 DESINSTALACIÓN COMPLETADA"
echo ""
print_success "Arch Linux Maintenance Script desinstalado exitosamente!"
echo ""
echo "💡 Para completar la desinstalación:"
echo "   • Reinicia tu terminal"
echo "   • O ejecuta: source $SHELL_RC"
echo ""
echo "👋 ¡Gracias por usar Arch Linux Maintenance Script!" 