from odoo import models, fields

class FishSector(models.Model):
    _name = 'fish.farm.sector'
    _description = 'Fish Farm Sector'

    name = fields.Char(required=True)
    description = fields.Text()
