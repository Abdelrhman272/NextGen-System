from odoo import http
from odoo.http import request

class FishFarmDashboard(http.Controller):
    @http.route('/fish_farm/dashboard', type='json', auth='user')
    def get_dashboard_data(self):
        # Example data - replace with actual queries
        return {
            'total_production': 1500,
            'avg_cost_per_kg': 12.5,
            'active_ponds': 25,
            'growth_rate': 78,
            'monthly_production': [
                {'month': 'Jan', 'production': 200},
                {'month': 'Feb', 'production': 300},
                {'month': 'Mar', 'production': 450},
                {'month': 'Apr', 'production': 550},
            ],
            'pond_status': [
                {'status': 'empty', 'count': 5},
                {'status': 'stocked', 'count': 15},
                {'status': 'harvesting', 'count': 5},
            ]
        }