# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FishStocking(models.Model):
    _name = 'fish_farm_management.fish_stocking'
    _description = 'سجل إلقاء الزريعة'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='المرجع',
        default=lambda self: _('New'),
        readonly=True,
        copy=False,
        tracking=True
    )
    pond_id = fields.Many2one(
        'fish_farm_management.pond',
        string='الحوض',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    fish_type_id = fields.Many2one(
        'product.product',
        string='نوع السمك/الجمبري',
        domain="[('is_fish_type', '=', True)]",
        required=True,
        tracking=True
    )
    stocking_date = fields.Date(
        string='تاريخ إلقاء الزريعة',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    quantity = fields.Float(
        string='الكمية (زريعة/يرقات)',
        required=True,
        tracking=True
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='وحدة القياس',
        related='fish_type_id.uom_id',
        readonly=True
    )
    # الحقل الجديد لتوافق مع XML
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='وحدة القياس',
        related='fish_type_id.uom_id',
        readonly=True
    )
    source_picking_id = fields.Many2one(
        'stock.picking',
        string='نقل المصدر',
        help='سجل نقل المخزون للزريعة/اليرقات.',
        readonly=True
    )
    harvest_record_id = fields.Many2one(
        'fish_farm_management.harvest_record',
        string='حصاد ذو صلة',
        help='الربط بسجل الحصاد إذا تم الحصاد.',
        readonly=True
    )
    state = fields.Selection(
        [
            ('draft', 'مسودة'),
            ('done', 'تم'),
            ('cancelled', 'ملغاة')
        ],
        string='الحالة',
        default='draft',
        required=True,
        tracking=True,
        copy=False
    )
    batch_id = fields.Many2one(
        'fish_farm_management.batch_traceability',
        string='رقم الدفعة',
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='الشركة',
        related='pond_id.company_id',
        store=True,
        readonly=True
    )

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence']
                    .next_by_code('fish_farm_management.fish_stocking')
                    or _('New')
                )
        records = super().create(vals_list)
        for res in records:
            if res.pond_id.status in ('empty', 'preparing'):
                res.pond_id.status = 'stocked'
            batch = self.env['fish_farm_management.batch_traceability'].create({
                'name': _('دفعة زريعة %s - حوض %s') % (
                    res.fish_type_id.name, res.pond_id.name
                ),
                'stocking_id': res.id,
                'fish_type_id': res.fish_type_id.id,
                'initial_quantity': res.quantity,
                'pond_id': res.pond_id.id,
                'start_date': res.stocking_date,
            })
            res.batch_id = batch.id
        return records

    def action_validate_stocking(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    _("يمكن تأكيد إلقاء الزريعة في حالة المسودة فقط.")
                )
            source_loc = self.env.ref('stock.stock_location_stock')
            dest_loc = self.env.ref('stock.stock_location_customers')
            picking_type = (
                self.env['stock.picking.type']
                .search([
                    ('code', '=', 'internal'),
                    ('warehouse_id.company_id', '=', self.env.company.id)
                ], limit=1)
            )
            if not picking_type:
                raise UserError(
                    _("لم يتم العثور على نوع نقل داخلي لشركتك.")
                )
            move_vals = {
                'name': _(
                    'إلقاء زريعة %s في حوض %s'
                ) % (record.fish_type_id.name, record.pond_id.name),
                'product_id': record.fish_type_id.id,
                'product_uom_qty': record.quantity,
                'product_uom': record.uom_id.id,
                'location_id': source_loc.id,
                'location_dest_id': dest_loc.id,
                'state': 'draft',
                'reference': record.name,
                'date': record.stocking_date,
            }
            move = self.env['stock.move'].create(move_vals)
            move._action_confirm()
            move._action_assign()
            move.with_context(skip_immediate_validate=True)._action_done()
            record.source_picking_id = move.picking_id.id
            record.state = 'done'
            record.message_post(
                body=_("تم تأكيد إلقاء الزريعة وإنشاء حركة المخزون.")
            )

    def action_cancel_stocking(self):
        for record in self:
            if record.state == 'done':
                if record.source_picking_id and record.source_picking_id.state != 'cancel':
                    record.source_picking_id.button_cancel()
                record.pond_id.status = 'empty'
            record.state = 'cancelled'
            record.message_post(body=_("تم إلغاء إلقاء الزريعة."))

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(
                    _("لا يمكن حذف سجل إلقاء الزريعة الذي تم تأكيده. يرجى إلغائه أولاً.")
                )
            if rec.harvest_record_id:
                raise UserError(
                    _("لا يمكن حذف سجل إلقاء الزريعة المرتبط بسجل حصاد.")
                )
            if rec.batch_id:
                rec.batch_id.unlink()
        return super().unlink()