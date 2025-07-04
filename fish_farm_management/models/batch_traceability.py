# -*- coding: utf-8 -*-
"""
Batch Traceability, Equipment, Fish Farm, Growth Measurement, Growth Model,
Health Record, Pond Cost, and Report Wizard models with docstrings and PEP8 fixes.
"""

# ----------------------------- batch_traceability.py -----------------------------
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils


class BatchTraceability(models.Model):
    """
    Tracks product batches: initial stocking to harvest, with metrics like FCR and
    survival rate.
    """

    _name = "fish_farm_management.batch_traceability"
    _description = "تتبع دفعة المنتج"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="رقم الدفعة",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True,
    )
    fish_type_id = fields.Many2one(
        "product.product",
        string="نوع السمك",
        required=True,
        domain="[('is_fish_type', '=', True)]",
        tracking=True,
    )
    pond_id = fields.Many2one(
        "fish_farm_management.pond",
        string="الحوض الأصلي",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    initial_quantity = fields.Float(
        string="الكمية الأولية (زريعة)",
        tracking=True,
    )
    start_date = fields.Date(
        string="تاريخ بدء الدفعة (إلقاء الزريعة)",
        required=True,
        tracking=True,
    )
    end_date = fields.Date(
        string="تاريخ انتهاء الدفعة (حصاد)",
        tracking=True,
        help="تاريخ آخر حصاد لهذه الدفعة.",
    )
    final_quantity_kg = fields.Float(
        string="الكمية النهائية (كجم)",
        tracking=True,
        help="إجمالي الوزن المنتج من هذه الدفعة.",
    )
    stocking_id = fields.Many2one(
        "fish_farm_management.fish_stocking",
        string="سجل إلقاء الزريعة",
        ondelete="restrict",
        help="الرابط بسجل الإلقاء الأصلي.",
    )
    harvest_ids = fields.One2many(
        "fish_farm_management.harvest_record",
        "batch_id",
        string="سجلات الحصاد",
    )
    sales_order_lines_ids = fields.Many2many(
        "sale.order.line",
        string="بنود أوامر البيع",
        compute="_compute_sales_data",
        store=False,
    )
    total_sales_qty = fields.Float(
        string="إجمالي الكمية المباعة (كجم)",
        compute="_compute_sales_data",
        store=False,
    )
    mortality_count = fields.Integer(
        string="إجمالي الوفيات",
        compute="_compute_batch_metrics",
        store=True,
    )
    fcr = fields.Float(
        string="معدل التحويل الغذائي (FCR)",
        compute="_compute_batch_metrics",
        store=True,
        digits=(16, 2),
    )
    survival_rate = fields.Float(
        string="معدل البقاء (%)",
        compute="_compute_batch_metrics",
        store=True,
        digits=(16, 2),
    )
    total_feed_consumed = fields.Float(
        string="إجمالي العلف (كجم)",
        compute="_compute_batch_metrics",
        store=True,
    )
    estimated_current_avg_weight_g = fields.Float(
        string="متوسط الوزن المقدر (جم)",
        compute="_compute_batch_metrics",
        store=True,
    )
    estimated_target_days_remaining = fields.Integer(
        string="الأيام المتبقية للهدف",
        compute="_compute_batch_metrics",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="الشركة",
        related="pond_id.company_id",
        store=True,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Assigns sequence number to new batches on creation.
        """
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fish_farm_management.batch_traceability"
                ) or _("New")
        return super().create(vals_list)

    @api.depends(
        "harvest_ids.total_weight",
        "pond_id.pond_feeding_ids.quantity",
        "pond_id.fish_health_ids.mortality_count",
        "start_date",
        "end_date",
        "fish_type_id",
        "stocking_id.quantity",
        "pond_id.fish_health_ids.record_date",
        "pond_id.pond_feeding_ids.feeding_date",
        "fish_type_id.fish_growth_model_ids.start_weight_g",
        "fish_type_id.fish_growth_model_ids.target_weight_g",
        "fish_type_id.fish_growth_model_ids.target_days",
        "pond_id.growth_measurement_ids.measurement_date",
        "pond_id.growth_measurement_ids.average_fish_weight_g",
    )
    def _compute_batch_metrics(self):
        """
        Calculates batch metrics such as mortality, FCR, and target days.
        """
        for batch in self:
            # Mortality count
            mortals = self.env["fish_farm_management.fish_health_record"].search(
                [
                    ("pond_id", "=", batch.pond_id.id),
                    ("record_date", ">=", batch.start_date),
                    ("record_date", "<=", batch.end_date or fields.Date.today()),
                    ("issue_type", "=", "mortality"),
                ]
            )
            batch.mortality_count = sum(rec.mortality_count for rec in mortals)
            # Feed consumed
            feeds = self.env["fish_farm_management.pond_feeding"].search(
                [
                    ("pond_id", "=", batch.pond_id.id),
                    ("feeding_date", ">=", batch.start_date),
                    ("feeding_date", "<=", batch.end_date or fields.Date.today()),
                    ("product_id.is_feed_type", "=", True),
                    ("state", "=", "done"),
                ]
            )
            batch.total_feed_consumed = sum(rec.quantity for rec in feeds)
            # Survival rate
            if batch.initial_quantity > 0:
                batch.survival_rate = (
                    (batch.initial_quantity - batch.mortality_count)
                    / batch.initial_quantity
                    * 100.0
                )
            else:
                batch.survival_rate = 0.0
            # FCR
            if batch.final_quantity_kg > 0:
                batch.fcr = batch.total_feed_consumed / batch.final_quantity_kg
            else:
                batch.fcr = 0.0
            # Estimated metrics
            est_weight = 0.0
            est_days = 0
            if batch.fish_type_id and batch.start_date:
                model = self.env["fish_farm_management.fish_growth_model"].search(
                    [
                        ("fish_type_id", "=", batch.fish_type_id.id),
                        ("company_id", "in", (False, batch.company_id.id)),
                    ],
                    limit=1,
                )
                if model:
                    days = (fields.Date.today() - batch.start_date).days
                    est_weight = model.get_estimated_weight_g(days)
                    if est_weight < model.target_weight_g:
                        rem = model.target_weight_g - est_weight
                        base = model.target_weight_g - model.start_weight_g
                        if base > 0:
                            est_days = int(rem / (base / model.target_days))
                else:
                    last = self.env[
                        "fish_farm_management.fish_growth_measurement"
                    ].search(
                        [
                            ("pond_id", "=", batch.pond_id.id),
                            ("fish_type_id", "=", batch.fish_type_id.id),
                            ("measurement_date", ">=", batch.start_date),
                            (
                                "measurement_date",
                                "<=",
                                batch.end_date or fields.Date.today(),
                            ),
                        ],
                        order="measurement_date DESC",
                        limit=1,
                    )
                    if last:
                        est_weight = last.average_fish_weight_g
            batch.estimated_current_avg_weight_g = est_weight
            batch.estimated_target_days_remaining = est_days

    @api.depends("harvest_ids.stock_picking_id.move_ids_without_package.sale_line_id")
    def _compute_sales_data(self):
        """
        Placeholder for computing sales linked to this batch.
        """
        for batch in self:
            sales = self.env["sale.order.line"]
            batch.sales_order_lines_ids = [(6, 0, sales.ids)]
            batch.total_sales_qty = 0.0

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        """
        Ensures start_date is before end_date if both are set.
        """
        for batch in self:
            if (
                batch.start_date
                and batch.end_date
                and (batch.start_date > batch.end_date)
            ):
                raise ValidationError(
                    _("تاريخ بدء الدفعة يجب أن يكون قبل تاريخ انتهائها.")
                )
