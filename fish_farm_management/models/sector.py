# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Sector(models.Model):
    _name = 'fish_farm_management.sector'
    _description = 'قطاع المزرعة'

    name = fields.Char(string='اسم القطاع', required=True, translate=True)
    fish_farm_id = fields.Many2one('fish_farm_management.fish_farm', string='المزرعة السمكية', required=True, ondelete='restrict')
    slice_ids = fields.One2many('fish_farm_management.slice', 'sector_id', string='الشرائح')
    company_id = fields.Many2one('res.company', string='الشركة', related='fish_farm_id.company_id', store=True, readonly=True)

    _sql_constraints = [
        ('name_farm_unique', 'unique(name, fish_farm_id)', 'يجب أن يكون اسم القطاع فريداً لكل مزرعة!'),
    ]