# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FishGrowthModel(models.Model):
    _name = 'fish_farm_management.fish_growth_model'
    _description = 'نموذج نمو الأسماك'

    name = fields.Char(string='اسم النموذج', required=True, translate=True, help='اسم فريد لنموذج النمو (مثل: بلطي - سريع النمو، بلطي - نمو قياسي).')
    fish_type_id = fields.Many2one('product.product', string='نوع السمك', required=True,
                                   domain="[('is_fish_type', '=', True)]",
                                   help='نوع السمك الذي ينطبق عليه هذا النموذج.')
    start_weight_g = fields.Float(string='الوزن الأولي (جرام)', required=True, help='متوسط وزن الزريعة عند البدء بالنمو (جرام).')
    target_weight_g = fields.Float(string='الوزن المستهدف (جرام)', required=True, help='الوزن المستهدف للسمكة الواحدة عند الحصاد (جرام).')
    target_days = fields.Integer(string='المدة المستهدفة (يوم)', required=True, help='عدد الأيام المتوقع للوصول إلى الوزن المستهدف.')
    
    growth_factors_ids = fields.One2many('fish_farm_management.growth_factor_line', 'growth_model_id', string='مراحل/عوامل النمو',
                                         help='يحدد هذا الجدول معدل النمو المتوقع على مراحل مختلفة أو تحت ظروف معينة (مثل درجة الحرارة).')
    
    notes = fields.Text(string='ملاحظات')
    company_id = fields.Many2one('res.company', string='الشركة', required=True, default=lambda self: self.env.company)

    _sql_constraints = [
        ('fish_type_model_unique', 'unique(fish_type_id, name, company_id)', 'يجب أن يكون لكل نوع سمك نموذج نمو فريد في كل شركة!'),
    ]

    @api.constrains('start_weight_g', 'target_weight_g', 'target_days')
    def _check_growth_parameters(self):
        for rec in self:
            if rec.start_weight_g <= 0 or rec.target_weight_g <= 0 or rec.target_days <= 0:
                raise ValidationError(_("يجب أن تكون الأوزان والأيام في نموذج النمو أكبر من صفر."))
            if rec.target_weight_g < rec.start_weight_g:
                raise ValidationError(_("الوزن المستهدف يجب أن يكون أكبر من الوزن الأولي."))

    # دالة لحساب الوزن المتوقع بناءً على الأيام المنقضية
    def get_estimated_weight_g(self, days_since_stocking):
        self.ensure_one()
        if days_since_stocking <= 0:
            return self.start_weight_g
        
        # مثال بسيط: نمو خطي. يمكن تعقيد هذا المنطق باستخدام growth_factors_ids
        if self.target_days > 0:
            growth_per_day = (self.target_weight_g - self.start_weight_g) / self.target_days
            estimated_weight = self.start_weight_g + (growth_per_day * days_since_stocking)
            return min(estimated_weight, self.target_weight_g * 1.2) # لا يتجاوز الوزن المستهدف بكثير
        return self.start_weight_g

class GrowthFactorLine(models.Model):
    _name = 'fish_farm_management.growth_factor_line'
    _description = 'عامل/مرحلة نمو'

    growth_model_id = fields.Many2one('fish_farm_management.fish_growth_model', string='نموذج النمو', required=True, ondelete='cascade')
    min_days = fields.Integer(string='من اليوم', required=True, default=0)
    max_days = fields.Integer(string='إلى اليوم', required=True)
    daily_growth_rate_g = fields.Float(string='معدل النمو اليومي (جرام/يوم)', help='متوسط النمو المتوقع يومياً في هذه المرحلة (جرام).')
    
    # يمكن إضافة عوامل تأثير إضافية مثل:
    # water_temperature_range = fields.Char(string='نطاق درجة حرارة المياه المثلى')
    # feed_type_id = fields.Many2one('product.product', string='نوع العلف الموصى به', domain="[('is_feed_type', '=', True)]")

    @api.constrains('min_days', 'max_days')
    def _check_days_range(self):
        for rec in self:
            if rec.min_days < 0 or rec.max_days < rec.min_days:
                raise ValidationError(_("نطاق الأيام غير صالح في عوامل النمو."))
            # يجب أن يكون هناك فحص لعدم تداخل الفترات الزمنية لنفس نموذج النمو