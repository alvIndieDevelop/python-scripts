# Pautas técnicas

## Código Python

- Seguir PEP 8, preferir líneas de hasta 100 caracteres y nombres predecibles.
- Usar `pathlib.Path`, f-strings, excepciones específicas y type hints en código nuevo.
- Escribir docstrings y comentarios en inglés; comentar motivos no evidentes, no cada
  instrucción.
- Validar entradas antes de construir rutas o comandos y no almacenar credenciales.

## Experiencia de usuario

- Usar lenguaje claro y explicar consecuencias antes de solicitar confirmación.
- Mantener valores seguros por defecto, progreso visible y resúmenes accionables.
- No comunicar riesgo exclusivamente mediante color o emoji.
- Conservar la terminología de riesgo existente: seguro, bajo, moderado y alto.

## Scripts independientes

- Mantener la portabilidad de un solo archivo y la biblioteca estándar cuando sea
  posible.
- Conservar CLI, menú interactivo, logging y confirmaciones existentes.
- Ejecutar comandos externos con límites claros, tratamiento específico de errores y
  comprobaciones de capacidades.
- En Windows, usar rutas del sistema como `LOCALAPPDATA`, detectar permisos de
  administrador y adaptar funciones al número de build cuando corresponda.

## Aplicaciones empaquetadas

Las aplicaciones pueden definir convenciones más cercanas. Deben mantener límites
entre presentación, dominio y servicios, y documentar su propio flujo de pruebas e
instalación.
