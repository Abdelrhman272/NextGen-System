from odoo import models, fields

class FishFeed(models.Model):
    _name = 'fish.farm.feed'
    _description = 'Feeding Operation'

    pond_id = fields.Many2one('fish.farm.pond', string="Pond", required=True)
    feed_date = fields.Date(required=True)
    feed_type = fields.Char()
    quantity_kg = fields.Float(string="Quantity (kg)")
    notes = fields.Text()
