from odoo import models, fields

class FishHarvestReportWizard(models.TransientModel):
    _name = 'fish.farm.harvest.report.wizard'
    _description = 'Wizard to Generate Harvest Report'

    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
