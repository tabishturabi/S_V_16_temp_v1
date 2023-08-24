# -*- coding: utf-8 -*-
{
    'name': "sim_card",

    'summary': """
    update sim card package type name with the new package type name  in the Upgrade SIM Card Package Request
    """,

    'description': """
    update sim card package type name with the new package type name  in the Upgrade SIM Card Package Request
    """,

    'author': "Al-Bassami || Rai Muhammad Kashif ",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1.0.27',
    'depends': ['base', 'hr', 'bsg_hr', 'bsg_branch_config','account_accountant','hr_payroll'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'wizard/refuse.xml',
        'views/sim_card_request.xml',
        'views/sim_card_receipt.xml',
        'views/sim_card_configuration.xml',
        'views/package_type.xml',
        'views/sim_card_define.xml',
        'views/sequence.xml',
        'views/delivery.xml',
        'views/upgrade_request.xml',
        'views/ext_employee.xml',
        'views/my_request.xml',
        'views/lost_sim.xml',
        'views/sim_card_owner.xml',
        'report/sim_card_delivery_report.xml',
        'report/sim_card_receipt_report.xml',
        'report/sim_card_movement_report.xml',
        'security/mail_template.xml',
        'security/record_rules.xml',
        'data/manager_template_view.xml',
        'data/finance_manager_template_view.xml',
        'data/manager_sim_upgrade_template_view.xml',
        'data/finance_sim_upgrade_template_view.xml',
        'data/ir_attachment.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
}
