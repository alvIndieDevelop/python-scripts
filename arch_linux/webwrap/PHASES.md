# WebWrap: Fases 1, 2 y 3

Este documento describe el alcance, estado y criterios de finalización de las tres
primeras fases de WebWrap. La implementación debe conservar la separación entre la
interfaz de usuario, el modelo, la persistencia, el lanzamiento de Chromium y la
generación de entradas de escritorio.

## Resumen

| Fase | Objetivo | Estado |
| --- | --- | --- |
| 1. Núcleo | Implementar y validar los servicios independientes de la interfaz | Completada |
| 2. Aplicación GTK | Añadir una interfaz nativa sobre los servicios existentes | Completada |
| 3. Gestión | Abrir, editar y eliminar desde la interfaz gráfica | En progreso |

## Principios comunes

- WebWrap administra definiciones y accesos de aplicaciones web; no renderiza sitios
  ni incorpora un motor de navegador.
- Chromium se ejecuta en modo aplicación mediante argumentos estructurados, nunca a
  través de una cadena enviada a un shell.
- Los datos siguen las rutas XDG y las entradas `.desktop` siguen el estándar
  freedesktop.
- El núcleo no debe depender de GTK ni conocer widgets, ventanas o diálogos.
- La interfaz no debe escribir directamente `apps.json`, copiar iconos, construir
  comandos de Chromium ni generar archivos `.desktop`.
- Las entradas del usuario y los datos persistidos se consideran no confiables y se
  validan en los límites correspondientes.
- Las funciones aplazadas no deben incorporarse sin ampliar explícitamente el alcance.

## Fase 1: Núcleo

### Objetivo

Construir una base comprobable sin interfaz gráfica para administrar aplicaciones web,
persistirlas de forma segura, generar sus accesos de escritorio y abrirlas con
Chromium. El CLI temporal permite validar el ciclo de vida completo del núcleo.

### Estado

La Fase 1 se completó en la versión `0.1.0`.

### Funcionalidad entregada

- Modelo inmutable `WebApp` con identificador estable y seguro para nombres de archivo.
- Validación de nombres, identificadores, iconos y URL `http` o `https`.
- Persistencia JSON versionada mediante `AppStore`.
- Escrituras atómicas para la base de datos, los iconos administrados y las entradas
  de escritorio.
- Detección y lanzamiento de Chromium sin usar un shell.
- Perfiles compartidos y perfiles aislados creados bajo demanda.
- Creación, actualización interna y eliminación de entradas `.desktop` compatibles
  con freedesktop.
- Copia opcional de iconos locales a almacenamiento administrado por WebWrap.
- CLI con los comandos `create`, `list`, `open` y `delete`.
- Rollback de mejor esfuerzo cuando una operación afecta varios artefactos.
- Conservación intencionada de los perfiles aislados al eliminar una aplicación.
- Pruebas unitarias del modelo, validación, almacenamiento, navegador y entradas de
  escritorio.

### Componentes

| Componente | Responsabilidad |
| --- | --- |
| `models/webapp.py` | Modelo serializable y validación de registros |
| `paths.py` | Resolución centralizada de rutas XDG |
| `validation.py` | Validación de entradas, IDs e iconos |
| `services/app_store.py` | Persistencia JSON atómica |
| `services/browser.py` | Argumentos y lanzamiento de Chromium |
| `services/desktop_entry.py` | Renderizado y ciclo de vida de `.desktop` |
| `main.py` | CLI temporal y coordinación de operaciones |

### Flujo principal

```text
CLI
  |
  v
Validación -> WebApp -> AppStore
                         |
                         +-> DesktopEntryService -> archivo .desktop
                         |
                         +-> BrowserService -> Chromium
```

### Datos administrados

Con `$XDG_DATA_HOME` definido, todas las rutas parten de ese directorio. Sin la
variable, se usa `~/.local/share`.

```text
$XDG_DATA_HOME/
├── webwrap/
│   ├── apps.json
│   ├── icons/
│   └── profiles/
└── applications/
    └── webwrap-<ID>.desktop
```

### Criterios de finalización

- [x] El paquete se instala en un entorno virtual con Python 3.10 o superior.
- [x] Las aplicaciones se pueden crear, listar, abrir y eliminar desde el CLI.
- [x] Los accesos `.desktop` se generan con argumentos correctamente escapados.
- [x] Los perfiles aislados se crean únicamente al abrir la aplicación.
- [x] Un JSON inválido se rechaza sin ser sobrescrito.
- [x] Las operaciones de archivos administrados son atómicas cuando corresponde.
- [x] La suite de pruebas unitarias se completa correctamente.

