# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WaterQualityReading(models.Model):
    _name = "fish_farm_management.water_quality_reading"
    _description = "قراءة جودة المياه"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="المرجع",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True,
    )
    pond_id = fields.Many2one(
        "fish_farm_management.pond",
        string="الحوض",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    reading_date = fields.Datetime(
        string="تاريخ ووقت القراءة",
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    ph = fields.Float(string="الرقم الهيدروجيني (pH)", digits=(16, 2), tracking=True)
    oxygen_level = fields.Float(
        string="مستوى الأكسجين المذاب (ملجم/لتر)", digits=(16, 2), tracking=True
    )
    temperature = fields.Float(
        string="درجة الحرارة (مئوية)", digits=(16, 2), tracking=True
    )
    ammonia = fields.Float(string="الأمونيا (ملجم/لتر)", digits=(16, 2), tracking=True)
    nitrite = fields.Float(string="النيتريت (ملجم/لتر)", digits=(16, 2), tracking=True)
    nitrate = fields.Float(string="النترات (ملجم/لتر)", digits=(16, 2), tracking=True)
    salinity = fields.Float(
        string="الملوحة (جزء في الألف)", digits=(16, 2), tracking=True
    )

    read_by_employee_id = fields.Many2one(
        "hr.employee", string="تمت القراءة بواسطة", ondelete="set null"
    )
    notes = fields.Text(string="ملاحظات")
    company_id = fields.Many2one(
        "res.company",
        string="الشركة",
        related="pond_id.company_id",
        store=True,
        readonly=True,
    )

    # حقل محسوب لتحديد ما إذا كانت القراءة خارج النطاق المسموح به
    is_alert = fields.Boolean(
        string="تنبيه!",
        compute="_compute_is_alert",
        store=True,
        help="يشير إلى ما إذا كانت أي من القراءات خارج النطاقات المحددة في الإعدادات.",
    )
    alert_reason = fields.Text(
        string="سبب التنبيه", compute="_compute_is_alert", store=True
    )

    @api.model_create_multi
    def create(self, vals_list):  # تم تغيير vals إلى vals_list
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fish_farm_management.water_quality_reading"
                ) or _("New")

        records = super(WaterQualityReading, self).create(
            vals_list
        )  # استدعاء create الأصلية مع القائمة

        return records

    @api.depends(
        "ph", "oxygen_level", "temperature", "ammonia", "nitrite", "nitrate", "salinity"
    )
    def _compute_is_alert(self):
        # جلب القيم القصوى والدنيا من إعدادات الموديول
        config = self.env["res.config.settings"].sudo().get_values()

        for rec in self:
            alert = False
            reasons = []

            # pH
            min_ph = float(config.get("fish_farm_management.min_ph", 6.5))
            max_ph = float(config.get("fish_farm_management.max_ph", 8.5))
            if not (min_ph <= rec.ph <= max_ph):
                alert = True
                reasons.append(
                    f"pH ({rec.ph}) خارج النطاق (%.1f-%.1f)." % (min_ph, max_ph)
                )

            # Oxygen
            min_oxygen = float(config.get("fish_farm_management.min_oxygen", 5.0))
            if rec.oxygen_level < min_oxygen:
                alert = True
                reasons.append(
                    f"الأكسجين ({rec.oxygen_level}) أقل من الحد الأدنى (%.1f)."
                    % min_oxygen
                )

            # Temperature
            min_temp = float(config.get("fish_farm_management.min_temperature", 20.0))
            max_temp = float(config.get("fish_farm_management.max_temperature", 30.0))
            if not (min_temp <= rec.temperature <= max_temp):
                alert = True
                reasons.append(
                    f"درجة الحرارة ({rec.temperature}) خارج النطاق (%.1f-%.1f)."
                    % (min_temp, max_temp)
                )

            # Ammonia
            max_ammonia = float(config.get("fish_farm_management.max_ammonia", 0.05))
            if rec.ammonia > max_ammonia:
                alert = True
                reasons.append(
                    f"الأمونيا ({rec.ammonia}) أعلى من الحد الأقصى (%.2f)."
                    % max_ammonia
                )

            # Nitrite
            max_nitrite = float(config.get("fish_farm_management.max_nitrite", 0.1))
            if rec.nitrite > max_nitrite:
                alert = True
                reasons.append(
                    f"النيتريت ({rec.nitrite}) أعلى من الحد الأقصى (%.2f)."
                    % max_nitrite
                )

            rec.is_alert = alert
            rec.alert_reason = "\n".join(reasons) if reasons else False

            # إرسال إشعار إذا كان هناك تنبيه
            if alert and rec.tracking_message_ids.filtered(
                lambda m: _("Water Quality Alert") in m.subject
            ).filtered(
                lambda m: fields.Date.today()
                == fields.Date.context_today(m.create_date)
            ):
                # Avoid sending too many alerts for the same issue on the same day
                pass
            elif alert:
                rec.message_post(
                    subject=_("تنبيه جودة المياه للحوض: %s") % rec.pond_id.name,
                    body=_(
                        "تم تسجيل قراءة لجودة المياه خارج النطاق الطبيعي للحوض %s بتاريخ %s. الأسباب: \n%s"
                    )
                    % (rec.pond_id.name, rec.reading_date, "\n".join(reasons)),
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=[
                        (4, p.id)
                        for p in self.env.ref(
                            "fish_farm_management.group_fish_farm_manager"
                        ).users.partner_id
                    ],  # إرسال للمدراء
                )
