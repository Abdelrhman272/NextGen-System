# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class FishGrowthMeasurement(models.Model):
    _name = 'fish_farm_management.fish_growth_measurement'
    _description = 'قياس نمو الأسماك'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='المرجع', default=lambda self: _('New'),
        readonly=True, copy=False, tracking=True
    )
    pond_id = fields.Many2one(
        'fish_farm_management.pond', string='الحوض',
        required=True, ondelete='restrict', tracking=True
    )
    measurement_date = fields.Date(
        string='تاريخ القياس', required=True,
        default=fields.Date.context_today, tracking=True
    )
    fish_type_id = fields.Many2one(
        'product.product', string='نوع السمك المقاس',
        required=True, domain="[('is_fish_type', '=', True)]", tracking=True
    )
    sample_count = fields.Integer(
        string='عدد العينات', required=True, default=1,
        help='عدد الأسماك التي تم أخذ عينة منها.'
    )
    total_sample_weight_g = fields.Float(
        string='إجمالي وزن العينات (جرام)', required=True,
        help='إجمالي وزن جميع الأسماك في العينة (جرام).'
    )
    average_fish_weight_g = fields.Float(
        string='متوسط وزن السمكة (جرام)',
        compute='_compute_average_weight', store=True,
        help='متوسط وزن السمكة الواحدة في العينة (جرام).'
    )
    notes = fields.Text(string='ملاحظات')
    company_id = fields.Many2one(
        'res.company', string='الشركة',
        related='pond_id.company_id', store=True, readonly=True
    )

    @api.depends('sample_count', 'total_sample_weight_g')
    def _compute_average_weight(self):
        for rec in self:
            if rec.sample_count > 0:
                rec.average_fish_weight_g = rec.total_sample_weight_g / rec.sample_count
            else:
                rec.average_fish_weight_g = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        """دعم الإنشاء على دفعات مع توليد المراجع عبر التسلسل."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence']
                    .next_by_code('fish_farm_management.fish_growth_measurement')
                    or _('New')
                )
        records = super(FishGrowthMeasurement, self).create(vals_list)
        return records

    @api.constrains('sample_count', 'total_sample_weight_g')
    def _check_measurement_values(self):
        for rec in self:
            if rec.sample_count <= 0:
                raise ValidationError(_("عدد العينات يجب أن يكون أكبر من صفر."))
            if rec.total_sample_weight_g <= 0:
                raise ValidationError(_("إجمالي وزن العينات يجب أن يكون أكبر من صفر."))
