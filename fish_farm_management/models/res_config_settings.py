# -*- coding: utf-8 -*-

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Water Quality Thresholds
    min_ph = fields.Float(string='الحد الأدنى لـ pH المياه', config_parameter='fish_farm_management.min_ph', default=6.5)
    max_ph = fields.Float(string='الحد الأقصى لـ pH المياه', config_parameter='fish_farm_management.max_ph', default=8.5)
    min_oxygen = fields.Float(string='الحد الأدنى للأكسجين المذاب (ملجم/لتر)', config_parameter='fish_farm_management.min_oxygen', default=5.0)
    max_temperature = fields.Float(string='الحد الأقصى لدرجة الحرارة (مئوية)', config_parameter='fish_farm_management.max_temperature', default=30.0)
    min_temperature = fields.Float(string='الحد الأدنى لدرجة الحرارة (مئوية)', config_parameter='fish_farm_management.min_temperature', default=20.0)
    max_ammonia = fields.Float(string='الحد الأقصى للأمونيا (ملجم/لتر)', config_parameter='fish_farm_management.max_ammonia', default=0.05)
    max_nitrite = fields.Float(string='الحد الأقصى للنيتريت (ملجم/لتر)', config_parameter='fish_farm_management.max_nitrite', default=0.1)

    # Performance Thresholds (for dashboard/list view coloring)
    fcr_warning_threshold = fields.Float(string='حد تحذير FCR', config_parameter='fish_farm_management.fcr_warning_threshold', default=1.5, help='معدل التحويل الغذائي الذي يعتبر عنده تحذير (أقل من هذا الرقم أفضل).')
    survival_rate_warning_threshold = fields.Float(string='حد تحذير معدل البقاء على قيد الحياة (%)', config_parameter='fish_farm_management.survival_rate_warning_threshold', default=80.0, help='معدل البقاء على قيد الحياة الذي يعتبر عنده تحذير (أقل من هذا الرقم يعتبر سيئ).')
    
    # Sorting Tolerance
    sorting_tolerance = fields.Float(string='سماحية الفرز (كجم)', config_parameter='fish_farm_management.sorting_tolerance', default=0.05, help='الحد الأقصى للفرق المسموح به بين الوزن المدخل والوزن المفرز في عملية الفرز.')