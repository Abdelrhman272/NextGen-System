from odoo import models, fields

class FishSlice(models.Model):
    _name = 'fish.farm.slice'
    _description = 'Fish Farm Slice'

    name = fields.Char(required=True)
    sector_id = fields.Many2one('fish.farm.sector', string="Sector", required=True)
    code = fields.Char()
