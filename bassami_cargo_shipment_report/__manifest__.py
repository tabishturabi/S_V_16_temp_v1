{
    'name': "bassami_cargo_shipment_report",
    'description': "bassami_cargo_shipment_report",
    'author': 'bassamitech',
    'website': "http://www.bassamitech.com",
    'category': 'sale',
    'version': '12.6.17',
    'application': True,
    'depends': ['base','web', 'bsg_cargo_sale'],
    'data': [
        'security/ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
        'views/sales_revenue_by_partner_type.xml',
        'revenue_partner_type_schedule.xml',
    ],
}