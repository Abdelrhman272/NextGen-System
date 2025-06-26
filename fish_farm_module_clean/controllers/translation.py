from odoo import http, _
from odoo.http import request
import json

class TranslationController(http.Controller):
    
    @http.route('/fish_farm/get_translations', type='json', auth="user")
    def get_translations(self, modules, lang):
        user_lang = request.env.user.lang or 'en_US'
        translations = request.env['ir.translation'].search_read([
            ('module', 'in', modules),
            ('lang', '=', user_lang),
            ('value', '!=', False)
        ], ['src', 'value'])
        
        return {t['src']: t['value'] for t in translations}
    
    @http.route('/fish_farm/set_user_language', type='json', auth="user")
    def set_user_language(self, lang_code):
        user = request.env.user
        user.write({'lang': lang_code})
        return {'success': True, 'message': _('Language changed successfully')}