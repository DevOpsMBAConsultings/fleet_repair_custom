from odoo import models, fields

class FleetServiceInventoryWarning(models.TransientModel):
    _name = 'fleet.service.inventory.warning'
    _description = 'Advertencia de Inventario de Servicio'

    service_id = fields.Many2one('fleet.vehicle.log.services', string='Servicio', required=True)
    message = fields.Html(string='Mensaje', readonly=True)
    next_state = fields.Selection([('in_progress', 'En Progreso'), ('done', 'Hecho')], default='in_progress')

    def action_continue(self):
        self.ensure_one()
        if self.service_id:
            if self.next_state == 'done':
                if self.service_id.part_line_ids and not self.service_id.picking_id:
                    self.service_id._create_stock_picking()
                self.service_id.write({'state': 'done'})
            else:
                self.service_id.write({'state': 'in_progress'})
        return {'type': 'ir.actions.act_window_close'}
