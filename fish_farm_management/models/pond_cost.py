# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PondCost(models.Model):
    _name = "fish_farm_management.pond_cost"
    _description = "إدخال تكلفة الحوض"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="المرجع",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True,
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="الحساب التحليلي",
        required=True,
        ondelete="restrict",
        help="الحساب التحليلي لتصنيف التكلفة.",
        tracking=True,
    )
    pond_id = fields.Many2one(
        "fish_farm_management.pond",
        string="الحوض",
        related="analytic_account_id.fish_farm_management_pond_id",
        store=True,
        readonly=True,
    )
    cost_date = fields.Date(
        string="تاريخ التكلفة",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    amount = fields.Monetary(
        string="المبلغ",
        required=True,
        tracking=True,
        currency_field="company_currency_id",
    )
    company_id = fields.Many2one(
        "res.company",
        string="الشركة",
        related="analytic_account_id.company_id",
        store=True,
        readonly=True,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id", string="عملة الشركة", readonly=True
    )
    description = fields.Text(string="الوصف")
    is_direct_cost = fields.Boolean(string="تكلفة مباشرة", default=True, tracking=True)
    purchase_order_id = fields.Many2one(
        "purchase.order", string="أمر الشراء ذو الصلة", readonly=True
    )
    expense_sheet_id = fields.Many2one(
        "hr.expense.sheet", string="كشف المصروفات ذو الصلة", readonly=True
    )
    employee_id = fields.Many2one(
        "hr.employee", string="الموظف ذو صلة", ondelete="set null"
    )
    account_move_id = fields.Many2one(
        "account.move", string="قيد المحاسبة", readonly=True, copy=False
    )
    state = fields.Selection(
        [("draft", "مسودة"), ("posted", "مرحل"), ("cancelled", "ملغاة")],
        string="الحالة",
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fish_farm_management.pond_cost"
                ) or _("New")
        return super(PondCost, self).create(vals_list)

    def action_post_cost(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("يمكن ترحيل التكلفة من حالة المسودة فقط."))
            if record.amount <= 0:
                raise ValidationError(_("مبلغ التكلفة يجب أن يكون أكبر من صفر."))
            journal = self.env["account.journal"].search(
                [("type", "=", "general"), ("company_id", "=", record.company_id.id)],
                limit=1,
            )
            if not journal:
                raise UserError(_("لم يتم العثور على دفتر يومية عام لشركتك."))
            expense_account = self.env["account.account"].search(
                [("code", "=", "600000"), ("company_id", "=", record.company_id.id)],
                limit=1,
            )
            credit_account = self.env["account.account"].search(
                [("code", "=", "201000"), ("company_id", "=", record.company_id.id)],
                limit=1,
            )
            if not expense_account or not credit_account:
                raise UserError(
                    _("الرجاء التأكد من تعريف حسابات المصروفات والدائن.")
                )
            move_lines = [
                (
                    0,
                    0,
                    {
                        "name": _("تكلفة حوض %s: %s")
                        % (record.pond_id.name, record.analytic_account_id.name),
                        "account_id": expense_account.id,
                        "debit": record.amount,
                        "credit": 0,
                        "analytic_account_id": record.analytic_account_id.id,
                        "partner_id": record.employee_id.address_home_id.partner_id.id
                        if record.employee_id and record.is_direct_cost
                        else False,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": _("دفع/استحقاق تكلفة حوض %s: %s")
                        % (record.pond_id.name, record.analytic_account_id.name),
                        "account_id": credit_account.id,
                        "debit": 0,
                        "credit": record.amount,
                        "partner_id": record.employee_id.address_home_id.partner_id.id
                        if record.employee_id and record.is_direct_cost
                        else False,
                    },
                ),
            ]
            move_vals = {
                "journal_id": journal.id,
                "date": record.cost_date,
                "ref": record.name,
                "line_ids": move_lines,
                "move_type": "entry",
                "company_id": record.company_id.id,
            }
            account_move = self.env["account.move"].create(move_vals)
            account_move.action_post()
            record.account_move_id = account_move.id
            record.state = "posted"
            record.message_post(body=_("تم ترحيل قيد التكلفة بنجاح."))

    def action_cancel_cost(self):
        """إلغاء السجل."""
        for rec in self:
            if rec.state == "cancelled":
                raise UserError(_("السجل ملغى بالفعل."))
            rec.state = "cancelled"
            rec.message_post(body=_("تم إلغاء تكلفة الحوض."))