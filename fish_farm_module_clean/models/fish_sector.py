from odoo import models, fields

class FishSector(models.Model):
    _name = 'fish.farm.sector'
    _description = 'Fish Farm Sector'

    name = fields.Char(string="اسم القطاع", required=True)
    code = fields.Char(string="الكود", required=True)
    description = fields.Text(string="الوصف")
