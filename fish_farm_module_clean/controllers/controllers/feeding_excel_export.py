from odoo import http
from odoo.http import request
import json

class FishFarmDashboardController(http.Controller):

    @http.route('/fish_farm/dashboard', type='http', auth='user', website=True)
    def fish_dashboard(self, **kw):
        ponds = request.env['fish.farm.pond'].sudo().search_count([])
        total_feed = sum(request.env['fish.farm.feed'].sudo().mapped('quantity'))
        total_harvest = sum(request.env['fish.farm.harvest'].sudo().mapped('quantity'))

        # Feed chart per pond
        feed_data = {}
        for rec in request.env['fish.farm.feed'].sudo().search([]):
            pond = rec.pond_id.name
            feed_data[pond] = feed_data.get(pond, 0) + rec.quantity

        # Harvest chart per pond
        harvest_data = {}
        for rec in request.env['fish.farm.harvest'].sudo().search([]):
            pond = rec.pond_id.name
            harvest_data[pond] = harvest_data.get(pond, 0) + rec.quantity

        return request.render('fish_farm_module_clean.fish_dashboard_template', {
            'pond_count': ponds,
            'total_feed': total_feed,
            'total_harvest': total_harvest,
            'feed_chart_labels': json.dumps(list(feed_data.keys())),
            'feed_chart_data': json.dumps(list(feed_data.values())),
            'harvest_chart_labels': json.dumps(list(harvest_data.keys())),
            'harvest_chart_data': json.dumps(list(harvest_data.values())),
        })

