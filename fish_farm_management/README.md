# Fish Farm Management Module for Odoo 18

## 💡 Overview

هذه الوحدة لـ Odoo 18 (`fish_farm_management`) تقدم حل ERP متكامل
لإدارة المزارع السمكية، بدءًا من تخزين الأفراد وحتى البيع والتحليلات
المتقدمة.

### Key Features

- **Financial Accounts:** إدارة الميزانيات والإيرادات والمصروفات.
- **Detailed Costing:** تتبع التكاليف المباشرة وغير المباشرة عبر
  هيكل هرمي (Farm → Sector → Slice → Pond).
- **Multi-channel Sales:** دعم POS، وكلاء، ومراكز توزيع، والمبيعات
  المباشرة مع الفاتورة الإلكترونية (VAT).
- **Purchase Management:** إدارة مشتريات اليرقات، العلف، الأدوية، وغيرها.
- **Inventory Management:** تتبع المخزون للمواد الخام والمنتجات النهائية.
- **CRM & Suppliers:** ربط بيانات الموردين والعملاء وسجلاتهم.
- **HR & Payroll:** إدارة الموظفين، العقود، الأجور، القروض، والتدريب.
- **Manufacturing:** دعم عمليات تجهيز المنتج قبل التصدير.
- **Export Operations:** خصائص لإدارة إجراءات التصدير.
- **Production Planning:** إنشاء وتتبع خطط الإنتاج الموسمية لكل حوض.
- **Health & Water Quality:** تتبع الحالات المرضية ومعايير جودة المياه.
- **Equipment & Maintenance:** تكامل مع وحدة `maintenance` للصيانة.
- **Batch Traceability:** تتبع كامل لدورة حياة الدفعات (FCR, Survival Rate).
- **Reporting & Analytics:** لوحة متابعة تفاعلية وWizard لتوليد
  تقارير PDF وExcel.
- **Configuration:** إعدادات قابلة للتعديل (FCR, Survival Rate,
  Sorting Tolerance).
- **Multilingual:** دعم عربي وإنجليزي.
- **Integration:** API، N8N، IoT (مستقبليًّا).

## 📁 Module Structure

```text
# راجع ملف Module structure.txt

```

⚙️ Configuration & Usage
إعداد thresholds وFCR عبر Fish Farm Management > Settings.

تعريف Master Data: Farms, Sectors, Slices, Ponds.

ضبط Growth Models وAnalytic Tags.

تسجيل العمليات اليومية عبر Fish Farm Management > Operations.

الوصول إلى التقارير عبر Fish Farm Management > Reports > Wizard.

🔗 Technical Notes
List Views: tree تم استبدالها بـ list.

Dashboard: OWL + Chart.js عبر JSON-RPC.

Excel Export: يعتمد على xlsxwriter.

Settings: ir.config_parameter + res.config.settings.

Odoo 18 Standards: توافق كامل مع الإصدارات الجديدة.

✅ Tested On
Odoo 18 Community.

Odoo.sh (Test).

👤 Developed by
NextGen Systems | Abdelrhman Elsayed
