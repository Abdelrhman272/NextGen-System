# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FishFarmEquipment(models.Model):
    _inherit = ['maintenance.equipment']
    fish_farm_id = fields.Many2one('fish_farm_management.fish_farm', string='المزرعة المرتبطة')
    _name = 'fish_farm_management.equipment'
    _description = 'معدات المزرعة السمكية'
    _inherit = ['maintenance.equipment'] # التوريث من Maintenance Equipment

    # حقول إضافية خاصة بالمزرعة السمكية إذا لزم الأمر
    # location_id = fields.Many2one('stock.location', string='موقع المعدة') # يمكن استخدامه لتحديد موقع المعدة داخل المزرعة
    pond_id = fields.Many2one('fish_farm_management.pond', string='الحوض المرتبط', help='إذا كانت هذه المعدة مخصصة لحوض معين.', ondelete='set null')
    equipment_type = fields.Selection([
        ('pump', 'مضخة'),
        ('aerator', 'جهاز تهوية'),
        ('generator', 'مولد كهرباء'),
        ('feeder', 'مغذية آلية'),
        ('sorter', 'جهاز فرز'),
        ('vehicle', 'مركبة'),
        ('other', 'أخرى'),
    ], string='نوع المعدة', default='other', tracking=True)
    serial_number = fields.Char(string='الرقم التسلسلي')
    purchase_date = fields.Date(string='تاريخ الشراء')
    warranty_expiry_date = fields.Date(string='تاريخ انتهاء الضمان')
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)

    # يمكن إضافة حقل One2many لسجلات الصيانة إذا لم تكن كافية التي يوفرها موديول Maintenance
    # maintenance_ids = fields.One2many('maintenance.request', 'equipment_id', string='طلبات الصيانة', readonly=True)

    @api.constrains('serial_number')
    def _check_unique_serial_number(self):
        for rec in self:
            if rec.serial_number and self.search_count([('serial_number', '=', rec.serial_number), ('id', '!=', rec.id)]) > 0:
                raise ValidationError(_("الرقم التسلسلي يجب أن يكون فريداً."))