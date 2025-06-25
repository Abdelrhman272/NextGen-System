from odoo import models, fields

class FishHarvest(models.Model):
    _name = 'fish.farm.harvest'
    _description = 'Harvest Operation'

    pond_id = fields.Many2one('fish.farm.pond', string="Pond", required=True)
    harvest_date = fields.Date(required=True)
    quantity_kg = fields.Float(string="Harvested Quantity (kg)")
    method = fields.Selection([
        ('full', 'Full Harvest'),
        ('partial', 'Partial Harvest')
    ], string="Harvest Method")
    quality_grade = fields.Selection([
        ('a', 'Grade A'),
        ('b', 'Grade B'),
        ('c', 'Grade C')
    ], string="Quality Grade")
    notes = fields.Text()
