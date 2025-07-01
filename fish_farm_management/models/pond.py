# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Pond(models.Model):
    _name = 'fish_farm_management.pond'
    _description = 'حوض السمك'

    name = fields.Char(string='رقم الحوض', required=True)
    slice_id = fields.Many2one('fish_farm_management.slice', string='الشريحة', required=True, ondelete='restrict')
    sector_id = fields.Many2one('fish_farm_management.sector', string='القطاع', related='slice_id.sector_id', store=True, readonly=True)
    fish_farm_id = fields.Many2one('fish_farm_management.fish_farm', string='المزرعة السمكية', related='sector_id.fish_farm_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='الشركة', related='slice_id.company_id', store=True, readonly=True)

    status = fields.Selection([
        ('empty', 'فارغ'),
        ('preparing', 'تجهيز'),
        ('stocked', 'مخزن به زريعة'),
        ('harvesting', 'حصاد'),
        ('idle', 'خامل'),
    ], string='الحالة', default='empty', required=True, copy=False)
    volume = fields.Float(string='الحجم (متر مكعب)', help='إجمالي حجم المياه في الحوض.')
    last_cleaning_date = fields.Date(string='تاريخ آخر تنظيف')
    capacity_kg = fields.Float(string='السعة القصوى (كجم أسماك)', help='أقصى وزن للأسماك يمكن أن يحتويه الحوض.')
    active_date = fields.Date(string='تاريخ التفعيل', help='تاريخ بداية استخدام الحوض للزراعة.')
    decommission_date = fields.Date(string='تاريخ التعطيل', help='تاريخ توقف الحوض عن الاستخدام.')

    # العلاقات مع السجلات الأخرى
    fish_stocking_ids = fields.One2many('fish_farm_management.fish_stocking', 'pond_id', string='تاريخ إلقاء الزريعة')
    pond_feeding_ids = fields.One2many('fish_farm_management.pond_feeding', 'pond_id', string='سجلات التغذية والمستلزمات')
    pond_cost_ids = fields.One2many('fish_farm_management.pond_cost', 'pond_id', string='تكاليف الحوض')
    harvest_record_ids = fields.One2many('fish_farm_management.harvest_record', 'pond_id', string='سجلات الحصاد')
    fish_health_ids = fields.One2many('fish_farm_management.fish_health_record', 'pond_id', string='سجلات صحة الأسماك')
    water_quality_ids = fields.One2many('fish_farm_management.water_quality_reading', 'pond_id', string='قراءات جودة المياه')
    production_plan_ids = fields.One2many('fish_farm_management.production_plan', 'pond_id', string='خطط الإنتاج')
    growth_measurement_ids = fields.One2many('fish_farm_management.fish_growth_measurement', 'pond_id', string='قياسات النمو') # إضافة علاقة جديدة

    # حقول محسوبة للعرض في لوحة القيادة أو القائمة
    current_fish_type_ids = fields.Many2many('product.product', string='أنواع الأسماك الحالية', compute='_compute_current_fish_types', store=True)
    total_stocked_qty = fields.Float(string='إجمالي الكمية المزروعة (زريعة)', compute='_compute_pond_summary_data', store=True)
    current_fish_count = fields.Integer(string='العدد التقريبي للأسماك', compute='_compute_pond_summary_data', store=True, help="العدد التقريبي بناءً على الزريعة المزروعة والوفيات المسجلة.")
    estimated_current_biomass_kg = fields.Float(string='الكتلة الحيوية المقدرة (كجم)', compute='_compute_pond_summary_data', store=True, help="الكتلة الحيوية المقدرة بناءً على النمو والعدد.")
    last_water_quality_ph = fields.Float(string='آخر pH للمياه', compute='_compute_last_water_quality', store=False)
    last_water_quality_oxygen = fields.Float(string='آخر أكسجين للمياه', compute='_compute_last_water_quality', store=False)

    @api.depends('fish_stocking_ids.fish_type_id', 'fish_stocking_ids.stocking_date', 'fish_stocking_ids.harvest_record_id')
    def _compute_current_fish_types(self):
        for pond in self:
            current_types = pond.fish_stocking_ids.filtered(lambda s: s.stocking_date and not s.harvest_record_id).mapped('fish_type_id')
            pond.current_fish_type_ids = [(6, 0, current_types.ids)]

    @api.depends('fish_stocking_ids.quantity', 'fish_health_ids.mortality_count', 'growth_measurement_ids.measurement_date', 'growth_measurement_ids.average_fish_weight_g')
    def _compute_pond_summary_data(self):
        from odoo.tools import date_utils
        for pond in self:
            total_stocked = sum(stock.quantity for stock in pond.fish_stocking_ids)
            total_mortality = sum(health.mortality_count for health in pond.fish_health_ids)
            
            pond.total_stocked_qty = total_stocked
            pond.current_fish_count = total_stocked - total_mortality if (total_stocked - total_mortality) > 0 else 0
            
            estimated_biomass = 0.0
            if pond.current_fish_count > 0 and pond.fish_stocking_ids:
                # حاول استخدام نموذج النمو لحساب الوزن المقدر
                # يجب أن نختار "الدفعة" أو "عملية إلقاء الزريعة" التي لا تزال نشطة في الحوض
                active_stocking = pond.fish_stocking_ids.filtered(lambda s: s.state == 'done' and not s.harvest_record_id)
                if active_stocking:
                    # في حالة وجود أكثر من نوع سمك أو دفعة، يجب تحديد أيها يتم تقديره
                    # هنا، نفترض الدفعة الأقدم النشطة أو الدفعة الرئيسية
                    main_stocking = active_stocking[0] # خذ أول دفعة نشطة (أقدمها)
                    
                    growth_model = self.env['fish_farm_management.fish_growth_model'].search([
                        ('fish_type_id', '=', main_stocking.fish_type_id.id),
                        ('company_id', 'in', (False, pond.company_id.id))
                    ], limit=1)

                    if growth_model:
                        days_since_stocking = (fields.Date.today() - main_stocking.stocking_date).days
                        estimated_weight_g_per_fish = growth_model.get_estimated_weight_g(days_since_stocking)
                        estimated_biomass = (pond.current_fish_count * estimated_weight_g_per_fish) / 1000.0 # تحويل من جرام إلى كجم
                    else:
                        # إذا لم يوجد نموذج نمو، يمكن العودة لمتوسط وزن افتراضي أو آخر قياس
                        latest_measurement = self.env['fish_farm_management.fish_growth_measurement'].search([
                            ('pond_id', '=', pond.id),
                            ('fish_type_id', '=', main_stocking.fish_type_id.id)
                        ], order='measurement_date DESC', limit=1)
                        if latest_measurement:
                            estimated_biomass = (pond.current_fish_count * latest_measurement.average_fish_weight_g) / 1000.0
                        else:
                            # fallback if no growth model or measurement
                            estimated_biomass = pond.current_fish_count * 0.1 / 1000.0 # 0.1 جرام لكل سمكة (مثال بسيط)
                
            pond.estimated_current_biomass_kg = estimated_biomass


    @api.depends('water_quality_ids.ph', 'water_quality_ids.oxygen_level', 'water_quality_ids.reading_date')
    def _compute_last_water_quality(self):
        for pond in self:
            latest_reading = self.env['fish_farm_management.water_quality_reading'].search([
                ('pond_id', '=', pond.id)
            ], order='reading_date DESC, id DESC', limit=1)
            pond.last_water_quality_ph = latest_reading.ph if latest_reading else 0.0
            pond.last_water_quality_oxygen = latest_reading.oxygen_level if latest_reading else 0.0

    @api.constrains('name', 'slice_id')
    def _check_unique_pond_name_per_slice(self):
        for pond in self:
            if self.search_count([('name', '=', pond.name), ('slice_id', '=', pond.slice_id.id), ('id', '!=', pond.id)]) > 0:
                raise ValidationError(_("يوجد حوض بهذا الرقم بالفعل في هذه الشريحة."))

    @api.constrains('active_date', 'decommission_date')
    def _check_dates(self):
        for pond in self:
            if pond.active_date and pond.decommission_date and pond.active_date > pond.decommission_date:
                raise ValidationError(_("تاريخ التفعيل يجب أن يكون قبل تاريخ التعطيل."))