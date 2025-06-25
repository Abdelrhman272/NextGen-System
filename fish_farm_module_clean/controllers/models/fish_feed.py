from odoo import models, fields

class FishFeed(models.Model):
    _name = 'fish.farm.feed'
    _description = 'Fish Feeding Record'

    feed_date = fields.Date(string="Feeding Date", required=True)
    pond_id = fields.Many2one('fish.farm.pond', string="Pond", required=True)
    quantity = fields.Float(string="Feed Quantity (kg)", required=True)
    feed_type = fields.Char(string="Feed Type")
