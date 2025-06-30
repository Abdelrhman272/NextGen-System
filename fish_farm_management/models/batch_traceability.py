# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils

class BatchTraceability(models.Model):
    _name = 'fish_farm_management.batch_traceability'
    _description = 'تتبع دفعة المنتج'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='رقم الدفعة', default=lambda self: _('New'), readonly=True, copy=False, tracking=True)
    fish_type_id = fields.Many2one('product.product', string='نوع السمك', required=True, domain="[('is_fish_type', '=', True)]", tracking=True)
    pond_id = fields.Many2one('fish_farm_management.pond', string='الحوض الأصلي', required=True, ondelete='restrict', tracking=True)
    
    initial_quantity = fields.Float(string='الكمية الأولية (زريعة)', tracking=True)
    start_date = fields.Date(string='تاريخ بدء الدفعة (إلقاء الزريعة)', required=True, tracking=True)
    end_date = fields.Date(string='تاريخ انتهاء الدفعة (حصاد)', tracking=True, help='تاريخ الانتهاء هو تاريخ آخر حصاد لهذه الدفعة.')
    final_quantity_kg = fields.Float(string='الكمية النهائية (كجم حصاد)', tracking=True, help='إجمالي الوزن المنتج من هذه الدفعة.')

    stocking_id = fields.Many2one('fish_farm_management.fish_stocking', string='سجل إلقاء الزريعة', ondelete='restrict', help='الرابط بسجل إلقاء الزريعة الأصلي لهذه الدفعة.')
    
    harvest_ids = fields.One2many('fish_farm_management.harvest_record', 'batch_id', string='سجلات الحصاد')
    # يجب أن يكون هناك ربط بين Sales Order Lines و Harvests/Batches لتتبع المبيعات
    sales_order_lines_ids = fields.Many2many('sale.order.line', string='بنود أوامر البيع', compute='_compute_sales_data', store=False)
    total_sales_qty = fields.Float(string='إجمالي الكمية المباعة (كجم)', compute='_compute_sales_data', store=False)
    
    mortality_count = fields.Integer(string='إجمالي الوفيات', compute='_compute_batch_metrics', store=True)
    fcr = fields.Float(string='معدل التحويل الغذائي (FCR)', compute='_compute_batch_metrics', store=True, digits=(16, 2))
    survival_rate = fields.Float(string='معدل البقاء على قيد الحياة (%)', compute='_compute_batch_metrics', store=True, digits=(16, 2))
    total_feed_consumed = fields.Float(string='إجمالي العلف المستهلك (كجم)', compute='_compute_batch_metrics', store=True)
    
    estimated_current_avg_weight_g = fields.Float(string='متوسط الوزن المقدر حالياً (جم)', compute='_compute_batch_metrics', store=True)
    estimated_target_days_remaining = fields.Integer(string='الأيام المتبقية للهدف', compute='_compute_batch_metrics', store=True)

    company_id = fields.Many2one('res.company', string='الشركة', related='pond_id.company_id', store=True, readonly=True)

    api.model
    def create(self, vals_list): # تم تغيير vals إلى vals_list
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fish_farm_management.batch_traceability') or _('New')
        
        records = super(BatchTraceability, self).create(vals_list) # استدعاء create الأصلية مع القائمة
        
        # لا يوجد منطق خاص يطبق على كل سجل فردي بعد الإنشاء في هذه الدالة
        return records

    @api.depends('harvest_ids.total_weight', 'pond_id.pond_feeding_ids.quantity', 'pond_id.fish_health_ids.mortality_count',
                 'start_date', 'end_date', 'fish_type_id', 'stocking_id.quantity',
                 'pond_id.fish_health_ids.record_date', 'pond_id.pond_feeding_ids.feeding_date',
                 'fish_type_id.fish_growth_model_ids.start_weight_g', 'fish_type_id.fish_growth_model_ids.target_weight_g',
                 'fish_type_id.fish_growth_model_ids.target_days', 'pond_id.growth_measurement_ids.measurement_date',
                 'pond_id.growth_measurement_ids.average_fish_weight_g')
    def _compute_batch_metrics(self):
        for batch in self:
            # إجمالي الوفيات المرتبطة بهذا الحوض وهذه الدفعة
            mortality_records = self.env['fish_farm_management.fish_health_record'].search([
                ('pond_id', '=', batch.pond_id.id),
                ('record_date', '>=', batch.start_date),
                ('record_date', '<=', batch.end_date if batch.end_date else fields.Date.today()),
                ('issue_type', '=', 'mortality'),
            ])
            batch.mortality_count = sum(rec.mortality_count for rec in mortality_records)

            # إجمالي العلف المستهلك المرتبط بهذا الحوض وتاريخ الدفعة
            feed_consumption_records = self.env['fish_farm_management.pond_feeding'].search([
                ('pond_id', '=', batch.pond_id.id),
                ('feeding_date', '>=', batch.start_date),
                ('feeding_date', '<=', batch.end_date if batch.end_date else fields.Date.today()),
                ('product_id.is_feed_type', '=', True),
                ('state', '=', 'done'),
            ])
            batch.total_feed_consumed = sum(rec.quantity for rec in feed_consumption_records)

            # معدل البقاء على قيد الحياة
            if batch.initial_quantity > 0:
                batch.survival_rate = (batch.initial_quantity - batch.mortality_count) / batch.initial_quantity * 100.0
            else:
                batch.survival_rate = 0.0

            # معدل التحويل الغذائي (FCR)
            if batch.final_quantity_kg > 0:
                batch.fcr = batch.total_feed_consumed / batch.final_quantity_kg
            else:
                batch.fcr = 0.0

            # تقدير متوسط الوزن الحالي والأيام المتبقية للهدف
            estimated_avg_weight_g = 0.0
            estimated_target_days_remaining = 0
            
            if batch.fish_type_id and batch.start_date:
                # حاول الحصول على نموذج النمو الخاص بنوع السمك
                growth_model = self.env['fish_farm_management.fish_growth_model'].search([
                    ('fish_type_id', '=', batch.fish_type_id.id),
                    ('company_id', 'in', (False, batch.company_id.id))
                ], limit=1)

                if growth_model:
                    days_since_stocking = (fields.Date.today() - batch.start_date).days
                    
                    estimated_avg_weight_g = growth_model.get_estimated_weight_g(days_since_stocking)

                    if estimated_avg_weight_g < growth_model.target_weight_g:
                        # تقدير الأيام المتبقية للوصول إلى الوزن المستهدف
                        remaining_growth = growth_model.target_weight_g - estimated_avg_weight_g
                        if (growth_model.target_weight_g - growth_model.start_weight_g) > 0:
                            # نسبة النمو المتبقية من إجمالي النمو
                            estimated_target_days_remaining = int(
                                (remaining_growth / ((growth_model.target_weight_g - growth_model.start_weight_g) / growth_model.target_days))
                            )
                        else:
                            estimated_target_days_remaining = 0
                    else:
                        estimated_target_days_remaining = 0 # تم الوصول للوزن المستهدف أو تجاوزه
                else:
                    # إذا لم يوجد نموذج نمو، حاول البحث عن آخر قياس نمو
                    latest_measurement = self.env['fish_farm_management.fish_growth_measurement'].search([
                        ('pond_id', '=', batch.pond_id.id),
                        ('fish_type_id', '=', batch.fish_type_id.id),
                        ('measurement_date', '>=', batch.start_date),
                        ('measurement_date', '<=', batch.end_date if batch.end_date else fields.Date.today()),
                    ], order='measurement_date DESC', limit=1)
                    if latest_measurement:
                        estimated_avg_weight_g = latest_measurement.average_fish_weight_g

            batch.estimated_current_avg_weight_g = estimated_avg_weight_g
            batch.estimated_target_days_remaining = estimated_target_days_remaining

    @api.depends('harvest_ids.stock_picking_id.move_ids_without_package.sale_line_id')
    def _compute_sales_data(self):
        for batch in self:
            sales_lines = self.env['sale.order.line']
            total_qty_sold = 0.0
            # هذا الربط مع المبيعات يحتاج إلى أنظمة Batch/Lot Numbering في Stock و Sales
            # بشكل افتراضي، أودو لا يربط سطر أمر البيع مباشرة بالدفعة من الحصاد
            # ستحتاج إلى تخصيص لتمرير معلومات الدفعة/اللوت من الفرز إلى حركة التسليم ثم إلى سطر أمر البيع
            
            # حل مبسط: البحث عن بنود بيع لمنتجات تم حصادها من هذه الدفعة
            # هذا يحتاج لتعريف منتجات الفرز لتكون مرتبطة بالدفعة الأصلية
            
            # مثال افتراضي (يحتاج تخصيص دقيق):
            # إذا كانت منتجات الفرز (مثل Tilapia Grade A) تحمل مرجع للدفعة الأصلية
            # for harvest_sorting_line in batch.harvest_ids.mapped('harvest_sorting_ids.sorting_line_ids'):
            #     sale_lines_for_product = self.env['sale.order.line'].search([
            #         ('product_id', '=', harvest_sorting_line.product_id.id),
            #         ('state', '=', 'sale'),
            #         ('order_id.date_order', '>=', batch.start_date),
            #         ('order_id.date_order', '<=', batch.end_date if batch.end_date else fields.Date.today()),
            #     ])
            #     sales_lines |= sale_lines_for_product
            #     total_qty_sold += sum(line.product_uom_qty for line in sale_lines_for_product)

            # للتبسيط حاليًا، هذا الحقل قد لا يكون دقيقًا ما لم يتم بناء تتبع كامل للمخزون بالدفعات.
            batch.sales_order_lines_ids = [(6, 0, sales_lines.ids)]
            batch.total_sales_qty = total_qty_sold

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for batch in self:
            if batch.start_date and batch.end_date and batch.start_date > batch.end_date:
                raise ValidationError(_("تاريخ بدء الدفعة يجب أن يكون قبل تاريخ انتهائها."))