# 1) Master Data & Base Settings
from . import fish_farm                # أساس المزرعة
from . import sector                   # قطاع
from . import slice                    # شريحة
from . import pond                     # الحوض
from . import res_config_settings      # إعدادات الموديول
from . import analytic_account_extension  # امتداد الحساب التحليلي

# 2) Traceability Extension
from . import batch_traceability       # تتبّع الدفعات

# 3) Harvest Models (بالترتيب الصحيح)
from . import harvest_record           # يعتمد عليه التالي
from . import harvest_delivery         # يعتمد على Harvest Record
from . import harvest_sorting          # يعتمد على Harvest Record
from . import harvest_sorting_line     # يعتمد على Harvest Sorting

# 4) Growth & Planning
from . import fish_growth_measurement  # قياس النمو (يعتمد على Pond)
from . import fish_growth_model        # موديل النمو (يعتمد على Product)
from . import production_plan          # خطة الإنتاج

# 5) Health & Quality
from . import fish_health_record       # سجل الصحة (يعتمد على Pond)
from . import fish_health_treatment    # علاج الصحة (يعتمد على Fish Health Record)
from . import water_quality_reading    # جودة المياه (يعتمد على Pond)

# 6) Operations Models
from . import fish_stocking            # يستهلك Pond
from . import pond_cost                # تكلفة الحوض (يعتمد على Pond)
from . import pond_feeding             # تغذية الأحواض (يعتمد على Pond)
