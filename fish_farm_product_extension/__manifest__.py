{
    'name': 'Fish Farm Product Extension',
    'version': '1.0',
    'summary': 'Adds specific fields to product.product for fish farm management.',
    'description': """
        This module extends the product.product model to include boolean fields
        necessary for categorizing products within a fish farm management system,
        such as:
        - Is Fish Type (for fingerlings, specific fish species)
        - Is Feed Type (for fish feed products)
        - Is Medicine Type (for fish medicines/treatments)
        - Is Harvested Product (for raw harvested fish before sorting/processing)
    """,
    'author': 'NextGen Systems | Abdelrhman Elsayed',
    'website': 'https://www.nextgen-systems.com', # Placeholder
    'category': 'Industries/Agriculture',
    'depends': [
        'product', # Depends on the base product module
    ],
    'data': [
        'data/product_data.xml',
        'views/product_template_views_extension.xml',
    ],
    'installable': True,
    'auto_install': False, # Set to True if you want it to auto-install with fish_farm_management
    'license': 'LGPL-3',
}