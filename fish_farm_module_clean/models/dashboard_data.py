
from odoo import models, fields, api
from datetime import datetime

class FishFarmDashboardData(models.Model):
    _name = 'fish.farm.dashboard.data'
    _description = 'Fish Farm Dashboard Data'

    def get_dashboard_data(self):
        Pond = self.env['fish.farm.pond']
        Seed = self.env['fish.farm.seed']
        Feed = self.env['fish.farm.feeding']
        Fish = self.env['fish.farm.fishing']
        Supplying = self.env['fish.farm.supplying']

        pond_count = Pond.search_count([])
        total_seed = sum(Seed.search([]).mapped('quantity_kg'))
        total_feed = sum(Feed.search([]).mapped('quantity_kg'))
        total_fishing = sum(Fish.search([]).mapped('quantity_kg'))
        total_supplying = sum(Supplying.search([]).mapped('quantity_kg'))

        # Get last 7 days feeding for line chart
        date_chart = []
        feed_chart = []
        today = fields.Date.today()
        for i in range(6, -1, -1):
            day = today - fields.Date.delta(days=i)
            daily_feed = sum(Feed.search([('date', '=', day)]).mapped('quantity_kg'))
            date_chart.append(str(day))
            feed_chart.append(daily_feed)

        return {
            'pond_count': pond_count,
            'total_seed': total_seed,
            'total_feed': total_feed,
            'total_fishing': total_fishing,
            'total_supplying': total_supplying,
            'feed_chart': {
                'labels': date_chart,
                'data': feed_chart
            }
        }
