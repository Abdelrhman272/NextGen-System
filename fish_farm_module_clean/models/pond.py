from odoo import models, fields, api

class FishPond(models.Model):
    _name = 'fish.pond'
    _description = 'Fish Pond'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'segment_id, name'

    name = fields.Char('Pond Name', required=True)
    code = fields.Char('Pond Code')
    segment_id = fields.Many2one('fish.farm.segment', 'Segment', required=True)
    sector_id = fields.Many2one('fish.farm.sector', related='segment_id.sector_id', store=True)
    farm_id = fields.Many2one('fish.farm', related='sector_id.farm_id', store=True)
    area = fields.Float('Area (m²)')
    depth = fields.Float('Depth (m)')
    volume = fields.Float('Volume (m³)', compute='_compute_volume')
    fish_type_ids = fields.Many2many('fish.type', string='Fish Types')
    state = fields.Selection([
        ('empty', 'Empty'),
        ('preparing', 'Preparing'),
        ('stocked', 'Stocked'),
        ('harvesting', 'Harvesting'),
        ('maintenance', 'Maintenance')
    ], 'Status', default='empty', tracking=True)
    current_cycle_id = fields.Many2one('fish.breeding.cycle', 'Current Breeding Cycle')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', copy=False)
    location_id = fields.Many2one('stock.location', 'Inventory Location', copy=False)
    
    @api.depends('area', 'depth')
    def _compute_volume(self):
        for pond in self:
            pond.volume = pond.area * pond.depth
    
    @api.model
    def create(self, vals):
        pond = super(FishPond, self).create(vals)
        # Create analytic account for cost tracking
        pond.analytic_account_id = self.env['account.analytic.account'].create({
            'name': f'{pond.name} - Analytic Account',
            'code': f'POND-{pond.id}',
            'company_id': pond.company_id.id,
        }).id
        return pond