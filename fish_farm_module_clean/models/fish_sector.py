from odoo import models, fields

class FishSector(models.Model):
    _name = 'fish.farm.sector'
    _description = 'Fish Farm Sector'
    _rec_name = 'name'

    name = fields.Char(string="اسم القطاع", required=True)
    code = fields.Char(string="الكود", required=True)
    description = fields.Text(string="الوصف")
