{
    "name": "Fish Farm Management",
    "version": "1.0",
    "summary": "Manage fish farm operations from seed to harvest",
    "depends": ["base", "web"],
    "category": "Operations",
    "data": [
        "security/ir.model.access.csv",
        "views/menus.xml",
        "views/fish_sector_views.xml",
        "views/fish_slice_views.xml",
        "views/fish_pond_views.xml",
        "views/fish_seed_views.xml",
        "views/fish_feed_views.xml",
        "views/fish_expense_views.xml",
        "views/fish_harvest_views.xml",
        "views/fish_dashboard_views.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "/fish_farm_module/static/lib/chart.js"
        ]
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3"
}
