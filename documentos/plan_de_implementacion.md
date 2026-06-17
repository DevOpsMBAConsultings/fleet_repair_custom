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

### 5. Fase 3: Personalización de Tipos de Servicio y Ocultamiento de Contratos
**Objetivo**: Eliminar la funcionalidad de contratos del entorno del cliente, y reemplazar las categorías de los tipos de servicio por clasificaciones exactas solicitadas por el negocio.

#### [NEW/MODIFY] `models/fleet_service_type.py`
Se creará un nuevo modelo/archivo para heredar `fleet.service.type` y agregar un nuevo campo llamado `custom_repair_category` que contenga exactamente: Mantenimiento, Mantenimiento Preventivo, Mantenimiento Correctivo, y Reparación. El campo nativo `category` será ignorado para evitar romper los datos internos de Odoo.

#### [NEW] `views/fleet_service_type_views.xml` (o archivo similar)
- Reemplazar el campo `category` por `custom_repair_category` en la vista de árbol (`fleet_vehicle_service_types_view_tree`).
- Reemplazar el campo en la vista de búsqueda (`fleet_vehicle_service_types_view_search`).
- Ocultar el menú de Contratos (`fleet.fleet_vehicle_log_contract_menu`) asignando `<menuitem id="fleet.fleet_vehicle_log_contract_menu" active="False"/>`.

### 6. Fase 4: Cierre de Ciclo de Inventario y Trazabilidad (Auto-consumo)
**Objetivo**: Dar de baja automáticamente el inventario cuando la orden pase a "Hecho" y permitir navegar desde el movimiento de inventario (Albarán) de vuelta a la Orden de Servicio original.

#### [NEW] `models/stock_picking.py`
Se heredará el modelo `stock.picking` para agregar un campo relacional (`fleet_service_id`, tipo Many2one) que conecte el movimiento directamente con la orden de servicio de la flota.

#### [MODIFY] `models/fleet_vehicle_log_services.py`
Se actualizará el método `_create_stock_picking()` para:
1. Asignar el nuevo campo `fleet_service_id` en el picking.
2. Añadir la lógica de auto-validación: Confirmar el picking (`action_confirm`), asignar el stock disponible (`action_assign`), rellenar las cantidades hechas (`quantity_done`), y validar el movimiento (`button_validate()`). Esto asegura que el inventario se descuente de forma inmediata y automática al cerrar la orden.

#### [MODIFY] `views/stock_picking_views.xml`
- Añadir el campo `fleet_service_id` en el formulario (`stock.view_picking_form`), preferiblemente en la misma pestaña o grupo donde está el Documento Origen (`origin`), dejándolo como solo lectura.

---

### Fase 6: Informe de Mantenimiento y Evidencias Fotográficas

Esta fase replicará la funcionalidad del módulo `servicio_reparacion` directamente en el módulo de flotas `fleet_repair_custom`.

#### [NEW] `models/fleet_service_image.py`
- Crear el modelo `fleet.service.image`.
- Campos: `service_id` (Many2one a `fleet.vehicle.log.services`), `sequence` (Integer), `image` (Binary), `description` (Char).
- Restricción: Límite máximo de 15 imágenes por servicio.

#### [MODIFY] `models/__init__.py`
- Importar `fleet_service_image`.

#### [MODIFY] `models/fleet_vehicle_log_services.py`
- Añadir los 4 campos de texto (tipo `Html` o `Text` según convenga para reportes limpios):
  - `antecedentes_servicio`
  - `hallazgos`
  - `accion_correctiva`
  - `recomendaciones`
- Añadir el campo `image_ids` (One2many a `fleet.service.image`).

#### [MODIFY] `security/ir.model.access.csv`
- Añadir los permisos correspondientes (read, write, create, unlink) para el nuevo modelo `fleet.service.image`.

#### [MODIFY] `views/fleet_vehicle_log_services_views.xml`
- Agregar dos nuevas pestañas (`<page>`) dentro del `<notebook>`:
  - **Informe de Mantenimiento**: Agrupará los 4 campos de texto libre.
  - **Evidencias Fotográficas**: Mostrará el `image_ids` con vista Kanban para visualizar las miniaturas, o lista.

### 7. Fase 5: Validación Flexible de Inventario (Pop-up de Confirmación)
**Objetivo**: Advertir al usuario si no hay inventario suficiente al pasar la orden a "En Progreso", pero darle la opción de "Continuar" bajo su propia responsabilidad o "Cancelar".

#### [NEW] `models/fleet_service_inventory_warning.py`
Se creará un modelo transitorio (`TransientModel`) llamado `fleet.service.inventory.warning` que actuará como el Pop-up. Contendrá un mensaje de texto mostrando qué piezas faltan y un botón para forzar el cambio de estado.

#### [NEW] `views/fleet_service_inventory_warning_views.xml`
Se creará la vista del Pop-up con los botones "Continuar" y "Cancelar".

#### [MODIFY] `models/fleet_vehicle_log_services.py`
Se actualizará el método `action_in_progress()` para:
1. Buscar la ubicación de stock principal.
2. Iterar sobre los repuestos solicitados y sumar el inventario disponible.
3. Si faltan productos, abrir el Pop-up (wizard) detallando qué falta (Requerido vs Disponible). Si el usuario da clic en "Continuar", el estado pasará forzosamente a "En Progreso". Si hay inventario completo, pasará directamente sin abrir nada.

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
