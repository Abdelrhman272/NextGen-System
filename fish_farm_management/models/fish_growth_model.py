# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class FishGrowthModel(models.Model):
    _name = 'fish_farm_management.fish_growth_model'
    _description = 'نموذج نمو الأسماك'

    fish_type_id = fields.Many2one(
        'product.product', string='نوع السمك', required=True,
        domain=[('is_fish_type', '=', True)],
        help='اختيار نوع السمك من الأصول المعرفة في النظام.'
    )
    start_weight_g = fields.Float(
        string='الوزن الابتدائي (غرام)', required=True,
        help='الوزن الابتدائي المتوقع عند بداية التربية.'
    )
    target_weight_g = fields.Float(
        string='الوزن المستهدف (غرام)', required=True,
        help='الوزن المستهدف عند نهاية دورة التربية.'
    )
    target_days = fields.Integer(
        string='عدد الأيام المستهدفة', required=True,
        help='عدد الأيام المتوقعة للوصول من الوزن الابتدائي إلى الوزن المستهدف.'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """دعم الإنشاء على دفعات batch create."""
        records = super(FishGrowthModel, self).create(vals_list)
        # هنا يمكن إضافة أي منطق إضافي بعد الإنشاء على كل سجل في records
        return records

    def write(self, vals):
        """الكتابة بدون @api.multi (مدعومة بالافتراضي على recordsets)."""
        res = super(FishGrowthModel, self).write(vals)
        # منطق بعد التعديل إن لزم
        return res

# ——————————————————————————————————————————————————————————————
# إضافة العلاقة العكسية على product.product لحل الاعتمادية fish_growth_model_ids
class ProductProduct(models.Model):
    _inherit = 'product.product'

    fish_growth_model_ids = fields.One2many(
        'fish_farm_management.fish_growth_model',
        'fish_type_id',
        string='نماذج النمو',
        help='نماذج النمو المرتبطة بكل نوع سمك'
    )
    fish_growth_measurement_ids = fields.One2many(
        'fish_farm_management.fish_growth_measurement',
        'fish_type_id',
        string='قراءات النمو',
        help='قراءات النمو المسجلة لكل نوع سمك'
    )
