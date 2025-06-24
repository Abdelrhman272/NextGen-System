from odoo import models, fields

class FishFarmSector(models.Model):
    _name = 'fish.farm.sector'
    _description = 'Fish Farm Sector'

    name = fields.Char(required=True)
    code = fields.Char()
    notes = fields.Text()


class FishFarmZone(models.Model):
    sector_id = fields.Many2one(related='sector_id', store=True, readonly=True)

    _name = 'fish.farm.zone'
    _description = 'Fish Farm Zone'

    name = fields.Char(required=True)
    code = fields.Char()
    sector_id = fields.Many2one('fish.farm.sector')
    notes = fields.Text()


class FishFarmPond(models.Model):

    def action_view_feedings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Feedings',
            'res_model': 'fish.farm.feeding',
            'view_mode': 'tree,form',
            'domain': [('pond_id', '=', self.id)],
            'context': {'default_pond_id': self.id},
        }

    def action_view_fishings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fishings',
            'res_model': 'fish.farm.fishing',
            'view_mode': 'tree,form',
            'domain': [('pond_id', '=', self.id)],
            'context': {'default_pond_id': self.id},
        }

    def action_view_supplies(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Supplying',
            'res_model': 'fish.farm.supplying',
            'view_mode': 'tree,form',
            'domain': [('pond_id', '=', self.id)],
            'context': {'default_pond_id': self.id},
        }

    sector_id = fields.Many2one(related='zone_id.sector_id', store=True, readonly=True)
    zone_id = fields.Many2one('fish.farm.zone')

    _name = 'fish.farm.pond'
    _description = 'Fish Farm Pond'

    name = fields.Char(required=True)
    zone_id = fields.Many2one('fish.farm.zone')
    area = fields.Float()
    notes = fields.Text()


class FishFarmSeed(models.Model):
    sector_id = fields.Many2one(related='pond_id.zone_id.sector_id', store=True, readonly=True)
    zone_id = fields.Many2one(related='pond_id.zone_id', store=True, readonly=True)

    _name = 'fish.farm.seed'
    _description = 'Fish Farm Seed'

    name = fields.Char(required=True)
    pond_id = fields.Many2one('fish.farm.pond')
    fish_type = fields.Char()
    quantity = fields.Float()
    date_added = fields.Date()


class FishFarmFeeding(models.Model):
    sector_id = fields.Many2one(related='pond_id.zone_id.sector_id', store=True, readonly=True)
    zone_id = fields.Many2one(related='pond_id.zone_id', store=True, readonly=True)

    _name = 'fish.farm.feeding'

    def action_export_feeding_pdf(self):
        return self.env.ref('fish_farm_module_clean.report_feeding_pdf_action').report_action(self)

    def action_export_feeding_excel(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/fish_farm/feeding/excel',
            'target': 'self',
        }
    _description = 'Fish Farm Feeding'

    name = fields.Char(string='Feeding Reference', required=True)
    date = fields.Date(string='Feeding Date', required=True)
    pond_id = fields.Many2one('fish.farm.pond', string='Pond', required=True)
    feed_type = fields.Char(string='Feed Type')
    quantity_kg = fields.Float(string='Quantity (KG)')
    notes = fields.Text(string='Notes')

class FishFarmFishing(models.Model):
    sector_id = fields.Many2one(related='pond_id.zone_id.sector_id', store=True, readonly=True)
    zone_id = fields.Many2one(related='pond_id.zone_id', store=True, readonly=True)

    _name = 'fish.farm.fishing'
    _description = 'Fish Farm Fishing'

    name = fields.Char(string='Fishing Reference', required=True)
    date = fields.Date(string='Fishing Date', required=True)
    pond_id = fields.Many2one('fish.farm.pond', string='Pond', required=True)
    quantity_kg = fields.Float(string='Quantity (KG)', required=True)
    notes = fields.Text(string='Notes')


class FishFarmSupplying(models.Model):
    sector_id = fields.Many2one(related='pond_id.zone_id.sector_id', store=True, readonly=True)
    zone_id = fields.Many2one(related='pond_id.zone_id', store=True, readonly=True)

    _name = 'fish.farm.supplying'
    _description = 'Fish Farm Supplying'

    name = fields.Char(string='Supplying Reference', required=True)
    date = fields.Date(string='Supplying Date', required=True)
    pond_id = fields.Many2one('fish.farm.pond', string='Pond', required=True)
    quantity_kg = fields.Float(string='Quantity (KG)', required=True)
    customer_name = fields.Char(string='Customer Name')
    notes = fields.Text(string='Notes')
    

from odoo import api

