# -*- coding: utf-8 -*-

{
    'name': 'Bassami HR Payroll',

    'version': '12.139',
    'category': 'HR',
    'summary': 'Bassami HR Payroll',
    'author': "Muhammad Yousef",
    'description': """
        Bassami HR Contract
    """,
    'depends': ['hr_payroll_account', 'bsg_trip_mgmt','bsg_employee_attachment','hr_holidays'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'data/ir_sequence_data.xml',
        'data/salary_structure.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'views/hr_payslip.xml',
        'views/res_country.xml',
        'views/hr_leave_allocation.xml',
        'views/account_journal_views.xml',
        'views/hr_job.xml',
        'views/hr_leave.xml',
        'wizard/batchwise_register_payment.xml',
        'wizard/payslipwise_register_payment.xml',
        'wizard/payslips_report.xml',
        'reports/payslip_report.xml',
        'data/ir_attachment.xml',

    ],
    'qweb': [],
    'application': True,
}
