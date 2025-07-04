# ----------------------------- fish_farm.py -----------------------------
from odoo import fields, models


class FishFarm(models.Model):
    """
    Represents a fish farm with sectors and company association.
    """

    _name = "fish_farm_management.fish_farm"
    _description = "مزرعة سمكية"

    name = fields.Char(string="اسم المزرعة", required=True, translate=True)
    location = fields.Char(string="الموقع", translate=True)
    sector_ids = fields.One2many(
        "fish_farm_management.sector",
        "fish_farm_id",
        string="القطاعات",
    )
    company_id = fields.Many2one(
        "res.company",
        string="الشركة",
        required=True,
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        (
            "name_unique",
            "unique(name, company_id)",
            "يجب أن يكون اسم المزرعة فريداً لكل شركة!",
        ),
    ]
