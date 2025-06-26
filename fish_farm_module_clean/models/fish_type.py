from odoo import models, fields, api

class FishType(models.Model):
    _name = 'fish.type'
    _description = 'Fish Type'
    _order = 'name'
    _inherit = ['fish.multilingual.mixin']

    name = fields.Char('Fish Type', required=True, translate=True)
    code = fields.Char('Fish Code')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    growth_period = fields.Integer('Growth Period (Days)', 
                                  help="Average number of days for the fish to reach harvest size")
    feed_conversion_ratio = fields.Float('Feed Conversion Ratio', 
                                        help="Kg of feed per Kg of fish")
    average_weight = fields.Float('Average Weight at Harvest (kg)')
    description = fields.Text('Description', translate=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)