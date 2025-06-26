from odoo import models, fields, api
from datetime import timedelta

class BreedingCycle(models.Model):
    _name = 'fish.breeding.cycle'
    _description = 'Fish Breeding Cycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char('Cycle Reference', required=True, index=True, default='New')
    pond_id = fields.Many2one('fish.pond', 'Pond', required=True)
    fish_type_id = fields.Many2one('fish.type', 'Fish Type', required=True)
    start_date = fields.Date('Start Date', default=fields.Date.today)
    end_date = fields.Date('End Date')
    duration = fields.Integer('Duration (Days)', compute='_compute_duration', store=True)
    initial_stock = fields.Integer('Initial Stock')
    estimated_harvest_date = fields.Date('Estimated Harvest Date', compute='_compute_estimated_harvest_date')
    harvest_ids = fields.One2many('fish.harvest', 'cycle_id', 'Harvests')
    total_harvested = fields.Float('Total Harvested (kg)', compute='_compute_total_harvested')
    feed_consumption = fields.Float('Feed Consumption (kg)')
    mortality_rate = fields.Float('Mortality Rate (%)')
    cost_ids = fields.One2many('fish.cost.distribution', 'cycle_id', 'Costs')
    total_cost = fields.Float('Total Cost', compute='_compute_total_cost')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('preparing', 'Preparing'),
        ('stocked', 'Stocked'),
        ('growing', 'Growing'),
        ('harvesting', 'Harvesting'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], 'Status', default='draft', tracking=True)
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for cycle in self:
            if cycle.start_date and cycle.end_date:
                delta = cycle.end_date - cycle.start_date
                cycle.duration = delta.days
            else:
                cycle.duration = 0
    
    @api.depends('start_date', 'fish_type_id')
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
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fish.breeding.cycle') or 'New'
        return super(BreedingCycle, self).create(vals)