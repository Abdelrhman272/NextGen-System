from odoo import models, fields
from datetime import date

class FishCostAnalysisWizard(models.TransientModel):
    _name = 'fish.farm.cost.analysis.wizard'
    _description = 'تحليل التكاليف حسب الحوض'

    date_from = fields.Date(string="من تاريخ", default=date.today)
    date_to = fields.Date(string="إلى تاريخ", default=date.today)
    pond_id = fields.Many2one('fish.farm.pond', string="الحوض")

class FishHarvestReportWizard(models.TransientModel):
    _name = 'fish.farm.harvest.report.wizard'
    _description = 'تقرير الصيد للحوض'

    date_from = fields.Date(string="من تاريخ", default=date.today)
    date_to = fields.Date(string="إلى تاريخ", default=date.today)
    pond_id = fields.Many2one('fish.farm.pond', string="الحوض")
