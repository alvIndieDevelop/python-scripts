# 🪟 Windows Scripts & Utilities

Scripts profesionales para gestión y mantenimiento de Windows 10 y Windows 11, diseñados para ser fáciles de usar tanto por desarrolladores como por usuarios no técnicos.

**Parte de [Python Scripts & Utilities Collection](../README.md)**

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🚀 Instalación](#-instalación)
- [💻 Uso](#-uso)
- [📦 Scripts Disponibles](#-scripts-disponibles)
- [🔍 Troubleshooting](#-troubleshooting)
- [📞 Soporte](#-soporte)

## ✨ Características

### 🎯 **Fácil de Usar**
- **Interfaz interactiva** con menú guiado paso a paso
- **Lenguaje simple** — sin jerga técnica
- **Niveles de riesgo** visuales (🟢 Seguro / 🔵 Bajo / 🟡 Moderado / 🔴 Alto)
- **Explicaciones** antes de cada acción

### 💾 **Gestión de Espacio**
- **Vista general** de todos tus discos
- **Escáner de carpetas** para encontrar qué ocupa más espacio
- **Buscador de archivos grandes** (videos, instaladores, etc.)
- **Detector de archivos duplicados** que desperdician espacio
- **Limpieza de archivos temporales** (basura del sistema)
- **Limpieza de Windows Update** (archivos de actualizaciones antiguas)

### ⚡ **Gestión de Rendimiento**
- **Dashboard del sistema** — CPU, memoria, disco, red
- **Monitor de procesos** — qué programas usan más recursos
- **Gestor de inicio** — programas que arrancan con Windows
- **Estado de servicios** — servicios importantes del sistema
- **Salud del disco** — verificar si los discos están sanos
- **Verificación de integridad** — reparar archivos de Windows

### 🪟 **Compatibilidad**
- **Windows 10** — Todas las versiones soportadas
- **Windows 11** — Optimizado para la versión más reciente
- **Sin dependencias externas** — Solo Python estándar
- **Detección automática** de versión de Windows

## 🚀 Instalación

### **Requisitos Previos**
- **Python**: 3.7 o superior
- **Sistema**: Windows 10 o Windows 11
- **Permisos**: Algunas funciones requieren ejecutar como Administrador

### **Paso 1: Descargar**

```powershell
# Clonar el repositorio
git clone https://github.com/alvIndieDevelop/python-scripts.git
cd python-scripts\windows
```

### **Paso 2: Ejecutar**

```powershell
# Gestor de Espacio (modo interactivo)
python space_manager.py

# Gestor de Rendimiento (modo interactivo)
python performance_manager.py
```

### **Paso 3: Para funciones avanzadas**

Algunas funciones necesitan permisos de administrador:
1. Busca "cmd" en el menú inicio
2. Clic derecho → "Ejecutar como administrador"
3. Navega hasta la carpeta del script y ejecútalo

## 💻 Uso

### **Modo Interactivo (Recomendado)**

Simplemente ejecuta el script sin argumentos:

```powershell
python space_manager.py
python performance_manager.py
```

Esto abrirá un menú interactivo con opciones numeradas fáciles de usar.

### **Modo Línea de Comandos**

Para usuarios avanzados o automatización:

```powershell
# ─── Gestor de Espacio ───
python space_manager.py --drives              # Ver espacio en discos
python space_manager.py --folders             # Escanear carpetas grandes
python space_manager.py --large-files 500     # Buscar archivos > 500 MB
python space_manager.py --duplicates          # Buscar archivos duplicados
python space_manager.py --old-downloads 90    # Descargas de más de 90 días
python space_manager.py --clean-temp          # Limpiar archivos temporales
python space_manager.py --clean-updates       # Limpiar Windows Update (admin)
python space_manager.py --system-files        # Info de archivos del sistema
python space_manager.py --report              # Exportar reporte de espacio
python space_manager.py --full                # Análisis completo

# ─── Gestor de Rendimiento ───
python performance_manager.py --dashboard     # Dashboard del sistema
python performance_manager.py --processes     # Procesos principales
python performance_manager.py --startup       # Programas de inicio
python performance_manager.py --services      # Estado de servicios del sistema
python performance_manager.py --disk-health   # Salud del disco
python performance_manager.py --power         # Plan de energía
python performance_manager.py --updates       # Estado de Windows Update
python performance_manager.py --sfc           # Verificar integridad (admin)
python performance_manager.py --full          # Chequeo completo
```

## 📦 Scripts Disponibles

### 💾 **Space Manager** (`space_manager.py`) — Gestor de Espacio

| Función | Descripción | Riesgo |
| ------- | ----------- | ------ |
| Vista de discos | Ver cuánto espacio tienen tus discos | 🟢 Seguro |
| Escáner de carpetas | Encontrar las carpetas más grandes | 🟢 Seguro |
| Archivos grandes | Buscar archivos muy grandes | 🟢 Seguro |
| Archivos duplicados | Encontrar copias idénticas | 🟢 Seguro |
| Descargas antiguas | Encontrar archivos viejos en Descargas | 🟢 Seguro |
| Limpiar temporales | Borrar archivos basura | 🔵 Bajo |
| Limpiar Windows Update | Borrar actualizaciones antiguas | 🟡 Moderado |
| Info de archivos del sistema | Ver pagefile e hibernación | 🟢 Seguro |
| Exportar reporte | Generar reporte de espacio | 🟢 Seguro |

### ⚡ **Performance Manager** (`performance_manager.py`) — Gestor de Rendimiento

| Función | Descripción | Riesgo |
| ------- | ----------- | ------ |
| Dashboard | Ver CPU, RAM, disco, red | 🟢 Seguro |
| Procesos | Ver programas consumiendo recursos | 🟢 Seguro |
| Programas de inicio | Ver qué arranca con Windows | 🟢 Seguro |
| Servicios | Estado de servicios del sistema | 🟢 Seguro |
| Salud del disco | Verificar estado de los discos | 🟢 Seguro |
| Plan de energía | Ver y gestionar plan de energía | 🟢 Seguro |
| Windows Update | Verificar si Windows está actualizado | 🟢 Seguro |
| Verificar integridad | Reparar archivos de Windows | 🟡 Moderado |

## 🔍 Troubleshooting

### **Problemas Comunes**

#### **❌ "Python no se reconoce como comando"**
```
💡 Python no está instalado o no está en el PATH.
   1. Descarga Python desde https://python.org
   2. Durante la instalación, marca "Add Python to PATH"
   3. Reinicia tu terminal
```

#### **❌ "Se requieren permisos de administrador"**
```
💡 Algunas funciones necesitan permisos especiales.
   1. Busca "cmd" en el menú inicio
   2. Clic derecho → "Ejecutar como administrador"
   3. Navega hasta la carpeta y ejecuta el script
```

#### **❌ "No se puede leer información del disco"**
```
💡 El acceso al disco puede estar restringido.
   • Ejecuta como administrador
   • Verifica que el disco esté conectado
   • Algunos discos externos pueden no ser legibles
```

#### **❌ "PowerShell muestra error de ejecución"**
```
💡 La política de ejecución puede estar restringida.
   Ejecuta como administrador:
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### **Logs y Debugging**
```powershell
# Ver log del gestor de espacio
Get-Content "$env:LOCALAPPDATA\SpaceManager\space_manager.log"

# Ver log del gestor de rendimiento
Get-Content "$env:LOCALAPPDATA\PerformanceManager\performance_manager.log"
```

## 📞 Soporte

### **Antes de Pedir Ayuda**
1. ✅ **Ejecuta como administrador** para funciones que lo requieran
2. ✅ **Verifica la versión de Python**: `python --version` (debe ser 3.7+)
3. ✅ **Revisa los logs** en `%LOCALAPPDATA%\SpaceManager\` o `%LOCALAPPDATA%\PerformanceManager\`
4. ✅ **Reinicia tu computadora** y vuelve a intentar

### **Información para Reportar Problemas**
- **Script afectado**: space_manager.py o performance_manager.py
- **Versión de Windows**: Windows 10 o 11, número de build
- **Versión de Python**: `python --version`
- **Ejecutado como**: Administrador o usuario normal
- **Error completo**: Copia el mensaje de error

## 🔗 Navegación del Repositorio

- **🏠 [README Principal](../README.md)** - Visión general del repositorio
- **🐧 [Arch Linux Scripts](../arch_linux/)** - Scripts específicos para Arch Linux
- **🐍 [Python Scripts](../python/)** - Scripts Python generales
- **🪟 [Windows Scripts](./)** - Scripts para Windows (estás aquí)

---

## 📊 Información del Proyecto

**Versión**: 1.0
**Autor**: alvIndieDevelop
**Licencia**: MIT
**Compatibilidad**: Windows 10, Windows 11
**Última actualización**: 2026-03-24

**¿Te gustó este proyecto?** ⭐ Dale una estrella al repositorio y compártelo!

---

**¡Gracias por usar Windows Scripts & Utilities!** 🚀
