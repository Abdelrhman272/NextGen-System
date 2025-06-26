from odoo import models, fields, api

class FishFarm(models.Model):
    _name = 'fish.farm'
    _description = 'Fish Farm'
    _order = 'name'

    name = fields.Char('Farm Name', required=True)
    code = fields.Char('Farm Code')
    manager_id = fields.Many2one('hr.employee', 'Farm Manager')
    start_date = fields.Date('Start Date')
    location = fields.Char('Location')
    sector_ids = fields.One2many('fish.farm.sector', 'farm_id', 'Sectors')
    total_area = fields.Float('Total Area (m²)', compute='_compute_total_area')
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    
    @api.depends('sector_ids.area')
    def _compute_total_area(self):
        for farm in self:
            farm.total_area = sum(sector.area for sector in farm.sector_ids)