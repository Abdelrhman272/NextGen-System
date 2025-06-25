from odoo import models, fields

class FishHarvest(models.Model):
    _name = 'fish.farm.harvest'
    _description = 'Fish Harvest'

    harvest_date = fields.Date(string="Harvest Date", required=True)
    pond_id = fields.Many2one('fish.farm.pond', string="Pond", required=True)
    quantity = fields.Float(string="Harvest Quantity (kg)", required=True)
    note = fields.Text(string="Notes")
