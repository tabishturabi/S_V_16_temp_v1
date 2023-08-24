# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_round


class HrEmployeeReligion(models.Model):
    _name = 'hr.employee.religion'
    _rec_name = 'religion_name'
    _order = 'sequence'

    religion_name = fields.Char('Name')
    sequence = fields.Integer('sequance')


class BsgInheritHrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_state = fields.Selection([
        ('on_job', 'On Job'),
        ('on_leave', 'On leave'),
        ('return_from_holiday', 'Return From Holiday'),
        ('resignation', 'Resignation'),
        ('suspended', 'Suspended'),
        ('service_expired','Service Expired'),
        ('contract_terminated', 'Contract Terminated'),
        ('ending_contract_during_trial_period','Ending Contract During Trial Period'),
        ('deceased', 'Deceased'),
        ('suspended_case', 'Suspended for Case'),

    ], string='Employee State',  default='on_job',track_visibility='always')
    state = fields.Selection([
        ('complete_data', 'Completed Data'),
        ('trail_period', 'Trail Period'),
        ('on_job', 'On Job'),
        ('on_leave', 'On Leave'),
        ('service_expired', 'Service Expired'),
    ], string='Employee State',  default='complete_data',track_visibility='always')
    employee_state = fields.Selection([
        ('on_job', 'On Job'),
        ('on_leave', 'On leave'),
        ('return_from_holiday', 'Return From Holiday'),
        ('resignation', 'Resignation'),
        ('suspended', 'Suspended'),
        ('service_expired','Service Expired'),
        ('contract_terminated', 'Contract Terminated'),
        ('ending_contract_during_trial_period','Ending Contract During Trial Period'),
        ('deceased', 'Deceased'),
        ('suspended_case', 'Suspended for Case'),

    ], string='Employee State',  default='on_job',track_visibility='always')
    employee_type = fields.Selection(selection=[('foreign', 'Foreign'), ('citizen', 'Citizen')],
                                     default='foreign', required=True)
    bsgjoining_date = fields.Date("Date of Join",readonly=True, track_visibility='always')
    bsg_totalyears = fields.Char("Total Years/Days", compute="_compute_dateofjoin", track_visibility='always')
    bsg_religion = fields.Selection([('Muslim', 'Muslim'), ('NonMuslim', 'Non Muslim')], string="Religion",
                                    track_visibility='always')
    bsg_religion = fields.Selection([('Muslim', 'Muslim'), ('NonMuslim', 'Non Muslim')], string="Religion",
                                    track_visibility='always')
    bsg_religion_id = fields.Many2one('hr.employee.religion', string="Religion", track_visibility='always')
    bsg_dependent = fields.Boolean("Have Dependent?", track_visibility='always')
    bsg_empiqama = fields.Many2one('hr.iqama', string="Iqama Number", track_visibility='always')
    bsg_passport = fields.Many2one('hr.passport', string="Passport", track_visibility='always')
    bsg_doc_type = fields.One2many('hr.emp.doc', 'hrdoc', string="Doc Type", track_visibility='always')
    bsg_insurance = fields.One2many('hr.insurance', 'employee_insurance', string="Employee Insurance",
                                    track_visibility='always')
    bsg_assets_emp = fields.One2many('hr.asset', 'assets_emp', string="Assets", track_visibility='always')
    bsg_empaccess_emp = fields.One2many('hr.emp.access.mgt', 'access_emp', string="Assets", track_visibility='always')
    bsg_family_employee = fields.One2many('hr.iqama.family', 'employee_id', string="Family Iqama", track_visibility='always')
    bsg_emergency = fields.One2many('hr.emergency.contact', 'emergency_employee', string="Emergency Contact",
                                    track_visibility='always')
    bsg_education = fields.One2many('hr.education', 'education_emp', string="Education", track_visibility='always')
    bsg_job_pos = fields.Char(related="job_id.name", track_visibility='always')
    bsg_country_name = fields.Char(related="country_id.name", string="Country Name", track_visibility='always')
    bsg_national_id = fields.Many2one('hr.nationality', string="National ID", track_visibility='always')
    bsg_bank_id = fields.Many2one('hr.banks', string="Bank Account Number", track_visibility='always')
    bsg_licence_no = fields.Char("Licence Number", track_visibility='always')
    bsg_issue_place = fields.Char("Issue Place", track_visibility='always')
    bsg_issue_date = fields.Date("Issue Date", track_visibility='always')
    bsg_exp_date = fields.Date("Expiry Join", track_visibility='always')
    name_english = fields.Char('English Name', track_visibility='always')
    mobile_private = fields.Char('Mobile Number', track_visibility='always')
    alternative_employee_id = fields.Many2one('hr.employee', track_visibility='always')
    current_leave_state = fields.Selection(
        selection_add=[('hr_specialist', 'Hr Specialist'), ('hr_specialist', 'Hr Specialist'),
                       ('hr_manager', 'Hr Manager'),
                       ('branch_supervisor', 'Branch Supervisor'), ('department_supervisor', 'Department Supervisor'),
                       ('area_manager', 'Area Manager'), ('branches_department_manager', 'Branches Department Manager'),
                       ('department_manager', 'Department Manager'), ('vice_em', 'vice Execution Manager'),
                       ('internal_audit_manager', 'Internal Audit Manager'),('accountant', 'Accountant'),
                       ('finance_manager', 'Finance Manager')])

    '''Tracking history of base fields'''

    name = fields.Char(track_visibility='always')
    user_id = fields.Many2one(track_visibility='always')
    active = fields.Boolean(track_visibility='always')
    # private partner
    address_home_id = fields.Many2one(track_visibility='always')
    is_address_home_a_company = fields.Boolean(track_visibility='always')
    country_id = fields.Many2one(track_visibility='always')
    gender = fields.Selection(track_visibility='always')
    marital = fields.Selection(track_visibility='always')
    spouse_complete_name = fields.Char(track_visibility='always')
    spouse_birthdate = fields.Date(track_visibility='always')
    children = fields.Integer(track_visibility='always')
    place_of_birth = fields.Char(track_visibility='always')
    country_of_birth = fields.Many2one(track_visibility='always')
    birthday = fields.Date(track_visibility='always')
    ssnid = fields.Char(track_visibility='always')
    sinid = fields.Char(track_visibility='always')
    identification_id = fields.Char(track_visibility='always')
    passport_id = fields.Char(track_visibility='always')
    bank_account_id = fields.Many2one(track_visibility='always')
    permit_no = fields.Char(track_visibility='always')
    visa_no = fields.Char(track_visibility='always')
    visa_expire = fields.Date(track_visibility='always')
    additional_note = fields.Text(track_visibility='always')
    certificate = fields.Selection(track_visibility='always')
    study_field = fields.Char(track_visibility='always')
    study_school = fields.Char(track_visibility='always')
    emergency_contact = fields.Char(track_visibility='always')
    emergency_phone = fields.Char(track_visibility='always')
    km_home_work = fields.Integer(track_visibility='always')
    google_drive_link = fields.Char(track_visibility='always')
    job_title = fields.Char(track_visibility='always')
    address_id = fields.Many2one(track_visibility='always')
    work_phone = fields.Char(track_visibility='always')
    mobile_phone = fields.Char(track_visibility='always')
    work_email = fields.Char(track_visibility='always')
    work_location = fields.Char(track_visibility='always')
    # employee in company
    job_id = fields.Many2one(track_visibility='always')
    department_id = fields.Many2one(track_visibility='always')
    parent_id = fields.Many2one(track_visibility='always')
    child_ids = fields.One2many(track_visibility='always')
    coach_id = fields.Many2one(track_visibility='always')
    category_ids = fields.Many2many(track_visibility='always')
    notes = fields.Text(track_visibility='always')
    color = fields.Integer(track_visibility='always')
    is_treasury_employee = fields.Boolean(string='Is Treasury Employee')
    salary_payment_method = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string="Salary Payment Method",
                                             default='bank', track_visibility='always', required=True)

    
    def _compute_remaining_leaves(self):
        remaining = self._get_remaining_leaves()
        for employee in self:
            employee.remaining_leaves = 0
            if remaining.get(employee.id, 0.0) is not None:
                employee.remaining_leaves = float_round(remaining.get(employee.id, 0.0), precision_digits=3)

    # khalid 06/02/2023
    
    def _compute_leaves_count(self):
        all_leaves = self.env['hr.leave.report'].read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.allocation_type', '!=', 'no'),
            ('holiday_status_id.active', '=', 'True'),
            ('state', '=', ['hr_specialist', 'hr_manager', 'validate',
                            'internal_audit_manager', 'finance_manager', 'accountant'])
        ], fields=['number_of_days', 'employee_id'], groupby=['employee_id'])
        mapping = dict([(leave['employee_id'][0], leave['number_of_days']) for leave in all_leaves])
        for employee in self:
            employee.leaves_count = float_round(mapping.get(employee.id, 0), precision_digits=2)


    def _get_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                (
                    SELECT holiday_status_id, number_of_days,
                        state, employee_id
                    FROM hr_leave_allocation where is_annual_allocation= true 
                    UNION ALL
                    SELECT holiday_status_id, (number_of_days * -1) as number_of_days,
                        state, employee_id
                    FROM hr_leave
                ) h
                join hr_leave_type s ON (s.id=h.holiday_status_id)
            WHERE
                s.active = true And h.state in 
                ('validate','hr_specialist', 'hr_manager','internal_audit_manager','finance_manager', 'accountant')  AND
                s.requires_allocation='yes' AND
                h.employee_id in %s
            GROUP BY h.employee_id""", (tuple(self.ids),))
        return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())

    @api.constrains('mobile_private')
    def check_mobile_private(self):
        if self.mobile_private:
            if len(self.mobile_private) < 10:
                raise UserError(_("Private mobile number must be more than 10 digits."))

    @api.constrains('bsg_empiqama')
    def check_bsg_empiqma(self):
        if self.bsg_empiqama:
            iqama_id = self.env['hr.employee'].search(
                [('bsg_empiqama', '=', self.bsg_empiqama.id), ('id', '!=', self.id)])
            if iqama_id:
                raise UserError(_("Your Entered Iqama number is already taken by another user"))

    @api.constrains('bsg_national_id')
    def check_bsg_national(self):
        if self.bsg_national_id:
            national_id = self.env['hr.employee'].search(
                [('bsg_national_id', '=', self.bsg_national_id.id), ('id', '!=', self.id)])
            if national_id:
                raise UserError(_("Your Entered National ID is already taken by another user"))

    def _compute_dateofjoin(self):
        for rec in self:
            date_today = datetime.today().strftime('%Y-%m-%d')
            day_from = fields.Datetime.from_string(rec.bsgjoining_date)
            day_to = fields.Datetime.from_string(date_today)
            date_diff = relativedelta(day_to, day_from)
            lang = self._context.get('lang', False)
            experince_str = ""
            years_str = lang == 'en_US' and 'Years' or 'سنه'
            monthes_str = lang == 'en_US' and 'Years' or 'شهر'
            days_str = lang == 'en_US' and 'Years' or 'يوم'
            if date_diff.years > 0:
                experince_str += ' %s %s' % (date_diff.years, years_str)

            if date_diff.months > 0:
                sep = date_diff.years > 0 and ' ' or ''
                experince_str += '%s %s %s' % (sep, date_diff.months, monthes_str)

            days = date_diff.days + 1
            if days > 0:
                sep = date_diff.months > 0 and ' و ' or ''
                experince_str += '%s %s %s' % (sep, days, days_str)
            rec.bsg_totalyears = experince_str

    
    def write(self, vals):
        if vals.get('department_id'):
            # Required Code will be added here
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>")
        HrEmployeeObj = super(BsgInheritHrEmployee, self).write(vals)
        return HrEmployeeObj

    @api.model
    def create(self, vals):
        HrEmployeeObj = super(BsgInheritHrEmployee, self).create(vals)
        if HrEmployeeObj.department_id and HrEmployeeObj.department_id.is_branch and HrEmployeeObj.department_id.bsg_branch_id:
            HrEmployeeObj.department_id.bsg_branch_id.member_ids = [HrEmployeeObj.id]
        return HrEmployeeObj

    # get employee paid days on month based on company work day in month - (payroll day + unpaid holidays)
    def get_paid_days_data(self, from_date, to_date, leaves,payslip_id):
        """
        modify the origin method in resource ==> resource_mixin
        @param contract: payslip contract
        @param date_from: date field
        @param date_to: date field
        @return: returns dictionary off employee worked days and hours based on employee contract types
        """
        # payslip_obj = self.env['hr.payslip'].searh([('employee_id','=',self.id)
        #                                               ,('date_from','>=',from_date),('date_to','<=',from_date) ])
        unpaid_leave_days = 0
        for rec in leaves:
            hol = leaves[rec]
            if hol['code'] and hol['code'] != 'GLOBAL':
                # if hol['holiday_id'].current_month == from_date.month:
                # 	unpaid_leave_days += hol['holiday_id'].current_month_work_days
                unpaid_leave_days += hol['number_of_days']

        start_date = from_date
        end_date = to_date
        diff_days = abs(end_date - start_date)
        work_days = int(diff_days.days) + 1
        if payslip_id.type=='salary':
            if work_days > 30:
                work_days = 30
            elif start_date.month == 2:
                if work_days > 27:
                    work_days = 30


        # if int(work_days) > self.env.user.company_id.work_days:
        #   work_days = self.env.user.company_id.work_days
        if not self.last_return_date:
            raise UserError(_("Pls set effective date om employee before creating payslip"))

        if start_date.date() < self.last_return_date < end_date.date():
            return_days_diff = (self.last_return_date - start_date.date()).days
            work_days -= return_days_diff

        work_days -= unpaid_leave_days
        hours = 8 * work_days
        return {
            'days': work_days,
            'hours': hours,
        }

    def compute_service_years_from_dates(self, date_from, date_to):

        service_years = 0.0
        service_months = 0.0
        service_days = 0.0
        print("IIIIIIIIIIIIIIIIIII")
        start_date = fields.Datetime.from_string(date_from)
        end_date = fields.Datetime.from_string(date_to)
        print("offffffffffffffff", start_date.timetuple())
        start_y, start_m, start_d, start_h, min, sec, wd, yd, i = start_date.timetuple()
        print("3333333333333333333333333333333")
        end_y, end_m, end_d, end_h, min, sec, wd, yd, i = end_date.timetuple()
        service_years = end_y - start_y
        service_months = (end_m - start_m)
        service_days = (end_d - start_d)
        # print(service_years ,  service_months ,service_days)
        if (end_m - start_m) < 0 and (end_d - start_d) < 0:
            service_months = abs(12 - (start_m - end_m))
            service_years = service_years - 1
            service_days = abs(30 - (start_d - end_d))
            service_months = service_months - 1
        elif (end_d - start_d) < 0 and (end_m - start_m) >= 0:
            service_days = abs(30 - (start_d - end_d))
            service_months = service_months - 1
            if service_months < 0:
                service_months = abs(12 + (service_months))
                service_years = service_years - 1
        elif (end_m - start_m) < 0 and (end_d - start_d) >= 0:
            service_months = abs(12 - (start_m - end_m))
            service_years = service_years - 1
        else:
            service_years = end_y - start_y
            service_months = (end_m - start_m)
            service_days = (end_d - start_d)

        return service_years, service_months, service_days
