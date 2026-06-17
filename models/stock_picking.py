from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fleet_service_id = fields.Many2one(
        'fleet.vehicle.log.services',
        string='Orden de Servicio',
        readonly=True,
        help="Orden de servicio de flota asociada a este movimiento de inventario."
    )
