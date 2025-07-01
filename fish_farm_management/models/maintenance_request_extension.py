# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class MaintenanceRequestExtension(models.Model):
    _inherit = 'maintenance.request'
    _description = 'Maintenance Request Extension for Fish Farm'

    # ربط طلب الصيانة مباشرة بالحوض
    # يمكن أن يكون equipment_id هو الحقل الرئيسي، وهذا حقل إضافي للراحة
    pond_id = fields.Many2one('fish_farm_management.pond', string='الحوض المرتبط', ondelete='set null',
                              help='الحوض الذي حدثت فيه المشكلة أو ترتبط به المعدة.',
                              # نطاق لجلب الأحواض من نفس المزرعة التي تتبع لها المعدة
                              domain="[('fish_farm_id', '=', equipment_id.fish_farm_id)]",
                              store=True, readonly=False) # اجعله غير للقراءة ليمكن تحديده يدويا

    # سبب خاص بالصيانة في سياق المزرعة
    farm_issue_type = fields.Selection([
        ('water_system_failure', 'فشل نظام المياه'),
        ('aeration_failure', 'فشل التهوية'),
        ('feeding_system_malfunction', 'عطل نظام التغذية'),
        ('generator_issue', 'مشكلة المولد'),
        ('other_farm_related', 'مشكلة أخرى متعلقة بالمزرعة'),
    ], string='نوع المشكلة بالمزرعة', help='تصنيف خاص لمشكلات الصيانة المتعلقة بعمليات المزرعة.')

    # حقل لتتبع الدفعة المتأثرة إذا كانت المشكلة قد أثرت على دفعة محددة
    batch_id = fields.Many2one('fish_farm_management.batch_traceability', string='الدفعة المتأثرة',
                               help='الدفعة التي تأثرت بهذه المشكلة (مثل توقف تهوية أثر على دفعة أسماك).', ondelete='set null')

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        # عندما تتغير المعدة، حاول تحديث الحوض المرتبط إذا كانت المعدة مرتبطة بحوض
        if self.equipment_id and self.equipment_id.pond_id:
            self.pond_id = self.equipment_id.pond_id
        else:
            self.pond_id = False