from odoo import models, fields

class FishExpense(models.Model):
    _name = 'fish.farm.expense'
    _description = 'Fish Farm Expense'

    pond_id = fields.Many2one('fish.farm.pond', string="الحوض")
    expense_type = fields.Selection([
        ('electricity', 'كهرباء'),
        ('labor', 'عمالة'),
        ('fuel', 'محروقات'),
        ('maintenance', 'صيانة'),
        ('other', 'أخرى')
    ], string="نوع المصروف")
    amount = fields.Float(string="القيمة")
    date = fields.Date(string="التاريخ")
    description = fields.Text(string="الوصف")
