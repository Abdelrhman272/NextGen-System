# ----------------------------- fish_health_record.py -----------------------------
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class FishHealthRecord(models.Model):
    """
    Logs fish health events: disease, mortality, injuries, treatments.
    """
    _name = 'fish_farm_management.fish_health_record'
    _description = 'سجل صحة الأسماك والأمراض'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='المرجع',
        default=lambda self: _('New'),
        readonly=True,
        copy=False,
        tracking=True,
    )
    pond_id = fields.Many2one(
        'fish_farm_management.pond',
        string='الحوض',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    record_date = fields.Date(
        string='تاريخ التسجيل',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    issue_type = fields.Selection(
        [
            ('disease', 'مرض'),
            ('mortality', 'وفيات'),
            ('injury', 'إصابة'),
            ('other', 'أخرى'),
        ],
        string='نوع المشكلة',
        required=True,
        tracking=True,
    )
    disease_name = fields.Char(string='اسم المرض/المشكلة', tracking=True)
    symptoms = fields.Text(string='الأعراض الملاحظة')
    diagnosis = fields.Text(string='التشخيص')
    treatment_ids = fields.One2many(
        'fish_farm_management.fish_health_record',
        'health_record_id',
        string='العلاجات المستخدمة',
    )
    mortality_count = fields.Integer(
        string='عدد الوفيات',
        default=0,
        tracking=True,
    )
    mortality_reason = fields.Char(string='سبب الوفاة', tracking=True)
    responsible_employee_id = fields.Many2one(
        'hr.employee',
        string='الموظف المسؤول',
        ondelete='set null',
    )
    notes = fields.Text(string='ملاحظات إضافية')
    company_id = fields.Many2one(
        'res.company',
        string='الشركة',
        related='pond_id.company_id',
        store=True,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Assigns sequence reference on batch creation.
        """
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence']
                    .next_by_code(
                        'fish_farm_management.fish_health_record'
                    ) or _('New')
                )
        return super().create(vals_list)

    @api.constrains('mortality_count')
    def _check_mortality_count(self):
        """
        Validates mortality_count > 0 when issue_type is mortality.
        """
        for rec in self:
            if rec.issue_type == 'mortality' and rec.mortality_count <= 0:
                raise ValidationError(
                    _(
                        "يجب أن يكون عدد الوفيات أكبر من صفر عند تسجيل وفاة."
                    )
                )