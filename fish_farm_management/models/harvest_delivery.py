# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HarvestDelivery(models.Model):
    _name = "fish_farm_management.harvest_delivery"
    _description = "تسليم الحصاد للمخزن"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="مرجع التسليم",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True,
    )
    harvest_record_id = fields.Many2one(
        "fish_farm_management.harvest_record",
        string="سجل الحصاد",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    delivery_date = fields.Date(
        string="تاريخ التسليم",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    delivered_weight = fields.Float(
        string="الوزن المسلم (كجم)", required=True, tracking=True
    )
    destination_location_id = fields.Many2one(
        "stock.location",
        string="موقع الوجهة",
        required=True,
        default=lambda self: self.env.ref("stock.stock_location_stock"),
    )
    stock_picking_id = fields.Many2one(
        "stock.picking",
        string="نقل المخزون",
        related="harvest_record_id.stock_picking_id",
        readonly=True,
        store=True,
    )
    notes = fields.Text(string="ملاحظات")
    state = fields.Selection(
        [("draft", "مسودة"), ("done", "تم"), ("cancelled", "ملغاة")],
        string="الحالة",
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    company_id = fields.Many2one(
        "res.company",
        string="الشركة",
        related="harvest_record_id.company_id",
        store=True,
        readonly=True,
    )

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fish_farm_management.harvest_delivery"
            ) or _("New")
        res = super(HarvestDelivery, self).create(vals)
        res.harvest_record_id.delivery_to_warehouse_id = res.id
        return res

    def action_validate_delivery(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("يمكن التحقق من عمليات التسليم في حالة المسودة فقط."))
            if record.delivered_weight <= 0:
                raise ValidationError(_("يجب أن يكون الوزن المسلم أكبر من صفر."))
            if not record.stock_picking_id or record.stock_picking_id.state != "done":
                raise UserError(
                    _("يجب تأكيد سجل الحصاد المرتبط أولاً لإنشاء حركة المخزون.")
                )
            record.state = "done"
            record.message_post(body=_("تم تأكيد تسليم الحصاد للمخزن."))

    def action_cancel_delivery(self):
        for record in self:
            record.state = "cancelled"
            record.message_post(body=_("تم إلغاء تسليم الحصاد."))
