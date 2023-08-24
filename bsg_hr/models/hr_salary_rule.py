from odoo import api, fields, models

class HrSalaryRule(models.Model):

    _inherit = "hr.salary.rule"

    leave_clearance = fields.Boolean("Leave Clearance")
    is_housing = fields.Boolean("Is Housing")
    is_eos = fields.Boolean("EOS")
    child_ids = fields.One2many('hr.salary.rule', 'parent_rule_id', string='Child Salary Rule', copy=True)
    parent_rule_id = fields.Many2one('hr.salary.rule', string='Parent Salary Rule', index=True)
    register_id = fields.Many2one('hr.contribution.register', string='Contribution Register')
    account_tax_id = fields.Many2one('account.tax', 'Tax')



    def _recursive_search_of_rules(self):
        """
        @return: returns a list of tuple (id, sequence) which are all the children of the passed rule_ids
        """
        children_rules = []
        for rule in self.filtered(lambda rule: rule.child_ids):
            children_rules += rule.child_ids._recursive_search_of_rules()
        return [(rule.id, rule.sequence) for rule in self] + children_rules

#
# class HrSalaryRuleCategory(models.Model):
#     _inherit = "hr.salary.rule.category"
#
#     include_in_leave_clearance = fields.Boolean("Include In Leave Clearance")
#

class HrContributionRegister(models.Model):
    _name = 'hr.contribution.register'
    _description = 'Contribution Register'

    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    partner_id = fields.Many2one('res.partner', string='Partner')
    name = fields.Char(required=True)
    register_line_ids = fields.One2many('hr.payslip.line', 'register_id',
        string='Register Line', readonly=True)
    note = fields.Text(string='Description')