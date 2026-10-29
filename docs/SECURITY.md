# Modelo de seguridad inicial

- Importa solo archivos JSON locales que el operador seleccione.
- No evalúa ni ejecuta contenido importado.
- No realiza conexiones de red por defecto.
- No almacena tokens ni contraseñas.
- SQLite se guarda en el directorio de datos del usuario.
- Los informes pueden contener indicadores sensibles: controla permisos y distribución.
- Los campos de texto importados deben tratarse como datos no confiables.
- El MVP no ofrece aislamiento multiusuario ni control de acceso; no lo expongas a la red.
- No lo presentes como herramienta certificada o sistema de misión crítica.
- Las acciones futuras que afecten sistemas deben requerir autorización, alcance explícito y registro.
