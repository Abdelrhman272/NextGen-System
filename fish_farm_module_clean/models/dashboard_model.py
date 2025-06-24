
from odoo import models, fields, api
from datetime import datetime

class FishFarmDashboard(models.TransientModel):
    _name = 'fish.farm.dashboard'
    _description = 'Fish Farm Dashboard'

    pond_count = fields.Integer(string='Number of Ponds', compute='_compute_dashboard_data')
    total_seed_kg = fields.Float(string='Total Seed Quantity (KG)', compute='_compute_dashboard_data')
    total_feed = fields.Float(string='Total Feed Quantity (KG)', compute='_compute_dashboard_data')
    total_fish_caught = fields.Float(string='Total Fish Caught (KG)', compute='_compute_dashboard_data')
    total_supplied = fields.Float(string='Total Supplied Quantity (KG)', compute='_compute_dashboard_data')
    last_update = fields.Datetime(string='Last Updated', compute='_compute_dashboard_data')

    @api.depends()
    def _compute_dashboard_data(self):
        Pond = self.env['fish.farm.pond']
        Seed = self.env['fish.farm.seed']
        Feed = self.env['fish.farm.feeding']
        Fish = self.env['fish.farm.fishing']
        Supplying = self.env['fish.farm.supplying']

        for rec in self:
            rec.pond_count = Pond.search_count([])
            rec.total_seed_kg = sum(Seed.search([]).mapped('quantity_kg'))
            rec.total_feed = sum(Feed.search([]).mapped('quantity_kg'))
            rec.total_fish_caught = sum(Fish.search([]).mapped('quantity_kg'))
            rec.total_supplied = sum(Supplying.search([]).mapped('quantity_kg'))
            rec.last_update = datetime.now()
