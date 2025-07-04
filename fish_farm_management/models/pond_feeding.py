# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PondFeeding(models.Model):
    _name = "fish_farm_management.pond_feeding"
    _description = "سجل تغذية الحوض والمستلزمات"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="المرجع",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True,
    )
    pond_id = fields.Many2one(
        "fish_farm_management.pond",
        string="الحوض",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    feeding_date = fields.Date(
        string="تاريخ التغذية/الاستخدام",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="المنتج (علف/دواء/مستلزم)",
        required=True,
        tracking=True,
        domain="['|', ('is_feed_type', '=', True), ('is_medicine_type', '=', True)]",
    )
    quantity = fields.Float(string="الكمية المستخدمة", required=True, tracking=True)
    product_uom_id = fields.Many2one(
        "uom.uom", string="وحدة القياس", related="product_id.uom_id", readonly=True
    )
    purchase_order_id = fields.Many2one(
        "purchase.order", string="أمر الشراء ذو الصلة", readonly=True
    )
    stock_move_id = fields.Many2one(
        "stock.move",
        string="حركة المخزون",
        readonly=True,
        help="حركة المخزون التي تم إنشاؤها لاستهلاك المنتج.",
    )
    description = fields.Text(string="ملاحظات")
    state = fields.Selection(
        [("draft", "مسودة"), ("done", "تم"), ("cancelled", "ملغاة")],
        string="الحالة",
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    batch_ids = fields.Many2many(
        "fish_farm_management.batch_traceability",
        "ffm_pond_feeding_batch_rel",
        "feeding_id",
        "batch_id",
        string="الدفعات المتأثرة",
        help="الدفعات التي تأثرت بهذه التغذية/المعالجة.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="الشركة",
        related="pond_id.company_id",
        store=True,
        readonly=True,
    )

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fish_farm_management.pond_feeding"
                ) or _("New")
        records = super(PondFeeding, self).create(vals_list)
        return records

    def action_validate_feeding(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("يمكن تأكيد سجل التغذية/المستلزمات في حالة المسودة فقط.")
                )
            if record.quantity <= 0:
                raise UserError(_("الكمية المستخدمة يجب أن تكون أكبر من صفر."))

            source_location = self.env.ref("stock.stock_location_stock")
            consumption_location = self.env.ref("stock.stock_location_customers")
            picking_type = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "internal"),
                    ("warehouse_id.company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
            if not picking_type:
                raise UserError(_("لم يتم العثور على نوع نقل داخلي لشركتك."))

            move_vals = {
                "name": _("استهلاك %s في حوض %s")
                % (record.product_id.name, record.pond_id.name),
                "product_id": record.product_id.id,
                "product_uom_qty": record.quantity,
                "product_uom": record.product_uom_id.id,
                "location_id": source_location.id,
                "location_dest_id": consumption_location.id,
                "state": "draft",
                "reference": record.name,
                "date": record.feeding_date,
            }
            stock_move = self.env["stock.move"].create(move_vals)
            stock_move.action_confirm()
            stock_move.action_assign()
            stock_move.with_context(skip_immediate_validate=True).action_done()

            record.stock_move_id = stock_move.id
            record.state = "done"

            active_batches = self.env["fish_farm_management.batch_traceability"].search(
                [
                    ("pond_id", "=", record.pond_id.id),
                    ("end_date", "=", False),
                ]
            )
            record.batch_ids = [(6, 0, active_batches.ids)]
            record.message_post(
                body=_("تم تأكيد سجل التغذية/المستلزمات وإنشاء حركة المخزون.")
            )
