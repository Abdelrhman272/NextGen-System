from odoo import models, fields

class FishSeed(models.Model):
    _name = 'fish.farm.seed'
    _description = 'Fish Seed Entry'
    _rec_name = 'fish_type'

    pond_id = fields.Many2one('fish.farm.pond', string="الحوض", required=True)
    fish_type = fields.Selection([
        ('tilapia', 'بلطي'),
        ('shrimp', 'جمبري'),
        ('other', 'أخرى')
    ], string="نوع الزريعة", required=True)
    quantity = fields.Float(string="الكمية (وحدة)")
    received_date = fields.Date(string="تاريخ التوريد")
