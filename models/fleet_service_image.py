# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetServiceImage(models.Model):
    _name = 'fleet.service.image'
    _description = 'Imagen de Orden de Servicio'
    _order = 'sequence, id'

    service_id = fields.Many2one(
        'fleet.vehicle.log.services',
        string='Servicio',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    image = fields.Binary(string='Imagen', attachment=True)
    description = fields.Char(string='Descripción', placeholder='Descripción de la imagen...')

    @api.constrains('service_id')
    def _check_max_images(self):
        for rec in self:
            if len(rec.service_id.image_ids) > 15:
                raise ValidationError(
                    'Se permite un máximo de 15 imágenes por orden de servicio.'
                )
