# Integración de Reparaciones de Flota con Inventario

Este plan detalla la arquitectura para solucionar el problema de gestión de repuestos en la reparación de camiones, mulas y botellas, manteniendo la simplicidad y minimizando la dependencia de múltiples módulos estándar de Odoo que puedan sobrecomplicar la operación.

## Decisiones de Arquitectura y Preguntas Resueltas

**1. Consumo de Inventario:** ¿Tienen una única bodega física desde donde despachan los repuestos, o cada taller/mecánico tiene su "bodega virtual"?
*Respuesta:* No tienen una bodega grande centralizada, sino áreas designadas (ej. estantes en la oficina de administración, áreas específicas en el taller). 
*Decisión:* Se usarán las ubicaciones estándar de Odoo (`stock.location`) para reflejar estas áreas y permitir el descuento del stock desde las mismas.

**2. Generación de Compras:** Cuando no hay inventario, Odoo puede generar automáticamente las órdenes de compra. ¿Prefieren que sea automático, usar reglas, o un botón manual?
*Respuesta:* Ellos ya manejan su proceso de compras de forma independiente. Por ahora solo desean llevar el control de inventario en las reparaciones.
*Decisión:* El proceso de compras actual se mantendrá intacto fuera de esta pantalla. El MVP no automatizará la creación de compras desde la orden de servicio.

**3. Enfoque Arquitectónico (Flota vs Mantenimiento/Reparaciones):** 
*Decisión Aprobada:* Se extenderá el modelo nativo de **Flota (Fleet)** (`fleet.vehicle.log.services`) para integrar el consumo de inventario. Esto evita duplicar información (como tener que registrar los vehículos como "Equipos" o "Productos").

**4. Foco del MVP:** 
El alcance se centrará estrictamente en lograr un mejor control de inventario, descontando las piezas y repuestos usados en cada servicio para llevar la trazabilidad de las reparaciones de manera eficiente.

## Cambios Propuestos

### 1. Módulo: `fleet_repair_custom`

#### [NEW] `models/fleet_vehicle_log_services.py`
Se extenderá el modelo nativo `fleet.vehicle.log.services` para incluir:
- **Estados del Servicio:** Borrador -> En Progreso -> Terminado.
- **Líneas de Repuestos:** Relación *One2many* hacia un nuevo modelo `fleet.service.part` donde se agregan los productos (filtros, aceites, etc.) y cantidades.
- **Lógica de Inventario:** Al pasar a estado "Terminado", se generará automáticamente un movimiento de inventario (`stock.picking` o `stock.move`) que descuente las piezas de la ubicación de existencias.

#### [NEW] `models/fleet_service_part.py`
Un modelo simple que contenga:
- Producto (`product_id`)
- Cantidad
- Relación a la orden de servicio (`service_id`)

#### [NEW] `views/fleet_vehicle_log_services_views.xml`
- Modificar el formulario nativo de servicios de flota para:
  - Añadir una barra de estado (*statusbar*).
  - Añadir una pestaña (Notebook) para "Repuestos".
  - Mostrar un Smart Button que enlace al movimiento de inventario (`stock.picking`).

#### [NEW] `security/ir.model.access.csv`
- Permisos de acceso para el nuevo modelo `fleet.service.part`.

## Plan de Verificación

### Verificación Manual
1. Instalar el módulo en una base de datos Odoo 16 CE local limpia.
2. Crear un vehículo de prueba.
3. Crear un repuesto de prueba (ej. "Filtro de Aceite") y ajustar su stock a 10 unidades.
4. Crear un servicio para el vehículo, agregar 2 "Filtros de Aceite" y pasarlo a "Terminado".
5. Verificar que el stock del "Filtro de Aceite" baje a 8 unidades automáticamente en el inventario.
