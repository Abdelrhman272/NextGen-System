### **ملف README.md للموديول الفرعي: `fish_farm_product_extension`**

````markdown
# Fish Farm Product Extension Module for Odoo 18

## 💡 Overview

This small, specialized Odoo 18 module (`fish_farm_product_extension`) extends the core `product.product` model. Its sole purpose is to introduce specific boolean fields that are crucial for categorizing products within the `Fish Farm Management` system. This approach ensures a clean separation of concerns and maintains the integrity of the base Odoo product model.

## 🌟 Features

This module adds the following boolean fields to the `product.template` (which `product.product` inherits from):

- **Is Fish Type? (`is_fish_type`):**
  - Identifies products representing different species of fish or fingerlings.
  - Used in `Fish Stocking` records and `Growth Models` within the `Fish Farm Management` module.
- **Is Feed Type? (`is_feed_type`):**
  - Marks products that are used as fish feed.
  - Used in `Pond Feeding` records within the `Fish Farm Management` module.
- **Is Medicine Type? (`is_medicine_type`):**
  - Designates products used for fish health treatments.
  - Used in `Pond Feeding` (for general supplies) and `Fish Health Records` (for specific treatments) within the `Fish Farm Management` module.
- **Is Harvested Product? (`is_harvested_product`):**
  - Flags products representing raw or processed fish after harvesting.
  - Used in `Harvest Sorting` and `Sales` processes within the `Fish Farm Management` module.

These fields are integrated into the product form and search views, allowing for easy classification and filtering of products relevant to fish farm operations.

## 📁 Module Structure

fish_farm_product_extension/
├── models/ # ORM models (extension to product.template)
│ ├── init.py
│ └── product_template_extension.py
├── views/ # UI views for product.template extension
│ └── product_template_views_extension.xml
├── init.py # Python package initialization
└── manifest.py # Module manifest file

## 🔗 Dependencies

This module only depends on the core Odoo `product` module.

## 🚀 Installation

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/your-organization/fish_farm_product_extension.git /path/to/your/odoo/custom_addons/fish_farm_product_extension
    ```

    _Replace `/path/to/your/odoo/custom_addons/` with the actual path to your Odoo custom addons directory._

2.  **Add to Odoo Addons Path:**
    Ensure that your `custom_addons` directory is correctly specified in your Odoo configuration file (`odoo.conf`).

3.  **Update Odoo Modules List:**

    - Navigate to "Apps" (or "Applications") in your Odoo instance.
    - Click on "Update Apps List" (or "Update Modules List").

4.  **Install the Module:**

    - Search for "Fish Farm Product Extension" in the Apps list.
    - Click on the "Install" button.

    **Important:** This module **must be installed before** the `Fish Farm Management` module, as the latter depends on the fields provided by this extension.

## 🔧 Technical Notes

- **Inheritance:** Extends `product.template` using standard Odoo inheritance mechanisms (`_inherit`).
- **View Extensions:** Modifies existing product form, tree, and search views to display and filter by the new fields.

## ✅ Tested On

- Odoo 18 (Community Edition)
- Odoo.sh (Test Instance)

## 👤 Developed by

**NextGen Systems** | Abdelrhman Elsayed
````
