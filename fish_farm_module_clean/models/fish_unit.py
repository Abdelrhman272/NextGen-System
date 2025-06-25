from odoo import models, fields

class FishUnit(models.Model):
    _name = 'fish.farm.unit'
    _description = 'Fish Farm Unit'

    name = fields.Char(string="اسم الشريحة", required=True)
    sector_id = fields.Many2one('fish.farm.sector', string="القطاع", required=True)
    code = fields.Char(string="الكود")
