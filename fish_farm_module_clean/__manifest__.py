{
    'name': 'Fish Farm Management',
    'version': '1.0',
    'summary': 'Manage fish farm sectors and zones',
    'author': 'NextGen Systems',
    'website': 'https://nextgensystems.net',
    'category': 'Agriculture',
    'depends': ['base'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/fish_farm_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}