# -*- coding: utf-8 -*-

{
    'name': 'Employee Loan',
    'category': 'HR',
    'description': """
                Manage Employee Loan.
                 """,
    'summary': 'Manage Employee Loan.',
    'version': '12.23',
    'author': 'Albassami.',
    'website': 'http://www.albassami.com',
    'depends': ['base','account','bsg_hr_payroll'],
    'data': [
        'security/loan_security.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        'data/loan_data.xml',
        'wizard/hr_employee_loan_register_payment.xml',
        'views/loan_type_view.xml',
        'views/loan_application_view.xml',
        'wizard/loan_calc_view.xml',
        'views/loan_setting_view.xml',
        'wizard/wizard_loan_reject_view.xml',
        'report/report_loan_summary.xml',
        'report/report_loan_contract.xml',
        'views/loan_prepayment_view.xml',
        'views/loan_advance_payment_view.xml',
        'views/loan_adjustment_view.xml',
        'views/loan_installment_delay.xml',
        'views/hr_payroll_view.xml',
        'data/mail_template_view.xml',
        'data/hr_payroll_data.xml',
        
        
        
    ],
    'demo': [
    ],
    'external_dependencies': {
        'python': [
            'numpy'
        ],
    },
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
