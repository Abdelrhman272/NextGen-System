# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HarvestSorting(models.Model):
    _name = 'fish_farm_management.harvest_sorting'
    _description = 'فرز الحصاد'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='مرجع الفرز', default=lambda self: _('New'), readonly=True, copy=False, tracking=True)
    harvest_record_id = fields.Many2one('fish_farm_management.harvest_record', string='سجل الحصاد الأصلي', required=True, ondelete='restrict', tracking=True)
    sorting_date = fields.Date(string='تاريخ الفرز', required=True, default=fields.Date.context_today, tracking=True)
    input_weight = fields.Float(string='الوزن المدخل للفرز (كجم)', required=True, tracking=True)
    sorting_line_ids = fields.One2many('fish_farm_management.harvest_sorting_line', 'sorting_id', string='تفاصيل الفرز')
    
    stock_picking_ids = fields.Many2many('stock.picking', string='حركات المخزون الناتجة', compute='_compute_stock_pickings', store=False) # لا تخزن في القاعدة
    
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('done', 'تم'),
        ('cancelled', 'ملغاة')
    ], string='الحالة', default='draft', required=True, tracking=True, copy=False)
    company_id = fields.Many2one('res.company', string='الشركة', related='harvest_record_id.company_id', store=True, readonly=True)

    @api.depends('name')
    def _compute_stock_pickings(self):
        for rec in self:
            # البحث عن حركات المخزون التي تم إنشاؤها بواسطة هذا الفرز
            rec.stock_picking_ids = self.env['stock.picking'].search([
                ('origin', 'like', rec.name + '%'), # يمكن أن تكون هناك حركات متعددة لها نفس الـ origin
                ('company_id', '=', rec.company_id.id)
            ])

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fish_farm_management.harvest_sorting') or _('New')
        res = super(HarvestSorting, self).create(vals)
        return res

    def action_validate_sorting(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("يمكن التحقق من عمليات الفرز في حالة المسودة فقط."))
            if not record.sorting_line_ids:
                raise ValidationError(_("الرجاء إضافة تفاصيل الفرز."))
            if record.input_weight <= 0:
                raise ValidationError(_("الوزن المدخل للفرز يجب أن يكون أكبر من صفر."))

            total_output_weight = sum(line.sorted_weight for line in record.sorting_line_ids)
            # يمكن إضافة فحص لضمان أن إجمالي الوزن المفرز لا يختلف كثيراً عن الوزن المدخل
            # استخدام إعدادات دقيقة للتسامح (tolerance)
            # Example: from odoo.addons.base.models.res_config import ConfigParameters
            # tolerance = float(self.env['ir.config_parameter'].sudo().get_param('fish_farm_management.sorting_tolerance', '0.01'))
            # if abs(total_output_weight - record.input_weight) > tolerance:
            #     raise UserError(_("إجمالي الوزن المفرز (%s كجم) لا يتطابق مع الوزن المدخل (%s كجم) ضمن التسامح المسموح به.") % (total_output_weight, record.input_weight))
            
            if abs(total_output_weight - record.input_weight) > 0.05: # سماحية صغيرة للتقريب 50 جرام
                 raise ValidationError(_("إجمالي الوزن المفرز (%.2f كجم) لا يتطابق مع الوزن المدخل (%.2f كجم).") % (total_output_weight, record.input_weight))


            # إنشاء حركات مخزون من المخزن الرئيسي إلى فئات المنتجات المفرزة
            source_location = self.env.ref('stock.stock_location_stock') # المخزن الرئيسي (حيث توجد الأسماك المحصودة)
            # يمكن تحديد مواقع مخزنية خاصة للمنتجات المفرزة حسب الدرجة/الحجم

            picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', record.company_id.id)], limit=1)
            if not picking_type:
                raise UserError(_("لم يتم العثور على نوع نقل داخلي لشركتك."))

            moves = []
            for line in record.sorting_line_ids:
                if not line.product_id:
                    raise ValidationError(_("يجب تحديد المنتج المفرز لكل سطر."))
                if not line.destination_location_id:
                    raise ValidationError(_("يجب تحديد موقع الوجهة لكل سطر فرز."))
                if line.sorted_weight <= 0:
                    raise ValidationError(_("الوزن المفرز يجب أن يكون أكبر من صفر لكل سطر."))

                moves.append((0, 0, {
                    'name': _('فرز حصاد %s: %s') % (record.harvest_record_id.name, line.product_id.name),
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.sorted_weight,
                    'product_uom': line.product_uom_id.id,
                    'location_id': source_location.id,
                    'location_dest_id': line.destination_location_id.id, # موقع الوجهة المحدد في سطر الفرز
                    'state': 'draft',
                    'reference': record.name,
                    'date': record.sorting_date,
                    'company_id': record.company_id.id,
                }))

            if moves:
                picking_vals = {
                    'picking_type_id': picking_type.id,
                    'location_id': source_location.id,
                    'location_dest_id': source_location.id, # النقل من المخزن إلى نفسه مع تغيير المنتج
                    'origin': record.name,
                    'move_ids_without_package': moves,
                    'company_id': record.company_id.id,
                }
                picking = self.env['stock.picking'].create(picking_vals)
                picking._action_confirm()
                picking._action_assign()
                picking.with_context(skip_immediate_validate=True)._action_done() # تأكيد وإتمام النقل
            
            record.state = 'done'
            record.message_post(body=_("تم تأكيد عملية الفرز وإنشاء حركات المخزون."))

    def action_cancel_sorting(self):
        for record in self:
            if record.state == 'done':
                # إلغاء جميع حركات المخزون المرتبطة
                for picking in record.stock_picking_ids:
                    if picking.state not in ('cancel', 'done'): # يمكن إلغاء فقط التي لم يتم إتمامها بالكامل
                        picking.button_cancel() # يجب التأكد من صلاحيات إلغاء حركات المخزون
                    elif picking.state == 'done':
                         raise UserError(_("لا يمكن إلغاء الفرز لأن هناك حركات مخزون تمت بالفعل. يجب عكسها يدوياً."))
            record.state = 'cancelled'
            record.message_post(body=_("تم إلغاء عملية الفرز."))

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("لا يمكن حذف سجل فرز تم الانتهاء منه. يرجى إلغائه أولاً."))
            for picking in rec.stock_picking_ids:
                if picking.state == 'done':
                    raise UserError(_("لا يمكن حذف سجل فرز لديه حركات مخزون تامة."))
                picking.unlink() # حذف حركة المخزون المرتبطة إذا لم تكن مؤكدة
        return super(HarvestSorting, self).unlink()

class HarvestSortingLine(models.Model):
    _name = 'fish_farm_management.harvest_sorting_line'
    _description = 'تفاصيل فرز الحصاد'

    sorting_id = fields.Many2one('fish_farm_management.harvest_sorting', string='عملية الفرز', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='المنتج المفرز (النوع/الجودة)', required=True,
                                 domain="[('is_harvested_product', '=', True)]") # يجب أن تكون منتجات ذات جودة/حجم معين
    sorted_weight = fields.Float(string='الوزن المفرز (كجم)', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='وحدة القياس', related='product_id.uom_id', readonly=True)
    destination_location_id = fields.Many2one('stock.location', string='موقع الوجهة', required=True,
                                              default=lambda self: self.env.ref('stock.stock_location_stock')) # يمكن أن يكون موقع فرعي لمنتجات الفرز
    notes = fields.Text(string='ملاحظات على الفرز')