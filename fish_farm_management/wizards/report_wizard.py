# -*- coding: utf-8 -*-

import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import date_utils


class FishFarmReportWizard(models.TransientModel):
    _name = "fish_farm_management.report_wizard"
    _description = "معالج توليد تقارير المزرعة السمكية"

    report_type = fields.Selection(
        [
            ("cost_analysis", "تقرير تحليل التكاليف"),
            ("harvest_performance", "تقرير أداء الحصاد والإنتاجية"),
            ("supplies_consumption", "تقرير استهلاك المستلزمات"),
            ("fish_health_water_quality", "تقرير صحة الأسماك وجودة المياه"),
            ("sales_profitability", "تقرير المبيعات والربحية"),
        ],
        string="نوع التقرير",
        required=True,
        default="cost_analysis",
    )

    report_type_display_name = fields.Char(
        string="اسم التقرير", compute="_compute_report_type_display_name"
    )

    @api.depends("report_type")
    def _compute_report_type_display_name(self):
        for rec in self:
            rec.report_type_display_name = dict(
                rec.fields["report_type"].selection
            ).get(rec.report_type, rec.report_type)

    date_from = fields.Date(string="من تاريخ", default=fields.Date.context_today)
    date_to = fields.Date(string="إلى تاريخ", default=fields.Date.context_today)

    # فلاتر عامة
    fish_farm_id = fields.Many2one("fish_farm_management.fish_farm", string="المزرعة")
    sector_id = fields.Many2one(
        "fish_farm_management.sector",
        string="القطاع",
        domain="[('fish_farm_id', '=', fish_farm_id)]",
    )
    slice_id = fields.Many2one(
        "fish_farm_management.slice",
        string="الشريحة",
        domain="[('sector_id', '=', sector_id)]",
    )
    pond_id = fields.Many2one(
        "fish_farm_management.pond",
        string="الحوض",
        domain="[('slice_id', '=', slice_id)]",
    )
    fish_type_id = fields.Many2one(
        "product.product", string="نوع السمك", domain="[('is_fish_type', '=', True)]"
    )

    # فلاتر خاصة بتقرير تحليل التكاليف
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="الحساب التحليلي",
    )

    # فلاتر خاصة بتقرير استهلاك المستلزمات
    product_category_id = fields.Many2one(
        "product.category",
        string="فئة المنتج",
    )
    supplier_id = fields.Many2one(
        "res.partner",
        string="المورد",
    )

    # فلاتر خاصة بتقرير صحة الأسماك وجودة المياه
    issue_type = fields.Selection(
        [
            ("disease", "مرض"),
            ("mortality", "وفيات"),
            ("injury", "إصابة"),
            ("other", "أخرى"),
        ],
        string="نوع المشكلة",
    )

    # فلاتر خاصة بتقرير المبيعات والربحية
    customer_id = fields.Many2one(
        "res.partner",
        string="العميل",
    )
    sales_channel = fields.Selection(
        [
            ("direct", "بيع مباشر"),
            ("agent", "وكيل"),
            ("pos", "نقطة بيع"),
            ("export", "تصدير"),
        ],
        string="قناة البيع",
    )

    def _prepare_report_filters(self):
        self.ensure_one()
        return {
            "date_from": (
                self.date_from.strftime("%Y-%m-%d") if self.date_from else False
            ),
            "date_to": self.date_to.strftime("%Y-%m-%d") if self.date_to else False,
            "fish_farm_id": self.fish_farm_id.id,
            "sector_id": self.sector_id.id,
            "slice_id": self.slice_id.id,
            "pond_id": self.pond_id.id,
            "fish_type_id": self.fish_type_id.id,
            "analytic_account_id": self.analytic_account_id.id,
            "product_category_id": self.product_category_id.id,
            "supplier_id": self.supplier_id.id,
            "issue_type": self.issue_type,
            "customer_id": self.customer_id.id,
            "sales_channel": self.sales_channel,
            "company_id": self.env.company.id,
        }

    def action_print_report_pdf(self):
        self.ensure_one()
        report_data_provider = self.env["fish_farm_management.report_data_provider"]

        filters = self._prepare_report_filters()

        report_data = {}
        report_name = ""

        if self.report_type == "cost_analysis":
            report_data = report_data_provider.get_cost_analysis_report_data(filters)
            report_name = "fish_farm_management.action_report_pond_cost_analysis"
        elif self.report_type == "harvest_performance":
            report_data = report_data_provider.get_harvest_performance_report_data(
                filters
            )
            report_name = "fish_farm_management.action_report_harvest_performance"
        elif self.report_type == "supplies_consumption":
            report_data = report_data_provider.get_supplies_consumption_report_data(
                filters
            )
            report_name = "fish_farm_management.action_report_supplies_consumption"
        elif self.report_type == "fish_health_water_quality":
            report_data = (
                report_data_provider.get_fish_health_water_quality_report_data(filters)
            )
            report_name = "fish_farm_management.action_report_fish_health_water_quality"
        elif self.report_type == "sales_profitability":
            report_data = report_data_provider.get_sales_profitability_report_data(
                filters
            )
            report_name = "fish_farm_management.action_report_sales_profitability"
        else:
            raise UserError(_("نوع التقرير غير مدعوم."))

        report_data["filters_display"] = {
            "date_range": f"{self.date_from or ''} - {self.date_to or ''}",
            "fish_farm": self.fish_farm_id.name,
            "sector": self.sector_id.name,
            "slice": self.slice_id.name,
            "pond": self.pond_id.name,
            "fish_type": self.fish_type_id.name,
            "analytic_account": self.analytic_account_id.name,
            "product_category": self.product_category_id.name,
            "supplier": self.supplier_id.name,
            "issue_type": (
                dict(self.fields["issue_type"].selection).get(self.issue_type, "")
                if self.issue_type
                else ""
            ),
            "customer": self.customer_id.name,
            "sales_channel": (
                dict(self.fields["sales_channel"].selection).get(self.sales_channel, "")
                if self.sales_channel
                else ""
            ),
        }
        report_data["company_name"] = self.env.company.name
        report_data["company_logo"] = (
            self.env.company.logo and self.env.company.logo.decode("utf-8") or False
        )
        report_data["currency_symbol"] = self.env.company.currency_id.symbol

        return self.env.ref(report_name).report_action(self, data=report_data)

    def action_export_report_excel(self):
        self.ensure_one()

        filters = self._prepare_report_filters()

        return {
            "type": "ir.actions.act_url",
            "url": f"/fish_farm_management/report/excel/{self.report_type}?filters={json.dumps(filters)}",
            "target": "new",
        }
