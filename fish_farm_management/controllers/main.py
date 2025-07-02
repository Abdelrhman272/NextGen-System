# -*- coding: utf-8 -*-
"""
Fish Farm Report Controller
----------------------------
Provides JSON endpoints for dashboard data and Excel exports.
"""

import base64
import io
import json
import logging
from datetime import datetime

import xlsxwriter
from odoo import http, fields, _
from odoo.http import request
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class FishFarmReportController(http.Controller):
    """
    Controller for Fish Farm dashboard and report export routes.
    """
    _name = 'fish_farm_management.report_controller'

    @http.route(
        '/fish_farm_management/dashboard_data',
        type='json', auth='user'
    )
    def get_dashboard_data(self):
        """
        Return dashboard data: KPIs, chart data, and recent alerts.
        """
        user = request.env.user
        company_id = user.company_id.id

        # KPIs
        active_ponds_count = request.env[
            'fish_farm_management.pond'
        ].search_count([
            ('status', '=', 'stocked'),
            ('company_id', '=', company_id)
        ])

        # Harvest weight this month
        start_month = date_utils.start_of(fields.Date.today(), 'month')
        end_month = date_utils.end_of(fields.Date.today(), 'month')
        harvest_recs = request.env[
            'fish_farm_management.harvest_record'
        ].search([
            ('harvest_date', '>=', start_month),
            ('harvest_date', '<=', end_month),
            ('state', '=', 'done'),
            ('company_id', '=', company_id)
        ])
        total_harvest_month = sum(harvest_recs.mapped('total_weight'))

        # Costs this month
        cost_recs = request.env[
            'fish_farm_management.pond_cost'
        ].search([
            ('cost_date', '>=', start_month),
            ('cost_date', '<=', end_month),
            ('state', '=', 'posted'),
            ('company_id', '=', company_id)
        ])
        total_costs_month = sum(cost_recs.mapped('amount'))

        # Feed consumed this month
        feed_recs = request.env[
            'fish_farm_management.pond_feeding'
        ].search([
            ('feeding_date', '>=', start_month),
            ('feeding_date', '<=', end_month),
            ('product_id.is_feed_type', '=', True),
            ('state', '=', 'done'),
            ('company_id', '=', company_id)
        ])
        total_feed_consumed_month = sum(feed_recs.mapped('quantity'))

        # Chart data
        cost_by_type_data = self._get_costs_by_type_data(company_id)
        harvest_by_month_data = self._get_harvest_by_month_data(company_id)
        pond_status_data = self._get_pond_status_data(company_id)

        # Recent water quality alerts
        recent_alerts = request.env[
            'fish_farm_management.water_quality_reading'
        ].search([
            ('is_alert', '=', True),
            (
                'reading_date', '>=',
                date_utils.subtract(fields.Datetime.now(), days=30)
            ),
            ('company_id', '=', company_id)
        ], limit=5, order='reading_date DESC')

        alerts_list = []
        for alert in recent_alerts:
            alerts_list.append({
                'pond_name': alert.pond_id.name,
                'reading_date': alert.reading_date.strftime(
                    '%Y-%m-%d %H:%M'
                ),
                'alert_reason': alert.alert_reason,
            })

        return {
            'kpis': {
                'active_ponds_count': active_ponds_count,
                'total_harvest_month': total_harvest_month,
                'total_costs_month': total_costs_month,
                'total_feed_consumed_month': total_feed_consumed_month,
            },
            'charts': {
                'cost_by_type': cost_by_type_data,
                'harvest_by_month': harvest_by_month_data,
                'pond_status_distribution': pond_status_data,
            },
            'recent_alerts': {
                'water_quality': alerts_list,
            }
        }

    def _get_costs_by_type_data(self, company_id):
        """
        Build bar chart data for costs by type for the last 6 months.
        """
        data, labels = [], []
        current_date = fields.Date.today()

        for i in range(6):
            month_start = date_utils.subtract(
                date_utils.start_of(current_date, 'month'),
                months=i
            )
            month_end = date_utils.end_of(month_start, 'month')
            costs = request.env[
                'fish_farm_management.pond_cost'
            ].read_group([
                ('cost_date', '>=', month_start),
                ('cost_date', '<=', month_end),
                ('state', '=', 'posted'),
                ('company_id', '=', company_id)
            ], fields=['amount', 'cost_type_id'],
               groupby=['cost_type_id'], orderby='cost_type_id')

            labels.append(month_start.strftime('%b %Y'))
            month_costs = {
                (grp['cost_type_id'][1] if grp['cost_type_id'] else _('غير محدد')):
                grp['amount'] for grp in costs
            }
            data.append(month_costs)

        cost_types = sorted({ct for month in data for ct in month})
        datasets = [{
            'label': ct,
            'data': [month.get(ct, 0.0) for month in data]
        } for ct in cost_types]

        return {
            'labels': list(reversed(labels)),
            'datasets': datasets,
        }

    def _get_harvest_by_month_data(self, company_id):
        """
        Build line chart data for harvest weight over the last 12 months.
        """
        labels, harvest_data = [], []
        current_date = fields.Date.today()

        for i in range(12):
            month_start = date_utils.subtract(
                date_utils.start_of(current_date, 'month'),
                months=i
            )
            month_end = date_utils.end_of(month_start, 'month')
            recs = request.env[
                'fish_farm_management.harvest_record'
            ].search([
                ('harvest_date', '>=', month_start),
                ('harvest_date', '<=', month_end),
                ('state', '=', 'done'),
                ('company_id', '=', company_id)
            ])
            labels.append(month_start.strftime('%b %Y'))
            harvest_data.append(sum(recs.mapped('total_weight')))

        return {
            'labels': list(reversed(labels)),
            'datasets': [{
                'label': _('إجمالي وزن الحصاد (كجم)'),
                'data': list(reversed(harvest_data)),
                'fill': False,
                'tension': 0.1
            }]
        }

    def _get_pond_status_data(self, company_id):
        """
        Build pie chart data for pond status distribution.
        """
        status_counts = request.env[
            'fish_farm_management.pond'
        ].read_group([
            ('company_id', '=', company_id)
        ], fields=['status'], groupby=['status'])

        labels, data, bg_colors = [], [], []
        status_colors = {
            'stocked': '#4CAF50', 'preparing': '#FFC107',
            'harvesting': '#FF9800', 'empty': '#9E9E9E',
            'idle': '#2196F3', 'cancelled': '#F44336'
        }

        for group in status_counts:
            code = group['status']
            name = dict(
                request.env['fish_farm_management.pond']
                ._fields['status'].selection
            ).get(code, code)
            labels.append(name)
            data.append(group['status_count'])
            bg_colors.append(status_colors.get(code, '#BDBDBD'))

        return {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': bg_colors,
                'hoverOffset': 4
            }]
        }
