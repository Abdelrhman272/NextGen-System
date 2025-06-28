# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # === Company-related fields ===
    # These settings are saved directly on the company record.
    # This is the best practice for default values.
    default_feed_product_id = fields.Many2one(
        related='company_id.default_feed_product_id',
        readonly=False
    )
    default_medicine_product_id = fields.Many2one(
        related='company_id.default_medicine_product_id',
        readonly=False
    )
    default_income_account_id = fields.Many2one(
        related='company_id.default_income_account_id',
        readonly=False
    )
    default_expense_account_id = fields.Many2one(
        related='company_id.default_expense_account_id',
        readonly=False
    )

    # === System Parameters (config_parameter) ===
    # These settings are saved system-wide and are not specific to one company.
    fish_farm_analytic_account_prefix = fields.Char(
        string='Analytic Account Prefix',
        config_parameter='fish_farm_management.analytic_account_prefix'
    )
    harvest_committee_size = fields.Integer(
        string='Harvest Committee Size',
        config_parameter='fish_farm_management.harvest_committee_size'
    )
    labor_cost_per_hour = fields.Float(
        string='Labor Cost per Hour',
        config_parameter='fish_farm_management.labor_cost_per_hour'
    )
    electricity_cost_per_kwh = fields.Float(
        string='Electricity Cost per kWh',
        config_parameter='fish_farm_management.electricity_cost_per_kwh'
    )
    enable_api_integration = fields.Boolean(
        string='Enable API Integration',
        config_parameter='fish_farm_management.enable_api_integration'
    )
    api_key = fields.Char(
        string='API Key',
        config_parameter='fish_farm_management.api_key'
    )
