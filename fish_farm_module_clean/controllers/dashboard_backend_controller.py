from odoo import http
from odoo.http import request

class FishFarmDashboardController(http.Controller):

    @http.route('/fish_farm/dashboard', auth='user', website=False)
    def dashboard(self, **kwargs):
        ponds = request.env['fish.farm.pond'].sudo().search([])
        domain = []
        if 'date_from' in kwargs and kwargs['date_from']:
            domain.append(('date', '>=', kwargs['date_from']))
        if 'date_to' in kwargs and kwargs['date_to']:
            domain.append(('date', '<=', kwargs['date_to']))
        if 'pond_id' in kwargs and kwargs['pond_id']:
            domain.append(('pond_id', '=', int(kwargs['pond_id'])))
        # قراءة بيانات فعلية من قاعدة البيانات
        pond_count = len(ponds)
        total_seeds = sum(request.env['fish.farm.seed'].sudo().mapped('quantity'))
        total_feeding = sum(request.env['fish.farm.feeding'].sudo().mapped('quantity_kg'))
        total_fishing = sum(request.env['fish.farm.fishing'].sudo().mapped('quantity_kg'))
        total_supplying = sum(request.env['fish.farm.supplying'].sudo().mapped('quantity_kg'))


        feeding_limit = float(request.env['ir.config_parameter'].sudo().get_param('fish_farm_module_clean.feeding_limit', default=100))
        fishing_limit = float(request.env['ir.config_parameter'].sudo().get_param('fish_farm_module_clean.fishing_limit', default=200))
        feeding_alert = total_feeding > feeding_limit
        fishing_alert = total_fishing > fishing_limit
        seed_obj = request.env['fish.farm.seed'].sudo().search(domain)
        feeding_obj = request.env['fish.farm.feeding'].sudo().search(domain)
        fishing_obj = request.env['fish.farm.fishing'].sudo().search(domain)
        supplying_obj = request.env['fish.farm.supplying'].sudo().search(domain)
        total_seeds = sum(seed_obj.mapped('quantity'))
        total_feeding = sum(feeding_obj.mapped('quantity_kg'))
        total_fishing = sum(fishing_obj.mapped('quantity_kg'))
        total_supplying = sum(supplying_obj.mapped('quantity_kg'))

        feeding_limit = float(request.env['ir.config_parameter'].sudo().get_param('fish_farm_module_clean.feeding_limit', default=100))
        fishing_limit = float(request.env['ir.config_parameter'].sudo().get_param('fish_farm_module_clean.fishing_limit', default=200))
        feeding_alert = total_feeding > feeding_limit
        fishing_alert = total_fishing > fishing_limit
        return request.render('fish_farm_module_clean.fish_farm_dashboard_template', {
            'pond_count': pond_count,
            'total_seeds': total_seeds,
            'total_feeding': total_feeding,
            'total_fishing': total_fishing,
            'total_supplying': total_supplying,
            'feeding_alert': feeding_alert,
            'fishing_alert': fishing_alert,
            'ponds': ponds
        })
            'pond_count': pond_count,
            'total_seeds': total_seeds,
            'total_feeding': total_feeding,
            'total_fishing': total_fishing,
            'total_supplying': total_supplying,
            'feeding_alert': feeding_alert,
            'fishing_alert': fishing_alert
        })
            'pond_count': pond_count,
            'total_seeds': total_seeds,
            'total_feeding': total_feeding,
            'total_fishing': total_fishing,
            'total_supplying': total_supplying,
        })