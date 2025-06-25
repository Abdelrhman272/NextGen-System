# # لو حبيت تضيف جداول مشتركة في الموديول كله (زي جدول farm أو عملية عامة)
from odoo import models, fields

class FishFarm(models.Model):
    _name = 'fish.farm'
    _description = 'Fish Farm General Info'

    name = fields.Char(string="Farm Name", required=True)
    location = fields.Char(string="Location")

