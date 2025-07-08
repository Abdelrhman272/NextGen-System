# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HarvestSorting(models.Model):
    _name = "fish_farm_management.harvest_sorting"
    _description = "فرز الحصاد"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # --------------------------------------------------
    # الحقول
    # --------------------------------------------------
    name = fields.Char(
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True,
    )
    harvest_record_id = fields.Many2one(
        "fish_farm_management.harvest_record",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    sorting_date = fields.Date(
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    input_weight = fields.Float(required=True, tracking=True)

    sorting_line_ids = fields.One2many(
        "fish_farm_management.harvest_sorting_line",
        "sorting_id",
        string="تفاصيل الفرز",
    )
    stock_picking_ids = fields.Many2many(
        "stock.picking",
        compute="_compute_stock_pickings",
        store=False,
    )
    scheduled_date = fields.Datetime(
        string="تاريخ الجدولة",
        compute='_compute_scheduled_date',
        store=False,
        readonly=True,
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
    company_id = fields.Many2one(
        "res.company",
        related="harvest_record_id.company_id",
        store=True,
        readonly=True,
    )

    # --------------------------------------------------
    # حساب الحركات
    # --------------------------------------------------
    @api.depends("name")
    def _compute_stock_pickings(self):
        for rec in self:
            rec.stock_picking_ids = self.env["stock.picking"].search(
                [("origin", "like", f"{rec.name}%"), ("company_id", "=", rec.company_id.id)]
            )
    @api.depends('name')
    def _compute_stock_pickings(self):
        for rec in self:
            rec.stock_picking_ids = self.env['stock.picking'].search([
                ('origin', 'like', f"{rec.name}%"),
                ('company_id', '=', rec.company_id.id)
            ])

    # --------------------------------------------------
    # إنشاء السجل
    # --------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fish_farm_management.harvest_sorting"
            ) or _("New")
        return super().create(vals)

    # --------------------------------------------------
    # تأكيد / إلغاء
    # --------------------------------------------------
    def action_validate_sorting(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("يمكن التحقق من عمليات الفرز في حالة المسودة فقط."))
            if not record.sorting_line_ids:
                raise ValidationError(_("الرجاء إضافة تفاصيل الفرز."))
            if record.input_weight <= 0:
                raise ValidationError(_("الوزن المدخل للفرز يجب أن يكون أكبر من صفر."))

            total_output_weight = sum(line.sorted_weight for line in record.sorting_line_ids)
            if abs(total_output_weight - record.input_weight) > 0.05:
                raise ValidationError(
                    _("إجمالي الوزن المفرز (%.2f كجم) لا يتطابق مع الوزن المدخل (%.2f كجم).")
                    % (total_output_weight, record.input_weight)
                )

            source_location = self.env.ref("stock.stock_location_stock")
            picking_type = self.env["stock.picking.type"].search(
                [("code", "=", "internal"), ("warehouse_id.company_id", "=", record.company_id.id)],
                limit=1,
            )
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
                moves.append(
                    (
                        0,
                        0,
                        {
                            "name": _("فرز حصاد %s: %s") % (record.harvest_record_id.name, line.product_id.name),
                            "product_id": line.product_id.id,
                            "product_uom_qty": line.sorted_weight,
                            "product_uom": line.product_uom_id.id,
                            "location_id": source_location.id,
                            "location_dest_id": line.destination_location_id.id,
                            "state": "draft",
                            "reference": record.name,
                            "date": record.sorting_date,
                            "company_id": record.company_id.id,
                        },
                    )
                )

            if moves:
                picking_vals = {
                    "picking_type_id": picking_type.id,
                    "location_id": source_location.id,
                    "location_dest_id": source_location.id,
                    "origin": record.name,
                    "move_ids_without_package": moves,
                    "company_id": record.company_id.id,
                }
                picking = self.env["stock.picking"].create(picking_vals)
                picking.action_confirm()
                picking.action_assign()
                picking.with_context(skip_immediate_validate=True).action_done()

            record.state = "done"
            record.message_post(body=_("تم تأكيد عملية الفرز وإنشاء حركات المخزون."))

    def action_cancel_sorting(self):
        """إلغاء الفرز ببساطة يغير الحالة ولا ينشئ حركات متعاكسة تلقائيًا."""
        for rec in self:
            if rec.state == "cancelled":
                continue
            rec.state = "cancelled"
            rec.message_post(body=_("تم إلغاء عملية الفرز."))
