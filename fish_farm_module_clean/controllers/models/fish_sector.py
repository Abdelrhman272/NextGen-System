from odoo import models, fields

class FishSector(models.Model):
    _name = 'fish.farm.sector'
    _description = 'Fish Sector'

    name = fields.Char(string="Sector Name", required=True)
    description = fields.Text(string="Description")
