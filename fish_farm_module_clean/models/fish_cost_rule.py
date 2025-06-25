from odoo import models, fields

class FishCostRule(models.Model):
    _name = 'fish.farm.cost.rule'
    _description = 'Fish Cost Distribution Rule'

    name = fields.Char(string="الاسم التعريفي", required=True)
    cost_type = fields.Selection([
        ('direct', 'تكاليف مباشرة'),
        ('indirect', 'تكاليف غير مباشرة')
    ], string="نوع التكلفة", required=True)
    distribution_percentage = fields.Float(string="نسبة التوزيع")
