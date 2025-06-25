from odoo import models, fields

class FishHarvest(models.Model):
    _name = 'fish.farm.harvest'
    _description = 'Fish Harvest Record'

    pond_id = fields.Many2one('fish.farm.pond', string="الحوض", required=True)
    harvest_date = fields.Date(string="تاريخ الحصاد", required=True)
    quantity_kg = fields.Float(string="الكمية بالكيلو")
    quality = fields.Selection([
        ('high', 'جودة عالية'),
        ('medium', 'جودة متوسطة'),
        ('low', 'جودة منخفضة')
    ], string="الجودة")
    round_number = fields.Integer(string="رقم دفعة الحصاد")
