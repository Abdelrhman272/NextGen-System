from odoo import models, fields

class FishCostRule(models.Model):
    _name = 'fish.farm.cost.rule'
    _description = 'Fish Cost Rule'

    name = fields.Char(string="Rule Name", required=True)
    fish_type = fields.Selection([('tilapia', 'Tilapia'), ('catfish', 'Catfish')], string="Fish Type", required=True)
    cost_per_kg = fields.Float(string="Cost Per KG")
