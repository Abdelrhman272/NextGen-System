from odoo import models, fields, api

class CostDistribution(models.Model):
    _name = 'fish.cost.distribution'
    _description = 'Fish Farm Cost Distribution'

    name = fields.Char('Description', required=True)
    date = fields.Date('Date', default=fields.Date.today)
    amount = fields.Float('Amount', required=True)
    cycle_id = fields.Many2one('fish.breeding.cycle', 'Breeding Cycle')
    pond_id = fields.Many2one('fish.pond', 'Pond', related='cycle_id.pond_id', store=True)
    cost_type = fields.Selection([
        ('feed', 'Feed'),
        ('electricity', 'Electricity'),
        ('labor', 'Labor'),
        ('medicine', 'Medicine'),
        ('fuel', 'Fuel'),
        ('other', 'Other'),
    ], 'Cost Type', required=True)
    note = fields.Text('Note')
    account_move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    
    def action_create_journal_entry(self):
        self.ensure_one()
        # Create journal entry logic
        return True