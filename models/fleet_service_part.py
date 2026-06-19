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
        if self.service_id.state == 'in_progress' and self.product_id and self.product_id.type == 'product':
            # Revisamos disponibilidad en inventario
            company_id = self.service_id.company_id.id or self.env.company.id
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
            
            # Buscamos la ubicación de salida del almacén
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
                            'title': _('Inventario Insuficiente'),
                            'message': _(
                                'No hay suficiente stock de "%s".\n'
                                'Requerido: %s\n'
                                'Disponible: %s\n\n'
                                'Sugerencia: Si el mecánico detectó que se necesita esta pieza mientras reparaba, '
                                'te sugerimos guardar el registro y presionar "Poner en Espera" para pausar el servicio '
                                'hasta que llegue el repuesto.'
                            ) % (self.product_id.name, self.quantity, available_qty)
                        }
                    }
