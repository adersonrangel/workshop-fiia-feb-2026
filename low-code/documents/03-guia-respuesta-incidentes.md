# Guía de Respuesta a Incidentes de Seguridad

**Versión:** 3.0  
**Última actualización:** Enero 2025  
**Responsable:** Security Engineering  
**Clasificación:** Interno — No compartir fuera del equipo de ingeniería  

---

## Alcance

Esta guía aplica a cualquier incidente que involucre:
- Acceso no autorizado a datos o sistemas
- Vulnerabilidades explotadas o descubiertas en producción
- Exposición de datos personales (PII) o datos financieros
- Ataques activos (DDoS, brute force, injection)
- Violación de compliance (GDPR, PCI-DSS, SOC2)

---

## Clasificación de Incidentes de Seguridad

### SEV-1: Brecha Activa
**Definición:** Un atacante tiene o tuvo acceso a datos sensibles, o una vulnerabilidad está siendo explotada activamente.

**Ejemplos:**
- SQL injection confirmada con extracción de datos
- Acceso no autorizado a la base de datos de producción
- Datos de tarjetas de crédito o contraseñas expuestos
- Ransomware o malware en servidores de producción

**Acciones inmediatas:**
1. Activar War Room en Slack (#security-incident)
2. Notificar al CISO y al CTO en los primeros 15 minutos
3. Aislar el sistema comprometido (cortar acceso de red si es necesario)
4. NO reiniciar ni limpiar nada — preservar evidencia forense
5. Documentar timeline con timestamps exactos
6. Si hay datos de usuarios comprometidos: preparar comunicación a usuarios dentro de 72 horas (requisito GDPR)

### SEV-2: Vulnerabilidad Crítica No Explotada
**Definición:** Se descubrió una vulnerabilidad seria pero no hay evidencia de que haya sido explotada.

**Ejemplos:**
- SQL injection descubierta en auditoría interna
- Endpoint expuesto sin autenticación que da acceso a datos sensibles
- Dependencia con CVE crítico (CVSS >= 9.0) en producción
- Secrets o API keys commiteados en repositorio público

**Acciones inmediatas:**
1. Notificar al Security Lead dentro de 1 hora
2. Evaluar blast radius: ¿qué datos están expuestos? ¿desde cuándo?
3. Aplicar mitigación temporal (WAF rule, feature flag, rollback)
4. Planificar fix permanente con deadline de 48 horas
5. Revisar logs de acceso para confirmar que no fue explotada
6. Si hay secrets expuestos: rotarlos INMEDIATAMENTE, sin esperar al fix

### SEV-3: Vulnerabilidad Menor
**Definición:** Vulnerabilidad de bajo riesgo o con condiciones de explotación poco probables.

**Ejemplos:**
- XSS reflejado en página con bajo tráfico
- Información de versión expuesta en headers HTTP
- Dependencia con CVE de severidad media (CVSS 4.0-6.9)
- Configuración subóptima de CORS

**Acciones inmediatas:**
1. Crear issue con prioridad High
2. Asignar al equipo de seguridad para el próximo sprint
3. Verificar que no hay otros endpoints con la misma vulnerabilidad
4. Deadline de resolución: 2 semanas

---

## Datos Sensibles — Clasificación

### Datos PCI (Payment Card Industry)
- Números de tarjeta de crédito/débito (nunca almacenamos, usamos tokenización vía Stripe)
- CVV (nunca debe existir en nuestros sistemas)
- Historial de transacciones
- **Si se exponen:** SEV-1 automático. Notificar a Stripe y al equipo legal.

### Datos PII (Personally Identifiable Information)
- Nombres completos, emails, direcciones, teléfonos
- Documentos de identidad
- Dirección IP + actividad (constituye PII bajo GDPR)
- **Si se exponen:** SEV-1 si más de 100 usuarios afectados. SEV-2 si menos de 100.

### Datos internos sensibles
- API keys, tokens de servicio, secrets
- Credenciales de bases de datos
- Configuración de infraestructura
- **Si se exponen:** SEV-2 mínimo. Rotar inmediatamente.

---

## Checklist Post-Incidente

Después de resolver cualquier incidente SEV-1 o SEV-2:

- [ ] Post-mortem escrito dentro de 48 horas
- [ ] Timeline completo del incidente documentado
- [ ] Root cause analysis completado
- [ ] Action items asignados con owners y deadlines
- [ ] Comunicación a usuarios enviada (si aplica GDPR)
- [ ] Logs y evidencia preservados por mínimo 90 días
- [ ] Revisión de sistemas similares para verificar que el mismo problema no existe en otro lugar
- [ ] Actualizar esta guía si se identifican gaps en el proceso

---

## Contactos de Emergencia

| Rol | Contacto | Cuándo notificar |
|-----|----------|-----------------|
| Security Lead | Canal #security-oncall | Todo incidente SEV-1 y SEV-2 |
| CISO | Escalación directa | SEV-1 siempre, SEV-2 si involucra PII |
| CTO | Escalación directa | SEV-1 siempre |
| Legal | legal@company.com | SEV-1 con datos de usuarios comprometidos |
| Stripe Support | Dashboard de Stripe | Cualquier incidente que involucre datos de pago |
| Equipo de Comunicaciones | Canal #comms-urgent | SEV-1 que requiera notificación a usuarios |

---

## Errores Comunes en Respuesta a Incidentes

1. **Reiniciar el servidor antes de investigar.** Esto destruye evidencia forense. Primero documentar, luego actuar.
2. **Asumir que "solo fue un scan".** Si un scanner encontró la vulnerabilidad, un atacante también puede encontrarla. Tratar como SEV-2 mínimo.
3. **No rotar secrets expuestos.** Un secret commiteado en git está comprometido para siempre, incluso si se borra del historial. Rotar inmediatamente.
4. **Subestimar el blast radius.** Si una vulnerabilidad existe en un endpoint, verificar TODOS los endpoints similares.
5. **No comunicar a tiempo.** GDPR requiere notificación dentro de 72 horas. No esperar a tener toda la información — comunicar lo que se sabe y actualizar después.
