{
    "name": "Employee Human Resource",
    "version": "12.13.71",
    "description": """ Employee Human Resource """,
    "depends": ["base","hr_payroll","hr_contract","bsg_hr"],
    "data": [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'security/record_rule.xml',
        # 'data/data.xml',
        # 'data/salary_rules.xml',
        'wizard/refuse.xml',
        'views/hr_exit_return.xml',
        'views/config.xml',
        'views/emp_transfer_view.xml',
        'wizard/termination_refuse.xml',
        'views/hr_termination.xml',
        'views/hr_termination_type.xml',
    ],
    "installable": True,
    "auto_install": False,
}

