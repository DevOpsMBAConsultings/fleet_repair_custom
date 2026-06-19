from odoo import models, fields, api, _

class FleetServicePart(models.Model):
    _name = 'fleet.service.part'
    _description = 'Repuestos consumidos en el servicio'

    service_id = fields.Many2one('fleet.vehicle.log.services', string='Servicio', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Repuesto/Insumo', required=True, domain=[('type', 'in', ['product', 'consu'])])
    quantity = fields.Float(string='Cantidad', default=1.0, required=True)
    uom_id = fields.Many2one(related='product_id.uom_id', string='Unidad de Medida', readonly=True)

    @api.onchange('product_id', 'quantity')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.type == 'product':
            # Revisamos disponibilidad en inventario
            company_id = self.service_id.company_id.id or self.env.company.id
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
            
            # Buscamos la ubicación de salida del almacén (igual que en _create_stock_picking)
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('warehouse_id', '=', warehouse.id)
            ], limit=1)
            
            if not picking_type:
                picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'outgoing'),
                    ('warehouse_id', '=', warehouse.id)
                ], limit=1)
            
            if picking_type and picking_type.default_location_src_id:
                location_id = picking_type.default_location_src_id
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', self.product_id.id),
                    ('location_id', '=', location_id.id)
                ])
                available_qty = sum(quants.mapped('available_quantity'))
                
                if available_qty < self.quantity:
                    return {
                        'warning': {
                            'title': _('Advertencia de Inventario'),
                            'message': _(
                                '¡Atención! Se han detectado problemas de disponibilidad en el inventario.\n\n'
                                'Falta inventario para la pieza:\n'
                                '- %s (Requerido: %s, Disponible: %s)\n\n'
                                'Si necesitas este repuesto, te sugerimos pulsar "Aceptar", guardar la línea y '
                                'luego presionar el botón "Poner en Espera" para detener temporalmente el servicio '
                                'hasta que se reciba el inventario.'
                            ) % (self.product_id.name, self.quantity, available_qty)
                        }
                    }
