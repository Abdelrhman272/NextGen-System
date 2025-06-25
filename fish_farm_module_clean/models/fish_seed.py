from odoo import models, fields

class FishSeed(models.Model):
    _name = 'fish.farm.seed'
    _description = 'Fish Seeding'

    name = fields.Char(string="Batch Reference", required=True)
    pond_id = fields.Many2one('fish.farm.pond', string="Pond", required=True)
    seed_date = fields.Date(string="Seeding Date", required=True)
    quantity = fields.Float(string="Quantity (kg)")
    fish_type = fields.Selection([('tilapia', 'Tilapia'), ('catfish', 'Catfish')], string="Fish Type")
