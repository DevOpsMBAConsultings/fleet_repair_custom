# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetServiceImage(models.Model):
    _name = 'fleet.service.image'
    _description = 'Imagen de Orden de Servicio'
    _order = 'sequence, id'

    service_id = fields.Many2one('fleet.vehicle.log.services', string='Servicio', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Secuencia', default=10)
    image_download = fields.Binary(string='Archivo', required=True)
    image = fields.Image(string='Imagen', related='image_download', max_width=1920, max_height=1920)
    image_filename = fields.Char(string='Nombre del Archivo')
    description = fields.Char(string='Descripción')

    def action_download(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/fleet.service.image/{self.id}/image_download?download=true',
            'target': 'self',
        }

    @api.constrains('service_id')
    def _check_image_limit(self):
        for record in self:
            count = self.search_count([('service_id', '=', record.service_id.id)])
            if count > 15:
                raise ValidationError("No se pueden agregar más de 15 imágenes por servicio.")
