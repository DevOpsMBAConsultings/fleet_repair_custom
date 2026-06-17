from odoo import models, fields

class FleetServicePart(models.Model):
    _name = 'fleet.service.part'
    _description = 'Repuestos consumidos en el servicio'

    service_id = fields.Many2one('fleet.vehicle.log.services', string='Servicio', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Repuesto/Insumo', required=True, domain=[('type', 'in', ['product', 'consu'])])
    quantity = fields.Float(string='Cantidad', default=1.0, required=True)
    uom_id = fields.Many2one(related='product_id.uom_id', string='Unidad de Medida', readonly=True)
