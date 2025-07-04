# ----------------------------- equipment.py -----------------------------
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FishFarmEquipment(models.Model):
    """
    Extends maintenance.equipment to link equipment with specific fish farm ponds.
    """

    _name = "fish_farm_management.equipment"
    _description = "معدات المزرعة السمكية"
    _inherit = ["maintenance.equipment"]

    fish_farm_id = fields.Many2one(
        "fish_farm_management.fish_farm",
        string="المزرعة المرتبطة",
    )
    pond_id = fields.Many2one(
        "fish_farm_management.pond",
        string="الحوض المرتبط",
        help="إذا كانت هذه المعدة مخصصة لحوض معين.",
        ondelete="set null",
    )
    equipment_type = fields.Selection(
        [
            ("pump", "مضخة"),
            ("aerator", "جهاز تهوية"),
            ("generator", "مولد"),
            ("feeder", "مغذية"),
            ("sorter", "جهاز فرز"),
            ("vehicle", "مركبة"),
            ("other", "أخرى"),
        ],
        string="نوع المعدة",
        default="other",
        tracking=True,
    )
    serial_number = fields.Char(string="الرقم التسلسلي")
    purchase_date = fields.Date(string="تاريخ الشراء")
    warranty_expiry_date = fields.Date(
        string="تاريخ انتهاء الضمان",
    )
    company_id = fields.Many2one(
        "res.company",
        string="الشركة",
        default=lambda self: self.env.company,
    )

    @api.constrains("serial_number")
    def _check_unique_serial_number(self):
        """
        Ensures the serial_number is unique across all equipment.
        """
        for rec in self:
            if rec.serial_number and (
                self.search_count(
                    [
                        ("serial_number", "=", rec.serial_number),
                        ("id", "!=", rec.id),
                    ]
                )
                > 0
            ):
                raise ValidationError(_("الرقم التسلسلي يجب أن يكون فريداً."))
