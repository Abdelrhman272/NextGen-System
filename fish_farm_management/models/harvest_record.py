# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HarvestRecord(models.Model):
    _name = "fish_farm_management.harvest_record"
    _description = "سجل حصاد السمك"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # --------------------------------------------------
    # الحقول
    # --------------------------------------------------
    name = fields.Char(
        string="مرجع الحصاد",
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
    harvest_date = fields.Date(
        string="تاريخ الحصاد",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    harvest_number = fields.Integer(
        string="رقم الصيد",
        help="رقم تسلسلي لمرات الحصاد من نفس الحوض.",
        default=1,
        tracking=True,
    )
    total_weight = fields.Float(
        string="إجمالي وزن الحصاد (كجم)", required=True, tracking=True
    )
    harvest_committee_ids = fields.Many2many(
        "hr.employee", string="لجنة الصيد", required=True
    )
    delivery_to_warehouse_id = fields.Many2one(
        "fish_farm_management.harvest_delivery",
        string="تسليم للمخزن",
        readonly=True,
        copy=False,
    )
    stock_picking_id = fields.Many2one(
        "stock.picking",
        string="نقل المخزون للمخزن",
        readonly=True,
        copy=False,
        help="سجل النقل الداخلي للبضاعة المحصودة.",
    )
    state = fields.Selection(
        [
            ("draft", "مسودة"),
            ("done", "تم"),
            ("cancelled", "ملغاة"),
        ],
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    batch_id = fields.Many2one(
        "fish_farm_management.batch_traceability",
        string="الدفعة المنتجة من",
        readonly=True,
        help="الدفعة التي تم حصادها من هذا السجل.",
    )
    fish_type_id = fields.Many2one(
        "product.product",
        string="نوع السمك الرئيسي (من الدفعة)",
        related="batch_id.fish_type_id",
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="pond_id.company_id",
        store=True,
        readonly=True,
    )

    # --------------------------------------------------
    # إنشاء السجل
    # --------------------------------------------------
    @api.model
    def create(self, vals_list):
        """يدعم إنشاء دفعة (batch) سجلات مرة واحدة."""
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fish_farm_management.harvest_record"
                ) or _("New")
        records = super().create(vals_list)

        # ربط الدفعة وتحديث حالة الحوض
        for rec in records:
            if rec.pond_id.status != "harvesting":
                rec.pond_id.status = "harvesting"

            existing_batch = self.env["fish_farm_management.batch_traceability"].search(
                [("pond_id", "=", rec.pond_id.id), ("end_date", "=", False)],
                limit=1,
                order="start_date DESC",
            )
            if existing_batch:
                rec.batch_id = existing_batch.id
                existing_batch.harvest_ids = [(4, rec.id)]

        return records

    # --------------------------------------------------
    # الأزرار (تأكيد / إلغاء)
    # --------------------------------------------------
    def action_validate_harvest(self):
        """ينشئ حركة مخزون ويُنهي الحصاد."""
        for record in self:
            if record.state != "draft":
                raise UserError(_("يمكن التحقق من سجلات الحصاد في حالة المسودة فقط."))
            if not record.harvest_committee_ids:
                raise UserError(_("الرجاء تحديد أعضاء لجنة الحصاد."))
            if record.total_weight <= 0:
                raise ValidationError(
                    _("لا يمكن أن يكون إجمالي وزن الحصاد صفرًا أو سالبًا.")
                )

            source_location = self.env.ref("stock.stock_location_customers")
            warehouse_location = self.env.ref("stock.stock_location_stock")
            picking_type = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "internal"),
                    ("warehouse_id.company_id", "=", record.company_id.id),
                ],
                limit=1,
            )
            if not picking_type:
                raise UserError(_("لم يتم العثور على نوع نقل داخلي لشركتك."))

            product_harvested = self.env["product.product"].search(
                [
                    ("is_harvested_product", "=", True),
                    ("company_id", "in", (False, record.company_id.id)),
                ],
                limit=1,
            )
            if not product_harvested:
                raise UserError(
                    _(
                        "الرجاء تعريف منتج عام للأسماك المحصودة ووضع علامة 'منتج محصود' عليه."
                    )
                )

            picking_vals = {
                "picking_type_id": picking_type.id,
                "location_id": source_location.id,
                "location_dest_id": warehouse_location.id,
                "origin": record.name,
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": product_harvested.name,
                            "product_id": product_harvested.id,
                            "product_uom_qty": record.total_weight,
                            "product_uom": product_harvested.uom_id.id,
                            "location_id": source_location.id,
                            "location_dest_id": warehouse_location.id,
                            "state": "draft",
                            "reference": record.name,
                            "date": record.harvest_date,
                            "company_id": record.company_id.id,
                        },
                    )
                ],
                "company_id": record.company_id.id,
            }
            picking = self.env["stock.picking"].create(picking_vals)
            picking.action_confirm()
            picking.action_assign()
            picking.with_context(skip_immediate_validate=True).action_done()

            record.stock_picking_id = picking.id
            record.state = "done"
            record.pond_id.status = "idle"

            if record.batch_id:
                record.batch_id.end_date = record.harvest_date
                record.batch_id.final_quantity_kg = record.total_weight

            record.message_post(body=_("تم تأكيد سجل الحصاد وإنشاء حركة المخزون."))

    def action_cancel_harvest(self):
        """يلغي الحصاد ويعيد حالة الحوض إذا لزم."""
        for record in self:
            if record.state == "cancelled":
                continue
            # إذا كان هناك حركة مخزون مرتبطة يجب التعامل معها يدويًا
            record.state = "cancelled"
            if record.pond_id and record.pond_id.status == "harvesting":
                record.pond_id.status = "idle"
            record.message_post(body=_("تم إلغاء سجل الحصاد."))
