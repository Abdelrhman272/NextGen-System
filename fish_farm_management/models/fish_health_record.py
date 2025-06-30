# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FishHealthRecord(models.Model):
    _name = 'fish_farm_management.fish_health_record'
    _description = 'سجل صحة الأسماك والأمراض'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='المرجع', default=lambda self: _('New'), readonly=True, copy=False, tracking=True)
    pond_id = fields.Many2one('fish_farm_management.pond', string='الحوض', required=True, ondelete='restrict', tracking=True)
    record_date = fields.Date(string='تاريخ التسجيل', required=True, default=fields.Date.context_today, tracking=True)
    
    issue_type = fields.Selection([
        ('disease', 'مرض'),
        ('mortality', 'وفيات'),
        ('injury', 'إصابة'),
        ('other', 'أخرى'),
    ], string='نوع المشكلة', required=True, tracking=True)
    
    disease_name = fields.Char(string='اسم المرض/المشكلة', attrs="{'required': [('issue_type', '=', 'disease')]}", tracking=True)
    symptoms = fields.Text(string='الأعراض الملاحظة')
    diagnosis = fields.Text(string='التشخيص')
    
    treatment_ids = fields.One2many('fish_farm_management.fish_health_treatment', 'health_record_id', string='العلاجات المستخدمة')
    
    mortality_count = fields.Integer(string='عدد الوفيات', default=0, tracking=True)
    mortality_reason = fields.Char(string='سبب الوفاة', attrs="{'invisible': [('issue_type', '!=', 'mortality')]}", tracking=True)
    
    responsible_employee_id = fields.Many2one('hr.employee', string='الموظف المسؤول', ondelete='set null')
    notes = fields.Text(string='ملاحظات إضافية')
    company_id = fields.Many2one('res.company', string='الشركة', related='pond_id.company_id', store=True, readonly=True)

    @api.model
    def create(self, vals_list): # تم تغيير vals إلى vals_list
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fish_farm_management.fish_health_record') or _('New')
        
        records = super(FishHealthRecord, self).create(vals_list) # استدعاء create الأصلية مع القائمة
        
        # لا يوجد منطق خاص يطبق على كل سجل فردي بعد الإنشاء في هذه الدالة
        return records

    @api.constrains('mortality_count')
    def _check_mortality_count(self):
        for rec in self:
            if rec.issue_type == 'mortality' and rec.mortality_count <= 0:
                raise ValidationError(_("يجب أن يكون عدد الوفيات أكبر من صفر عند تسجيل حالة وفاة."))

class FishHealthTreatment(models.Model):
    _name = 'fish_farm_management.fish_health_treatment'
    _description = 'تفاصيل العلاج الصحي للأسماك'

    health_record_id = fields.Many2one('fish_farm_management.fish_health_record', string='سجل الصحة', required=True, ondelete='cascade')
    treatment_date = fields.Date(string='تاريخ العلاج', required=True, default=fields.Date.context_today)
    medicine_id = fields.Many2one('product.product', string='الدواء المستخدم', required=True,
                                  domain="[('is_medicine_type', '=', True)]")
    dosage = fields.Char(string='الجرعة/الكمية')
    product_uom_id = fields.Many2one('uom.uom', string='وحدة القياس', related='medicine_id.uom_id', readonly=True)
    quantity_used = fields.Float(string='الكمية المستخدمة (المخزنية)', help='الكمية الفعلية التي تم استهلاكها من المخزون.')
    treatment_notes = fields.Text(string='ملاحظات العلاج')
    stock_move_id = fields.Many2one('stock.move', string='حركة المخزون', readonly=True, help='حركة المخزون التي تم إنشاؤها لاستهلاك الدواء.')

    @api.model
    def create(self, vals):
        res = super(FishHealthTreatment, self).create(vals)
        # إنشاء حركة مخزون لاستهلاك الدواء
        if res.medicine_id and res.quantity_used > 0:
            source_location = res.env.ref('stock.stock_location_stock')
            consumption_location = res.env.ref('stock.stock_location_customers')
            picking_type = res.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', res.health_record_id.company_id.id)], limit=1)
            if not picking_type:
                raise UserError(_("لم يتم العثور على نوع نقل داخلي لشركتك."))

            move_vals = {
                'name': _('علاج %s لحوض %s') % (res.medicine_id.name, res.health_record_id.pond_id.name),
                'product_id': res.medicine_id.id,
                'product_uom_qty': res.quantity_used,
                'product_uom': res.product_uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': consumption_location.id,
                'state': 'draft',
                'reference': res.health_record_id.name,
                'date': res.treatment_date,
                'company_id': res.health_record_id.company_id.id,
            }
            stock_move = res.env['stock.move'].create(move_vals)
            stock_move._action_confirm()
            stock_move._action_assign()
            stock_move.with_context(skip_immediate_validate=True)._action_done()
            res.stock_move_id = stock_move.id
        return res

    def unlink(self):
        for rec in self:
            if rec.stock_move_id and rec.stock_move_id.state != 'cancel':
                rec.stock_move_id.button_cancel() # إلغاء حركة المخزون عند حذف العلاج
        return super(FishHealthTreatment, self).unlink()