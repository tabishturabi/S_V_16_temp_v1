from odoo import fields, models,api


class HrLeaveType(models.Model):

    _inherit = "hr.leave.type"

    advance_request_years = fields.Integer("Advance Request Years")
    working_days = fields.Boolean("Working Days Only")
    official_holidays = fields.Boolean("Include Official Holidays")
    include_weekend = fields.Boolean("Include Weekend")
    exit_return_permission = fields.Boolean("Exit Return Permission")
    exit_return_permission_duration = fields.Integer("Exit Return Permission Duration")
    issuing_ticket = fields.Boolean("Issuing Ticket")
    period_ticket = fields.Integer("Period Ticket")
    mission_chick = fields.Boolean("Mission Chick")
    attach_chick = fields.Boolean("Attach Chick")
    alternative_chick = fields.Boolean("Alternative Chick")
    used_once = fields.Boolean("Used Once")
    issuing_clearance_form = fields.Boolean("Issuing Clearance Form")
    issuing_deliver_custody = fields.Boolean("Issuing Deliver Custody")
    minimum_duration = fields.Float("Minimum Duration")
    leave_type = fields.Selection(selection=[
        ('sick', 'Sick'), ('unpaid', 'Un Paid'), ('paid', 'Paid'),
        ('death', 'Death'), ('birth', 'Birth'), ('marry', 'Marry'),
        ('haj', 'Haj'), ('birthdelivery', 'Birth Delivery Female'),
        ('test', 'Exams or Tests'), ('other', 'Other'),],string="Leave Type")

    
    def get_days(self, employee_id):
        # need to use `dict` constructor to create a dict per id
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)

        requests = self.env['hr.leave'].search([
            ('employee_id', '=', employee_id),

            ('state', 'in', ['confirm', 'validate1', 'validate','draft', 'hr_specialist', 'hr_manager',
                             'internal_audit_manager','finance_manager', 'accountant']),
            ('holiday_status_id', 'in', self.ids)
        ])

        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids)
        ])

        for request in requests:
            status_dict = result[request.holiday_status_id.id]
            status_dict['virtual_remaining_leaves'] -= (request.number_of_hours_display
                                                    if request.leave_type_request_unit == 'hour'
                                                    else request.number_of_days)
            if request.state == 'validate':
                status_dict['leaves_taken'] += (request.number_of_hours_display
                                            if request.leave_type_request_unit == 'hour'
                                            else request.number_of_days)
                status_dict['remaining_leaves'] -= (request.number_of_hours_display
                                                if request.leave_type_request_unit == 'hour'
                                                else request.number_of_days)

        for allocation in allocations.sudo():
            status_dict = result[allocation.holiday_status_id.id]
            if allocation.state == 'validate':
                # note: add only validated allocation even for the virtual
                # count; otherwise pending then refused allocation allow
                # the employee to create more leaves than possible
                status_dict['virtual_remaining_leaves'] += (allocation.number_of_hours_display
                                                          if allocation.type_request_unit == 'hour'
                                                          else allocation.number_of_days)
                status_dict['max_leaves'] += (allocation.number_of_hours_display
                                            if allocation.type_request_unit == 'hour'
                                            else allocation.number_of_days)
                status_dict['remaining_leaves'] += (allocation.number_of_hours_display
                                                  if allocation.type_request_unit == 'hour'
                                                  else allocation.number_of_days)

        return result