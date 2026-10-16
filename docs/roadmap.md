# Roadmap

El trabajo futuro se prioriza por seguridad y mantenibilidad, sin fechas obsoletas.

- Ampliar pruebas focalizadas de parsing CLI, subprocesses y comprobaciones de
  seguridad en las utilidades independientes.
- Mejorar type hints y mensajes de error sin romper flags ni flujos interactivos.
- Revisar compatibilidad real por versiones de Windows y reemplazar herramientas
  obsoletas cuando exista una alternativa estable.
- Evaluar automatización de pruebas, lint y releases antes de introducir CI.
- Considerar nuevas utilidades de archivos, conversión de datos, análisis de logs,
  APIs y bases de datos cuando exista un caso de uso concreto.

La extracción de código común entre scripts solo debe realizarse si se decide abandonar
su portabilidad como archivos independientes o si un proceso de distribución incorpora
ese código de forma explícita.
