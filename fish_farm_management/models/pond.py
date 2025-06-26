from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FishPond(models.Model):
    _name = 'fish.pond'
    _description = 'Fish Pond'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'segment_id, name'

    # ------------------------------------------------------------------
    # FIELDS
    # ------------------------------------------------------------------
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
    ], default='empty', tracking=True)

    current_cycle_id = fields.Many2one('fish.breeding.cycle', 'Current Breeding Cycle')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', copy=False)
    location_id = fields.Many2one('stock.location', 'Inventory Location', copy=False)

    # ------------------------------------------------------------------
    # COMPUTES
    # ------------------------------------------------------------------
    @api.depends('area', 'depth')
    def _compute_volume(self):
        for pond in self:
            pond.volume = pond.area * pond.depth

    # ------------------------------------------------------------------
    # CRUD OVERRIDES
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        ponds = super().create(vals_list)
        for pond in ponds:
            if not pond.analytic_account_id:
                pond.analytic_account_id = self.env['account.analytic.account'].create({
                    'name': f'{pond.name} - Analytic Account',
                    'code': f'POND-{pond.id}',
                    'company_id': pond.company_id.id,
                }).id
        return ponds

    # ------------------------------------------------------------------
    # ACTIONS (form header buttons)
    # ------------------------------------------------------------------
    def action_start_cycle(self):
        """Start a new breeding cycle only if pond is empty."""
        BreedingCycle = self.env['fish.breeding.cycle']
        for pond in self:
            if pond.state != 'empty':
                raise UserError(_("You can only start a new cycle when the pond is empty."))
            cycle = BreedingCycle.create({
                'pond_id': pond.id,
                'fish_type_id': pond.fish_type_ids[:1].id if pond.fish_type_ids else False,
                'start_date': fields.Date.today(),
                'state': 'running',
            })
            pond.current_cycle_id = cycle.id
            pond.state = 'stocked'
        return True

    def action_view_cycle(self):
        """Open the current breeding cycle form."""
        self.ensure_one()
        if not self.current_cycle_id:
            raise UserError(_("No breeding cycle is linked to this pond."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Current Breeding Cycle'),
            'res_model': 'fish.breeding.cycle',
            'view_mode': 'form',
            'res_id': self.current_cycle_id.id,
            'target': 'current',
        }
