from odoo import models, fields

class FishPond(models.Model):
    _name = 'fish.farm.pond'
    _description = 'Fish Pond'

    name = fields.Char(required=True)
    slice_id = fields.Many2one('fish.farm.slice', string="Slice", required=True)
    area_m2 = fields.Float(string="Area (m²)")
    water_source = fields.Selection([
        ('fresh', 'Fresh Water'),
        ('sea', 'Sea Water'),
        ('mixed', 'Mixed')
    ], string="Water Source")
