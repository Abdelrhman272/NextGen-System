from odoo import http
from odoo.http import request

class FishFarmDashboard(http.Controller):
    @http.route('/fish_farm/dashboard/data', auth='user', type='json')
    def dashboard_data(self):
        return {
            'total_production': 1500,  # استبدل ببيانات حقيقية
            'monthly_production': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'values': [100, 200, 150, 300, 250, 400],
            },
            'pond_status': {
                'labels': ['Active', 'Maintenance', 'Empty'],
                'values': [15, 3, 2],
            }
        }