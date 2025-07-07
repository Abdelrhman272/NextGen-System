# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class FishHealthTreatment(models.Model):
    _name = "fish_farm_management.fish_health_treatment"
    _description = "تفاصيل العلاج الصحي للأسماك"

    health_record_id = fields.Many2one(
        "fish_farm_management.fish_health_record",
        string="سجل الصحة",
        required=True,
        ondelete="cascade",
    )
    treatment_date = fields.Date(
        string="تاريخ العلاج", required=True, default=fields.Date.context_today
    )
    medicine_id = fields.Many2one(
        "product.product",
        string="الدواء المستخدم",
        required=True,
        domain="[('is_medicine_type', '=', True)]",
    )
    dosage = fields.Char(string="الجرعة/الكمية")
    product_uom_id = fields.Many2one(
        "uom.uom", string="وحدة القياس", related="medicine_id.uom_id", readonly=True
    )
    quantity_used = fields.Float(
        string="الكمية المستخدمة (المخزنية)",
        help="الكمية الفعلية التي تم استهلاكها من المخزون.",
    )
    treatment_notes = fields.Text(string="ملاحظات العلاج")
    stock_move_id = fields.Many2one(
        "stock.move",
        string="حركة المخزون",
        readonly=True,
        help="حركة المخزون التي تم إنشاؤها لاستهلاك الدواء.",
    )

    @api.model
    def create(self, vals_list):
        records = super(FishHealthTreatment, self).create(vals_list)
        for res in records:
            # إنشاء حركة مخزون لاستهلاك الدواء
            if res.medicine_id and res.quantity_used > 0:
                source_location = res.env.ref("stock.stock_location_stock")
                # تأكد أن res.health_record_id موجود قبل الوصول إلى company_id
                company_id = (
                    res.health_record_id.company_id.id
                    if res.health_record_id
                    else self.env.company.id
                )

                consumption_location = res.env.ref(
                    "stock.stock_location_customers"
                )  # موقع افتراضي للاستهلاك
                picking_type = res.env["stock.picking.type"].search(
                    [
                        ("code", "=", "internal"),
                        ("warehouse_id.company_id", "=", company_id),
                    ],
                    limit=1,
                )
                if not picking_type:
                    raise UserError(_("لم يتم العثور على نوع نقل داخلي لشركتك."))

                move_vals = {
                    "name": _(
                        "علاج %s لحوض %s"
                    ) % (
                        rec.medicine_id.name,
                        rec.health_record_id.pond_id.name,
                    ),
                    "product_id": res.medicine_id.id,
                    "product_uom_qty": res.quantity_used,
                    "product_uom": res.product_uom_id.id,
                    "location_id": source_location.id,
                    "location_dest_id": consumption_location.id,
                    "state": "draft",
                    "reference": (
                        res.health_record_id.name if res.health_record_id else ""
                    ),
                    "date": res.treatment_date,
                    "company_id": company_id,
                }
                stock_move = res.env["stock.move"].create(move_vals)
                stock_move.action_confirm()
                stock_move.action_assign()
                stock_move.with_context(skip_immediate_validate=True).action_done()
                res.stock_move_id = stock_move.id
        return records

    def unlink(self):
        for rec in self:
            if rec.stock_move_id and rec.stock_move_id.state != "cancel":
                rec.stock_move_id.button_cancel()  # إلغاء حركة المخزون عند حذف العلاج
        return super(FishHealthTreatment, self).unlink()
