from odoo import models, fields

class FishExpense(models.Model):
    _name = 'fish.farm.expense'
    _description = 'Direct or Indirect Expense'

    pond_id = fields.Many2one('fish.farm.pond', string="Related Pond")
    date = fields.Date(required=True)
    type = fields.Selection([
        ('electricity', 'Electricity'),
        ('fuel', 'Fuel'),
        ('labor', 'Labor'),
        ('other', 'Other')
    ], string="Expense Type", required=True)
    amount = fields.Monetary(string="Amount")
    description = fields.Text()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
