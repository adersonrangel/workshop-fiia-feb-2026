# Política de Triaje de Issues — Equipo de Ingeniería

**Versión:** 2.1  
**Última actualización:** Enero 2025  
**Responsable:** Equipo de Platform Engineering  

---

## Propósito

Este documento define los criterios oficiales para clasificar la prioridad de issues reportados en nuestros sistemas. Todo issue debe ser evaluado bajo estos criterios antes de ser asignado a un sprint.

---

## Niveles de Prioridad

### Urgent (SLA: respuesta en 30 minutos, resolución en 4 horas)

Un issue es Urgent cuando cumple AL MENOS UNO de estos criterios:

- **Seguridad comprometida:** Vulnerabilidades activas como SQL injection, XSS, exposición de datos personales (PII), acceso no autorizado a bases de datos, o cualquier brecha que exponga datos de usuarios.
- **Producción completamente caída:** El sistema principal no responde y los usuarios no pueden realizar ninguna acción.
- **Pérdida activa de datos:** Corrupción de datos en curso, backups fallando con datos no recuperables, o procesos de escritura produciendo datos incorrectos.
- **Impacto financiero directo:** El sistema de pagos está caído, las transacciones están fallando, o hay cargos duplicados a los usuarios.
- **Incumplimiento regulatorio:** Cualquier situación que nos ponga en violación de GDPR, PCI-DSS, SOC2, o regulaciones locales de protección de datos.

**Protocolo de respuesta Urgent:**
1. Notificar inmediatamente al on-call engineer vía PagerDuty.
2. Abrir canal de incidente en Slack (#incidents).
3. Comunicar a stakeholders en máximo 1 hora.
4. Post-mortem obligatorio dentro de 48 horas después de la resolución.

### High (SLA: respuesta en 2 horas, resolución en 24 horas)

Un issue es High cuando cumple AL MENOS UNO de estos criterios:

- **Funcionalidad crítica rota:** Login, registro, checkout, o cualquier flujo principal del usuario no funciona correctamente pero el sistema sigue parcialmente operativo.
- **Más del 20% de usuarios afectados:** El issue impacta a una porción significativa de la base de usuarios activos.
- **Degradación severa de performance:** Tiempos de respuesta superiores a 5 segundos en endpoints críticos, o tasa de error superior al 5%.
- **Integración de terceros crítica caída:** Pasarela de pagos, proveedor de autenticación OAuth, o servicio de email transaccional no responde.
- **Funcionalidad de negocio bloqueada:** Los equipos internos no pueden realizar operaciones esenciales (facturación, soporte al cliente, reportes financieros).

**Protocolo de respuesta High:**
1. Asignar a un ingeniero dentro de las próximas 2 horas.
2. Notificar al tech lead del equipo responsable.
3. Actualización de status cada 4 horas hasta resolución.

### Medium (SLA: respuesta en 24 horas, resolución en 1 semana)

Un issue es Medium cuando cumple AL MENOS UNO de estos criterios:

- **Funcionalidad secundaria rota:** Features que no son parte del flujo principal pero que afectan la experiencia del usuario (dark mode, preferencias, exportar datos, notificaciones).
- **Workaround disponible:** El usuario puede completar su tarea por un camino alternativo aunque la experiencia no sea ideal.
- **Menos del 20% de usuarios afectados:** El issue impacta a un segmento menor de usuarios.
- **Performance degradada pero funcional:** Tiempos de respuesta entre 2 y 5 segundos, o tasa de error entre 1% y 5%.
- **Deuda técnica con impacto visible:** Tests flaky que bloquean CI, logs excesivos que llenan el almacenamiento, o dependencias deprecated con warnings visibles.

**Protocolo de respuesta Medium:**
1. Incluir en el backlog para priorización en el próximo sprint planning.
2. Asignar owner para investigación.

### Low (SLA: respuesta en 1 semana, resolución según capacidad)

Un issue es Low cuando cumple TODOS estos criterios:

- **Sin impacto funcional:** El sistema funciona correctamente.
- **Cosmético o de mejora:** Typos, alineación visual, mejoras de copy, optimizaciones menores de UI.
- **Documentación:** Actualización de READMEs, diagramas de arquitectura, runbooks.
- **Refactoring menor:** Mejoras de código que no cambian comportamiento ni afectan performance.
- **Cero usuarios afectados directamente:** El issue solo es visible para el equipo de desarrollo.

**Protocolo de respuesta Low:**
1. Agregar al backlog con etiqueta "nice-to-have".
2. Resolver cuando haya capacidad libre o como tarea de onboarding.

---

## Reglas Especiales

### Escalación automática a Urgent
Cualquier issue que mencione las siguientes palabras clave debe ser tratado como potencialmente Urgent hasta que se demuestre lo contrario:
- "SQL injection", "XSS", "vulnerabilidad", "brecha", "datos expuestos"
- "producción caída", "todos los usuarios", "no pueden acceder"
- "datos corruptos", "pérdida de datos", "backup fallido"
- "PCI", "GDPR", "compliance", "auditoría"
- "cargos duplicados", "pagos fallidos", "transacciones perdidas"

### Regla de contexto insuficiente
Si un issue no proporciona suficiente información para determinar la prioridad con confianza:
- Asignar **Medium** como prioridad por defecto.
- Agregar una nota indicando qué información falta para una clasificación más precisa.
- Solicitar al reportador que complete la información.

### Regla de horario
- Issues reportados fuera de horario laboral (después de las 6pm o fines de semana) que sean Urgent siguen el protocolo normal de PagerDuty.
- Issues High reportados fuera de horario se atienden al inicio del siguiente día laboral, a menos que el tech lead decida escalar.

### Regla de acumulación
Si hay 3 o más issues Medium abiertos que afectan el mismo componente o servicio, el conjunto debe escalarse a High para investigar una posible causa raíz común.
