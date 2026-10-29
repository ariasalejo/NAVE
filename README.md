# NAVE — Centro Abierto de Inteligencia y Auditoría

**NAVE** es un proyecto comunitario y modular para organizar inteligencia de amenazas (CTI), evidencias y auditorías defensivas en equipos modestos. Este repositorio contiene el **MVP local inicial**: no pretende reemplazar OpenCTI, MISP, Wazuh, TheHive ni Greenbone.

> Estado: prototipo inicial, ejecución local, sin servicios externos ni acciones ofensivas. No se presenta como certificado ni apto todavía para entornos gubernamentales o de misión crítica.

## Objetivos

- Registrar indicadores con procedencia, fecha y contexto.
- Importar datos JSON explícitos, normalizarlos y deduplicarlos.
- Mantener una bitácora local de operaciones.
- Producir informes reproducibles.
- Construir una base extensible para conectores STIX/TAXII y herramientas defensivas.
- Aplicar la regla: **diagnosticar antes de modificar; evidencias antes de conclusiones**.

## Requisitos

- Python 3.14 recomendado para el entorno del usuario; el código inicial usa la biblioteca estándar y declara Python `>=3.11`.
- SQLite (incluido con la mayoría de las compilaciones de Python).
- No requiere Docker, bases de datos remotas, claves API ni paquetes de terceros.

## Inicio rápido en Ubuntu/Lubuntu

Desde la carpeta del proyecto:

```bash
python3 --version
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
nave doctor
nave ingest-json examples/indicators.json
nave indicators
nave report --output reports/primer-informe.md
```

Si el sistema no permite crear entornos virtuales, no instales paquetes globalmente; revisa primero los paquetes `python3-venv` de tu distribución.

### Alternativa sin instalar el paquete

```bash
PYTHONPATH=src python3 -m nave doctor
PYTHONPATH=src python3 -m nave ingest-json examples/indicators.json
PYTHONPATH=src python3 -m nave indicators
```

La base de datos se crea en `~/.local/share/nave/nave.db` de forma predeterminada. Puedes cambiarla con `NAVE_DB=/ruta/nave.db`. Para pruebas, usa una ruta temporal.

## Comandos disponibles

- `nave doctor`: comprueba Python, SQLite, base de datos y herramientas conocidas; no instala ni modifica herramientas del sistema.
- `nave ingest-json ARCHIVO`: importa una lista JSON de indicadores.
- `nave indicators`: lista indicadores guardados.
- `nave report --output ARCHIVO`: genera un informe Markdown.
- `nave audit-log`: muestra las últimas entradas de la bitácora.

### Formato de entrada

```json
[
  {
    "type": "domain",
    "value": "example.org",
    "source": "manual-demo",
    "confidence": 50,
    "labels": ["example"],
    "notes": "Dominio reservado para documentación."
  }
]
```

El ejemplo usa `example.org`, reservado para documentación. No contiene infraestructura maliciosa real. La puntuación de confianza es una anotación inicial, no un veredicto automatizado.

## Estructura

```text
src/nave/       núcleo Python
examples/       datos de demostración seguros
tests/          pruebas unitarias
docs/           arquitectura, seguridad y roadmap
reports/        informes generados (no se versionan)
```

## Principios de seguridad

1. Las importaciones son explícitas: no se descarga ni ejecuta contenido remoto automáticamente.
2. NAVE no escanea redes, no modifica firewalls y no responde a incidentes por su cuenta.
3. Los indicadores conservan su fuente y hora de ingestión.
4. Las conclusiones deben distinguir hechos, inferencias y confianza.
5. Antes de conectar una API externa, guardar credenciales fuera del repositorio.
6. No importar datos personales o sensibles sin autorización y base legítima.
7. Validar cada conector y dependencia en un entorno de pruebas.

## Roadmap

- **Fase 0 — Base local (incluida):** CLI, SQLite, ingestión JSON, deduplicación, auditoría, informes y tests.
- **Fase 1 — Calidad de datos:** esquema versionado, exportación JSON, relaciones entre entidades, migraciones y pruebas de integridad.
- **Fase 2 — CTI estándar:** soporte STIX 2.1/TAXII mediante dependencias compatibles verificadas; validación y procedencia de objetos.
- **Fase 3 — Integraciones defensivas:** conectores opcionales de solo lectura con Nmap (solo objetivos autorizados), TShark, YARA, Lynis y Greenbone/OpenVAS.
- **Fase 4 — API y panel:** API local autenticada y dashboard; evaluar FastAPI y compatibilidad real con Python 3.14 antes de incorporarla.
- **Fase 5 — Plataformas externas:** integraciones con MISP, OpenCTI, Wazuh y TheHive/Cortex; cada servicio tiene sus propios requisitos y coste de recursos.
- **Fase 6 — Preparación institucional:** control de acceso robusto, gestión de secretos, copias verificadas, retención, revisión independiente, pruebas de seguridad y documentación operativa.

## Licencia

MIT. Revisa las licencias de cada herramienta integrada antes de distribuir una solución combinada. Consulta `LICENSE`.

## Estado honesto

Este repositorio es una base inicial ejecutable, no una plataforma SOC/CTI completa. No se incluyen datos comerciales, credenciales, acuerdos de intercambio, feeds de pago ni certificaciones. Las integraciones externas deben implementarse y probarse antes de anunciarse como disponibles.
