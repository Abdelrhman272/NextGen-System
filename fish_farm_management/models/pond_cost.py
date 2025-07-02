# ----------------------------- pond_cost.py -----------------------------
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class PondCost(models.Model):
    """
    Records and posts pond-related costs to accounting entries.
    """
    _name = 'fish_farm_management.pond_cost'
    _description = 'إدخال تكلفة الحوض'
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
    cost_date = fields.Date(
        string='تاريخ التكلفة',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    cost_type_id = fields.Many2one(
        'account.analytic.tag',
        string='نوع التكلفة',
        required=True,
        tracking=True,
        help='علامات تحليلية لتصنيف التكلفة.',
        domain="[('analytic_tag_group_id.name','=','Pond Cost Types')]"
    )
    amount = fields.Monetary(
        string='المبلغ',
        required=True,
        tracking=True,
        currency_field='company_currency_id',
    )
    company_id = fields.Many2one(
        'res.company',
        string='الشركة',
        related='pond_id.company_id',
        store=True,
        readonly=True,
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        string='عملة الشركة',
        related='company_id.currency_id',
        readonly=True,
    )
    description = fields.Text(string='الوصف')
    is_direct_cost = fields.Boolean(
        string='تكلفة مباشرة',
        default=True,
        tracking=True,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='أمر الشراء ذو صلة',
        readonly=True,
    )
    expense_sheet_id = fields.Many2one(
        'hr.expense.sheet',
        string='كشف المصروفات ذو صلة',
        readonly=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='الموظف ذو صلة',
        ondelete='set null',
    )
    account_move_id = fields.Many2one(
        'account.move',
        string='قيد المحاسبة',
        readonly=True,
        copy=False,
    )
    state = fields.Selection(
        [
            ('draft', 'مسودة'),
            ('posted', 'مرحل'),
            ('cancelled', 'ملغاة'),
        ],
        string='الحالة',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Generates sequence reference for new cost entries.
        """
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence']
                    .next_by_code(
                        'fish_farm_management.pond_cost'
                    ) or _('New')
                )
        return super().create(vals_list)

    def action_post_cost(self):
        """
        Posts cost as accounting journal entry.
        """
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    _("يمكن ترحيل التكلفة من المسودة فقط.")
                )
            if record.amount <= 0:
                raise ValidationError(
                    _("المبلغ يجب أن يكون أكبر من صفر.")
                )
            journal = self.env['account.journal'].search([
                ('type', '=', 'general'),
                ('company_id', '=', record.company_id.id),
            ], limit=1)
            if not journal:
                raise UserError(
                    _("لم يتم العثور على دفتر يومية عام.")
                )
            expense_ac = self.env['account.account'].search([
                ('code', '=', '600000'),
                ('company_id', '=', record.company_id.id),
            ], limit=1)
            credit_ac = self.env['account.account'].search([
                ('code', '=', '201000'),
                ('company_id', '=', record.company_id.id),
            ], limit=1)
            if not expense_ac or not credit_ac:
                raise UserError(
                    _(
                        "تأكد من تعريف حسابات المصروفات والدائن المناسبة."
                    )
                )
            move_lines = [
                (0, 0, {
                    'name': _(
                        "تكلفة حوض %s: %s"
                    ) % (
                        record.pond_id.name, record.cost_type_id.name
                    ),
                    'account_id': expense_ac.id,
                    'debit': record.amount,
                    'credit': 0,
                    'analytic_tag_ids': [(6, 0, [record.cost_type_id.id])],
                }),
                (0, 0, {
                    'name': _(
                        "دفع/استحقاق تكلفة %s: %s"
                    ) % (
                        record.pond_id.name, record.cost_type_id.name
                    ),
                    'account_id': credit_ac.id,
                    'debit': 0,
                    'credit': record.amount,
                }),
            ]
            move = self.env['account.move'].create({
                'journal_id': journal.id,
                'date': record.cost_date,
                'ref': record.name,
                'line_ids': move_lines,
                'move_type': 'entry',
            })
            move.action_post()
            record.account_move_id = move.id
            record.state = 'posted'
            record.message_post(
                body=_("تم ترحيل قيد التكلفة بنجاح.")
            )

    def action_cancel_cost(self):
        """
        Cancels posted cost and related accounting move.
        """
        for record in self:
            if record.state == 'posted' and record.account_move_id:
                record.account_move_id.button_draft()
                record.account_move_id.button_cancel()
            record.state = 'cancelled'
            record.message_post(
                body=_("تم إلغاء سجل التكلفة.")
            )

    def unlink(self):
        """
        Prevents deletion of posted costs; removes draft moves.
        """
        for rec in self:
            if rec.state == 'posted':
                raise UserError(
                    _("لا يمكن حذف تكلفة مرحل. يرجى إلغائها أولاً.")
                )
            if rec.account_move_id:
                rec.account_move_id.unlink()
        return super().unlink()
