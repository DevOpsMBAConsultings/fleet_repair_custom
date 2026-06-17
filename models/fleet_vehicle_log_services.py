from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('waiting', 'En Espera'),
        ('in_progress', 'En Progreso'),
        ('done', 'Hecho'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='draft', required=True, tracking=True)
    
    part_line_ids = fields.One2many('fleet.service.part', 'service_id', string='Repuestos / Insumos')
    picking_id = fields.Many2one('stock.picking', string='Movimiento de Inventario', readonly=True, copy=False)

    def action_waiting(self):
        for record in self:
            record.state = 'waiting'

    def action_in_progress(self):
        for record in self:
            missing_items = []
            company_id = record.company_id.id or self.env.company.id
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing'),
                ('warehouse_id', '=', warehouse.id)
            ], limit=1)
            
            if picking_type and picking_type.default_location_src_id:
                location_id = picking_type.default_location_src_id
                for line in record.part_line_ids:
                    if line.product_id.type == 'product':
                        quants = self.env['stock.quant'].search([
                            ('product_id', '=', line.product_id.id),
                            ('location_id', '=', location_id.id)
                        ])
                        available_qty = sum(quants.mapped('available_quantity'))
                        if available_qty < line.quantity:
                            missing_items.append(f"- {line.product_id.name} (Requerido: {line.quantity}, Disponible: {available_qty})")
            
            if missing_items:
                message = "Falta inventario para las siguientes piezas:\n" + "\n".join(missing_items) + "\n\nSi le das a Continuar, la orden pasará a En Progreso."
                wizard = self.env['fleet.service.inventory.warning'].create({
                    'service_id': record.id,
                    'message': message
                })
                return {
                    'name': 'Advertencia de Inventario',
                    'type': 'ir.actions.act_window',
                    'res_model': 'fleet.service.inventory.warning',
                    'res_id': wizard.id,
                    'view_mode': 'form',
                    'target': 'new',
                }
                
            record.state = 'in_progress'

    def action_done(self):
        for record in self:
            if record.part_line_ids and not record.picking_id:
                record._create_stock_picking()
            record.state = 'done'
            
    def action_cancel(self):
        for record in self:
            if record.picking_id and record.picking_id.state not in ('done', 'cancel'):
                record.picking_id.action_cancel()
            record.state = 'cancelled'

    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def _create_stock_picking(self):
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']
        
        for record in self:
            company_id = record.company_id.id or self.env.company.id
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing'),
                ('warehouse_id', '=', warehouse.id)
            ], limit=1)
            
            if not picking_type:
                raise UserError(_("No se encontró un tipo de operación de salida (Delivery) en el almacén principal."))
                
            location_dest_id = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
            if not location_dest_id:
                location_dest_id = picking_type.default_location_dest_id
            
            picking_vals = {
                'picking_type_id': picking_type.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': location_dest_id.id,
                'origin': f"{(record.description or 'Servicio')} - {record.vehicle_id.name}",
                'fleet_service_id': record.id,
                'company_id': company_id,
            }
            picking = StockPicking.create(picking_vals)
            
            for line in record.part_line_ids:
                move_vals = {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': picking.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                }
                StockMove.create(move_vals)
                
            # Validar automáticamente el picking
            picking.action_confirm()
            picking.action_assign()
            for move in picking.move_ids_without_package:
                move.quantity_done = move.product_uom_qty
            picking.button_validate()
            
            record.picking_id = picking.id
            
    def action_view_picking(self):
        self.ensure_one()
        if not self.picking_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': 'Movimiento de Inventario',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
            'target': 'current',
        }
