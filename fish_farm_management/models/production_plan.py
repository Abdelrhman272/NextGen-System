# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductionPlan(models.Model):
    _name = "fish_farm_management.production_plan"
    _description = "خطة الإنتاج"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="المرجع",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True,
    )
    plan_date = fields.Date(
        string="تاريخ الخطة",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )

    pond_id = fields.Many2one(
        "fish_farm_management.pond",
        string="الحوض المستهدف",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    fish_type_id = fields.Many2one(
        "product.product",
        string="نوع السمك المخطط",
        required=True,
        domain="[('is_fish_type', '=', True)]",
        tracking=True,
    )

    planned_stocking_date = fields.Date(
        string="تاريخ إلقاء الزريعة المخطط", required=True, tracking=True
    )
    planned_stocking_quantity = fields.Float(
        string="كمية الزريعة المخططة", required=True, tracking=True
    )

    planned_harvest_date = fields.Date(
        string="تاريخ الحصاد المخطط", required=True, tracking=True
    )
    planned_harvest_weight = fields.Float(
        string="الوزن المستهدف عند الحصاد (كجم)", tracking=True
    )

    responsible_employee_id = fields.Many2one(
        "hr.employee", string="المسؤول عن الخطة", ondelete="set null"
    )
    notes = fields.Text(string="ملاحظات")
    state = fields.Selection(
        [
            ("draft", "مسودة"),
            ("confirmed", "مؤكدة"),
            ("in_progress", "قيد التنفيذ"),
            ("completed", "مكتملة"),
            ("cancelled", "ملغاة"),
        ],
        string="الحالة",
        default="draft",
        required=True,
        tracking=True,
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
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fish_farm_management.production_plan"
            ) or _("New")
        res = super(ProductionPlan, self).create(vals_list)
        return res

    @api.constrains("planned_stocking_date", "planned_harvest_date")
    def _check_dates(self):
        for plan in self:
            if (
                plan.planned_stocking_date
                and plan.planned_harvest_date
                and plan.planned_stocking_date > plan.planned_harvest_date
            ):
                raise ValidationError(
                    _("تاريخ إلقاء الزريعة المخطط يجب أن يكون قبل تاريخ الحصاد المخطط.")
                )

    def action_confirm_plan(self):
        for record in self:
            if record.state == "draft":
                record.state = "confirmed"
                record.message_post(body=_("تم تأكيد خطة الإنتاج."))

    def action_start_production(self):
        for record in self:
            if record.state == "confirmed":
                record.state = "in_progress"
                record.message_post(body=_("بدء تنفيذ خطة الإنتاج."))

    def action_complete_plan(self):
        for record in self:
            if record.state == "in_progress":
                record.state = "completed"
                record.message_post(body=_("تم اكتمال خطة الإنتاج."))

    def action_cancel_plan(self):
        for record in self:
            if record.state not in ("completed", "cancelled"):
                record.state = "cancelled"
                record.message_post(body=_("تم إلغاء خطة الإنتاج."))
