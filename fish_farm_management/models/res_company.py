# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    """
    This class inherits from res.company to add new fields.
    These fields will hold the default values for the fish_farm_management module,
    making them specific to each company in a multi-company environment.
    """
    _inherit = 'res.company'

    # The string attribute provides the label for the field in the UI.
    # The domain attribute helps filter the records shown in the dropdown.

    default_feed_product_id = fields.Many2one(
        'product.product',
        string='Default Feed Product',
        help="This product will be suggested by default in feeding operations."
    )

    default_medicine_product_id = fields.Many2one(
        'product.product',
        string='Default Medicine Product',
        help="This product will be suggested by default in treatment operations."
    )

    default_income_account_id = fields.Many2one(
        'account.account',
        string='Default Income Account',
        domain="[('user_type_id.type', '=', 'income')]",
        help="Default income account for fish sale revenues."
    )

    default_expense_account_id = fields.Many2one(
        'account.account',
        string='Default Expense Account',
        domain="[('user_type_id.type', '=', 'expense')]",
        help="Default expense account for farm operational costs."
    )
