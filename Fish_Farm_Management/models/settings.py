from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fish_farm_analytic_account_prefix = fields.Char(
        string='Analytic Account Prefix',
        config_parameter='fish_farm_management.analytic_account_prefix',
        default='POND'
    )
    
    default_feed_product_id = fields.Many2one(
        'product.product', 
        string='Default Feed Product',
        default_model='fish_farm_management.fish_farm_settings'
    )
    
    default_medicine_product_id = fields.Many2one(
        'product.product', 
        string='Default Medicine Product',
        default_model='fish_farm_management.fish_farm_settings'
    )
    
    harvest_committee_size = fields.Integer(
        string='Harvest Committee Size',
        default=3,
        config_parameter='fish_farm_management.harvest_committee_size'
    )
    
    # Accounting settings
    default_income_account_id = fields.Many2one(
        'account.account', 
        string='Default Income Account',
        domain=[('internal_type', '=', 'income')]
    )
    
    default_expense_account_id = fields.Many2one(
        'account.account', 
        string='Default Expense Account',
        domain=[('internal_type', '=', 'expense')]
    )
    
    # Cost settings
    labor_cost_per_hour = fields.Float(
        string='Labor Cost per Hour',
        default=25.0,
        config_parameter='fish_farm_management.labor_cost_per_hour'
    )
    
    electricity_cost_per_kwh = fields.Float(
        string='Electricity Cost per KWh',
        default=1.5,
        config_parameter='fish_farm_management.electricity_cost_per_kwh'
    )
    
    # Integration settings
    enable_api_integration = fields.Boolean(
        string='Enable API Integration',
        config_parameter='fish_farm_management.enable_api_integration'
    )
    
    api_key = fields.Char(
        string='API Key',
        config_parameter='fish_farm_management.api_key'
    )
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # Save settings logic
        return True
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # Load settings logic
        return res