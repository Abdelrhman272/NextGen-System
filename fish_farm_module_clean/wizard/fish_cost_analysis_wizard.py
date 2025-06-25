from odoo import models, fields

class FishCostAnalysisWizard(models.TransientModel):
    _name = 'fish.farm.cost.analysis.wizard'
    _description = 'Wizard for Cost Analysis'

    fish_type = fields.Selection([
        ('tilapia', 'Tilapia'),
        ('catfish', 'Catfish'),
    ], string="Fish Type", required=True)
