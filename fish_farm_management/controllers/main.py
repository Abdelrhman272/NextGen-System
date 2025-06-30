# -*- coding: utf-8 -*-

import io
import json
from datetime import datetime
import base64

import xlsxwriter
from odoo import http
from odoo.http import request, content_disposition
import logging

_logger = logging.getLogger(__name__)

class FishFarmReportController(http.Controller):
    _name = 'fish_farm_management.report_controller'

    # ... (existing export_excel_report function) ...

    @http.route('/fish_farm_management/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self):
        """
        Fetches data for the custom Fish Farm Management dashboard.
        """
        user = request.env.user
        company_id = user.company_id.id

        # 1. KPIs (Key Performance Indicators)
        # Total active ponds
        active_ponds_count = request.env['fish_farm_management.pond'].search_count([
            ('status', '=', 'stocked'),
            ('company_id', '=', company_id)
        ])

        # Total harvest weight this month
        current_month_start = date_utils.start_of(fields.Date.today(), 'month')
        current_month_end = date_utils.end_of(fields.Date.today(), 'month')
        total_harvest_month = sum(request.env['fish_farm_management.harvest_record'].search([
            ('harvest_date', '>=', current_month_start),
            ('harvest_date', '<=', current_month_end),
            ('state', '=', 'done'),
            ('company_id', '=', company_id)
        ]).mapped('total_weight'))

        # Total costs this month
        total_costs_month = sum(request.env['fish_farm_management.pond_cost'].search([
            ('cost_date', '>=', current_month_start),
            ('cost_date', '<=', current_month_end),
            ('state', '=', 'posted'),
            ('company_id', '=', company_id)
        ]).mapped('amount'))

        # Total feed consumed this month
        total_feed_consumed_month = sum(request.env['fish_farm_management.pond_feeding'].search([
            ('feeding_date', '>=', current_month_start),
            ('feeding_date', '<=', current_month_end),
            ('product_id.is_feed_type', '=', True),
            ('state', '=', 'done'),
            ('company_id', '=', company_id)
        ]).mapped('quantity'))

        # 2. Charts Data
        # Costs by Type (Bar Chart) - Last 6 months
        cost_by_type_data = self._get_costs_by_type_data(company_id)

        # Harvest Production by Month (Line Chart) - Last 12 months
        harvest_by_month_data = self._get_harvest_by_month_data(company_id)

        # Pond Status Distribution (Pie Chart)
        pond_status_data = self._get_pond_status_data(company_id)
        
        # Water Quality Alerts (Table/List of recent alerts)
        recent_water_alerts = request.env['fish_farm_management.water_quality_reading'].search([
            ('is_alert', '=', True),
            ('reading_date', '>=', date_utils.subtract(fields.Datetime.now(), days=30)),
            ('company_id', '=', company_id)
        ], limit=5, order='reading_date DESC')
        
        water_alerts_list = []
        for alert in recent_water_alerts:
            water_alerts_list.append({
                'pond_name': alert.pond_id.name,
                'reading_date': alert.reading_date.strftime('%Y-%m-%d %H:%M'),
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
                'water_quality': water_alerts_list,
            }
        }

    def _get_costs_by_type_data(self, company_id):
        # Data for costs by type for a bar chart
        data = []
        labels = []
        current_date = fields.Date.today()
        # Get costs for last 6 months
        for i in range(6):
            month_start = date_utils.subtract(date_utils.start_of(current_date, 'month'), months=i)
            month_end = date_utils.end_of(month_start, 'month')
            
            costs = request.env['fish_farm_management.pond_cost'].read_group([
                ('cost_date', '>=', month_start),
                ('cost_date', '<=', month_end),
                ('state', '=', 'posted'),
                ('company_id', '=', company_id)
            ], fields=['amount', 'cost_type_id'], groupby=['cost_type_id'], orderby='cost_type_id')

            month_label = month_start.strftime('%b %Y') # e.g., Jun 2025
            labels.append(month_label)
            
            month_costs = {}
            for cost_group in costs:
                cost_type_name = cost_group['cost_type_id'][1] if cost_group['cost_type_id'] else _('غير محدد')
                month_costs[cost_type_name] = cost_group['amount']
            data.append(month_costs)
        
        # Reformat for Chart.js (datasets by cost type)
        cost_types = sorted(list(set(cost_type for month_data in data for cost_type in month_data.keys())))
        
        datasets = []
        for cost_type in cost_types:
            datasets.append({
                'label': cost_type,
                'data': [month_data.get(cost_type, 0.0) for month_data in data],
                # 'backgroundColor': '...' # You can define colors here
            })
        
        return {
            'labels': list(reversed(labels)), # Show recent month last
            'datasets': datasets,
        }

    def _get_harvest_by_month_data(self, company_id):
        # Data for harvest production by month for a line chart
        labels = []
        harvest_data = []
        current_date = fields.Date.today()

        for i in range(12): # Last 12 months
            month_start = date_utils.subtract(date_utils.start_of(current_date, 'month'), months=i)
            month_end = date_utils.end_of(month_start, 'month')
            
            total_weight = sum(request.env['fish_farm_management.harvest_record'].search([
                ('harvest_date', '>=', month_start),
                ('harvest_date', '<=', month_end),
                ('state', '=', 'done'),
                ('company_id', '=', company_id)
            ]).mapped('total_weight'))
            
            labels.append(month_start.strftime('%b %Y'))
            harvest_data.append(total_weight)
        
        return {
            'labels': list(reversed(labels)),
            'datasets': [{
                'label': _('إجمالي وزن الحصاد (كجم)'),
                'data': list(reversed(harvest_data)),
                'fill': False,
                'borderColor': 'rgb(75, 192, 192)',
                'tension': 0.1
            }]
        }

    def _get_pond_status_data(self, company_id):
        # Data for pond status distribution for a pie chart
        status_counts = request.env['fish_farm_management.pond'].read_group([
            ('company_id', '=', company_id)
        ], fields=['status'], groupby=['status'])
        
        labels = []
        data = []
        background_colors = []
        
        status_colors = {
            'stocked': '#4CAF50',    # Green
            'preparing': '#FFC107',  # Amber
            'harvesting': '#FF9800', # Orange
            'empty': '#9E9E9E',      # Grey
            'idle': '#2196F3',       # Blue
            'cancelled': '#F44336',  # Red (if applicable, though statusbar does not show cancelled for pond directly)
        }

        for status_group in status_counts:
            status_code = status_group['status']
            status_display_name = dict(request.env['fish_farm_management.pond']._fields['status'].selection).get(status_code, status_code)
            
            labels.append(status_display_name)
            data.append(status_group['status_count'])
            background_colors.append(status_colors.get(status_code, '#BDBDBD')) # Default light grey

        return {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': background_colors,
                'hoverOffset': 4
            }]
        }