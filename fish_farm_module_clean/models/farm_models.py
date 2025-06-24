
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FishFarmSector(models.Model):
    _name = "fish.farm.sector"
    _description = "Fish Farm Sector"

    name = fields.Char(required=True)
    description = fields.Text()

class FishFarmPond(models.Model):
    _name = "fish.farm.pond"
    _description = "Fish Farm Pond"

    name = fields.Char(required=True)
    sector_id = fields.Many2one("fish.farm.sector", string="Sector", required=True)
    area = fields.Float()
    water_type = fields.Selection([('fresh', 'Fresh Water'), ('salt', 'Salt Water')])

class FishFarmSeed(models.Model):
    _name = "fish.farm.seed"
    _description = "Fish Farm Seed"

    date = fields.Date(required=True, default=fields.Date.today)
    pond_id = fields.Many2one("fish.farm.pond", string="Pond", required=True)
    sector_id = fields.Many2one(related="pond_id.sector_id", store=True)
    fish_type = fields.Char()
    quantity = fields.Float()
    supplier = fields.Char()

class FishFarmFeeding(models.Model):
    _name = "fish.farm.feeding"
    _description = "Fish Farm Feeding"

    date = fields.Date(required=True, default=fields.Date.today)
    pond_id = fields.Many2one("fish.farm.pond", string="Pond", required=True)
    sector_id = fields.Many2one(related="pond_id.sector_id", store=True)
    feed_type = fields.Char()
    quantity = fields.Float()
    unit = fields.Selection([('kg', 'Kg'), ('g', 'Gram')])

    @api.constrains('quantity')
    def _check_quantity_warning(self):
        for record in self:
            limit = self.env['ir.config_parameter'].sudo().get_param('fish_farm.feeding_limit')
            if limit and record.quantity > float(limit):
                raise UserError(_("Feeding quantity exceeds the configured threshold."))

class FishFarmFishing(models.Model):
    _name = "fish.farm.fishing"
    _description = "Fish Farm Fishing"

    date = fields.Date(required=True, default=fields.Date.today)
    pond_id = fields.Many2one("fish.farm.pond", string="Pond", required=True)
    sector_id = fields.Many2one(related="pond_id.sector_id", store=True)
    quantity = fields.Float()
    method = fields.Char()

class FishFarmSupplying(models.Model):
    _name = "fish.farm.supplying"
    _description = "Fish Farm Supplying"

    date = fields.Date(required=True, default=fields.Date.today)
    pond_id = fields.Many2one("fish.farm.pond", string="Pond", required=True)
    sector_id = fields.Many2one(related="pond_id.sector_id", store=True)
    supplier = fields.Char()
    product = fields.Char()
    quantity = fields.Float()



class FishFarmZone(models.Model):
    _name = 'fish.farm.zone'
    _description = 'Fish Farm Zone'

    name = fields.Char(string='Zone Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
