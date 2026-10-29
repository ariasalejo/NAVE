# Roadmap por hitos

## Hito 0 — MVP local
[ x ] CLI básica
[ x ] SQLite
[ x ] Importación JSON
[ x ] Deduplicación
[ x ] Bitácora
[ x ] Informe Markdown
[ x ] Pruebas unitarias iniciales

## Hito 1 — Datos fiables
- [ ] Migraciones versionadas
- [ ] Exportación/backup y restauración probada
- [ ] Relaciones y entidades
- [ ] Validación más estricta por tipo de indicador
- [ ] Informe de procedencia y límites de confianza

## Hito 2 — Estándares CTI
- [ ] Validar STIX 2.1
- [ ] Implementar TAXII como conector opcional
- [ ] Confirmar compatibilidad de dependencias con Python 3.14
- [ ] Pruebas con fixtures públicos y no sensibles

## Hito 3 — Herramientas defensivas
- [ ] Importar resultados exportados de Lynis
- [ ] Importar resultados de YARA
- [ ] Conector autorizado de Nmap XML
- [ ] Conector de TShark/Zeek
- [ ] Integración de Greenbone por API, primero solo lectura

## Hito 4 — Interfaz
- [ ] API local con autenticación
- [ ] Dashboard de indicadores, fuentes, relaciones y eventos
- [ ] Búsqueda y filtros
- [ ] Exportación CSV/JSON/Markdown

## Hito 5 — CTI/SOC interoperable
- [ ] MISP
- [ ] OpenCTI
- [ ] Wazuh
- [ ] TheHive/Cortex
- [ ] Control de acceso, secretos, retención, observabilidad y recuperación
