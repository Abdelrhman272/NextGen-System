# -*- coding: utf-8 -*-

# النماذج الأساسية التي لا تعتمد على غيرها بشكل كبير أو التي تعتمد عليها نماذج أخرى
# إعدادات الموديول (عادة لا تعتمد على نماذج أخرى في نفس الموديول)
# نماذج الحصاد المتقدمة (تعتمد على Pond و Batch)
# نماذج التتبع (تعتمد على نماذج أخرى مثل Stocking, Harvest, Pond)
# نماذج النمو والتخطيط (المضافة مؤخراً)
# نماذج الصيانة (المضافة مؤخراً)
# نماذج الصحة والجودة
# نماذج العمليات الأساسية التي تعتمد على Pond والمنتجات
from . import \
    batch_traceability  # يعتمد على Pond, Fish Stocking, Harvest, Growth Models
from . import \
    equipment  # يورث من maintenance.equipment، لا يعتمد على نماذجنا بشكل كبير في التهيئة المبكرة
from . import fish_growth_measurement  # يعتمد على Pond ونماذج النمو
from . import fish_growth_model  # يعتمد على Product
from . import fish_health_record  # يعتمد على Pond
from . import fish_stocking  # يعتمد على Pond
from . import harvest_delivery  # يعتمد على Harvest Record
from . import harvest_record  # يعتمد على Pond, Batch
from . import harvest_sorting  # يعتمد على Harvest Record
from . import \
    maintenance_request_extension  # يورث من maintenance.request ويعتمد على Pond و Batch
from . import pond  # Pond يعتمد على fish_farm, sector, slice
from . import pond_cost  # يعتمد على Pond
from . import pond_feeding  # يعتمد على Pond
from . import production_plan  # إضافة خطة الإنتاج
from . import water_quality_reading  # يعتمد على Pond
from . import fish_farm, res_config_settings, sector, slice
