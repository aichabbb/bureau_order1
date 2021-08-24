# -*- coding: utf-8 -*-


{
    'name': "bureau ",

    'summary': """  """,

    'description': """ """,

    'author': "",
    'website': "",
    'price' : '10.0',
    'currency' : 'USD',


    'category': 'Uncategorized',
    'version': '12.0.1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'hr'],

    # always loaded
    'data': [


        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',

        'views/emission.xml',
        'views/reception.xml',
        'views/piece_joint.xml',
        'views/kanban_dashbord.xml',
        'views/searsh.xml',
        'rapots/bureau_order_raport.xml',
        'rapots/report.xml',

        'data/email_template_valider_reception.xml',
        'data/sequence.xml',
        'wizards/accese_recepption.xml',
        'views/add_scss.xml',
        'wizards/motive_refuser.xml',

    ],

    # only loaded in demonstration mode
    'installable': True,
    'application': True,
    'auto_install': False,
}
