from odoo import models, api, _
from odoo.exceptions import UserError
import requests
import json

class AutoTranslator(models.AbstractModel):
    _name = 'fish.auto.translator'
    _description = 'Automatic Translator'
    
    def translate_text(self, text, source_lang='en', target_lang=None):
        """ترجمة النصوص تلقائياً باستخدام API خارجي"""
        if not text:
            return ""
            
        if not target_lang:
            target_lang = self.env.user.lang or 'ar'
            
        # استخدام خدمة الترجمة المجانية (مثال: MyMemory API)
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_lang}|{target_lang}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = json.loads(response.text)
                if data.get('responseData') and data['responseData'].get('translatedText'):
                    return data['responseData']['translatedText']
        except Exception as e:
            raise UserError(_("Translation error: %s") % str(e))
        
        return text
    
    def auto_translate_record(self, record, field_names, source_lang='en'):
        """ترجمة سجل تلقائياً"""
        target_lang = self.env.user.lang or 'ar'
        translations = {}
        
        for field_name in field_names:
            if hasattr(record, field_name):
                original_text = getattr(record, field_name)
                if original_text:
                    translated = self.translate_text(original_text, source_lang, target_lang)
                    translations[field_name] = translated
        
        if translations:
            record.with_context(lang=target_lang).write(translations)
        return True