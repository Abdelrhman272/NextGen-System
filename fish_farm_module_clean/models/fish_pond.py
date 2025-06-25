from odoo import models, fields

class FishPond(models.Model):
    _name = 'fish.farm.pond'
    _description = 'Fish Pond'

    name = fields.Char(string="Pond Name", required=True)
    sector_id = fields.Many2one('fish.farm.sector', string="Sector", required=True)
    size = fields.Float(string="Size (m²)")
