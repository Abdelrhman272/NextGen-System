# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    # الحقول التى أضفتها سابقًا
    default_feed_product_id = fields.Many2one(
        'product.product',
        string='Default Feed Product',
        help="This product will be suggested by default in feeding operations."
    )
    default_medicine_product_id = fields.Many2one(
        'product.product',
        string='Default Medicine Product',
    )
    default_income_account_id = fields.Many2one(
        'account.account',
        string='Default Income Account',
        domain="[('user_type_id.type', '=', 'income')]",
    )
    default_expense_account_id = fields.Many2one(
        'account.account',
        string='Default Expense Account',
        domain="[('user_type_id.type', '=', 'expense')]",
    )

    # ⬅️⬅️⬅️  **أضف السطر التالى**  ⬅️⬅️⬅️
    # حقل توافقى ليُرضى اختبارات Enterprise القديمة.
    # related يجعل قيمته هى نفس قيمة default_feed_product_id.
    feed_product_id = fields.Many2one(
        'product.product',
        string='Feed Product (compatibility)',
        related='default_feed_product_id',
        readonly=False,
        store=True,
        help="Deprecated field kept for compatibility with Enterprise tests."
    )
