from odoo import models, fields

class FishFeed(models.Model):
    _name = 'fish.farm.feed'
    _description = 'Fish Feeding Operation'

    pond_id = fields.Many2one('fish.farm.pond', string="الحوض", required=True)
    date = fields.Date(string="تاريخ التغذية", required=True)
    item = fields.Char(string="نوع الغذاء / الدواء")
    quantity = fields.Float(string="الكمية")
    notes = fields.Text(string="ملاحظات")
