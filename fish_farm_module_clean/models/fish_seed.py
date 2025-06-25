from odoo import models, fields

class FishSeed(models.Model):
    _name = 'fish.farm.seed'
    _description = 'Fish Seeding'

    name = fields.Char(required=True)
    pond_id = fields.Many2one('fish.farm.pond', string="Pond", required=True)
    seed_date = fields.Date(required=True)
    fish_type = fields.Selection([
        ('tilapia', 'Tilapia'),
        ('shrimp', 'Shrimp'),
        ('catfish', 'Catfish'),
        ('other', 'Other')
    ], string="Fish Type", required=True)
    quantity_kg = fields.Float(string="Quantity (kg)")
