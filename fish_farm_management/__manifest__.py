{
    'name': 'Fish Farm Management',
    'version': '1.0',
    'summary': 'Comprehensive ERP solution for Fish Farms with advanced operations, costing, and reporting.',
    'description': """
        This Odoo module provides a comprehensive ERP solution specifically tailored for the unique operations and management needs of a fish farm. It integrates various core ERP functionalities to streamline processes from stocking and feeding to harvesting, costing, and sales, with a focus on advanced analytics and decision support.

        Key Features:
        - Financial Accounts Integration (Balance Sheet, Revenues, Expenses)
        - Detailed Costing (Direct/Indirect) with Tree-like Cost Centers (Farm -> Sector -> Slice -> Pond)
        - Multi-channel Sales Management (POS, Agents, Distribution, Direct)
        - Comprehensive Purchase Management
        - Full Inventory Management for Inputs (Fingerlings, Feed, Medicine) and Outputs (Harvested Fish)
        - Supplier and Customer Relationship Management (CRM integration recommended)
        - Human Resources Management (Employee files, contracts, salaries, allowances, incentives, training)
        - Manufacturing Processes (for value-added products like exported fish)
        - Export Operations Management
        - Advanced Operational Management:
            - Production Planning
            - Fish Health & Disease Management
            - Water Quality Management with Readings & Alerts
            - Equipment & Maintenance Management
            - Waste Management
        - Advanced Analytics & Reporting:
            - Performance Analysis (FCR, Survival Rates, Growth)
            - Forecasting (Harvest, Consumption, Sales)
            - Business Intelligence Dashboards
            - Traceability (Farm-to-Fork)
        - Integration Capabilities:
            - API for external web applications
            - Social Media Integration (recommended)
            - Automation platforms (e.g., N8N) (recommended)
            - IoT Integration (for sensors)
            - GPS Tracking (for distribution)
        - Multilingual support (Arabic & English)
        - Configurable settings and dynamic list view decorations.
    """,
    'author': 'NextGen Systems | Abdelrhman Elsayed',
    'website': 'https://www.nextgen-systems.com', # Placeholder, replace with actual
    'category': 'Industries/Agriculture',
    'depends': [
        'account',
        'hr',
        'stock',
        'sale_management',
        'purchase',
        'mrp', # For manufacturing processes
        'point_of_sale', # If POS is heavily used
        'crm', # For comprehensive CRM
        'hr_expense', # For personal advances/expenses
        'hr_payroll', # If salary processing is done via Odoo Payroll
        'analytic', # For analytic accounts and tags
        'maintenance', # For advanced equipment maintenance
        'fish_farm_product_extension', # Custom module to extend product.product
    ],
    'data': [
        'security/fish_farm_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/product_data.xml', # For initial product types (fish, feed, medicine)
        'data/analytic_tag_data.xml', # For initial analytic tags for costs

        'views/menu_items.xml',
        'views/fish_farm_views.xml',
        'views/sector_views.xml',
        'views/slice_views.xml',
        'views/pond_views.xml',
        'views/fish_stocking_views.xml',
        'views/pond_feeding_views.xml',
        'views/pond_cost_views.xml',
        'views/harvest_record_views.xml',
        'views/harvest_delivery_views.xml',
        'views/harvest_sorting_views.xml',
        'views/fish_health_views.xml',
        'views/water_quality_views.xml',
        'views/equipment_views.xml', # Extended maintenance.equipment views
        'views/maintenance_request_views_extension.xml', # Extended maintenance.request views
        'views/production_plan_views.xml',
        'views/batch_traceability_views.xml',
        'views/fish_growth_model_views.xml', # New views for growth models
        'views/fish_growth_measurement_views.xml', # New views for growth measurements
        'views/fish_farm_settings_views.xml', # For configurable limits/settings
        'views/menu_items.xml', # This file will contain the action for the dashboard

        'wizards/report_wizard_views.xml', # Wizard for custom report generation

        'reports/report_actions.xml', # Report definitions (PDF)
        'reports/report_pond_cost_analysis_template.xml',
        'reports/report_harvest_performance_template.xml',
        'reports/report_supplies_consumption_template.xml',
        'reports/report_fish_health_water_quality_template.xml',
        'reports/report_sales_profitability_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fish_farm_management/static/src/js/dashboard_main.js', # For main dashboard
            'fish_farm_management/static/src/xml/fish_farm_dashboard.xml', # For dashboard QWeb
            'fish_farm_management/static/src/css/dashboard.css',
            'fish_farm_management/static/src/js/excel_export.js', # For frontend Excel export trigger
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}