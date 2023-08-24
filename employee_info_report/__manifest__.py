{
    'name': "employee_info_report",
    'description': "employee_info_report",
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'category': 'sale',
    'version': '12.0.1.3',
    'application': True,
    'depends': ['base','bsg_hr','bsg_hr_payroll'],
    'data': [
            'security/access_security.xml',
            'security/ir.model.access.csv',
            'template.xml'
             ],
    
}