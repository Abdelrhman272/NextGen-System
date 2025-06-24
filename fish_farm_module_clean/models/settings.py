from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_pond_capacity_kg = fields.Float(string='Default Pond Capacity (KG)', default=1000)
    feeding_alert_enabled = fields.Boolean(string='Enable Feeding Notifications', default=True)