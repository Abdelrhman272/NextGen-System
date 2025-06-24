
from odoo import http
from odoo.http import request

class FishFarmDashboardController(http.Controller):

    @http.route('/fish_farm/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        dashboard_model = request.env['fish.farm.dashboard.data'].sudo()
        data = dashboard_model.get_dashboard_data()
        return data
