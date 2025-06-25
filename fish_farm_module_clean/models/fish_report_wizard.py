from odoo import models, fields
from datetime import date

class FishCostAnalysisWizard(models.TransientModel):
    _name = 'fish.farm.cost.analysis.wizard'
    _description = 'تحليل التكاليف حسب الحوض'

    date_from = fields.Date(string="من تاريخ", default=date.today)
    date_to = fields.Date(string="إلى تاريخ", default=date.today)
    pond_id = fields.Many2one('fish.farm.pond', string="الحوض")

    def print_report(self):
        data = {
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'pond_id': self.pond_id.id,
            },
        }
        return self.env.ref('fish_farm_module_clean.action_report_fish_cost_analysis').report_action(self, data=data)
