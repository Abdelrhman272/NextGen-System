from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class BreedingCycle(models.Model):
    _name = 'fish.breeding.cycle'
    _description = 'Fish Breeding Cycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(
        string='Cycle Reference',
        required=True,
        index=True,
        default='New',
        copy=False
    )
    pond_id = fields.Many2one(
        'fish.pond',
        string='Pond',
        required=True,
        tracking=True
    )
    fish_type_id = fields.Many2one(
        'fish.type',
        string='Fish Type',
        required=True,
        tracking=True
    )
    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.today,
        tracking=True
    )
    end_date = fields.Date(
        string='End Date',
        tracking=True
    )
    duration = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration',
        store=True
    )
    initial_stock = fields.Integer(
        string='Initial Stock',
        required=True
    )
    estimated_harvest_date = fields.Date(
        string='Estimated Harvest Date',
        compute='_compute_estimated_harvest_date',
        store=True
    )
    harvest_ids = fields.One2many(
        'fish.harvest',
        'cycle_id',
        string='Harvests'
    )
    total_harvested = fields.Float(
        string='Total Harvested (kg)',
        compute='_compute_total_harvested',
        store=True
    )
    feed_consumption = fields.Float(
        string='Feed Consumption (kg)',
        tracking=True
    )
    mortality_rate = fields.Float(
        string='Mortality Rate (%)',
        compute='_compute_mortality_rate',
        store=True
    )
    cost_ids = fields.One2many(
        'fish.cost.distribution',
        'cycle_id',
        string='Costs'
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('preparing', 'Preparing'),
        ('stocked', 'Stocked'),
        ('growing', 'Growing'),
        ('harvesting', 'Harvesting'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], string='Status',
        default='draft',
        tracking=True
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Cycle reference must be unique!'),
        ('positive_stock', 'CHECK(initial_stock >= 0)', 'Initial stock must be positive!'),
        ('valid_dates', 'CHECK(start_date <= end_date OR end_date IS NULL)', 'End date cannot be before start date!')
    ]

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for cycle in self:
            if cycle.start_date and cycle.end_date:
                delta = cycle.end_date - cycle.start_date
                cycle.duration = delta.days
            else:
                cycle.duration = 0

    @api.depends('start_date', 'fish_type_id.growth_period')
    def _compute_estimated_harvest_date(self):
        for cycle in self:
            if cycle.start_date and cycle.fish_type_id and cycle.fish_type_id.growth_period:
                cycle.estimated_harvest_date = cycle.start_date + timedelta(days=cycle.fish_type_id.growth_period)
            else:
                cycle.estimated_harvest_date = False

    @api.depends('harvest_ids.quantity')
    def _compute_total_harvested(self):
        for cycle in self:
            cycle.total_harvested = sum(harvest.quantity for harvest in cycle.harvest_ids)

    @api.depends('cost_ids.amount')
    def _compute_total_cost(self):
        for cycle in self:
            cycle.total_cost = sum(cost.amount for cost in cycle.cost_ids)

    @api.depends('initial_stock', 'harvest_ids.quantity')
    def _compute_mortality_rate(self):
        for cycle in self:
            if cycle.initial_stock > 0:
                total_harvested = sum(harvest.quantity for harvest in cycle.harvest_ids)
                cycle.mortality_rate = ((cycle.initial_stock - total_harvested) / cycle.initial_stock) * 100
            else:
                cycle.mortality_rate = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('fish.breeding.cycle') or 'New'
        return super().create(vals_list)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for cycle in self:
            if cycle.start_date and cycle.end_date and cycle.end_date < cycle.start_date:
                raise ValidationError(_("End date cannot be before start date!"))