from odoo import models, fields, api

class MultilingualModel(models.AbstractModel):
    _name = 'fish.multilingual.mixin'
    _description = 'Multilingual Mixin'
    
    def _get_translated_field(self, field_name, lang=None):
        """Get translated field based on language"""
        lang = lang or self.env.context.get('lang') or self.env.user.lang
        translation = self.env['ir.translation'].search([
            ('name', '=', f"{self._name},{field_name}"),
            ('res_id', '=', self.id),
            ('lang', '=', lang)
        ], limit=1)
        return translation.value or getattr(self, field_name)
    
    def _set_translated_field(self, field_name, value, lang=None):
        """Update translated field based on language"""
        lang = lang or self.env.context.get('lang') or self.env.user.lang
        translation = self.env['ir.translation'].search([
            ('name', '=', f"{self._name},{field_name}"),
            ('res_id', '=', self.id),
            ('lang', '=', lang)
        ])
        
        if translation:
            translation.write({'value': value})
        else:
            self.env['ir.translation'].create({
                'name': f"{self._name},{field_name}",
                'res_id': self.id,
                'lang': lang,
                'type': 'model',
                'value': value
            })
            
        if lang == self.env.ref('base.lang_en').code:
            self.write({field_name: value})