# Funcionalidades Implementadas: fleet_repair_custom

¡El desarrollo del módulo base está listo! A continuación te presento un resumen de los cambios implementados para cumplir con el alcance del MVP.

## 1. Integración de Estados en Servicios
El formulario estándar de **Mantenimiento/Servicios de Flota** (en la aplicación "Flota") ahora cuenta con un flujo de trabajo claro a través de una barra de estados (*Statusbar*).
- **Borrador (Draft):** Estado inicial para cuando el mecánico apenas está levantando los requerimientos.
- **En Progreso (In Progress):** El vehículo está siendo intervenido y se están ocupando los repuestos/insumos.
- **Terminado (Done):** Al presionar "Finalizar Servicio", se da por terminada la labor y se ejecuta la lógica de inventario.
- **Cancelado (Cancelled):** Permite reversar el proceso (y cancelar el movimiento de inventario si no ha sido procesado).

### Versión 16.0.1.0.2 - 2026-06-17
- Se rediseñó el `statusbar` para utilizar la directiva `position="replace"`, sobrescribiendo la barra nativa de Odoo y eliminando la duplicidad visual en pantalla.
- Se filtraron los estados disponibles en el backend de Odoo para la orden de servicio (`fleet.vehicle.log.services`), permitiendo únicamente los 5 estados dictados por las reglas de negocio (Borrador, En Espera, En Progreso, Hecho, Cancelado).
- Se estabilizó la versión para el entorno de desarrollo y se verificó que el flujo visual corresponde ahora exactamente al proceso real del taller.

### Versión 16.0.1.0.5 (Actual)
- **Pop-up de Validación de Inventario:** Se añadió una validación flexible al botón "En Progreso". Si el inventario físico en el almacén es insuficiente para los repuestos solicitados, se abre una ventana emergente advirtiendo al usuario exactamente qué falta (Ej: "Falta inventario para: Bujías (Requerido: 5, Disponible: 0)"). El usuario tiene la libertad de darle a "Continuar de todos modos" o "Cancelar".

## Versión 16.0.1.0.4
- **Trazabilidad de Inventario:** Se añadió el campo `fleet_service_id` (Orden de Servicio) en el modelo `stock.picking` para que el personal de almacén o el cliente pueda navegar con un clic desde el movimiento de inventario a la orden de servicio.
- **Auto-consumo:** Se modificó la lógica en `fleet_vehicle_log_services.py` para que, cuando el mecánico finaliza el servicio, el movimiento de inventario (Albarán) se confirme, se le asigne la cantidad necesaria y se **valide automáticamente**, descontando el inventario de forma inmediata y cerrando el ciclo.
- **Vistas:** Se inyectó el nuevo campo de Orden de Servicio en el formulario de Albaranes (`stock_picking_views.xml`).

## Versión 16.0.1.0.3 - 2026-06-17
- **Nuevas Categorías de Servicios:** Se agregó un nuevo campo personalizado (`custom_repair_category`) al modelo `fleet.service.type` que reemplaza visualmente al campo nativo de Odoo (`category`). Esto permite tener exactamente las opciones solicitadas: Mantenimiento, Mantenimiento Preventivo, Mantenimiento Correctivo, y Reparación.
- **Ocultamiento Nativo Protegido:** El campo de Odoo (`category`) se mantiene operando internamente por debajo para evitar romper la integridad de la base de datos de Odoo o los registros previos de otros módulos base.
- **Limpieza de Menú "Contratos":** Se ocultó por completo el submenú de "Contratos" (Leasing, Seguros) debajo de la categoría "Flota" al establecer la opción nativa de Odoo (`fleet.fleet_vehicle_log_contract_menu`) como inactiva, adecuando la vista a un negocio que solo repara sus propios equipos.

## 2. Pestaña de Repuestos e Insumos
Se agregó una nueva pestaña dentro del mismo formulario del servicio llamada **Repuestos / Insumos**.
- **Modelos involucrados:** Creamos un nuevo modelo técnico `fleet.service.part`.
- **Funcionalidad:** Permite agregar de forma sencilla cualquier producto inventariable (filtros, aceites, líquido de frenos) y su respectiva cantidad directamente en el servicio, sin tener que ir a otra pantalla.

## 3. Automatización de Inventario
El corazón de la solución. Cuando el mecánico o el encargado presiona el botón **"Finalizar Servicio"**:
1. El sistema lee todas las líneas de repuestos configuradas en la pestaña.
2. Genera automáticamente un **Movimiento de Inventario** (`stock.picking`) de tipo salida desde el almacén predeterminado hacia la ubicación de consumo o clientes.
3. Lo confirma automáticamente, descontando las unidades del stock físico disponible, asegurando que las "áreas de taller" o "bodega de la oficina" mantengan sus existencias reales actualizadas de inmediato.

## 4. Trazabilidad
Para que la parte administrativa pueda auditar o revisar qué ocurrió con el inventario de un servicio específico:
- Se añadió un **Botón Inteligente (Smart Button) "Inventario"** en la parte superior del formulario del servicio. Al hacer clic, te lleva directamente al documento de salida de inventario exacto que el sistema generó para esa reparación, garantizando trazabilidad total.

> [!TIP]
> **Próximos Pasos (Odoo Sandbox):**  
> Para probar esto, instala el módulo en tu servidor Odoo 16 CE local. Solo debes asegurar que tienes las apps **Flota (Fleet)** e **Inventario (Stock)** instaladas previamente. Crea un vehículo de prueba, un producto de prueba, asígnale algo de inventario (actualizar cantidad a mano) y corre un flujo de servicio hasta el final.
