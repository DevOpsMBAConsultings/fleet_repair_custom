{
    'name': 'Gestión de Reparaciones de Flota',
    'version': '16.0.1.0.4',
    'category': 'Human Resources/Fleet',
    'summary': 'Control de inventario para reparaciones y mantenimientos de vehículos',
    'author': 'MBA Consultings',
    'depends': ['fleet', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_log_services_views.xml',
        'views/fleet_service_type_views.xml',
        'views/fleet_menu_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
