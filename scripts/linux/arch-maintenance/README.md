# 🐧 Arch Linux Maintenance Script

Script profesional de mantenimiento para Arch Linux con funcionalidades avanzadas de gestión del sistema, limpieza automática y recordatorios inteligentes.

**Parte de [Python Scripts & Utilities Collection](../README.md)**

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🚀 Instalación](#-instalación)
- [💻 Uso](#-uso)
- [🔧 Funcionalidades](#-funcionalidades)
- [📚 Ejemplos de Uso](#-ejemplos-de-uso)
- [⚙️ Configuración](#️-configuración)
- [🗂️ Estructura de Archivos](#️-estructura-de-archivos)
- [🔍 Troubleshooting](#-troubleshooting)
- [📞 Soporte](#-soporte)

## ✨ Características

### 🔧 **Mantenimiento del Sistema**

- **Actualización automática** de paquetes del sistema (pacman)
- **Gestión de paquetes AUR** con yay
- **Sincronización de bases de datos** de paquetes
- **Detección de actualizaciones** del kernel

### 🧹 **Limpieza y Optimización**

- **Limpieza de caché** de paquetes (pacman y AUR)
- **Eliminación de paquetes huérfanos**
- **Limpieza de logs del sistema** (systemd)
- **Actualización de base de datos** locate
- **Análisis de uso de disco** y archivos grandes

### 🏥 **Monitoreo de Salud**

- **Estado de servicios** del sistema
- **Monitoreo de carga** del sistema
- **Análisis de memoria** y uso de CPU
- **Verificación de espacio** en disco
- **Comprobación de conectividad** de red

### ⏰ **Recordatorios Inteligentes**

- **Recordatorios automáticos** configurables
- **Frecuencias personalizables** (diario, semanal, mensual)
- **Integración con shell** (bash, zsh)
- **Notificaciones visuales** atractivas

### 🎨 **Interfaz de Usuario**

- **Menú interactivo** fácil de usar
- **Comandos de línea** directos
- **Logging detallado** de todas las operaciones
- **Feedback visual** con emojis y colores

## 🚀 Instalación

### **Requisitos Previos**

- **Sistema**: Arch Linux (recomendado) o derivados
- **Python**: Python 3.7 o superior
- **Dependencias**: sudo, pacman, yay (opcional)
- **Shell**: Bash, Zsh, o compatible

### **Paso 1: Descargar el Script**

```bash
# Clonar el repositorio principal
git clone https://github.com/alvIndieDevelop/python-scripts.git
cd python-scripts/scripts/linux/arch-maintenance

# O navegar desde el repositorio clonado
cd scripts/linux/arch-maintenance
```

### **Paso 2: Instalar en el Sistema**

```bash
# Hacer ejecutable e instalar
chmod +x arch_maintenance.py
python3 arch_maintenance.py --install
```

### **Paso 3: Verificar la Instalación**

```bash
# Verificar que esté instalado correctamente
python3 arch_maintenance.py --check-install

# Probar el comando corto
archm --help
```

### **Paso 4: Configurar Recordatorios**

Durante la instalación, el script te preguntará:

- **Frecuencia de recordatorios** (diario, semanal, quincenal, mensual, personalizado)
- **Si quieres ejecutar mantenimiento ahora** para probar
- **Configuración del shell** (se actualiza automáticamente)

## 💻 Uso

### **Comandos Principales**

#### **Mantenimiento Completo**

```bash
# Ejecutar todo el mantenimiento del sistema
archm-maintenance --full

# O usando el comando corto
archm --full
```

#### **Operaciones Específicas**

```bash
# Solo actualizar paquetes del sistema
archm-maintenance --update

# Solo actualizar paquetes AUR
archm-maintenance --aur

# Solo limpiar caché y paquetes huérfanos
archm-maintenance --clean

# Solo verificar salud del sistema
archm-maintenance --health

# Solo analizar uso de disco
archm-maintenance --disk

# Solo limpiar logs del sistema
archm-maintenance --logs
```

#### **Información y Estado**

```bash
# Mostrar estado general del sistema
archm-maintenance --status

# Mostrar ayuda completa
archm-maintenance --help

# Verificar estado de instalación
archm-maintenance --check-install
```

#### **Menú Interactivo**

```bash
# Lanzar menú interactivo
archm-maintenance

# O simplemente
archm
```

### **Comandos Cortos Disponibles**

```bash
archm --full      # Mantenimiento completo
archm --update    # Solo actualización
archm --clean     # Solo limpieza
archm --health    # Solo verificación de salud
archm --help      # Ayuda
```

## 🔧 Funcionalidades

### **Sistema de Pestañas Interactivo**

El script incluye un menú numerado con opciones:

1. **Full System Maintenance** - Mantenimiento completo
2. **System Update Only** - Solo actualización del sistema
3. **AUR Packages Update** - Solo actualización de paquetes AUR
4. **Clean Package Cache** - Limpieza de caché
5. **Clean Systemd Logs** - Limpieza de logs del sistema
6. **Update Locate Database** - Actualizar base de datos locate
7. **Check System Health** - Verificar salud del sistema
8. **Check Disk Usage** - Analizar uso de disco
9. **Show System Status** - Mostrar estado del sistema
10. **Install Script to System** - Instalar script en el sistema
11. **Uninstall Script from System** - Desinstalar script del sistema
12. **Check Installation Status** - Verificar estado de instalación

### **Logging Inteligente**

- **Archivo de log**: `~/.arch_maintenance.log`
- **Timestamps** para todas las operaciones
- **Niveles de log** (INFO, WARNING, ERROR, SUCCESS)

### **Seguridad y Confirmaciones**

- **Confirmaciones** para operaciones críticas
- **Modo dry-run** para ver qué se haría
- **Verificación de permisos** antes de ejecutar

## 📚 Ejemplos de Uso

### **Mantenimiento Diario**

```bash
# Verificación rápida del sistema
archm --health

# Actualización de paquetes si es necesario
archm --update
```

### **Mantenimiento Semanal**

```bash
# Mantenimiento completo semanal
archm --full

# Verificar estado después del mantenimiento
archm --status
```

### **Limpieza de Emergencia**

```bash
# Cuando el disco esté lleno
archm --clean
archm --disk
archm --logs
```

### **Verificación de Instalación**

```bash
# Verificar que todo esté funcionando
archm --check-install

# Probar funcionalidades básicas
archm --status
archm --health
```

### **Mantenimiento Avanzado**

```bash
# Solo paquetes AUR
archm --aur

# Análisis detallado de disco
archm --disk

# Limpieza completa de logs
archm --logs
```

## ⚙️ Configuración

### **Recordatorios Automáticos**

#### **Frecuencias Disponibles**

- **Diario**: Cada 24 horas
- **Semanal**: Cada 7 días
- **Quincenal**: Cada 14 días
- **Mensual**: Cada 28 días
- **Personalizado**: Días específicos que elijas

#### **Cómo Funcionan**

1. **Cada vez que abras una terminal**, el script verifica si es momento del mantenimiento
2. **Si es momento**, te muestra un recordatorio visual atractivo
3. **Te pregunta** si quieres ejecutar mantenimiento ahora
4. **Si no**, te recuerda cuándo aparecerá de nuevo

#### **Personalización**

```bash
# Editar configuración de recordatorios
nano ~/.config/arch-maintenance/maintenance-reminder.sh

# Cambiar frecuencia manualmente
# Cambiar el valor de REMINDER_DAYS
```

### **Configuración del Shell**

El script actualiza automáticamente:

- `~/.bashrc` (para Bash)
- `~/.zshrc` (para Zsh)
- `~/.profile` (para otros shells)

**Añade al PATH**:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Configura recordatorios**:

```bash
source ~/.config/arch-maintenance/maintenance-reminder.sh
```

## 🗂️ Estructura de Archivos

### **Archivos de Instalación**

```
~/.local/bin/
├── archm-maintenance          # Script principal
└── archm                     # Comando corto (alias)

~/.config/arch-maintenance/
├── maintenance-reminder.sh   # Script de recordatorios
```

### **Archivos de Control**

```
~/.arch_maintenance.log       # Log principal de mantenimiento
~/.arch_maintenance_reminder  # Control de recordatorios
~/.arch_maintenance_status    # Estado del último mantenimiento
```

### **Archivos de Configuración del Shell**

```
~/.bashrc                     # Configuración de Bash
~/.zshrc                      # Configuración de Zsh
~/.profile                    # Configuración general
```

## 🔍 Troubleshooting

### **Problemas Comunes**

#### **El comando no se encuentra**

```bash
# Verificar que esté en el PATH
echo $PATH | grep ~/.local/bin

# Si no está, añadirlo manualmente
export PATH="$HOME/.local/bin:$PATH"

# O reiniciar la terminal
# O ejecutar:
source ~/.bashrc  # o ~/.zshrc
```

#### **Error de permisos**

```bash
# Verificar permisos del script
ls -la ~/.local/bin/archm-maintenance

# Hacer ejecutable si es necesario
chmod +x ~/.local/bin/archm-maintenance

# Verificar configuración de sudo
sudo pacman -Syu
```

#### **Recordatorios no aparecen**

```bash
# Verificar que el script esté en tu PATH
which archm-maintenance

# Verificar configuración del shell
cat ~/.bashrc | grep archm-maintenance

# Verificar archivo de recordatorios
ls -la ~/.config/arch-maintenance/

# Probar manualmente
source ~/.config/arch-maintenance/maintenance-reminder.sh
```

#### **Errores de Python**

```bash
# Verificar versión de Python
python3 --version

# Verificar dependencias
python3 -c "import subprocess, pathlib, argparse, shutil, stat"

# Instalar dependencias faltantes si es necesario
sudo pacman -S python
```

### **Logs y Debugging**

```bash
# Ver logs en tiempo real
tail -f ~/.arch_maintenance.log

# Ver últimos 50 líneas
tail -50 ~/.arch_maintenance.log

# Buscar errores específicos
grep "ERROR" ~/.arch_maintenance.log

# Ver estado del último mantenimiento
cat ~/.arch_maintenance_status
```

### **Reinstalación**

```bash
# Desinstalar completamente
archm-maintenance --uninstall

# Limpiar archivos residuales
rm -rf ~/.config/arch-maintenance
rm ~/.arch_maintenance*

# Reinstalar
python3 arch_maintenance.py --install
```

## 📞 Soporte

### **Antes de Pedir Ayuda**

1. ✅ **Revisa los logs** en `~/.arch_maintenance.log`
2. ✅ **Verifica la instalación** con `archm --check-install`
3. ✅ **Prueba comandos básicos** como `archm --status`
4. ✅ **Revisa esta documentación** completa
5. ✅ **Verifica requisitos** del sistema

### **Información Útil para Reportar Problemas**

- **Versión del script**: `archm --version`
- **Sistema operativo**: `uname -a`
- **Versión de Python**: `python3 --version`
- **Shell usado**: `echo $SHELL`
- **Logs relevantes**: Últimas líneas de `~/.arch_maintenance.log`
- **Comando que falla**: Comando exacto y error completo

### **Canales de Soporte**

- 📧 **Issues del repositorio**: Para bugs y problemas
- 📖 **Documentación**: Esta página y comentarios del código
- 🔍 **Logs del sistema**: Para debugging avanzado

## 🎯 Casos de Uso Avanzados

### **Automatización con Cron**

```bash
# Añadir a crontab para mantenimiento automático
crontab -e

# Mantenimiento completo cada domingo a las 2:00 AM
0 2 * * 0 /home/usuario/.local/bin/archm-maintenance --full

# Verificación de salud diaria a las 8:00 AM
0 8 * * * /home/usuario/.local/bin/archm-maintenance --health
```

### **Integración con Otros Scripts**

```bash
#!/bin/bash
# Script personalizado de mantenimiento

# Ejecutar mantenimiento básico
archm --update
archm --clean

# Verificar estado
archm --health

# Notificar resultado
if [ $? -eq 0 ]; then
    notify-send "Mantenimiento completado exitosamente"
else
    notify-send "Error en el mantenimiento" "Revisar logs"
fi
```

### **Monitoreo Remoto**

```bash
# Verificar estado desde otra máquina
ssh usuario@servidor "archm --status"

# Ejecutar mantenimiento remoto
ssh usuario@servidor "archm --full"
```

## 🔗 Navegación del Repositorio

- **🏠 [README Principal](../../../README.md)** - Visión general del repositorio
- **🐧 [Utilidades Linux](../README.md)** - Índice de herramientas Linux
- **🔧 [Developer Environment](../developer-environment/README.md)** - Entorno de desarrollo
- **🪟 [Utilidades Windows](../../windows/README.md)** - Herramientas para Windows

---

## 🎉 ¡Disfruta de un Sistema Arch Linux Optimizado!

---

**Versión**: 2.0  
**Autor**: alvIndieDevelop  
**Licencia**: MIT  

**¿Te gustó este script?** ⭐ Dale una estrella al repositorio y compártelo con la comunidad de Arch Linux!
