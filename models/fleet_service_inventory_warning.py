from odoo import models, fields

class FleetServiceInventoryWarning(models.TransientModel):
    _name = 'fleet.service.inventory.warning'
    _description = 'Advertencia de Inventario de Servicio'

    service_id = fields.Many2one('fleet.vehicle.log.services', string='Servicio', required=True)
    message = fields.Text(string='Mensaje', readonly=True)

    def action_continue(self):
        self.ensure_one()
        if self.service_id:
            # Forzar el estado a "En Progreso" ignorando la advertencia
            self.service_id.write({'state': 'in_progress'})
        return {'type': 'ir.actions.act_window_close'}