### Validación

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -m webwrap --help
```

## Fase 2: Aplicación GTK

### Objetivo

Añadir una interfaz gráfica nativa para iniciar WebWrap, mostrar las aplicaciones
existentes y crear nuevas aplicaciones mediante un diálogo. La interfaz debe reutilizar
el núcleo de la Fase 1 en lugar de duplicar su lógica.

### Estado

La Fase 2 está completada en la versión `0.2.0`.

### Dependencias previstas

- GTK4.
- Libadwaita.
- PyGObject.
- Chromium.

Estas dependencias se añaden para la aplicación gráfica. El modelo y los servicios del
núcleo deben continuar siendo independientes de GTK y fáciles de probar sin una sesión
gráfica.

### Alcance

1. **Inicio de la aplicación**
   - Crear la aplicación GTK/Libadwaita y su ciclo de vida.
   - Definir un identificador de aplicación estable.
   - Abrir o presentar una única ventana principal al activar la aplicación.
   - Traducir errores de inicio a mensajes comprensibles, sin mostrar tracebacks al
     usuario.

2. **Ventana principal**
   - Usar patrones nativos de Libadwaita.
   - Mostrar el nombre WebWrap y una acción visible para añadir una aplicación.
   - Mantener la ventana pequeña, clara y adaptable.
   - Evitar lógica de persistencia o generación de archivos dentro de los widgets.

3. **Listado de aplicaciones**
   - Cargar los registros mediante `AppStore`.
   - Mostrar como mínimo el nombre y el dominio de cada aplicación.
   - Mostrar el icono administrado cuando exista y un recurso predeterminado en caso
     contrario.
   - Actualizar el listado después de crear una aplicación sin reiniciar WebWrap.
   - Presentar un estado vacío cuando todavía no existan registros.

4. **Diálogo para añadir una aplicación**
   - Solicitar nombre y URL.
   - Validar los campos con las funciones existentes del núcleo.
   - Crear el modelo, persistirlo y generar su entrada `.desktop` mediante los
     servicios existentes.
   - Mantener el diálogo abierto y mostrar un error entendible si falla una operación.
   - Cerrar el diálogo y actualizar el listado únicamente después de completar todos
     los artefactos correctamente.

### Límite entre UI y servicios

```text
GTK / Libadwaita
  |
  | solicita acciones y presenta resultados
  v
Coordinación de aplicación
  |
  +-> validación y WebApp
  +-> AppStore
  +-> DesktopEntryService
  +-> BrowserService
```

La capa GTK puede coordinar casos de uso, pero no debe reimplementar validación,
serialización, rutas XDG, escape freedesktop ni argumentos de Chromium.

### Manejo de errores

La interfaz debe convertir como mínimo estos fallos en mensajes visibles y concisos:

- URL o nombre no válido.
- Base de datos JSON dañada o con versión no compatible.
- Falta de permisos para leer o escribir datos XDG.
- Fallo al crear la entrada de escritorio.

Los detalles técnicos pueden registrarse para diagnóstico, pero no deben reemplazar el
mensaje orientado al usuario.

### Estrategia de pruebas

- Mantener la suite de la Fase 1 como prueba de regresión obligatoria.
- Probar la coordinación entre la UI y los servicios sin depender de datos XDG reales.
- Probar la carga inicial, el estado vacío y la actualización del listado.
- Probar las validaciones y los errores del diálogo de alta.
- Evitar una suite gráfica extensa en esta fase; priorizar lógica extraída y pruebas de
  humo de inicio donde el entorno lo permita.
- Usar un `XDG_DATA_HOME` temporal para las pruebas de integración.

### Criterios de finalización

- [x] WebWrap inicia como aplicación GTK4/Libadwaita sin depender del CLI.
- [x] La ventana principal muestra los registros existentes desde `AppStore`.
- [x] El estado vacío dirige claramente al usuario hacia la acción de añadir.
- [x] El diálogo de alta valida nombre y URL antes de persistir.
- [x] Una creación correcta actualiza `apps.json`, genera el `.desktop` y refresca la
  lista.
- [x] Un fallo parcial conserva la consistencia definida en la Fase 1.
- [x] Los errores esperados aparecen como mensajes de UI sin tracebacks.
- [x] Las pruebas del núcleo siguen pasando y existe cobertura focalizada para la nueva
  coordinación.
- [x] La documentación de instalación incluye las dependencias gráficas reales.

## Fase 3: Gestión gráfica

### Estado

La versión `0.3.0` completa las acciones gráficas de abrir, editar y eliminar. La fase
permanece en progreso hasta incorporar selección de icono y perfil aislado en los
formularios.

### Funcionalidad entregada

- [x] Abrir una aplicación desde su fila mediante `BrowserService`.
- [x] Editar nombre y URL sin cambiar el ID, icono ni configuración de perfil.
- [x] Regenerar atómicamente el launcher después de una edición.
- [x] Restaurar el registro anterior si falla la actualización del launcher.
- [x] Solicitar confirmación antes de eliminar.
- [x] Eliminar registro, launcher e icono administrado con rollback de mejor esfuerzo.
- [x] Preservar datos de perfiles aislados después de eliminar una aplicación.
- [x] Resincronizar la lista gráfica con el almacenamiento tras errores parciales.
- [ ] Seleccionar o cambiar un icono desde los formularios gráficos.
- [ ] Elegir entre perfil compartido y aislado desde los formularios gráficos.

## Fuera del alcance de estas fases

Las siguientes funciones pertenecen a fases posteriores o al trabajo futuro:

- Gestión o eliminación de perfiles desde la interfaz.
- Descarga automática de favicons.
- Compatibilidad con Brave, Google Chrome, Vivaldi, Edge u otros navegadores.
- Detección de manifiestos PWA.
- Importación, exportación, sincronización o copias de seguridad.
- Banderas personalizadas de Chromium.
- Integraciones específicas de Hyprland u otro compositor.
- AppStream, `PKGBUILD` y empaquetado de distribución.

La eliminación manual de perfiles continúa fuera de alcance para evitar pérdida de
datos del navegador.

## Regla de avance

Las nuevas fases deben conservar las invariantes de seguridad y consistencia del
núcleo. Cualquier cambio en el modelo, las rutas, el formato JSON o la semántica de
eliminación requiere primero pruebas de regresión y la actualización de `README.md` y
`agent.md`.
