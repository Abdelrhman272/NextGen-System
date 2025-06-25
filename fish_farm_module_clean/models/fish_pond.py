from odoo import models, fields

class FishPond(models.Model):
    _name = 'fish.farm.pond'
    _description = 'Fish Farm Pond'

    name = fields.Char(string="اسم الحوض", required=True)
    unit_id = fields.Many2one('fish.farm.unit', string="الشريحة", required=True)
    volume = fields.Float(string="السعة (م³)")
    fish_type = fields.Selection([
        ('tilapia', 'بلطي'),
        ('shrimp', 'جمبري'),
        ('other', 'أخرى')
    ], string="نوع السمك")
