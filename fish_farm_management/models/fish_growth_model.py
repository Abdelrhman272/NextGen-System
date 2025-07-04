# ----------------------------- fish_growth_model.py -----------------------------
from odoo import _, api, fields, models


class FishGrowthModel(models.Model):
    """
    Defines growth parameters: start and target weight and duration.
    """

    _name = "fish_farm_management.fish_growth_model"
    _description = "نموذج نمو الأسماك"

    fish_type_id = fields.Many2one(
        "product.product",
        string="نوع السمك",
        required=True,
        domain=[("is_fish_type", "=", True)],
        help="اختيار نوع السمك من الأصول المعرفة.",
    )
    start_weight_g = fields.Float(
        string="الوزن الابتدائي (جم)",
        required=True,
        help="الوزن عند بداية التربية.",
    )
    target_weight_g = fields.Float(
        string="الوزن المستهدف (جم)",
        required=True,
        help="الوزن عند نهاية دورة التربية.",
    )
    target_days = fields.Integer(
        string="عدد الأيام المستهدفة",
        required=True,
        help="مدة التربية للوصول للوزن المستهدف.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Supports batch create without extra logic post-creation.
        """
        return super().create(vals_list)

    def write(self, vals):
        """
        Updates growth model fields; placeholder for post-write logic.
        """
        return super().write(vals)


class ProductProduct(models.Model):
    """
    Extends product to add relations for growth models and measurements.
    """

    _inherit = "product.product"

    fish_growth_model_ids = fields.One2many(
        "fish_farm_management.fish_growth_model",
        "fish_type_id",
        string="نماذج النمو",
        help="نماذج النمو المرتبطة بكل نوع سمك",
    )
    fish_growth_measurement_ids = fields.One2many(
        "fish_farm_management.fish_growth_measurement",
        "fish_type_id",
        string="قراءات النمو",
        help="قراءات النمو المسجلة لكل نوع سمك",
    )
