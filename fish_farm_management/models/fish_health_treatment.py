# -*- coding: utf-8 -*-
# File: models/fish_health_treatment.py

from odoo import _, api, fields, models
from odoo.exceptions import UserError

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
        "uom.uom",
        string="وحدة القياس",
        related="medicine_id.uom_id",
        readonly=True,
    )
    quantity_used = fields.Float(
        string="الكمية المستخدمة", 
        help="الكمية الفعلية التي تم استهلاكها من المخزون."
    )
    treatment_notes = fields.Text(string="ملاحظات العلاج")
    stock_move_id = fields.Many2one(
        "stock.move",
        string="حركة المخزون",
        readonly=True,
        help="حركة المخزون التي تم إنشاؤها لاستهلاك الدواء.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.medicine_id and rec.quantity_used > 0:
                source_loc = rec.env.ref("stock.stock_location_stock")
                dest_loc = rec.env.ref("stock.stock_location_customers")
                picking_type = rec.env["stock.picking.type"].search(
                    [
                        ("code", "=", "internal"),
                        ("warehouse_id.company_id", "=", rec.health_record_id.company_id.id),
                    ],
                    limit=1,
                )
                if not picking_type:
                    raise UserError(_("لم يتم العثور على نوع نقل داخلي لشركتك."))
                move_vals = {
                    "name": _("علاج %s لحوض %s") % (
                        rec.medicine_id.name, rec.health_record_id.pond_id.name
                    ),
                    "product_id": rec.medicine_id.id,
                    "product_uom_qty": rec.quantity_used,
                    "product_uom": rec.product_uom_id.id,
                    "location_id": source_loc.id,
                    "location_dest_id": dest_loc.id,
                    "reference": rec.health_record_id.name,
                    "date": rec.treatment_date,
                    "company_id": rec.health_record_id.company_id.id,
                }
                move = rec.env["stock.move"].create(move_vals)
                move.action_confirm()
                move.action_assign()
                move.with_context(skip_immediate_validate=True).action_done()
                rec.stock_move_id = move.id
        return records

    def unlink(self):
        for rec in self:
            if rec.stock_move_id and rec.stock_move_id.state != "cancel":
                rec.stock_move_id.button_cancel()
        return super().unlink()
