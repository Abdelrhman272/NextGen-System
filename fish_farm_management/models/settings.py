from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

PARAM_PREFIX = "fish_farm_management."

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # -------- General --------
    default_feed_product_id = fields.Many2one(
        "product.product", string="Default Feed Product",
        config_parameter=PARAM_PREFIX + "default_feed_product_id")

    default_medicine_product_id = fields.Many2one(
        "product.product", string="Default Medicine Product",
        config_parameter=PARAM_PREFIX + "default_medicine_product_id")

    harvest_committee_size = fields.Integer(
        string="Harvest Committee Size",
        config_parameter=PARAM_PREFIX + "harvest_committee_size",
        default=3)

    fish_farm_analytic_account_prefix = fields.Char(
        string="Analytic Account Prefix",
        config_parameter=PARAM_PREFIX + "analytic_account_prefix",
        default="POND")

    # -------- Accounting --------
    default_income_account_id = fields.Many2one(
        "account.account", string="Default Income Account",
        domain=[("internal_type", "=", "income")],
        config_parameter=PARAM_PREFIX + "default_income_account_id")

    default_expense_account_id = fields.Many2one(
        "account.account", string="Default Expense Account",
        domain=[("internal_type", "=", "expense")],
        config_parameter=PARAM_PREFIX + "default_expense_account_id")

    # -------- Cost parameters --------
    labor_cost_per_hour = fields.Float(
        string="Labor Cost per Hour",
        config_parameter=PARAM_PREFIX + "labor_cost_per_hour",
        default=25.0)

    electricity_cost_per_kwh = fields.Float(
        string="Electricity Cost per kWh",
        config_parameter=PARAM_PREFIX + "electricity_cost_per_kwh",
        default=1.5)

    # -------- Integration --------
    enable_api_integration = fields.Boolean(
        string="Enable API Integration",
        config_parameter=PARAM_PREFIX + "enable_api_integration")

    api_key = fields.Char(
        string="API Key", config_parameter=PARAM_PREFIX + "api_key")

    # Optional: small safety check
    @api.constrains("harvest_committee_size")
    def _check_committee_size(self):
        for rec in self:
            if rec.harvest_committee_size <= 0:
                raise ValidationError(_("Committee size must be positive."))
