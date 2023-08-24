# -*- coding: utf-8 -*-
from odoo import models, fields,api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round

class SaleRveneueByPartnerTypeReport(models.AbstractModel):
    _name = 'report.bsg_hr_payroll.payslips_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        record_wizard = self.env['hr.payslip.pdf.wizard'].browse(self._context.get('active_id'))
        payslip_run_id = record_wizard.payslip_run_id
        branch_id = record_wizard.branch_id
        category_ids = record_wizard.category_ids
        salary_payment_method = record_wizard.salary_payment_method
        lines = payslip_run_id.slip_ids
        if branch_id:
            lines = lines.filtered(lambda l: l.branch_id == branch_id)
        if salary_payment_method:
            lines = lines.filtered(lambda l: l.salary_payment_method == salary_payment_method)
        if len(category_ids) > 0:
            lines = lines.filtered(lambda l: l.category_ids and l.category_ids[0].id in category_ids.ids)
        if not lines:
            raise ValidationError("NO records matching your selected filters!")
        branch_ids = lines.mapped('branch_id')
        grouped_by_branch = {}
        all_basic = 0.00
        all_food_allow = 0.00
        all_trans_allow = 0.00
        all_housing_allow = 0.00
        all_work_nature_allow = 0.00
        all_extra_hours_allow = 0.00
        all_other_allow = 0.00
        all_gross = 0.00
        all_gossi = 0.00
        all_loan_input = 0.00
        all_deductions = 0.00
        all_total_deudctions = 0.00
        all_net = 0.00
        all_emp_count = 0.00

        for branch in branch_ids:
            branch_slip_ids = lines.filtered(lambda l: l.branch_id == branch)
            # brnach_employee_ids = branch_slip_ids.mapped('employee_id')
            brnach_basic = 0.00
            brnach_food_allow = 0.00
            branch_trans_allow = 0.00
            branch_housing_allow = 0.00
            branch_work_nature_allow = 0.00
            branch_extra_hours_allow = 0.00
            brnach_other_allow = 0.00
            brnach_gross = 0.00
            brnach_gossi = 0.00
            brnach_loan_input = 0.00
            brnach_deductions = 0.00
            brnach_total_deudctions = 0.00
            brnach_net = 0.00
            branch_emp_count = 0
            branch_dept_list = {}
            branch_department_ids = branch_slip_ids.mapped('department_id')
            for department_id in branch_department_ids:
                department_slips = branch_slip_ids.filtered(lambda slip: slip.department_id == department_id)
                dept_basic = 0.00
                dept_food_allow = 0.00
                dept_trans_allow = 0.00
                dept_housing_allow = 0.00
                dept_work_nature_allow = 0.00
                dept_extra_hours_allow = 0.00
                dept_other_allow = 0.00
                dept_gross = 0.00
                dept_gossi = 0.00
                dept_loan_input = 0.00
                dept_deductions = 0.00
                dept_total_deudctions = 0.00
                dept_net = 0.00
                dept_slip_list = []
                for slip in department_slips:
                    # slip = branch_slip_ids.filtered(lambda slip:slip.employee_id.id == employee_id.id)
                    vals = {}
                    vals['code'] = slip.employee_id.driver_code
                    vals['employee_name'] = slip.employee_id.name
                    vals['job'] = slip.job_id and slip.job_id.name or ''
                    basic = float_round(
                        slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'BASIC').total or 0.00, 2)
                    food_allow = float_round(
                        slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'FA').total or 0.00, 2)
                    if self.env.user.company_id.company_code == "BIC":
                        trans_allow = float_round(
                            sum(slip.line_ids.filtered(
                                lambda l: l.salary_rule_id.code in ['CA', 'CA22', 'CA23']).mapped('total')), 2)
                        housing_allow = float_round(sum(
                            slip.line_ids.filtered(lambda l: l.salary_rule_id.code in ['HRA3', 'HRA2', 'HA20']).mapped(
                                'total')), 2)
                    else:
                        trans_allow = float_round(
                            slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'CA').total or 0.00, 2)
                        housing_allow = float_round(sum(
                            slip.line_ids.filtered(lambda l: l.salary_rule_id.code in ['HRA3', 'HRA2']).mapped(
                                'total')), 2)
                    work_nature_allow = float_round(
                        slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'NWA').total or 0.00, 2)
                    extra_hours_allow = float_round(
                        slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'ADDMHRS').total or 0.00, 2)
                    other_allow = float_round(sum(slip.line_ids.filtered(
                        lambda l: l.salary_rule_id.code in ['ADDHRS', 'ADDDAYS', 'ADDVAR']).mapped('total')), 2)
                    additonal_hrs = float_round(
                        slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'ADDMHRS').total or 0.00, 2)
                    gross = float_round(
                        slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'GROSS').total or 0.00, 2) + additonal_hrs
                    gossi = float_round(slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'GOSI').total or 0.00,
                                        2)
                    # loans = slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'Basic').total
                    loan_input = float_round(
                        slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'LOAN').total or 0.00, 2)
                    deductions = float_round(sum(slip.line_ids.filtered(
                        lambda l: l.category_id.code == 'DED' and l.salary_rule_id.code != 'GOSI').mapped(
                        'total')) - loan_input, 2)
                    total_deudctions = float_round(deductions + loan_input + gossi, 2)
                    net = float_round(slip.line_ids.filtered(lambda l: l.salary_rule_id.code == 'NET').total or 0.00, 2)
                    dept_basic += basic
                    dept_food_allow += food_allow
                    dept_trans_allow += trans_allow
                    dept_housing_allow += housing_allow
                    dept_work_nature_allow += work_nature_allow
                    dept_extra_hours_allow += extra_hours_allow
                    dept_other_allow += other_allow
                    dept_gross += gross
                    dept_gossi += abs(gossi)
                    dept_loan_input += abs(loan_input)
                    dept_deductions += abs(deductions)
                    dept_total_deudctions += abs(total_deudctions)
                    dept_net += net
                    vals['basic'] = float_round(basic, 2)
                    vals['food_allow'] = float_round(food_allow, 2)
                    vals['trans_allow'] = float_round(trans_allow, 2)
                    vals['housing_allow'] = float_round(housing_allow, 2)
                    vals['work_nature_allow'] = float_round(work_nature_allow, 2)
                    vals['extra_hours_allow'] = float_round(extra_hours_allow, 2)
                    vals['other_allow'] = float_round(other_allow, 2)
                    vals['gross'] = float_round(gross, 2)
                    vals['gossi'] = float_round(abs(gossi), 2)
                    vals['loan_input'] = float_round(abs(loan_input), 2)
                    vals['deductions'] = float_round(abs(deductions), 2)
                    vals['total_deudctions'] = float_round(abs(total_deudctions), 2)
                    vals['net'] = float_round(net, 2)
                    dept_slip_list.append(vals)

                brnach_basic += float_round(dept_basic, 2)
                brnach_food_allow += dept_food_allow
                branch_trans_allow += dept_trans_allow
                branch_housing_allow += float_round(dept_housing_allow, 2)
                branch_work_nature_allow += dept_work_nature_allow
                branch_extra_hours_allow += dept_extra_hours_allow
                brnach_other_allow += dept_other_allow
                brnach_gross += dept_gross
                brnach_gossi += abs(dept_gossi)
                brnach_loan_input += abs(dept_loan_input)
                brnach_deductions += abs(dept_deductions)
                brnach_total_deudctions += abs(dept_total_deudctions)
                brnach_net += dept_net
                dept_emp_count = len(dept_slip_list)
                branch_emp_count += dept_emp_count
                branch_dept_list[department_id] = {
                    'dept_emp_count': dept_emp_count,
                    'dept_slip_list': dept_slip_list,
                    'dept_basic': float_round(dept_basic, 2),
                    'dept_food_allow': float_round(dept_food_allow, 2),
                    'dept_trans_allow': float_round(dept_trans_allow, 2),
                    'dept_housing_allow': float_round(dept_housing_allow, 2),
                    'dept_work_nature_allow': float_round(dept_work_nature_allow, 2),
                    'dept_extra_hours_allow': float_round(dept_extra_hours_allow, 2),
                    'dept_other_allow': float_round(dept_other_allow, 2),
                    'dept_gross': float_round(dept_gross, 2),
                    'dept_gossi': float_round(dept_gossi, 2),
                    'dept_loan_input': float_round(dept_loan_input, 2),
                    'dept_deductions': float_round(dept_deductions, 2),
                    'dept_total_deudctions': float_round(dept_total_deudctions, 2),
                    'dept_net': float_round(dept_net, 2),
                }

            all_basic += float_round(brnach_basic, 2)
            all_food_allow += float_round(brnach_food_allow, 2)
            all_trans_allow += float_round(branch_trans_allow, 2)
            all_housing_allow += float_round(branch_housing_allow, 2)
            all_work_nature_allow += float_round(branch_work_nature_allow, 2)
            all_extra_hours_allow += float_round(branch_extra_hours_allow, 2)
            all_other_allow += float_round(brnach_other_allow, 2)
            all_gross += float_round(brnach_gross, 2)
            all_gossi += float_round(brnach_gossi, 2)
            all_loan_input += float_round(brnach_loan_input, 2)
            all_deductions += float_round(brnach_deductions, 2)
            all_total_deudctions += float_round(brnach_total_deudctions, 2)
            all_net += float_round(brnach_net, 2)
            all_emp_count += branch_emp_count

            grouped_by_branch[branch] = {
                'branch_emp_count': branch_emp_count,
                'branch_dept_list': branch_dept_list,
                'branch_basic': float_round(brnach_basic, 2),
                'branch_food_allow': float_round(brnach_food_allow, 2),
                'branch_trans_allow': float_round(branch_trans_allow, 2),
                'branch_housing_allow': float_round(branch_housing_allow, 2),
                'branch_work_nature_allow': float_round(branch_work_nature_allow, 2),
                'branch_extra_hours_allow': float_round(branch_extra_hours_allow, 2),
                'branch_other_allow': float_round(brnach_other_allow, 2),
                'branch_gross': float_round(brnach_gross, 2),
                'branch_gossi': float_round(brnach_gossi, 2),
                'branch_loan_input': float_round(brnach_loan_input, 2),
                'branch_deductions': float_round(brnach_deductions, 2),
                'branch_total_deudctions': float_round(brnach_total_deudctions, 2),
                'branch_net': float_round(brnach_net, 2),

            }

        return {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'grouped_by_branch': grouped_by_branch,
            'batch_name': payslip_run_id.name,
            'payment_method': salary_payment_method,
            'all_basic': float_round(all_basic, 2),
            'all_food_allow': float_round(all_food_allow, 2),
            'all_trans_allow': float_round(all_trans_allow, 2),
            'all_housing_allow': float_round(all_housing_allow, 2),
            'all_work_nature_allow': float_round(all_work_nature_allow, 2),
            'all_extra_hours_allow': float_round(all_extra_hours_allow, 2),
            'all_other_allow': float_round(all_other_allow, 2),
            'all_gross': float_round(all_gross, 2),
            'all_gossi': float_round(all_gossi, 2),
            'all_loan_input': float_round(all_loan_input, 2),
            'all_deductions': float_round(all_deductions, 2),
            'all_total_deudctions': float_round(all_total_deudctions, 2),
            'all_net': float_round(all_net, 2),
            'all_emp_count': all_emp_count
        }



class HrPayslipXlsWizard(models.TransientModel):
    _name = 'hr.payslip.pdf.wizard'
    payslip_run_id = fields.Many2one('hr.payslip.run', required=True)
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch')
    salary_payment_method = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string = "Salary Payment Method")
    category_ids = fields.Many2many(
        'hr.employee.category',
        string='Tags')
    
    def generate_report(self):
        data = {}
        data['form'] = self.read(['payslip_run_id','branch_id','salary_payment_method', 'category_ids'])[0]
        return self.env.ref('bsg_hr_payroll.action_paysip_report_pdf').with_context({'active_id':self.id}).report_action(self, data=data)


