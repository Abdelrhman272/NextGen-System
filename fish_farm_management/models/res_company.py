# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    # الحقول الأصلية
    default_feed_product_id = fields.Many2one(
        "product.product",
        string="Default Feed Product",
        help="Product suggested by default in feeding operations."
    )
    default_medicine_product_id = fields.Many2one(
        "product.product",
        string="Default Medicine Product",
        help="Product suggested by default in treatment operations."
    )
    default_income_account_id = fields.Many2one(
        "account.account",
        string="Default Income Account",
        domain="[('user_type_id.type', '=', 'income')]",
        help="Default income account for fish sales."
    )
    default_expense_account_id = fields.Many2one(
        "account.account",
        string="Default Expense Account",
        domain="[('user_type_id.type', '=', 'expense')]",
        help="Default expense account for farm costs."
    )

    # حقول التوافق القديمة
    feed_product_id = fields.Many2one(
        "product.product",
        string="Feed Product (compatibility)",
        compute="_compute_feed_product_id",
        inverse="_inverse_feed_product_id",
        store=True
    )
    medicine_product_id = fields.Many2one(
        "product.product",
        string="Medicine Product (compatibility)",
        compute="_compute_medicine_product_id",
        inverse="_inverse_medicine_product_id",
        store=True
    )
    income_account_id = fields.Many2one(
        "account.account",
        string="Income Account (compatibility)",
        compute="_compute_income_account_id",
        inverse="_inverse_income_account_id",
        store=True
    )
    expense_account_id = fields.Many2one(
        "account.account",
        string="Expense Account (compatibility)",
        compute="_compute_expense_account_id",
        inverse="_inverse_expense_account_id",
        store=True
    )

    # ───────────────
    # Feed Product
    # ───────────────
    @api.depends("default_feed_product_id")
    def _compute_feed_product_id(self):
        for rec in self:
            rec.feed_product_id = rec.default_feed_product_id

    def _inverse_feed_product_id(self):
        for rec in self:
            rec.default_feed_product_id = rec.feed_product_id

    # ───────────────
    # Medicine Product
    # ───────────────
    @api.depends("default_medicine_product_id")
    def _compute_medicine_product_id(self):
        for rec in self:
            rec.medicine_product_id = rec.default_medicine_product_id

    def _inverse_medicine_product_id(self):
        for rec in self:
            rec.default_medicine_product_id = rec.medicine_product_id

    # ───────────────
    # Income Account
    # ───────────────
    @api.depends("default_income_account_id")
    def _compute_income_account_id(self):
        for rec in self:
            rec.income_account_id = rec.default_income_account_id

    def _inverse_income_account_id(self):
        for rec in self:
            rec.default_income_account_id = rec.income_account_id

    # ───────────────
    # Expense Account
    # ───────────────
    @api.depends("default_expense_account_id")
    def _compute_expense_account_id(self):
        for rec in self:
            rec.expense_account_id = rec.default_expense_account_id

    def _inverse_expense_account_id(self):
        for rec in self:
            rec.default_expense_account_id = rec.expense_account_id
