from odoo import http
from odoo.http import request
import json
from datetime import datetime, timedelta

class FishFarmDashboardController(http.Controller):
    
    @http.route('/fish_farm/dashboard/data', auth='user', type='json')
    def dashboard_data(self):
        # Get production data (last 6 months)
        months = []
        production_values = []
        
        today = datetime.now()
        for i in range(6, 0, -1):
            month = today - timedelta(days=30*i)
            months.append(month.strftime('%b %Y'))
            production_values.append(1000 * i)  # Replace with actual data
        
        # Get pond status data
        Pond = request.env['fish.farm.pond']
        pond_status = {
            'statuses': ['Active', 'Maintenance', 'Empty'],
            'counts': [
                Pond.search_count([('status', '=', 'active')]),
                Pond.search_count([('status', '=', 'maintenance')]),
                Pond.search_count([('status', '=', 'empty')])
            ]
        }
        
        # Get recent activities
        activities = []
        Activity = request.env['fish.farm.activity']
        for activity in Activity.search([], limit=5, order='date desc'):
            activities.append({
                'date': activity.date.strftime('%Y-%m-%d'),
                'type': activity.activity_type,
                'description': activity.description,
                'pond': activity.pond_id.name
            })
        
        return {
            'production': {
                'months': months,
                'values': production_values
            },
            'pondStatus': pond_status,
            'activities': activities
        }