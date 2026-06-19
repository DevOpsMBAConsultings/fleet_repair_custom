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

    # Informe de Mantenimiento
    antecedentes_servicio = fields.Html(string='Antecedentes del servicio')
    hallazgos = fields.Html(string='Hallazgos')
    accion_correctiva = fields.Html(string='Acción Correctiva')
    recomendaciones = fields.Html(string='Recomendaciones')

    # Imágenes (Usando modelo personalizado)
    image_ids = fields.One2many(
        'fleet.service.image',
        'service_id',
        string='Evidencias Fotográficas'
    )

    def action_waiting(self):
        for record in self:
            record.state = 'waiting'

    def _check_inventory_and_proceed(self, next_state):
        for record in self:
            missing_items = []
            company_id = record.company_id.id or self.env.company.id
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
            
            # Buscar ubicación de salida (igual que en onchange)
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
                for line in record.part_line_ids:
                    if line.product_id.type == 'product':
                        quants = self.env['stock.quant'].search([
                            ('product_id', '=', line.product_id.id),
                            ('location_id', '=', location_id.id)
                        ])
                        available_qty = sum(quants.mapped('available_quantity'))
                        if available_qty < line.quantity:
                            missing_items.append(f"<li><b>{line.product_id.name}</b> (Requerido: {line.quantity}, Disponible: {available_qty})</li>")
            
            if missing_items:
                state_label = "En Progreso" if next_state == 'in_progress' else "Hecho"
                message = "<p style='font-size: 15px; margin-bottom: 10px;'>Falta inventario para las siguientes piezas:</p><ul style='font-size: 14px;'>"
                message += "".join(missing_items)
                message += f"</ul><p style='font-size: 14px; margin-top: 15px;'><em>¿Desea continuar y pasar a {state_label} de todos modos?</em></p>"
                
                wizard = self.env['fleet.service.inventory.warning'].create({
                    'service_id': record.id,
                    'message': message,
                    'next_state': next_state
                })
                return {
                    'name': 'Advertencia de Inventario',
                    'type': 'ir.actions.act_window',
                    'res_model': 'fleet.service.inventory.warning',
                    'res_id': wizard.id,
                    'view_mode': 'form',
                    'target': 'new',
                }
                
            # Si no hay faltantes, proceder directamente
            if next_state == 'done':
                if record.part_line_ids and not record.picking_id:
                    record._create_stock_picking()
                record.state = 'done'
            else:
                record.state = 'in_progress'

    def action_in_progress(self):
        return self._check_inventory_and_proceed('in_progress')

    def action_done(self):
        return self._check_inventory_and_proceed('done')
            
    def action_cancel(self):
        for record in self:
            if record.picking_id and record.picking_id.state not in ('done', 'cancel'):
                record.picking_id.action_cancel()
            record.state = 'cancelled'

    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def action_reopen(self):
        for record in self:
            record.state = 'in_progress'

    def _create_stock_picking(self):
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']
        
        for record in self:
            company_id = record.company_id.id or self.env.company.id
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
            
            # Buscamos operación interna (Consumo propio)
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('warehouse_id', '=', warehouse.id)
            ], limit=1)
            
            if not picking_type:
                picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'outgoing'),
                    ('warehouse_id', '=', warehouse.id)
                ], limit=1)
                
            if not picking_type:
                raise UserError(_("No se encontró un tipo de operación válida para procesar el inventario."))
                
            # Enviamos a la ubicación virtual de inventario/ajustes para registrar el gasto
            location_dest_id = self.env['stock.location'].search([('usage', '=', 'inventory'), ('company_id', 'in', [False, company_id])], limit=1)
            if not location_dest_id:
                location_dest_id = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
            if not location_dest_id:
                location_dest_id = picking_type.default_location_dest_id
            
            picking_vals = {
                'picking_type_id': picking_type.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': location_dest_id.id,
                'origin': f"{(record.description or 'Servicio Flota')} - {record.vehicle_id.name}",
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
                
            # =================================================================
            # AQUÍ COMIENZA EL CAMBIO (REEMPLAZA LO ANTERIOR)
            # =================================================================
            picking.action_confirm()
            picking.action_assign() 
            
            for move in picking.move_ids_without_package:
                move.quantity_done = move.product_uom_qty
            
            picking.with_context(skip_backorder=True, skip_immediate=True).button_validate()
            
            record.picking_id = picking.id
            # =================================================================

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
