# Changelog

## 0.3.1

- Serializa las mutaciones de `AppStore` con un bloqueo exclusivo de Linux para evitar
  actualizaciones perdidas entre procesos.
- Rechaza referencias de iconos persistidas que no pertenezcan al almacenamiento
  administrado de WebWrap.
- Ignora valores relativos o vacíos de `XDG_DATA_HOME` y usa el fallback estándar.
- Mejora los metadatos del paquete y amplía las pruebas de rutas, CLI y concurrencia.

## 0.3.0

- Añade apertura, edición de nombre/URL y eliminación confirmada desde la GUI.
- Conserva el ID, icono y perfil al editar y regenera el launcher.
- Implementa rollback de mejor esfuerzo para actualizaciones y eliminaciones.
- Preserva intencionadamente los perfiles aislados al eliminar registros.

## 0.2.0

- Añade la aplicación GTK4/Libadwaita, la lista de aplicaciones y el diálogo de alta.
- Mantiene GTK fuera del núcleo y presenta errores esperados sin tracebacks.

## 0.1.0

- Introduce el modelo `WebApp`, validación, persistencia JSON versionada, entradas
  `.desktop`, lanzamiento de Chromium y perfiles aislados bajo demanda.
- Añade los comandos `create`, `list`, `open` y `delete`, iconos administrados,
  escrituras atómicas y pruebas unitarias del núcleo.
