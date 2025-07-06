# -*- coding: utf-8 -*-
from odoo import models, fields, _

class HarvestSortingLine(models.Model):
    _name = 'fish_farm_management.harvest_sorting_line'
    _description = 'تفاصيل فرز الحصاد'

    sorting_id = fields.Many2one(
        'fish_farm_management.harvest_sorting',
        string='سجل الفرز',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='المنتج',
        required=True
    )
    sorted_weight = fields.Float(
        string='الوزن المفرز (كجم)',
        required=True
    )
    destination_location_id = fields.Many2one(
        'stock.location',
        string='موقع الوجهة',
        required=True
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='وحدة القياس',
        related='product_id.uom_id',
        readonly=True,
        store=True,
    )
    notes = fields.Text(
        string='ملاحظات'
    )
