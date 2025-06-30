# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FishStocking(models.Model):
    _name = 'fish_farm_management.fish_stocking'
    _description = 'سجل إلقاء الزريعة'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # لإضافة تتبع الرسائل والأنشطة

    name = fields.Char(string='المرجع', default=lambda self: _('New'), readonly=True, copy=False, tracking=True)
    pond_id = fields.Many2one('fish_farm_management.pond', string='الحوض', required=True, ondelete='restrict', tracking=True)
    fish_type_id = fields.Many2one('product.product', string='نوع السمك/الجمبري',
                                   domain="[('is_fish_type', '=', True)]", required=True, tracking=True)
    stocking_date = fields.Date(string='تاريخ إلقاء الزريعة', required=True, default=fields.Date.context_today, tracking=True)
    quantity = fields.Float(string='الكمية (زريعة/يرقات)', required=True, tracking=True)
    uom_id = fields.Many2one('uom.uom', string='وحدة القياس', related='fish_type_id.uom_id', readonly=True)
    source_picking_id = fields.Many2one('stock.picking', string='نقل المصدر', help='سجل نقل المخزون للزريعة/اليرقات.', readonly=True)
    harvest_record_id = fields.Many2one('fish_farm_management.harvest_record', string='حصاد ذو صلة', help='الربط بسجل الحصاد إذا تم الحصاد.', readonly=True)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('done', 'تم'),
        ('cancelled', 'ملغاة')
    ], string='الحالة', default='draft', required=True, tracking=True, copy=False)
    batch_id = fields.Many2one('fish_farm_management.batch_traceability', string='رقم الدفعة', readonly=True)
    company_id = fields.Many2one('res.company', string='الشركة', related='pond_id.company_id', store=True, readonly=True)


    @api.model
    def create(self, vals):
        # دعم تمرير dict أو قائمة
        vals_list = [vals] if isinstance(vals, dict) else vals
    
        for v in vals_list:
            if v.get('name', _('New')) == _('New'):
                v['name'] = self.env['ir.sequence'].next_by_code('fish_farm_management.fish_stocking') or _('New')
    
        records = super(FishStocking, self).create(vals_list)
    
        for rec in records:
            if rec.pond_id.status in ('empty', 'preparing'):
                rec.pond_id.status = 'stocked'
    
            batch = self.env['fish_farm_management.batch_traceability'].create({
                'name': _('دفعة زريعة %s - حوض %s') % (rec.fish_type_id.name, rec.pond_id.name),
                'stocking_id': rec.id,
                'fish_type_id': rec.fish_type_id.id,
                'initial_quantity': rec.quantity,
                'pond_id': rec.pond_id.id,
                'start_date': rec.stocking_date,
            })
            rec.batch_id = batch.id
    
        return records

    def action_validate_stocking(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("يمكن تأكيد إلقاء الزريعة في حالة المسودة فقط."))
            
            # إنشاء حركة مخزون لاستهلاك المنتج من المخزن
            source_location = self.env.ref('stock.stock_location_stock') # موقع المخزن الرئيسي
            # يمكن تعريف موقع خاص بالاحواض
            destination_location = self.env.ref('stock.stock_location_customers') # موقع افتراضي للاستهلاك (أو موقع الأحواض الافتراضي)

            picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', self.env.company.id)], limit=1)
            if not picking_type:
                raise UserError(_("لم يتم العثور على نوع نقل داخلي لشركتك."))

            move_vals = {
                'name': _('إلقاء زريعة %s في حوض %s') % (record.fish_type_id.name, record.pond_id.name),
                'product_id': record.fish_type_id.id,
                'product_uom_qty': record.quantity,
                'product_uom': record.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': destination_location.id,
                'state': 'draft',
                'reference': record.name,
                'date': record.stocking_date,
            }
            stock_move = self.env['stock.move'].create(move_vals)
            stock_move._action_confirm()
            stock_move._action_assign()
            stock_move.with_context(skip_immediate_validate=True)._action_done()
            
            record.source_picking_id = stock_move.picking_id.id # ربط بالنقل الذي تم إنشاؤه
            record.state = 'done'
            record.message_post(body=_("تم تأكيد إلقاء الزريعة وإنشاء حركة المخزون."))

    def action_cancel_stocking(self):
        for record in self:
            if record.state == 'done':
                if record.source_picking_id and record.source_picking_id.state != 'cancel':
                    record.source_picking_id.button_cancel() # إلغاء النقل المخزني
                record.pond_id.status = 'empty' # قد تحتاج لمنطق أكثر تعقيدًا إذا كانت الأحواض بها أنواع أسماك أخرى
            record.state = 'cancelled'
            record.message_post(body=_("تم إلغاء إلقاء الزريعة."))

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("لا يمكن حذف سجل إلقاء الزريعة الذي تم تأكيده. يرجى إلغائه أولاً."))
            if rec.harvest_record_id:
                raise UserError(_("لا يمكن حذف سجل إلقاء الزريعة المرتبط بسجل حصاد."))
            if rec.batch_id:
                rec.batch_id.unlink() # حذف سجل الدفعة المرتبط
        return super(FishStocking, self).unlink()