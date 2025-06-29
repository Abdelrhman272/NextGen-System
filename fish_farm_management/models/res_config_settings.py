# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
    System Settings for Fish Farm Management.

    - الحقول المرتبطة (related) تُخزَّن على مستوى الشركة، لذلك نُعرِّف
      default_model='res.company' لتُحدِّث حقولَ company.
    - الحقول التي تُخزَّن كنظاميّة عامّة نستخدم لها config_parameter.
    """
    _inherit = "res.config.settings"

    # ────────────────────────────────────────────────────────────────────
    # Company-level defaults  (stored on res.company)
    # ────────────────────────────────────────────────────────────────────
    default_feed_product_id = fields.Many2one(
        "product.product",
        string="Default Feed Product",
        related="company_id.default_feed_product_id",
        readonly=False,
        default_model="res.company",
    )

    default_medicine_product_id = fields.Many2one(
        "product.product",
        string="Default Medicine Product",
        related="company_id.default_medicine_product_id",
        readonly=False,
        default_model="res.company",
    )

    default_income_account_id = fields.Many2one(
        "account.account",
        string="Default Income Account",
        related="company_id.default_income_account_id",
        readonly=False,
        default_model="res.company",
    )

    default_expense_account_id = fields.Many2one(
        "account.account",
        string="Default Expense Account",
        related="company_id.default_expense_account_id",
        readonly=False,
        default_model="res.company",
    )

    # ────────────────────────────────────────────────────────────────────
    # Global parameters (stored in ir.config_parameter)
    # ────────────────────────────────────────────────────────────────────
    fish_farm_analytic_account_prefix = fields.Char(
        string="Analytic Account Prefix",
        config_parameter="fish_farm_management.analytic_account_prefix",
    )

    harvest_committee_size = fields.Integer(
        string="Harvest Committee Size",
        config_parameter="fish_farm_management.harvest_committee_size",
    )

    labor_cost_per_hour = fields.Float(
        string="Labor Cost per Hour",
        config_parameter="fish_farm_management.labor_cost_per_hour",
    )

    electricity_cost_per_kwh = fields.Float(
        string="Electricity Cost per kWh",
        config_parameter="fish_farm_management.electricity_cost_per_kwh",
    )

    enable_api_integration = fields.Boolean(
        string="Enable API Integration",
        config_parameter="fish_farm_management.enable_api_integration",
    )

    api_key = fields.Char(
        string="API Key",
        config_parameter="fish_farm_management.api_key",
    )
