{
    "name": "Fish Farm Management",
    "summary": "إدارة المزرعة السمكية من الأحواض حتى الصيد والتكاليف",
    "description": "نظام متكامل لإدارة العمليات التشغيلية للمزارع السمكية باستخدام Odoo 18.",
    "author": "NextGen Systems",
    "website": "https://nextgensystems.net",
    "category": "Industries",
    "version": "1.0.0",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/fish_sequences.xml",
        "data/fish_defaults.xml",
        "views/fish_sector_views.xml",
        "views/fish_unit_views.xml",
        "views/fish_pond_views.xml",
        "views/fish_seed_views.xml",
        "views/fish_feed_views.xml",
        "views/fish_expense_views.xml",
        "views/fish_harvest_views.xml",
        "views/fish_species_views.xml",
        "views/fish_cost_rule_views.xml",
        "views/dashboard_view.xml",
        "views/actions.xml",
        "views/menus.xml",
        "report/report_cost_analysis.xml",
        "report/report_harvest_summary.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "fish_farm_module_clean/static/src/js/dashboard.js"
        ]
    },
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
