from odoo import _, fields, models

class FishFarm(models.Model):
    _name = "fish_farm_management.fish_farm"
    _description = _("Fish Farm")

    name = fields.Char(string=_("Farm Name"), required=True, translate=True)
    location = fields.Char(string=_("Location"), translate=True)
    sector_ids = fields.One2many(
        "fish_farm_management.sector",
        "fish_farm_id",
        string=_("Sectors"),
    )
    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        required=True,
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        (
            "name_unique",
            "unique(name, company_id)",
            _("The farm name must be unique per company!"),
        ),
    ]
