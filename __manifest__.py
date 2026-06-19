{
    'name': 'Gestión de Reparaciones de Flota',
    'version': '16.0.1.0.25',
    'category': 'Human Resources/Fleet',
    'summary': 'Control de inventario para reparaciones y mantenimientos de vehículos',
    'description': """
Módulo de Gestión de Reparaciones de Flota
==========================================
Este módulo permite a las empresas llevar un control exhaustivo sobre los servicios de mantenimiento y reparaciones de sus vehículos.

Características Principales:
* Control de inventario en tiempo real al agregar repuestos a una orden de servicio.
* Avisos dinámicos en caso de falta de stock de refacciones.
* Integración nativa con Odoo Inventory para devoluciones y ajustes.
* Restricciones de estado para asegurar la auditoría y cierre correcto de las órdenes de servicio.

Desarrollado por MBA Consultings.
    """,
    'author': 'MBA Consultings',
    'website': 'https://mbaconsultings.com',
    'depends': ['fleet', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_log_services_views.xml',
        'views/fleet_service_type_views.xml',
        'views/fleet_menu_views.xml',
        'views/stock_picking_views.xml',
        'views/fleet_service_inventory_warning_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
