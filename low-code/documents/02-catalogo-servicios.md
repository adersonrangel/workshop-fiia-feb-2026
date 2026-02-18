# Catálogo de Servicios — Arquitectura del Sistema

**Versión:** 1.4  
**Última actualización:** Enero 2025  
**Responsable:** Equipo de Platform Engineering  

---

## Servicios Críticos (Tier 1)

Estos servicios son esenciales para el funcionamiento del negocio. Cualquier interrupción impacta directamente a los usuarios o al revenue.

### API Gateway
- **Descripción:** Punto de entrada único para todas las peticiones de clientes. Maneja autenticación, rate limiting y routing.
- **Stack:** Kong + Nginx
- **Uptime SLA:** 99.99%
- **Equipo responsable:** Platform Engineering
- **Impacto si cae:** Ningún usuario puede acceder a la aplicación. Impacto total.
- **Dependencias:** Auth Service, todos los microservicios downstream.
- **Monitoreo:** Datadog, PagerDuty con alerta inmediata.

### Auth Service
- **Descripción:** Maneja autenticación (login, registro, tokens JWT), autorización (roles, permisos) y sesiones de usuario.
- **Stack:** Node.js + Redis (sesiones) + PostgreSQL (usuarios)
- **Uptime SLA:** 99.99%
- **Equipo responsable:** Security Engineering
- **Impacto si cae:** Ningún usuario puede iniciar sesión. Sesiones activas expiran sin renovación.
- **Datos sensibles:** Contraseñas hasheadas, tokens de sesión, datos de 2FA. Clasificación PCI: alta.
- **Monitoreo:** Datadog + alertas de intentos de login fallidos (>100/min = posible ataque).

### Payment Service
- **Descripción:** Procesa transacciones de pago, gestiona suscripciones, emite facturas y maneja reembolsos.
- **Stack:** Python + Stripe SDK + PostgreSQL
- **Uptime SLA:** 99.95%
- **Equipo responsable:** Payments Team
- **Impacto si cae:** Los usuarios no pueden completar compras ni suscribirse. Pérdida directa de revenue.
- **Datos sensibles:** Tokens de tarjeta (nunca almacenamos números completos), historial de transacciones. Clasificación PCI: crítica.
- **Monitoreo:** Stripe Dashboard + Datadog + alertas por transacciones fallidas (>2% tasa de error).
- **Nota:** Cualquier issue relacionado con pagos duplicados o cargos incorrectos es automáticamente Urgent.

### User Database (PostgreSQL Primary)
- **Descripción:** Base de datos principal con datos de usuarios, perfiles, configuraciones y relaciones.
- **Stack:** PostgreSQL 16 + PgBouncer
- **Uptime SLA:** 99.99%
- **Equipo responsable:** Database Engineering
- **Impacto si cae:** Pérdida total de funcionalidad. Ningún servicio puede operar sin datos de usuarios.
- **Backup:** Replicación síncrona a standby. Snapshots cada 6 horas a S3.
- **Nota:** Cualquier issue de corrupción de datos o pérdida de registros es automáticamente Urgent.

---

## Servicios Importantes (Tier 2)

Estos servicios soportan funcionalidades importantes pero no bloquean el flujo principal del usuario.

### Notification Service
- **Descripción:** Envía emails transaccionales, push notifications y SMS.
- **Stack:** Python + Celery + SendGrid (email) + Firebase (push) + Twilio (SMS)
- **Uptime SLA:** 99.9%
- **Equipo responsable:** Communications Team
- **Impacto si cae:** Los usuarios no reciben confirmaciones, alertas ni notificaciones. No bloquea funcionalidad core.
- **Degradación graceful:** Si SendGrid cae, los emails se encolan y se reenvían cuando el servicio se recupere. No se pierden.

### Search Service
- **Descripción:** Motor de búsqueda para productos, contenido y usuarios.
- **Stack:** Elasticsearch + Python
- **Uptime SLA:** 99.9%
- **Equipo responsable:** Search & Discovery
- **Impacto si cae:** Los usuarios no pueden buscar, pero pueden navegar por categorías y acceder a contenido via links directos.

### Analytics Service
- **Descripción:** Recopila eventos de usuario, genera métricas de negocio y alimenta dashboards internos.
- **Stack:** Python + ClickHouse + Metabase
- **Uptime SLA:** 99.5%
- **Equipo responsable:** Data Engineering
- **Impacto si cae:** Sin visibilidad de métricas para equipos internos. Cero impacto para usuarios finales.

### File Storage Service
- **Descripción:** Almacena y sirve archivos subidos por usuarios (imágenes de perfil, documentos, attachments).
- **Stack:** Node.js + AWS S3 + CloudFront CDN
- **Uptime SLA:** 99.9%
- **Equipo responsable:** Platform Engineering
- **Impacto si cae:** Las imágenes y archivos no cargan. La funcionalidad core sigue operando.

---

## Servicios Auxiliares (Tier 3)

Estos servicios son internos o de soporte. Su caída no afecta a usuarios finales.

### CI/CD Pipeline
- **Descripción:** Pipeline de integración y despliegue continuo.
- **Stack:** GitHub Actions + ArgoCD + Docker
- **Equipo responsable:** DevOps
- **Impacto si cae:** Los equipos no pueden desplegar. No afecta a usuarios.

### Internal Admin Panel
- **Descripción:** Panel de administración para soporte al cliente y operaciones internas.
- **Stack:** React + Node.js
- **Equipo responsable:** Internal Tools
- **Impacto si cae:** El equipo de soporte no puede gestionar tickets ni ver datos de usuarios. No afecta a usuarios directamente.

### Documentation Site
- **Descripción:** Sitio de documentación técnica interna y API docs públicos.
- **Stack:** Docusaurus + GitHub Pages
- **Equipo responsable:** Developer Experience
- **Impacto si cae:** Desarrolladores no pueden consultar documentación. Cero impacto operativo.

---

## Matriz de Impacto por Servicio

| Servicio | Tier | Si cae → Prioridad mínima | Usuarios afectados |
|----------|------|---------------------------|-------------------|
| API Gateway | 1 | Urgent | 100% |
| Auth Service | 1 | Urgent | 100% |
| Payment Service | 1 | Urgent | Usuarios comprando |
| User Database | 1 | Urgent | 100% |
| Notification Service | 2 | High | Usuarios esperando notificaciones |
| Search Service | 2 | High | Usuarios buscando |
| Analytics Service | 2 | Medium | 0% (solo interno) |
| File Storage | 2 | High | Usuarios con archivos |
| CI/CD Pipeline | 3 | Medium | 0% (solo devs) |
| Admin Panel | 3 | Medium | 0% (solo soporte) |
| Documentation Site | 3 | Low | 0% (solo devs) |
