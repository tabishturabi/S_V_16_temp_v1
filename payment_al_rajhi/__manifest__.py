# -*- coding: utf-8 -*-
{
    "name": "Al Rajhi Payment Acquirer",
    "summary": """The module allows the customers to make payment for their online orders with Al Rajhi  Payment Gateway on odoo website. The module integrates Al Rajhi  Payment Acquirer with Odoo.""",
    "category": "Website",
    "version": "1.1.8",
    "sequence": 1,
    "author": "Albassami",
    "license": "Other proprietary",
    "maintainer": "Albassami",
    "website": "Albassami",
    "description": """Odoo Al Rajhi  Payment Acquirer
Odoo with Al Rajhi  Payment Acquirer
Odoo Al Rajhi  Payment Gateway
Payment Gateway
Al Rajhi  Payment Gateway
Al Rajhi  integration
Al Rajhi  Integration
Payment acquirer
Payment processing
Payment processor
Website payments
Sale orders payment
Customer payment
Integrate Al Rajhi  payment acquirer in Odoo
Integrate Al Rajhi  payment gateway in Odoo""",
    "depends": [
        'payment',
    ],
    "data": [
        'security/groups.xml',
        'views/payment_view.xml',
        'views/template.xml',
        'data/payment_data.xml',
    ],
    "demo": [],
    "images": ['static/description/banner.png'],
    "application": True,
    "installable": True,

}
