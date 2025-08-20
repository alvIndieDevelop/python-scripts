# 🚀 Arch Linux Maintenance Script

Script profesional de mantenimiento para Arch Linux con recordatorios automáticos.

## ✨ Características

- 🔧 **Mantenimiento completo del sistema**
- 📦 **Gestión de paquetes** (pacman + AUR)
- 🧹 **Limpieza automática** de caché y logs
- 🏥 **Verificación de salud** del sistema
- 💾 **Análisis de uso de disco**
- ⏰ **Recordatorios automáticos** configurables
- 🎨 **Interfaz visual atractiva** con emojis y colores

## 🚀 Instalación

### 1. Descargar el script

```bash
git clone <tu-repositorio>
cd arch-maintenance-script
```

### 2. Ejecutar el instalador

```bash
chmod +x install.sh
./install.sh
```

### 3. Seguir las instrucciones

El instalador te preguntará:

- **Frecuencia de recordatorios** (semanal, quincenal, mensual, personalizado)
- **Si quieres ejecutar mantenimiento ahora** para probar

## 💻 Uso

### Comandos principales

```bash
# Mantenimiento completo
archm-maintenance --full

# Menú interactivo
archm-maintenance

# Solo actualización del sistema
archm-maintenance --update

# Solo limpieza de caché
archm-maintenance --clean

# Ver estado del sistema
archm-maintenance --status

# Mostrar ayuda
archm-maintenance --help
```

### Comandos cortos

```bash
# Usando el alias corto
archm --help
archm --full
```

## ⏰ Recordatorios Automáticos

El script se configura automáticamente para mostrar recordatorios según la frecuencia que elijas:

- **Semanal**: Cada 7 días
- **Quincenal**: Cada 14 días
- **Mensual**: Cada 28 días
- **Personalizado**: Días que especifiques

### Cómo funcionan

1. **Cada vez que abras una terminal**, el script verifica si es momento del mantenimiento
2. **Si es momento**, te muestra un recordatorio atractivo
3. **Te pregunta** si quieres ejecutar mantenimiento ahora
4. **Si no**, te recuerda que aparecerá de nuevo en X días

## 🗂️ Estructura de Archivos

```
~/.local/bin/
├── archm-maintenance          # Script principal
└── archm                     # Comando corto

~/.config/arch-maintenance/
└── maintenance-reminder.sh  # Script de recordatorios

~/.arch_maintenance.log      # Log de mantenimiento
~/.arch_maintenance_reminder # Control de recordatorios
```

## 🔧 Desinstalación

Si quieres desinstalar el script:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## 📋 Requisitos

- **Sistema**: Arch Linux (recomendado)
- **Dependencias**: Python 3, sudo
- **Shell**: Bash, Zsh, o compatible

## 🎯 Casos de Uso

### Mantenimiento Regular

```bash
# Ejecutar mantenimiento completo semanalmente
archm-maintenance --full
```

### Verificación Rápida

```bash
# Solo verificar estado del sistema
archm-maintenance --health
```

### Limpieza de Emergencia

```bash
# Limpiar caché cuando el disco esté lleno
archm-maintenance --clean
```

## 💡 Consejos

1. **Ejecuta mantenimiento semanalmente** para mantener tu sistema optimizado
2. **Usa `--dry-run`** para ver qué se haría sin ejecutar cambios
3. **Revisa los logs** en `~/.arch_maintenance.log` para debugging
4. **Personaliza la frecuencia** de recordatorios según tus necesidades

## 🐛 Solución de Problemas

### El comando no se encuentra

```bash
# Reinicia tu terminal o ejecuta:
source ~/.bashrc  # o ~/.zshrc
```

### Error de permisos

```bash
# Asegúrate de tener sudo configurado
sudo pacman -Syu
```

### Recordatorios no aparecen

```bash
# Verifica que el script esté en tu PATH
echo $PATH | grep ~/.local/bin

# Revisa la configuración del shell
cat ~/.bashrc | grep archm-maintenance
```

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs en `~/.arch_maintenance.log`
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que el script esté en tu PATH

## 🎉 ¡Disfruta de un sistema Arch Linux bien mantenido!

---

**Versión**: 2.0  
**Autor**: Tu nombre  
**Licencia**: MIT
