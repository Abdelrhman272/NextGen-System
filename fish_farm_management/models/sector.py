from odoo import models, fields, api

class FishFarmSector(models.Model):
    _name = 'fish.farm.sector'
    _description = 'Fish Farm Sector'
    _order = 'sequence, name'

    name = fields.Char('Sector Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    farm_id = fields.Many2one('fish.farm', 'Farm', required=True)
    segment_ids = fields.One2many('fish.farm.segment', 'sector_id', 'Segments')
    area = fields.Float('Area (m²)')
    description = fields.Text('Description', translate=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.depends('segment_ids.area')
    def _compute_total_area(self):
        for sector in self:
            sector.area = sum(segment.area for segment in sector.segment_ids)