# -*- coding: utf-8 -*-
# © 2019 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Intelligenti CRM',
    'summary': '',
    'description': 'Intelligenti CRM',
    'author': 'Intelligenti.io',
    'category': 'Sales',
    'license': 'AGPL-3',
    'website': 'http://www.intelligenti.io',
    'version': '11.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'crm',
    ],
    'data': ['security/crm_security.xml',
             'security/ir.model.access.csv',
             'wizard/crm_lead_wizard_view.xml',
             'views/crm_lead_view.xml',
            ],
}
