# Arquitectura de NAVE

## Decisión inicial

Empezar como una aplicación local modular con CLI + SQLite. La máquina de referencia tiene 3,7 GiB de RAM y alrededor de 1,2 GiB disponibles durante el diagnóstico; por eso no se recomienda arrancar con OpenSearch, múltiples servicios Java, contenedores o una pila CTI completa en el mismo equipo.

## Límites del MVP

Incluye:
- registro local de indicadores;
- normalización básica por tipo;
- deduplicación por tipo + valor normalizado + fuente;
- confianza declarada entre 0 y 100;
- bitácora de eventos de importación;
- informe Markdown.

No incluye todavía:
- validación reputacional externa;
- análisis automático de malware;
- STIX/TAXII;
- API de red;
- autenticación multiusuario;
- grafo avanzado;
- conectores de OpenCTI/MISP/Wazuh/Greenbone;
- motor de correlación o respuesta automática.

## Modelo de datos

`indicators` conserva el valor original, tipo, valor normalizado, fuente, confianza declarada, etiquetas, notas y fechas. El hash de contenido deduplica la combinación tipo/valor/fuente. La bitácora registra eventos de importación y duplicados.

La puntuación actual es confianza aportada por la fuente; no es un scoring de riesgo ni una conclusión sobre que el indicador sea malicioso.

## Evolución propuesta

1. Esquemas versionados, migraciones y exportación.
2. Relaciones explícitas entre indicadores, fuentes, observaciones y casos.
3. STIX 2.1/TAXII con librerías compatibles comprobadas.
4. Adaptadores de solo lectura para herramientas locales.
5. API local autenticada y panel web.
6. Conectores a plataformas externas.
7. Controles institucionales: roles, secretos, retención, respaldos, pruebas de penetración y recuperación.

## Integraciones

Las herramientas externas se consideran sistemas separados con sus propios requisitos. NAVE no debe copiar datos ni ejecutar acciones sin límites. Cada conector tendrá:
- configuración explícita;
- permisos mínimos;
- timeout y límites de tamaño;
- validación de entrada;
- registros sin secretos;
- modo de solo lectura cuando sea posible;
- pruebas con datos ficticios.
