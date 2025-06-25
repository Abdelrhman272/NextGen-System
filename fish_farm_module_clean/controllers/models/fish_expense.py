from odoo import models, fields

class FishExpense(models.Model):
    _name = 'fish.farm.expense'
    _description = 'Fish Farm Expense'

    name = fields.Char(string="Expense Reference", required=True)
    date = fields.Date(string="Date", required=True)
    amount = fields.Monetary(string="Amount", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self.env.company.currency_id)
    description = fields.Text(string="Description")
