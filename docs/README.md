# Centro de Documentacion

Este directorio concentra la documentacion operativa del proyecto `PDF_IA_Rework`.

## Archivos clave

- `docs/01_fase1_estado.md`: Estado real de Fase 1, validaciones, pendientes y cierre.
- `docs/02_mapeo_fastapi_drf.md`: Que reemplaza que en la migracion FastAPI -> Django/DRF.
- `docs/03_tracking_plan.md`: Checklist por fases y bitacora de progreso.
- `docs/04_decisiones_tecnicas.md`: Decisiones tomadas, alternativas y motivos.
- `docs/05_arquitectura_general.md`: Arquitectura objetivo y flujo real del sistema.
- `docs/06_estructura_backend.md`: Estructura oficial de backend y reglas por app.
- `docs/07_contratos_api.md`: Contratos API, convenciones y endpoints planificados.
- `docs/08_modelo_datos.md`: Entidades, relaciones y estrategia de migraciones.
- `docs/09_pasos_decisiones.md`: Paso a paso por fase (¿QUÉ, ¿CÓMO, ¿QUÉ usamos). Referencia para código.
- `docs/10_fase4_arquitectura_detallada.md`: Análisis profundo de Fase 4 (Notebooks + Documentos + Chat). 3 opciones de diseño, funciones habilitadas, prep para PDF+OCR.

## Fuente oficial de seguimiento

- El estado oficial del proyecto se mantiene en `docs/03_tracking_plan.md`.
- Los demas documentos son de apoyo o referencia historica.

## Documentos de referencia historica

- `docs/ROADMAP.md`
- `docs/STACK_TECNOLOGICO.md`
- `docs/PDF_IA_REWORK_PLAN.md`

## Regla de trabajo

- No borrar historial: agregar cambios como entradas de bitacora con fecha.
- Mantener un unico estado fuente: el avance oficial vive en `docs/03_tracking_plan.md`.
- Antes de iniciar una fase, confirmar alcance y criterio de cierre en el tracker.

## Convencion de actualizacion

Usar formato:

- `Fecha`: YYYY-MM-DD
- `Cambio`: que se hizo
- `Impacto`: que habilita
- `Siguiente paso`: accion inmediata