class FishFarmPond(models.Model):

    def action_view_feedings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Feedings',
            'res_model': 'fish.farm.feeding',
            'view_mode': 'tree,form',
            'domain': [('pond_id', '=', self.id)],
            'context': {'default_pond_id': self.id},
        }

    def action_view_fishings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fishings',
            'res_model': 'fish.farm.fishing',
            'view_mode': 'tree,form',
            'domain': [('pond_id', '=', self.id)],
            'context': {'default_pond_id': self.id},
        }

    def action_view_supplies(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Supplying',
            'res_model': 'fish.farm.supplying',
            'view_mode': 'tree,form',
            'domain': [('pond_id', '=', self.id)],
            'context': {'default_pond_id': self.id},
        }

    _inherit = 'fish.farm.pond'

    feeding_count = fields.Integer(string='Feeding Count', compute='_compute_feeding_count', store=True)
    fishing_total_kg = fields.Float(string='Total Fish Caught (KG)', compute='_compute_fishing_total', store=True)
    seeding_total_qty = fields.Float(string='Total Fish Seeded', compute='_compute_seeding_total', store=True)
    supplying_total_kg = fields.Float(string='Total Fish Supplied (KG)', compute='_compute_supplying_total', store=True)
    remaining_estimate_kg = fields.Float(string='Estimated Remaining Fish (KG)', compute='_compute_remaining_estimate', store=True)

    @api.depends('feeding_count')
    def _compute_feeding_count(self):
        for record in self:
            record.feeding_count = self.env['fish.farm.feeding'].search_count([('pond_id', '=', record.id)])

    @api.depends('fishing_total_kg')
    def _compute_fishing_total(self):
        for record in self:
            record.fishing_total_kg = sum(
                self.env['fish.farm.fishing'].search([('pond_id', '=', record.id)]).mapped('quantity_kg')
            )

    @api.depends('seeding_total_qty')
    def _compute_seeding_total(self):
        for record in self:
            record.seeding_total_qty = sum(
                self.env['fish.farm.seed'].search([('pond_id', '=', record.id)]).mapped('quantity')
            )

    @api.depends('supplying_total_kg')
    def _compute_supplying_total(self):
        for record in self:
            record.supplying_total_kg = sum(
                self.env['fish.farm.supplying'].search([('pond_id', '=', record.id)]).mapped('quantity_kg')
            )

    @api.depends('seeding_total_qty', 'fishing_total_kg', 'supplying_total_kg')
    def _compute_remaining_estimate(self):
        for record in self:
            record.remaining_estimate_kg = (
                record.seeding_total_qty - (record.fishing_total_kg + record.supplying_total_kg)
            )

from odoo import models, fields, api

class FishFarmPond(models.Model):
    _name = 'fish.farm.pond'
    _description = 'Fish Farm Pond'

    name = fields.Char(required=True)
    zone_id = fields.Many2one('fish.farm.zone')
    area = fields.Float()
    notes = fields.Text()
    sector_id = fields.Many2one(related='zone_id.sector_id', store=True, readonly=True)

    feeding_count = fields.Integer(string='Feeding Count', compute='_compute_feeding_count', store=True)
    fishing_total_kg = fields.Float(string='Total Fish Caught (KG)', compute='_compute_fishing_total', store=True)
    seeding_total_qty = fields.Float(string='Total Fish Seeded', compute='_compute_seeding_total', store=True)
    supplying_total_kg = fields.Float(string='Total Fish Supplied (KG)', compute='_compute_supplying_total', store=True)
    remaining_estimate_kg = fields.Float(string='Estimated Remaining Fish (KG)', compute='_compute_remaining_estimate', store=True)

    def action_view_feedings(self):
        if self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Feedings',
                'res_model': 'fish.farm.feeding',
                'view_mode': 'tree,form',
                'domain': [('pond_id', '=', self.id)],
                'context': {'default_pond_id': self.id},
            }

    def action_view_fishings(self):
        if self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Fishings',
                'res_model': 'fish.farm.fishing',
                'view_mode': 'tree,form',
                'domain': [('pond_id', '=', self.id)],
                'context': {'default_pond_id': self.id},
            }

    def action_view_supplies(self):
        if self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Supplying',
                'res_model': 'fish.farm.supplying',
                'view_mode': 'tree,form',
                'domain': [('pond_id', '=', self.id)],
                'context': {'default_pond_id': self.id},
            }

    @api.depends('feeding_count')
    def _compute_feeding_count(self):
        for record in self:
            record.feeding_count = self.env['fish.farm.feeding'].search_count([('pond_id', '=', record.id)])

    @api.depends('fishing_total_kg')
    def _compute_fishing_total(self):
        for record in self:
            record.fishing_total_kg = sum(
                self.env['fish.farm.fishing'].search([('pond_id', '=', record.id)]).mapped('quantity_kg')
            )

    @api.depends('seeding_total_qty')
    def _compute_seeding_total(self):
        for record in self:
            record.seeding_total_qty = sum(
                self.env['fish.farm.seed'].search([('pond_id', '=', record.id)]).mapped('quantity')
            )

    @api.depends('supplying_total_kg')
    def _compute_supplying_total(self):
        for record in self:
            record.supplying_total_kg = sum(
                self.env['fish.farm.supplying'].search([('pond_id', '=', record.id)]).mapped('quantity_kg')
            )

    @api.depends('seeding_total_qty', 'fishing_total_kg', 'supplying_total_kg')
    def _compute_remaining_estimate(self):
        for record in self:
            record.remaining_estimate_kg = (
                record.seeding_total_qty - (record.fishing_total_kg + record.supplying_total_kg)
            )