from odoo import models, http
from odoo.http import request
import json

class FishFarmDashboard(models.Model):
    _name = 'fish.farm.dashboard'
    _description = 'Fish Farm Dashboard'

    def get_dashboard_data(self):
        return {
            'production': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'datasets': [{
                    'label': 'Fish Production',
                    'data': [65, 59, 80, 81, 56, 55],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                }]
            },
            'pondStatus': {
                'labels': ['Active', 'Maintenance', 'Empty'],
                'datasets': [{
                    'data': [300, 50, 100],
                    'backgroundColor': [
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 205, 86)'
                    ],
                }]
            }
        }

class DashboardController(http.Controller):
    @http.route('/fish_farm/dashboard/data', auth='user', type='json')
    def dashboard_data(self):
        return request.env['fish.farm.dashboard'].get_dashboard_data()