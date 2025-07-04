# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Slice(models.Model):
    _name = "fish_farm_management.slice"
    _description = "شريحة القطاع"

    name = fields.Char(string="اسم الشريحة", required=True, translate=True)
    sector_id = fields.Many2one(
        "fish_farm_management.sector",
        string="القطاع",
        required=True,
        ondelete="restrict",
    )
    fish_farm_id = fields.Many2one(
        "fish_farm_management.fish_farm",
        string="المزرعة السمكية",
        related="sector_id.fish_farm_id",
        store=True,
        readonly=True,
    )
    pond_ids = fields.One2many(
        "fish_farm_management.pond", "slice_id", string="الأحواض"
    )
    company_id = fields.Many2one(
        "res.company",
        string="الشركة",
        related="sector_id.company_id",
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "name_sector_unique",
            "unique(name, sector_id)",
            "يجب أن يكون اسم الشريحة فريداً لكل قطاع!",
        ),
    ]
