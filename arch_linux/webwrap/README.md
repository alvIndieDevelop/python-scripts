# WebWrap

WebWrap 0.3.0 crea accesos de aplicaciones web para Chromium desde una interfaz
GTK4/Libadwaita o desde la línea de comandos. Cada aplicación se registra con un
identificador estable y obtiene una entrada de escritorio compatible con el estándar
freedesktop, utilizable por lanzadores de Arch Linux y entornos como Hyprland.

El núcleo usa únicamente la biblioteca estándar de Python. La interfaz gráfica usa
PyGObject, GTK4 y Libadwaita proporcionados por el sistema.

El alcance y los criterios de las primeras etapas se describen en
[`PHASES.md`](PHASES.md).

## Requisitos

- Python 3.10 o superior.
- PyGObject, GTK 4.8 o superior y Libadwaita 1.5 o superior para la interfaz gráfica.
- Chromium disponible como `chromium` en `PATH` para abrir las aplicaciones.
- Un lanzador o entorno de escritorio compatible con entradas `.desktop` de
  freedesktop.

## Instalación

Instale primero las dependencias del sistema en Arch Linux:

```bash
sudo pacman -S python python-gobject gtk4 libadwaita chromium
```

Arch Linux protege el Python del sistema mediante PEP 668. La forma recomendada de
instalar WebWrap en modo editable es usar un entorno virtual que pueda ver PyGObject:

```bash
python -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -e .
```

Si `.venv` se creó anteriormente sin `--system-site-packages`, desactívelo, elimine
ese entorno local y créelo de nuevo con el comando anterior. El código del proyecto y
los datos de WebWrap no se almacenan dentro del entorno virtual.

Mientras el entorno esté activado, el comando `webwrap` estará disponible. También
puede ejecutarse el paquete como módulo:

```bash
webwrap --help
python -m webwrap --help
webwrap-gui --help
```

No se recomienda `python -m pip install --user -e .` en Arch Linux porque el Python
administrado por el sistema puede rechazarlo por PEP 668.

## Interfaz gráfica

Inicie la aplicación con el entorno virtual activado:

```bash
webwrap-gui
```

La ventana principal muestra las aplicaciones existentes. Use el botón `+` o
`Add Web App` para abrir el diálogo de creación, introduzca un nombre y una URL
HTTP(S), y pulse `Create`. La lista se actualiza sin reiniciar WebWrap.

Cada fila incluye `Open`, que inicia Chromium en modo aplicación. El menú de tres
puntos permite editar el nombre y la URL o eliminar la aplicación con confirmación.
La edición conserva el ID, el icono y la configuración de perfil existentes. La
eliminación conserva intencionadamente los datos de perfiles aislados.

La selección de iconos y perfiles aislados al crear sigue disponible mediante el CLI.
La edición de esas opciones todavía no está disponible.

## Línea de comandos

Los ejemplos usan `webwrap`; puede sustituirse por `python -m webwrap` dentro del
entorno virtual.

### Crear una aplicación

```bash
webwrap create --name "Documentación Python" --url "https://docs.python.org/3/"
```

La salida muestra el identificador generado, por ejemplo:

```text
Created documentacion-python-a1b2c3d4
```

El identificador combina una versión normalizada del nombre con un sufijo aleatorio.
Es estable durante la vida del registro y se usa con `open` y `delete`.

La URL debe usar `http` o `https`, incluir un nombre de host y no contener espacios.

### Añadir un icono

```bash
webwrap create \
  --name "Correo" \
  --url "https://mail.example.com" \
  --icon "$HOME/Imágenes/correo.png"
```

El icono debe ser un archivo normal legible. Se admiten las extensiones `.ico`,
`.jpeg`, `.jpg`, `.png`, `.svg` y `.webp`. WebWrap copia el archivo a su propio
directorio de datos; no depende del archivo de origen después de crear la aplicación.

### Usar un perfil aislado

```bash
webwrap create \
  --name "Trabajo" \
  --url "https://intranet.example.com" \
  --isolated-profile
```

El directorio del perfil se crea al abrir la aplicación por primera vez, no durante
`create`. Sin esta opción, Chromium usa su perfil habitual.

