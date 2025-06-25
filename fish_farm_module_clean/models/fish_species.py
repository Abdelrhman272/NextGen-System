from odoo import models, fields

class FishSpecies(models.Model):
    _name = 'fish.farm.species'
    _description = 'Fish Species Master'
    _rec_name = 'name'

    name = fields.Char(string="نوع السمك", required=True)
    average_growth_period = fields.Integer(string="متوسط فترة النمو (يوم)")
