# Arquitectura del repositorio

El repositorio combina dos estilos intencionados.

## Aplicaciones empaquetadas

`apps/webwrap` usa un paquete con diseño `src/`, metadatos en `pyproject.toml`, pruebas
y capas separadas para presentación, casos de uso, modelo y servicios. La GUI y el CLI
comparten `operations.py`; el núcleo no importa GTK.

## Utilidades independientes

Los proyectos de `scripts/` son archivos autónomos para facilitar su descarga y uso.
Encapsulan estado y operaciones en clases cuando resulta útil, pero no comparten un
paquete común. Ofrecen argumentos para automatización y menús guiados para usuarios
menos técnicos.

Las utilidades Linux dependen de comandos del sistema como `pacman`, `systemctl` o
`sudo`. Las utilidades Windows usan PowerShell, herramientas de Windows, detección de
privilegios y comprobaciones de versión. La biblioteca Python puede ser estándar sin
que eso implique ausencia de dependencias del sistema.

## Seguridad y artefactos

Las operaciones destructivas deben validarse, explicarse y confirmarse. Los proyectos
mantienen sus propios logs, configuración y rutas de instalación, documentados en sus
README. Los fallos parciales deben degradarse de forma comprensible y evitar pérdida de
datos cuando exista una estrategia de recuperación razonable.
