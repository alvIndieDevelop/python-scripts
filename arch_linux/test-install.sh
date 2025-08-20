#!/bin/bash

# Test script for Arch Linux Maintenance Script
# This script tests the installation without actually installing

echo "🧪 Testing Arch Linux Maintenance Script Installation"
echo "=================================================="
echo ""

# Check if main script exists
if [ -f "arch_maintenance.py" ]; then
    echo "✅ Main script found: arch_maintenance.py"
else
    echo "❌ Main script not found: arch_maintenance.py"
    exit 1
fi

# Check if install script exists
if [ -f "install.sh" ]; then
    echo "✅ Install script found: install.sh"
else
    echo "❌ Install script not found: install.sh"
    exit 1
fi

# Check if uninstall script exists
if [ -f "uninstall.sh" ]; then
    echo "✅ Uninstall script found: uninstall.sh"
else
    echo "❌ Uninstall script not found: uninstall.sh"
    exit 1
fi

# Check if README exists
if [ -f "README.md" ]; then
    echo "✅ README found: README.md"
else
    echo "❌ README not found: README.md"
fi

# Check script permissions
if [ -x "install.sh" ]; then
    echo "✅ Install script is executable"
else
    echo "❌ Install script is not executable"
fi

if [ -x "uninstall.sh" ]; then
    echo "✅ Uninstall script is executable"
else
    echo "❌ Uninstall script is not executable"
fi

# Test Python script syntax
echo ""
echo "🔍 Testing Python script syntax..."
if python3 -m py_compile arch_maintenance.py; then
    echo "✅ Python script syntax is valid"
else
    echo "❌ Python script has syntax errors"
    exit 1
fi

# Test Python script help
echo ""
echo "🔍 Testing Python script help..."
if python3 arch_maintenance.py --help > /dev/null 2>&1; then
    echo "✅ Python script help works correctly"
else
    echo "❌ Python script help has errors"
fi

# Check dependencies
echo ""
echo "🔍 Checking system dependencies..."
DEPENDENCIES=("python3" "sudo" "bash")
MISSING_DEPS=()

for dep in "${DEPENDENCIES[@]}"; do
    if command -v "$dep" &> /dev/null; then
        echo "✅ $dep is available"
    else
        echo "❌ $dep is missing"
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Missing dependencies: ${MISSING_DEPS[*]}"
    echo "💡 Install them before running the installer"
else
    echo ""
    echo "🎉 All dependencies are available!"
fi

# Check if we're on Arch Linux
echo ""
echo "🔍 Checking system compatibility..."
if grep -q "Arch Linux" /etc/os-release 2>/dev/null; then
    echo "✅ Running on Arch Linux"
else
    echo "⚠️  Not running on Arch Linux (may still work)"
fi

echo ""
echo "🧪 Test completed!"
echo ""
echo "💡 To install, run: ./install.sh"
echo "💡 To uninstall, run: ./uninstall.sh"
echo "💡 To test the script: python3 arch_maintenance.py --help"
echo ""
echo "💡 After installation, you can use:"
echo "   • archm-maintenance --help"
echo "   • archm --help" 