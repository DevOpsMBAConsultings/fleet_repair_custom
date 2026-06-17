from odoo import models, fields

class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    custom_repair_category = fields.Selection([
        ('mantenimiento', 'Mantenimiento'),
        ('preventivo', 'Mantenimiento Preventivo'),
        ('correctivo', 'Mantenimiento Correctivo'),
        ('reparacion', 'Reparación')
    ], string='Categoría', default='mantenimiento')
