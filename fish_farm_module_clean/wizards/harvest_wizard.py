from odoo import models, fields, api

class HarvestWizard(models.TransientModel):
    _name = 'fish.harvest.wizard'
    _description = 'Fish Harvest Wizard'
    
    cycle_id = fields.Many2one('fish.breeding.cycle', 'Breeding Cycle', required=True)
    harvest_date = fields.Date('Harvest Date', default=fields.Date.today)
    quantity = fields.Float('Quantity (kg)', required=True)
    quality = fields.Selection([
        ('a', 'Grade A'),
        ('b', 'Grade B'),
        ('c', 'Grade C')
    ], 'Quality Grade', required=True, default='a')
    committee_member_ids = fields.Many2many('hr.employee', string='Committee Members')
    
    def action_create_harvest(self):
        self.ensure_one()
        harvest = self.env['fish.harvest'].create({
            'cycle_id': self.cycle_id.id,
            'harvest_date': self.harvest_date,
            'quantity': self.quantity,
            'quality': self.quality,
            'committee_member_ids': [(6, 0, self.committee_member_ids.ids)]
        })
        return {
            'name': 'Harvest Record',
            'type': 'ir.actions.act_window',
            'res_model': 'fish.harvest',
            'res_id': harvest.id,
            'view_mode': 'form',
            'target': 'current',
        }