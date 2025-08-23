# 🔧 Developer Environment Setup Script

Script completo para configurar automáticamente un ambiente de desarrollo profesional en Arch Linux.

**Parte de [Python Scripts Collection](../README.md)**

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🚀 Instalación](#-instalación)
- [💻 Uso](#-uso)
- [🛠️ Herramientas Incluidas](#️-herramientas-incluidas)
- [🔧 Configuración Post-Instalación](#-configuración-post-instalación)
- [📝 Logging y Estado](#-logging-y-estado)
- [🎯 Casos de Uso](#-casos-de-uso)
- [🔍 Troubleshooting](#-troubleshooting)

## ✨ Características

### 🎯 **Instalación Automática**
- **Gestión inteligente** de paquetes ya instalados
- **Soporte para AUR** con yay para paquetes no oficiales
- **Instalación no interactiva** con confirmación automática
- **Verificación de dependencias** del sistema

### 🖥️ **Interfaz de Usuario**
- **Menú interactivo** atractivo con 14 opciones
- **Comandos de línea** para automatización
- **Feedback visual** con emojis y colores
- **Navegación intuitiva** con validación de entrada

### 🔧 **Configuración Automática**
- **Servicios del sistema** configurados automáticamente
- **Grupos de usuario** configurados para Docker
- **Bases de datos** inicializadas y servicios iniciados
- **Variables de entorno** configuradas para NVM

### 📝 **Logging y Monitoreo**
- **Archivo de log** detallado en `~/.dev_env_setup.log`
- **Estado de instalación** en tiempo real
- **Reportes de progreso** y resúmenes
- **Troubleshooting** con información detallada

## 🚀 Instalación

### **Requisitos Previos**
- **Sistema**: Arch Linux (recomendado) o derivados
- **Python**: Python 3.7 o superior
- **Privilegios**: sudo para instalación de paquetes
- **Dependencias**: pacman, yay (opcional para AUR)

### **Paso 1: Descargar el Script**
```bash
# Clonar el repositorio principal
git clone https://github.com/alvIndieDevelop/python-scripts.git
cd python-scripts/python/developer_enviroment
```

### **Paso 2: Hacer Ejecutable**
```bash
chmod +x developer_enviroment.py
```

### **Paso 3: Verificar Dependencias**
```bash
# Verificar que yay esté instalado (para paquetes AUR)
yay --version

# Si no está instalado, instalarlo
sudo pacman -S yay
```

## 💻 Uso

### **Modo Interactivo (Recomendado)**
```bash
sudo python3 developer_enviroment.py
```

### **Comandos de Línea**
```bash
# Instalar todas las herramientas
sudo python3 developer_enviroment.py --all

# Ver herramientas disponibles
sudo python3 developer_enviroment.py --list

# Ver estado de instalación
sudo python3 developer_enviroment.py --status

# Ver log de instalación
sudo python3 developer_enviroment.py --log

# Ayuda completa
sudo python3 developer_enviroment.py --help
```

### **Menú Interactivo**
```
🔧 Developer Environment Setup Menu
==================================================
1.  📦 Install NVM (Node Version Manager)
2.  🟢 Install Node.js
3.  💻 Install Visual Studio Code
4.  🐳 Install Docker
5.  📝 Install Git
6.  🐍 Install Python
7.  ⚡ Install UV (Python Package Manager)
8.  🐘 Install PostgreSQL
9.  🔴 Install Redis
10. 🍃 Install MongoDB
11. 🚀 Install All Tools
12. 📋 Show Available Tools
13. 📊 Show Installation Status
14. 📝 View Installation Log
0.  🚪 Exit
```

## 🛠️ Herramientas Incluidas

### **🌐 Desarrollo Web**
- **NVM & Node.js**: Gestor de versiones y runtime JavaScript
- **Python & UV**: Lenguaje Python y gestor de paquetes rápido

### **💻 Herramientas de Desarrollo**
- **Visual Studio Code**: Editor de código profesional
- **Git**: Control de versiones distribuido

### **🐳 Contenedores y DevOps**
- **Docker**: Plataforma de contenedores para aplicaciones

### **🗄️ Bases de Datos**
- **PostgreSQL**: Base de datos relacional avanzada
- **Redis**: Almacén de datos en memoria
- **MongoDB**: Base de datos NoSQL orientada a documentos

## 🔧 Configuración Post-Instalación

### **Docker**
- ✅ Servicio iniciado y habilitado
- ✅ Usuario añadido al grupo docker
- 💡 **Nota**: Requiere cerrar sesión y volver a entrar

### **PostgreSQL**
- ✅ Base de datos inicializada
- ✅ Servicio iniciado y habilitado
- 💡 **Conectar**: `sudo -u postgres psql`

### **MongoDB**
- ✅ Directorios de datos creados
- ✅ Servicio iniciado y habilitado

### **NVM**
- ✅ Node.js LTS instalado automáticamente
- 💡 **Usar**: `source ~/.nvm/nvm.sh`

## 📝 Logging y Estado

### **Archivo de Log**
- **Ubicación**: `~/.dev_env_setup.log`
- **Formato**: `YYYY-MM-DD HH:MM:SS - Action - STATUS - Details`
- **Ejemplo**: `2024-08-23 17:30:15 - Install Docker - SUCCESS`

### **Verificar Estado**
```bash
# Ver estado actual
sudo python3 developer_enviroment.py --status

# Ver log reciente
sudo python3 developer_enviroment.py --log
```

## 🎯 Casos de Uso

### **🆕 Configuración Inicial**
```bash
# Instalar todo el ambiente de desarrollo
sudo python3 developer_enviroment.py --all
```

### **🔧 Instalación Selectiva**
```bash
# Solo herramientas web
sudo python3 developer_enviroment.py
# Seleccionar: 1 (NVM), 2 (Node.js), 6 (Python)

# Solo bases de datos
sudo python3 developer_enviroment.py
# Seleccionar: 8 (PostgreSQL), 9 (Redis), 10 (MongoDB)
```

### **🤖 Automatización**
```bash
#!/bin/bash
# Script de despliegue automático
cd /path/to/python-scripts/python/developer_enviroment
sudo python3 developer_enviroment.py --all
```

## 🔍 Troubleshooting

### **Problemas Comunes**

#### **❌ Error de Privilegios**
```bash
❌ This script requires sudo privileges to install packages.
💡 Please run: sudo python3 developer_enviroment.py
```

#### **⚠️ Paquete Ya Instalado**
```bash
ℹ️  Docker is already installed
```

#### **🔧 Error de Post-Instalación**
```bash
⚠️  Post-install setup failed: [error details]
```

### **Logs y Debugging**
```bash
# Ver log completo
cat ~/.dev_env_setup.log

# Ver últimas 20 líneas
tail -20 ~/.dev_env_setup.log

# Buscar errores específicos
grep "FAILED" ~/.dev_env_setup.log
```

### **Reinstalación**
```bash
# Desinstalar paquetes problemáticos
sudo pacman -R package_name

# Reinstalar con el script
sudo python3 developer_enviroment.py
# Seleccionar la opción correspondiente
```

## 🔗 Navegación del Repositorio

- **🏠 [README Principal](../../README.md)** - Visión general del repositorio
- **🐍 [Python Scripts](../README.md)** - Colección de scripts Python
- **🐧 [Arch Linux Scripts](../../arch_linux/)** - Scripts específicos para Arch Linux
- **🪟 [Windows Scripts](../../windows/)** - Scripts para Windows (próximamente)

---

## 📊 Información del Proyecto

**Versión**: 1.0  
**Autor**: alvIndieDevelop  
**Licencia**: MIT  
**Última actualización**: $(date +%Y-%m-%d)

**¿Te gustó este script?** ⭐ Dale una estrella al repositorio y compártelo con la comunidad!

---

**¡Gracias por usar Developer Environment Setup Script!** 🚀
