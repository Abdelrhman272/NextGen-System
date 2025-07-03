# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AnalyticAccountExtension(models.Model):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account Extension for Fish Farm'

    # إضافة حقل Many2one لربط الحساب التحليلي بالحوض
    fish_farm_management_pond_id = fields.Many2one(
        'fish_farm_management.pond',
        string='حوض المزرعة السمكية',
        ondelete='set null',
        help='ربط هذا الحساب التحليلي بحوض معين في المزرعة السمكية.'
    )