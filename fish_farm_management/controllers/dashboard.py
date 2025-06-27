from odoo import http
from odoo.http import request
import json

class FishFarmDashboardController(http.Controller):
    @http.route('/fish_farm/dashboard/data', auth='user', type='json')
    def dashboard_data(self):
        return {
            'production': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'datasets': [{
                    'label': 'Fish Production (kg)',
                    'data': [65, 59, 80, 81, 56, 55],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                }]
            },
            'pondStatus': {
                'labels': ['Active', 'Maintenance', 'Empty'],
                'datasets': [{
                    'data': [300, 50, 100],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)'
                    ],
                    'borderWidth': 1
                }]
            }
        }