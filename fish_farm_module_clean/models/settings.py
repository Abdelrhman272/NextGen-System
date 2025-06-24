from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_pond_capacity_kg = fields.Float(string='Default Pond Capacity (KG)', default=1000)
    feeding_alert_enabled = fields.Boolean(string='Enable Feeding Notifications', default=True)

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    feeding_limit = fields.Float(string="Feeding Limit (KG)", config_parameter='fish_farm_module_clean.feeding_limit', default=100.0)
    fishing_limit = fields.Float(string="Fishing Limit (KG)", config_parameter='fish_farm_module_clean.fishing_limit', default=200.0)
