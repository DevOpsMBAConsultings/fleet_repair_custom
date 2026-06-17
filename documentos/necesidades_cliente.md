# Análisis de Necesidades del Cliente - Gestión de Flota e Inventario

## Contexto del Proyecto
- **Entorno:** Odoo 16 (Iniciando en Community como sandbox, luego Odoo.sh y finalmente Producción Enterprise).
- **Cliente:** Empresa que maneja una flota de camiones, mulas y botellas (transporte de concreto).
- **Objetivo Principal:** Llevar un control preciso del inventario de repuestos e insumos (filtros, aceites, frenos, etc.) y cómo estos se consumen durante las reparaciones y mantenimientos de la flota.

## Problemática Actual
- El cliente tiene un deficiente manejo de inventario de repuestos.
- En ocasiones inician reparaciones y se dan cuenta sobre la marcha que ya contaban con la parte en el inventario o, por el contrario, que les hace falta y deben detener el trabajo.
- Quieren evitar compras innecesarias y tener trazabilidad de qué repuesto se usó en qué vehículo.

## Flujo Operativo Requerido
1. **Revisión Inicial:** El vehículo (camión, mula, botella) llega de un trabajo y es revisado por el mecánico.
2. **Reporte:** El mecánico identifica la necesidad de mantenimiento/reparación y envía el reporte a la oficina.
3. **Orden de Servicio:** La oficina crea la orden de reparación/mantenimiento.
4. **Validación de Inventario:** 
   - Se verifica si hay inventario de las piezas/insumos requeridos en las distintas áreas designadas (ej. estantes en administración, áreas en el taller).
   - **Si NO hay inventario:** El servicio queda en *stand by* y se procede a realizar la adquisición mediante el proceso de compras que la empresa ya maneja actualmente de forma independiente. Al llegar los repuestos, se reanuda.
   - **Si SÍ hay inventario:** Se inicia el servicio.
5. **Cierre de Orden:** El mecánico termina el trabajo, pasa el informe final, se actualiza la orden de servicio y **se da de baja el inventario** consumido.
### 6. Personalización de Categorías y Tipos de Servicio
- **Tipos de Categorías:** La clasificación estándar de "Contratos" y "Servicios" no aplica para el flujo de negocio del cliente.
- **Nuevas Categorías Requeridas:** En los tipos de servicio (Tipos de mantenimiento), se debe poder agrupar usando estrictamente estas categorías personalizadas:
  - Mantenimiento
  - Mantenimiento Preventivo
  - Mantenimiento Correctivo
  - Reparación
- **Ocultamiento de Contratos:** El menú y funcionalidad de "Contratos" de la flota debe ser ocultado ya que la empresa repara sus propios equipos y no maneja un esquema de contratistas de este estilo.
7. **Data Histórica:** Capacidad de subir (importar) los servicios y mantenimientos existentes mediante plantillas de Excel, manteniendo el historial de reparaciones por vehículo sin descontar el inventario actual.

## Premisas de Diseño
- Mantener la solución lo más sencilla posible.
- Hacer uso de la menor cantidad de módulos adicionales.
- Asegurar una experiencia de usuario fluida y directa.
