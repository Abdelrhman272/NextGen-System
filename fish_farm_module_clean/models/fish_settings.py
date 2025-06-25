from odoo import models, fields

class FishFarmSettings(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    max_feed_per_day = fields.Float(string="Max Feed Per Day (kg)")
