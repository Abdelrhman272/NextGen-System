from odoo import models, fields

class FishFarmSector(models.Model):
    _name = 'fish.farm.sector'
    _description = 'Fish Farm Sector'

    name = fields.Char(required=True)
    code = fields.Char()
    notes = fields.Text()


class FishFarmZone(models.Model):
    _name = 'fish.farm.zone'
    _description = 'Fish Farm Zone'

    name = fields.Char(required=True)
    code = fields.Char()
    sector_id = fields.Many2one('fish.farm.sector')
    notes = fields.Text()


class FishFarmPond(models.Model):
    _name = 'fish.farm.pond'
    _description = 'Fish Farm Pond'

    name = fields.Char(required=True)
    zone_id = fields.Many2one('fish.farm.zone')
    area = fields.Float()
    notes = fields.Text()


class FishFarmSeed(models.Model):
    _name = 'fish.farm.seed'
    _description = 'Fish Farm Seed'

    name = fields.Char(required=True)
    pond_id = fields.Many2one('fish.farm.pond')
    fish_type = fields.Char()
    quantity = fields.Float()
    date_added = fields.Date()


class FishFarmFeeding(models.Model):
    _name = 'fish.farm.feeding'
    _description = 'Fish Farm Feeding'

    name = fields.Char(string='Feeding Reference', required=True)
    date = fields.Date(string='Feeding Date', required=True)
    pond_id = fields.Many2one('fish.farm.pond', string='Pond', required=True)
    feed_type = fields.Char(string='Feed Type')
    quantity_kg = fields.Float(string='Quantity (KG)')
    notes = fields.Text(string='Notes')

class FishFarmFishing(models.Model):
    _name = 'fish.farm.fishing'
    _description = 'Fish Farm Fishing'

    name = fields.Char(string='Fishing Reference', required=True)
    date = fields.Date(string='Fishing Date', required=True)
    pond_id = fields.Many2one('fish.farm.pond', string='Pond', required=True)
    quantity_kg = fields.Float(string='Quantity (KG)', required=True)
    notes = fields.Text(string='Notes')


class FishFarmSupplying(models.Model):
    _name = 'fish.farm.supplying'
    _description = 'Fish Farm Supplying'

    name = fields.Char(string='Supplying Reference', required=True)
    date = fields.Date(string='Supplying Date', required=True)
    pond_id = fields.Many2one('fish.farm.pond', string='Pond', required=True)
    quantity_kg = fields.Float(string='Quantity (KG)', required=True)
    customer_name = fields.Char(string='Customer Name')
    notes = fields.Text(string='Notes')
    