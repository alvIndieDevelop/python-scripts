# Python Scripts & Utilities

Colección de aplicaciones empaquetadas y utilidades Python independientes para Linux
y Windows. Cada proyecto mantiene sus propios requisitos y documentación; no existe
una política única de plataforma o dependencias para todo el repositorio.

## Proyectos

| Proyecto | Plataforma | Requisitos principales | Ejecución |
| --- | --- | --- | --- |
| [WebWrap](apps/webwrap/README.md) | Arch Linux y escritorios freedesktop | Python 3.10+, Chromium; GTK4, Libadwaita y PyGObject para la GUI | `webwrap --help` / `webwrap-gui` |
| [Arch Maintenance](scripts/linux/arch-maintenance/README.md) | Arch Linux y derivados | Python 3.7+, `pacman`, `sudo`; `yay` opcional | `python3 scripts/linux/arch-maintenance/arch_maintenance.py --help` |
| [Developer Environment](scripts/linux/developer-environment/README.md) | Arch Linux y derivados | Python 3.7+, ejecución con `sudo`, `pacman`; `yay` opcional | `sudo python3 scripts/linux/developer-environment/developer_environment.py --help` |
| [Space Manager](scripts/windows/README.md#-space-manager-space_managerpy--gestor-de-espacio) | Windows 10/11 | Python 3.7+ o ejecutable generado | `python scripts\windows\space_manager.py` |
| [Performance Manager](scripts/windows/README.md#-performance-manager-performance_managerpy--gestor-de-rendimiento-v20) | Windows 10/11 | Python 3.7+ o ejecutable generado | `python scripts\windows\performance_manager.py` |

Los scripts independientes usan únicamente la biblioteca estándar de Python, aunque
invocan herramientas propias de su sistema operativo. WebWrap es un paquete con una
interfaz gráfica cuyas dependencias GTK se instalan desde el sistema.

## Estructura

```text
python-scripts/
├── apps/
│   └── webwrap/
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   └── technical-guidelines.md
└── scripts/
    ├── linux/
    │   ├── arch-maintenance/
    │   └── developer-environment/
    └── windows/
```

Consulte [la arquitectura](docs/architecture.md), [las pautas técnicas](docs/technical-guidelines.md)
y [el roadmap](docs/roadmap.md) para contribuir. Las instrucciones específicas y los
efectos sobre el sistema están documentados junto a cada proyecto.

## Licencia

Este repositorio se distribuye bajo la [licencia MIT](LICENSE).
