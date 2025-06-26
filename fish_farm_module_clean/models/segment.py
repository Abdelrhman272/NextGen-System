from odoo import models, fields, api

class FishFarmSegment(models.Model):
    _name = 'fish.farm.segment'
    _description = 'Fish Farm Segment'
    _order = 'sequence, name'

    name = fields.Char('Segment Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    sector_id = fields.Many2one('fish.farm.sector', 'Sector', required=True)
    farm_id = fields.Many2one('fish.farm', related='sector_id.farm_id', store=True)
    pond_ids = fields.One2many('fish.pond', 'segment_id', 'Ponds')
    area = fields.Float('Area (m²)')
    description = fields.Text('Description', translate=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)