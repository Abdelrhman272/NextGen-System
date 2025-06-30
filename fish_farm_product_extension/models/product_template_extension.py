# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductTemplateExtension(models.Model):
    _inherit = 'product.template' # Inherit from product.template (the base for product.product)
    _description = 'Product Template Extension for Fish Farm'

    is_fish_type = fields.Boolean(string='Is Fish Type?',
                                  help='Check if this product represents a type of fish or fingerling.')
    is_feed_type = fields.Boolean(string='Is Feed Type?',
                                  help='Check if this product represents a type of fish feed.')
    is_medicine_type = fields.Boolean(string='Is Medicine Type?',
                                      help='Check if this product represents a fish medicine or treatment.')
    is_harvested_product = fields.Boolean(string='Is Harvested Product?',
                                          help='Check if this product represents a raw, unprocessed harvested fish product.')