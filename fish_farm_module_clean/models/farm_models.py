
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FishFarmSector(models.Model):
    _name = "fish.farm.sector"
    _description = "Fish Farm Sector"

    name = fields.Char(required=True)
    code = fields.Char()
    notes = fields.Text()
    description = fields.Text()

class FishFarmPond(models.Model):
    _name = "fish.farm.pond"
    _description = "Fish Farm Pond"

    name = fields.Char(required=True)
    zone_id = fields.Many2one("fish.farm.zone", string="Zone", required=True)
    sector_id = fields.Many2one(related="zone_id.sector_id", store=True)
    area = fields.Float()
    water_type = fields.Selection([('fresh', 'Fresh Water'), ('salt', 'Salt Water')])
    notes = fields.Text()

    seeding_total_qty = fields.Float(compute="_compute_statistics", store=True)
    feeding_count = fields.Integer(compute="_compute_statistics", store=True)
    fishing_total_kg = fields.Float(compute="_compute_statistics", store=True)
    supplying_total_kg = fields.Float(compute="_compute_statistics", store=True)
    remaining_estimate_kg = fields.Float(compute="_compute_statistics", store=True)

    @api.depends('seed_ids.quantity', 'feeding_ids', 'fishing_ids.quantity_kg', 'supplying_ids.quantity_kg')
    def _compute_statistics(self):
        for pond in self:
            seed_qty = sum(pond.seed_ids.mapped('quantity'))
            feeding_count = len(pond.feeding_ids)
            fishing_total = sum(pond.fishing_ids.mapped('quantity_kg'))
            supplying_total = sum(pond.supplying_ids.mapped('quantity_kg'))
            pond.seeding_total_qty = seed_qty
            pond.feeding_count = feeding_count
            pond.fishing_total_kg = fishing_total
            pond.supplying_total_kg = supplying_total
            pond.remaining_estimate_kg = seed_qty - fishing_total - supplying_total

    seed_ids = fields.One2many('fish.farm.seed', 'pond_id', string='Seeds')
    feeding_ids = fields.One2many('fish.farm.feeding', 'pond_id', string='Feedings')
    fishing_ids = fields.One2many('fish.farm.fishing', 'pond_id', string='Fishing')
    supplying_ids = fields.One2many('fish.farm.supplying', 'pond_id', string='Supplying')

class FishFarmSeed(models.Model):
    _name = "fish.farm.seed"
    _description = "Fish Farm Seed"

    name = fields.Char()
    date_added = fields.Date(required=True, default=fields.Date.today)
    pond_id = fields.Many2one("fish.farm.pond", string="Pond", required=True)
    zone_id = fields.Many2one(related="pond_id.zone_id", store=True)
    sector_id = fields.Many2one(related="pond_id.sector_id", store=True)
    fish_type = fields.Char()
    quantity = fields.Float()
    supplier = fields.Char()

class FishFarmFeeding(models.Model):
    _name = "fish.farm.feeding"
    _description = "Fish Farm Feeding"

    name = fields.Char()
    date = fields.Date(required=True, default=fields.Date.today)
    pond_id = fields.Many2one("fish.farm.pond", string="Pond", required=True)
    zone_id = fields.Many2one(related="pond_id.zone_id", store=True)
    sector_id = fields.Many2one(related="pond_id.sector_id", store=True)
    feed_type = fields.Char()
    quantity_kg = fields.Float()
    notes = fields.Text()

    @api.constrains('quantity_kg')
    def _check_quantity_warning(self):
        for record in self:
            limit = self.env['ir.config_parameter'].sudo().get_param('fish_farm.feeding_limit')
            if limit and record.quantity_kg > float(limit):
                raise UserError(_("Feeding quantity exceeds the configured threshold."))

class FishFarmFishing(models.Model):
    _name = "fish.farm.fishing"
    _description = "Fish Farm Fishing"

    name = fields.Char()
    date = fields.Date(required=True, default=fields.Date.today)
    pond_id = fields.Many2one("fish.farm.pond", string="Pond", required=True)
    zone_id = fields.Many2one(related="pond_id.zone_id", store=True)
    sector_id = fields.Many2one(related="pond_id.sector_id", store=True)
    quantity_kg = fields.Float()
    method = fields.Char()
    notes = fields.Text()

class FishFarmSupplying(models.Model):
    _name = "fish.farm.supplying"
    _description = "Fish Farm Supplying"

    name = fields.Char()
    date = fields.Date(required=True, default=fields.Date.today)
    pond_id = fields.Many2one("fish.farm.pond", string="Pond", required=True)
    zone_id = fields.Many2one(related="pond_id.zone_id", store=True)
    sector_id = fields.Many2one(related="pond_id.sector_id", store=True)
    customer_name = fields.Char()
    product = fields.Char()
    quantity_kg = fields.Float()
    notes = fields.Text()



class FishFarmZone(models.Model):
    _name = 'fish.farm.zone'
    _description = 'Fish Farm Zone'

    name = fields.Char(string='Zone Name', required=True)
    code = fields.Char()
    sector_id = fields.Many2one('fish.farm.sector', string='Sector', required=True)
    description = fields.Text(string='Description')
    notes = fields.Text()
    active = fields.Boolean(default=True)
