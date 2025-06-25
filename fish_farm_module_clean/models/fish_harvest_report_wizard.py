from odoo import models, fields
from datetime import date

class FishHarvestReportWizard(models.TransientModel):
    _name = 'fish.farm.harvest.report.wizard'
    _description = 'تقرير الصيد للحوض'

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
        return self.env.ref('fish_farm_module_clean.action_report_fish_harvest_summary').report_action(self, data=data)
