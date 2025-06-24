# Fish Farm Management - Odoo 18 Custom Module

This custom Odoo 18 module is built to manage the full operation of a fish farm with multilingual support (Arabic & English).

---

## 🌟 Features

### 🎯 Dashboard
- Visual KPIs for feeding, fishing, supplying
- Dynamic charts and indicators

### 🧩 Core Modules
- Pond Management
- Seed Entry
- Feeding Records
- Fishing Operations
- Supplying Logs

### 📊 Reports
- Production Report
- Daily Report
- Feeding/Fishing/Supplying Summary
- All reports available in PDF & Excel exportable formats

### ⚙️ Settings
- Feeding, Fishing, and Supplying threshold limits
- Adjustable via configuration UI
- Automatically impact list view colors

### 🌍 Multilingual
- Fully translatable interface (Arabic & English)
- Language auto-switch based on Odoo user preference

---

## 🔧 Technical Notes

- Dynamic decorations in list views based on configurable limits
- Uses `ir.config_parameter` for system settings
- All views follow Odoo 18 standards (tree -> list replaced)

---

## 📁 Module Structure

```bash
fish_farm_module_clean/
├── controllers/         # For PDF/Excel export
├── models/              # All ORM models for ponds, feeding, etc.
├── reports/             # QWeb reports
├── static/              # Assets
├── views/               # List/form views, dashboards, settings
├── security/
├── __init__.py
├── __manifest__.py
```

---

## ✅ Installation

1. Upload to Odoo custom addons path
2. Activate Developer Mode
3. Update Apps List
4. Install the module: `Fish Farm Management`

---

## 🧪 Tested On

- Odoo 18 (Community Edition)
- Odoo.sh (Test Instance)

---

## 👤 Developed by
**NextGen Systems** | Abdelrhman Elsayed