from odoo import http
from odoo.http import request
import json

class FishFarmDashboardController(http.Controller):

    @http.route('/fish_farm/dashboard', type='http', auth='user', website=True)
    def fish_dashboard(self, **kw):
        ponds = request.env['fish.farm.pond'].sudo().search_count([])
        total_feed = sum(request.env['fish.farm.feed'].sudo().mapped('quantity_kg'))
        total_harvest = sum(request.env['fish.farm.harvest'].sudo().mapped('quantity_kg'))

        # Feed chart
        feed_data = {}
        feeds = request.env['fish.farm.feed'].sudo().read_group(
            [('pond_id', '!=', False)], ['quantity_kg'], ['pond_id']
        )
        for rec in feeds:
            name = rec['pond_id'][1] if rec['pond_id'] else 'Unknown'
            feed_data[name] = rec['quantity_kg']

        # Harvest chart
        harvest_data = {}
        harvests = request.env['fish.farm.harvest'].sudo().read_group(
            [('pond_id', '!=', False)], ['quantity_kg'], ['pond_id']
        )
        for rec in harvests:
            name = rec['pond_id'][1] if rec['pond_id'] else 'Unknown'
            harvest_data[name] = rec['quantity_kg']

        return request.render('fish_farm_module.fish_dashboard_template', {
            'ponds': ponds,
            'total_feed': total_feed,
            'total_harvest': total_harvest,
            'feed_labels': json.dumps(list(feed_data.keys())),
            'feed_data': json.dumps(list(feed_data.values())),
            'harvest_labels': json.dumps(list(harvest_data.keys())),
            'harvest_data': json.dumps(list(harvest_data.values())),
        })
