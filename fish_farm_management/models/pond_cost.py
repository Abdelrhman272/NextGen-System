# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PondCost(models.Model):
    _name = 'fish_farm_management.pond_cost'
    _description = 'إدخال تكلفة الحوض'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='المرجع', default=lambda self: _('New'), readonly=True, copy=False, tracking=True)
    pond_id = fields.Many2one('fish_farm_management.pond', string='الحوض', required=True, ondelete='restrict', tracking=True)
    cost_date = fields.Date(string='تاريخ التكلفة', required=True, default=fields.Date.context_today, tracking=True)
    
    cost_type_id = fields.Many2one('account.analytic.tag', string='نوع التكلفة', required=True, tracking=True,
                                   help='الربط بالعلامات التحليلية لتصنيف التكلفة (مثل: كهرباء، عمالة، علف).',
                                   domain="[('analytic_tag_group_id.name', '=', 'Pond Cost Types')]")
    amount = fields.Monetary(string='المبلغ', required=True, tracking=True, currency_field='company_currency_id')
    company_id = fields.Many2one('res.company', string='الشركة', related='pond_id.company_id', store=True, readonly=True)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='عملة الشركة', readonly=True)

    description = fields.Text(string='الوصف')
    is_direct_cost = fields.Boolean(string='تكلفة مباشرة', default=True, tracking=True)
    
    # ربط اختياري بمستندات المصدر
    purchase_order_id = fields.Many2one('purchase.order', string='أمر الشراء ذو الصلة', readonly=True)
    expense_sheet_id = fields.Many2one('hr.expense.sheet', string='كشف المصروفات ذو الصلة', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='الموظف ذو الصلة', ondelete='set null') # لتكاليف العمالة المباشرة
    
    account_move_id = fields.Many2one('account.move', string='قيد المحاسبة', readonly=True, copy=False) # ربط بقيد المحاسبة
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('posted', 'مرحل'),
        ('cancelled', 'ملغاة')
    ], string='الحالة', default='draft', required=True, tracking=True, copy=False)

    @api.model
    def create(self, vals_list): # تم تغيير vals إلى vals_list
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fish_farm_management.pond_cost') or _('New')
        
        records = super(PondCost, self).create(vals_list) # استدعاء create الأصلية مع القائمة
        
        # لا يوجد منطق خاص يطبق على كل سجل فردي بعد الإنشاء في هذه الدالة
        return records

    def action_post_cost(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("يمكن ترحيل التكلفة من حالة المسودة فقط."))
            if record.amount <= 0:
                raise ValidationError(_("مبلغ التكلفة يجب أن يكون أكبر من صفر."))
            
            # **إنشاء قيد محاسبي:**
            # هذا الجزء يتطلب تحديد الحسابات والدفاتر المناسبة في نظام أودو الخاص بك.
            # ستحتاج إلى تحديد حسابات مصروفات محددة لأنواع التكلفة المختلفة.
            # مثال: حسابات للمصروفات، حساب للموردين أو النقدية/البنك.

            journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', record.company_id.id)], limit=1)
            if not journal:
                raise UserError(_("لم يتم العثور على دفتر يومية عام لشركتك."))

            # ابحث عن حساب المصروفات بناءً على نوع التكلفة أو حساب افتراضي
            # هذا الجزء يحتاج لتعريف منطق الربط بين Analytic Tag وحساب المصروفات
            expense_account = self.env['account.account'].search([('code', '=', '600000'), ('company_id', '=', record.company_id.id)], limit=1) # مثال: حساب مصروفات عام
            # حساب الدائن (مثال: حساب دائن متنوع أو حساب نقدية/بنك إذا كان الدفع نقداً)
            credit_account = self.env['account.account'].search([('code', '=', '201000'), ('company_id', '=', record.company_id.id)], limit=1) # مثال: حساب دائنون متنوعون

            if not expense_account or not credit_account:
                raise UserError(_("الرجاء التأكد من تعريف حسابات المصروفات والدائن المناسبة في المحاسبة."))

            move_lines = [
                (0, 0, {
                    'name': _('تكلفة حوض %s: %s') % (record.pond_id.name, record.cost_type_id.name),
                    'account_id': expense_account.id,
                    'debit': record.amount,
                    'credit': 0,
                    'analytic_tag_ids': [(6, 0, record.cost_type_id.ids)],
                    # 'analytic_account_id': record.pond_id.analytic_account_id.id, # إذا كان الحوض مرتبط بحساب تحليلي
                    'partner_id': record.employee_id.address_home_id.partner_id.id if record.employee_id and record.is_direct_cost else False,
                }),
                (0, 0, {
                    'name': _('دفع/استحقاق تكلفة حوض %s: %s') % (record.pond_id.name, record.cost_type_id.name),
                    'account_id': credit_account.id,
                    'debit': 0,
                    'credit': record.amount,
                    'partner_id': record.employee_id.address_home_id.partner_id.id if record.employee_id and record.is_direct_cost else False,
                }),
            ]

            move_vals = {
                'journal_id': journal.id,
                'date': record.cost_date,
                'ref': record.name,
                'line_ids': move_lines,
                'move_type': 'entry', # قيد يومية عام
                'company_id': record.company_id.id,
            }
            
            account_move = self.env['account.move'].create(move_vals)
            account_move.action_post() # ترحيل القيد تلقائياً
            
            record.account_move_id = account_move.id
            record.state = 'posted'
            record.message_post(body=_("تم ترحيل قيد التكلفة بنجاح."))

    def action_cancel_cost(self):
        for record in self:
            if record.state == 'posted':
                if record.account_move_id and record.account_move_id.state == 'posted':
                    record.account_move_id.button_draft() # إلغاء ترحيل
                    record.account_move_id.button_cancel() # إلغاء القيد
            record.state = 'cancelled'
            record.message_post(body=_("تم إلغاء سجل التكلفة."))

    def unlink(self):
        for rec in self:
            if rec.state == 'posted':
                raise UserError(_("لا يمكن حذف سجل تكلفة مرحل. يرجى إلغائه أولاً."))
            if rec.account_move_id:
                rec.account_move_id.unlink() # حذف القيد إذا لم يكن مرحلاً
        return super(PondCost, self).unlink()