### Listar aplicaciones

```bash
webwrap list
```

La tabla muestra `ID`, `NAME` y `URL`. Si no hay registros, la salida es
`No web apps configured.`. Use esta lista para recuperar el identificador de una
aplicación.

### Abrir una aplicación

```bash
webwrap open documentacion-python-a1b2c3d4
```

WebWrap inicia Chromium con `--app=<URL>` y, cuando corresponde, con el directorio
del perfil aislado.

### Eliminar una aplicación

```bash
webwrap delete documentacion-python-a1b2c3d4
```

La eliminación quita el registro, la entrada `.desktop` y el icono copiado que
gestiona WebWrap. Los datos de un perfil aislado se conservan intencionadamente para
evitar borrar datos del navegador de forma irreversible.

## Datos y rutas XDG

WebWrap usa `$XDG_DATA_HOME`. Si la variable no existe, usa `~/.local/share`.
Suponiendo la ruta predeterminada, los archivos son:

| Contenido | Ruta |
| --- | --- |
| Base de datos | `~/.local/share/webwrap/apps.json` |
| Iconos copiados | `~/.local/share/webwrap/icons/` |
| Perfiles aislados | `~/.local/share/webwrap/profiles/<ID>/` |
| Entradas de escritorio | `~/.local/share/applications/webwrap-<ID>.desktop` |

Las entradas de escritorio se guardan directamente en el directorio XDG
`applications`; no se encuentran dentro de `webwrap/`.

No edite `apps.json` mientras usa WebWrap. Si el JSON está dañado, el programa se
detiene sin sobrescribirlo para permitir su recuperación manual.

## Pruebas

Desde el directorio de WebWrap y con el entorno virtual activado:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -m webwrap --help
python -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1')"
webwrap-gui --help
```

Para una prueba manual sin tocar los datos XDG reales, use un directorio temporal:

```bash
tmp_data="$(mktemp -d)"
XDG_DATA_HOME="$tmp_data" python -m webwrap create \
  --name "Prueba" \
  --url "https://example.com"
XDG_DATA_HOME="$tmp_data" python -m webwrap list
XDG_DATA_HOME="$tmp_data" python -m webwrap delete APP_ID
rm -rf "$tmp_data"
```

Sustituya `APP_ID` por el valor mostrado por `create` o `list`. Abrir Chromium requiere
una sesión gráfica y no forma parte de esta prueba de ciclo de vida.

## Solución de problemas

### Chromium no está disponible

Si aparece `Chromium is not installed or is not available in PATH.`, instale Chromium
y compruebe que se resuelve con:

```bash
command -v chromium
```

### El acceso no aparece en el lanzador

Compruebe que existe en `$XDG_DATA_HOME/applications` o, si no se configuró la
variable, en `~/.local/share/applications`. Algunos lanzadores mantienen caché;
ciérrelos y ábralos de nuevo o reinicie la sesión gráfica.

### Error de permisos o JSON dañado

Revise los permisos de `$XDG_DATA_HOME/webwrap` y de
`$XDG_DATA_HOME/applications`. Un mensaje sobre JSON malformado o un esquema no
válido indica que `apps.json` requiere inspección o restauración manual; WebWrap no
lo reemplaza automáticamente.

### Pip rechaza la instalación

El error `externally-managed-environment` corresponde a PEP 668. Cree y active el
entorno virtual indicado en la sección de instalación en vez de modificar el Python
del sistema.

## Limitaciones actuales

- Solo se admite Chromium.
- La interfaz gráfica todavía no permite seleccionar iconos o perfiles aislados.
- No existe un comando CLI para editar; la edición está disponible en la interfaz.
- No se descargan favicons automáticamente.
- No se admiten variantes de navegador ni selección de ejecutable.
- No hay comando para editar una aplicación existente.
- No se eliminan perfiles aislados al borrar una aplicación.
- No se usan APIs específicas de Hyprland; la integración depende de entradas
  `.desktop` estándar.

## Licencia

WebWrap forma parte de este repositorio bajo la licencia MIT. Consulte el archivo
[`../../LICENSE`](../../LICENSE).
