# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.tools import date_utils
import logging

_logger = logging.getLogger(__name__)

class FishFarmReportDataProvider(models.AbstractModel):
    _name = 'fish_farm_management.report_data_provider'
    _description = 'مزود بيانات تقارير المزرعة السمكية'

    def _get_base_domain(self, filters):
        domain = []
        if filters.get('date_from'):
            domain.append(('create_date', '>=', filters['date_from'] + ' 00:00:00')) # Assuming create_date is datetime
        if filters.get('date_to'):
            domain.append(('create_date', '<=', filters['date_to'] + ' 23:59:59'))
        if filters.get('pond_id'):
            domain.append(('pond_id', '=', filters['pond_id']))
        elif filters.get('slice_id'):
            domain.append(('pond_id.slice_id', '=', filters['slice_id']))
        elif filters.get('sector_id'):
            domain.append(('pond_id.sector_id', '=', filters['sector_id']))
        elif filters.get('fish_farm_id'):
            domain.append(('pond_id.fish_farm_id', '=', filters['fish_farm_id']))
        
        domain.append(('company_id', '=', filters.get('company_id') or self.env.company.id))
        return domain

    def get_cost_analysis_report_data(self, filters):
        domain = self._get_base_domain(filters)
        if filters.get('cost_type_id'):
            domain.append(('cost_type_id', '=', filters['cost_type_id']))
        
        costs = self.env['fish_farm_management.pond_cost'].search(domain)
        
        report_lines = []
        total_amount = 0.0
        
        # Group by pond and cost type
        grouped_costs = {}
        for cost in costs:
            pond_name = cost.pond_id.name if cost.pond_id else _('غير محدد')
            cost_type_name = cost.cost_type_id.name if cost.cost_type_id else _('غير محدد')
            
            if pond_name not in grouped_costs:
                grouped_costs[pond_name] = {}
            
            if cost_type_name not in grouped_costs[pond_name]:
                grouped_costs[pond_name][cost_type_name] = 0.0
            
            grouped_costs[pond_name][cost_type_name] += cost.amount
            total_amount += cost.amount
        
        for pond, types in grouped_costs.items():
            for cost_type, amount in types.items():
                report_lines.append({
                    'pond_name': pond,
                    'cost_type_name': cost_type,
                    'amount': amount,
                })
        
        return {
            'title': _('تقرير تحليل تكاليف الأحواض'),
            'header': [_('الحوض'), _('نوع التكلفة'), _('المبلغ')],
            'lines': report_lines,
            'total_amount': total_amount,
            'filters': filters,
        }

    def get_harvest_performance_report_data(self, filters):
        domain = self._get_base_domain(filters)
        if filters.get('fish_type_id'):
            domain.append(('fish_type_id', '=', filters['fish_type_id'])) # Assuming fish_type_id on harvest_record for main fish type
        
        harvests = self.env['fish_farm_management.harvest_record'].search(domain)
        
        report_lines = []
        total_harvest_weight = 0.0
        
        for harvest in harvests:
            fcr = harvest.batch_id.fcr if harvest.batch_id else 0.0
            survival_rate = harvest.batch_id.survival_rate if harvest.batch_id else 0.0

            report_lines.append({
                'name': harvest.name,
                'pond_name': harvest.pond_id.name,
                'fish_type_name': harvest.fish_type_id.name if harvest.fish_type_id else '',
                'harvest_date': harvest.harvest_date,
                'total_weight': harvest.total_weight,
                'fcr': fcr,
                'survival_rate': survival_rate,
            })
            total_harvest_weight += harvest.total_weight
            
        return {
            'title': _('تقرير أداء الحصاد والإنتاجية'),
            'header': [_('المرجع'), _('الحوض'), _('نوع السمك'), _('التاريخ'), _('الوزن (كجم)'), _('FCR'), _('معدل البقاء (%)')],
            'lines': report_lines,
            'total_harvest_weight': total_harvest_weight,
            'filters': filters,
        }

    def get_supplies_consumption_report_data(self, filters):
        domain = self._get_base_domain(filters)
        if filters.get('product_category_id'):
            domain.append(('product_id.categ_id', '=', filters['product_category_id']))
        if filters.get('supplier_id'):
            domain.append(('purchase_order_id.partner_id', '=', filters['supplier_id']))
        
        consumptions = self.env['fish_farm_management.pond_feeding'].search(domain)
        
        report_lines = []
        total_quantity_consumed = 0.0
        
        for consump in consumptions:
            report_lines.append({
                'name': consump.name,
                'pond_name': consump.pond_id.name,
                'feeding_date': consump.feeding_date,
                'product_name': consump.product_id.name,
                'quantity': consump.quantity,
                'uom_name': consump.product_uom_id.name,
                'supplier_name': consump.purchase_order_id.partner_id.name if consump.purchase_order_id else '',
            })
            total_quantity_consumed += consump.quantity # Summing up quantities regardless of UOM for total, be careful here
            
        return {
            'title': _('تقرير استهلاك المستلزمات'),
            'header': [_('المرجع'), _('الحوض'), _('التاريخ'), _('المنتج'), _('الكمية'), _('الوحدة'), _('المورد')],
            'lines': report_lines,
            'total_quantity_consumed': total_quantity_consumed,
            'filters': filters,
        }

    def get_fish_health_water_quality_report_data(self, filters):
        health_domain = self._get_base_domain(filters)
        water_domain = self._get_base_domain(filters)

        if filters.get('issue_type'):
            health_domain.append(('issue_type', '=', filters['issue_type']))
        
        health_records = self.env['fish_farm_management.fish_health_record'].search(health_domain)
        water_readings = self.env['fish_farm_management.water_quality_reading'].search(water_domain)

        health_lines = []
        for rec in health_records:
            health_lines.append({
                'name': rec.name,
                'pond_name': rec.pond_id.name,
                'record_date': rec.record_date,
                'issue_type': dict(rec.fields['issue_type'].selection).get(rec.issue_type, ''),
                'disease_name': rec.disease_name,
                'mortality_count': rec.mortality_count,
            })
        
        water_lines = []
        for rec in water_readings:
            water_lines.append({
                'name': rec.name,
                'pond_name': rec.pond_id.name,
                'reading_date': rec.reading_date,
                'ph': rec.ph,
                'oxygen_level': rec.oxygen_level,
                'temperature': rec.temperature,
                'ammonia': rec.ammonia,
                'is_alert': _('نعم') if rec.is_alert else _('لا'),
                'alert_reason': rec.alert_reason,
            })

        return {
            'title': _('تقرير صحة الأسماك وجودة المياه'),
            'health_header': [_('المرجع'), _('الحوض'), _('التاريخ'), _('نوع المشكلة'), _('المرض/المشكلة'), _('الوفيات')],
            'health_lines': health_lines,
            'water_header': [_('المرجع'), _('الحوض'), _('التاريخ'), _('pH'), _('أكسجين (ملجم/لتر)'), _('حرارة (مئوية)'), _('أمونيا'), _('تنبيه'), _('سبب التنبيه')],
            'water_lines': water_lines,
            'filters': filters,
        }

    def get_sales_profitability_report_data(self, filters):
        # This report requires more complex logic to link sales to harvested batches
        # and calculate profitability. Assuming sale.order and sale.order.line are used.

        sale_domain = []
        if filters.get('date_from'):
            sale_domain.append(('date_order', '>=', filters['date_from'] + ' 00:00:00'))
        if filters.get('date_to'):
            sale_domain.append(('date_order', '<=', filters['date_to'] + ' 23:59:59'))
        if filters.get('customer_id'):
            sale_domain.append(('partner_id', '=', filters['customer_id']))
        if filters.get('sales_channel'):
            # This requires a 'sales_channel' field on sale.order or custom logic
            # sale_domain.append(('sales_channel', '=', filters['sales_channel']))
            pass # Placeholder
        
        # Filter sales for products originating from fish farm (e.g., is_harvested_product)
        sale_domain.append(('order_line.product_id.is_harvested_product', '=', True))
        sale_domain.append(('company_id', '=', filters.get('company_id') or self.env.company.id))

        sales_orders = self.env['sale.order'].search(sale_domain)
        
        report_lines = []
        total_sales_value = 0.0
        total_profit = 0.0

        for order in sales_orders:
            for line in order.order_line.filtered(lambda l: l.product_id.is_harvested_product):
                # Calculate cost of goods sold for profitability (simple example)
                # In real scenario, COGS would come from stock valuation or specific cost methods
                cogs = line.product_id.standard_price * line.product_uom_qty
                profit = (line.price_unit * line.product_uom_qty) - cogs

                report_lines.append({
                    'order_name': order.name,
                    'customer_name': order.partner_id.name,
                    'order_date': order.date_order,
                    'product_name': line.product_id.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'subtotal': line.price_subtotal,
                    'cogs': cogs,
                    'profit': profit,
                })
                total_sales_value += line.price_subtotal
                total_profit += profit
                
        return {
            'title': _('تقرير المبيعات والربحية'),
            'header': [_('أمر البيع'), _('العميل'), _('التاريخ'), _('المنتج'), _('الكمية'), _('سعر الوحدة'), _('الإجمالي الفرعي'), _('التكلفة'), _('الربح')],
            'lines': report_lines,
            'total_sales_value': total_sales_value,
            'total_profit': total_profit,
            'filters': filters,
        }