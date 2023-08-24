from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ummalqura.hijri_date import HijriDate
from dateutil.relativedelta import relativedelta


class RenewalVehicleDocumentExt(models.Model):
    _inherit = 'renewal.vehicle.document'

    # @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_vehicle_enhancement.action_attachment')
        return res

    # @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'renewal.vehicle.document'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for renewal_vehicle in self:
            renewal_vehicle.attachment_number = attachment.get(renewal_vehicle.id, 0)

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            type_ids = []
            self.model_id_x = self.vehicle_id.model_id if self.vehicle_id.model_id else None
            self.vehicle_type_id_x = self.vehicle_id.vehicle_type if self.vehicle_id.vehicle_type else None
            if self.vehicle_type_id_x:
                self.analytic_account_id = self.vehicle_type_id_x.analytic_account_id if self.vehicle_type_id_x.analytic_account_id else None
            self.chassis_no_x = self.vehicle_id.vin_sn if self.vehicle_id.vin_sn else ''
            self.estmaira_serial_no_x = self.vehicle_id.estmaira_serial_no if self.vehicle_id.estmaira_serial_no else None
            self.driver_name_x = self.vehicle_id.bsg_driver if self.vehicle_id.bsg_driver else None
            self.driver_code_x = self.vehicle_id.bsg_driver.driver_code if self.vehicle_id.bsg_driver.driver_code else None
            self.plate_no_x = self.vehicle_id.plate if self.vehicle_id.plate else None
            self.vehicle_status_x = self.vehicle_id.vehicle_status if self.vehicle_id.vehicle_status else None
            self.model_year_x = self.vehicle_id.model_year if self.vehicle_id.model_year else None
            document_type_ids = self.env['document.info.fleet'].search(
                [('document_id', '=', self.vehicle_id.id)])
            for rec in document_type_ids:
                type_ids.append(rec.document_type_id.id)
            return {'domain': {'document_type': [('id', 'in', type_ids)]}}

    @api.onchange('document_type')
    def _onchange_document_type(self):
        if self.document_type and self.vehicle_id:
            dates = self.env['document.info.fleet'].search(
                [('document_id', '=', self.vehicle_id.id), ('document_type_id', '=', self.document_type.id)], limit=1)
            if dates:
                self.exp_date = dates.expiry_date if dates.expiry_date else False
                self.issue_date = dates.issue_date if dates.issue_date else False
                self.renewal_exp_date = self.issue_date + relativedelta(
                    years=self.document_type.year_of_renew) if self.issue_date and self.document_type.year_of_renew else False
            else:
                self.exp_date = False
                self.issue_date = False

        else:
            self.exp_date = False
            self.issue_date = False

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    user_id = fields.Many2one('res.users', string='Requester', track_visibility='always')
    expense_id = fields.Many2one('expense.accounting.petty', string='Expense ID', track_visibility='always')
    model_id_x = fields.Many2one('fleet.vehicle.model', string='Vehicle Name')
    vehicle_type_id_x = fields.Many2one('bsg.vehicle.type.table', string='Vehicle Type Name')
    chassis_no_x = fields.Char(string='Chassis Number')
    estmaira_serial_no_x = fields.Integer(string='Estmaira Serial No.')
    request_date = fields.Date(default=fields.Date.today, string='Request Date')
    sign_to = fields.Char(string='Sign To')
    driver_name_x = fields.Many2one('hr.employee', string='Driver Name')
    driver_code_x = fields.Char(string='Driver Code')
    plate_no_x = fields.Char(string='Plate No.')
    vehicle_status_x = fields.Many2one('bsg.vehicle.status', string='Vehicle Status')
    model_year_x = fields.Char(string='Model Year')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('submit', 'Submit'), ('manager_approval', 'Manager Approval'),
                              ('reject', 'Reject'), ('petty_cash', 'Petty Cash'), ('done', 'Done'),
                              ('cancel', 'Cancel')], string='State',
                             default='draft')

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    def set_expense_id(self, expense_id):
        if expense_id:
            self.write({'expense_id': expense_id, 'state': 'petty_cash'})

    def _get_label(self):
        for rec in self:
            label = ' تجديد ' + ' - ' + str(rec.document_type.name) + '-' + ' شاحنة رقم ' + ' - ' + str(
                rec.vehicle_id.taq_number)
            return label

    # @api.multi
    def action_petty_cash(self):
        if not self.user_id:
            raise UserError(_('Requester is mandatory for further process'))
        if self.state == 'manager_approval':
            expence_action = self.env.ref('advance_petty_expense_mgmt.petty_expence_create_wizard_action')
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            attach_ids = self.env['ir.attachment'].search(
                [('res_model', '=', 'renewal.vehicle.document'), ('res_id', 'in', self.ids)])
            action = expence_action.read()[0]
            action['context'] = "{'default_user_id':%d,\
                               'default_line_ref':'%s',\
                               'default_partner_id':%d,\
                               'default_analytic_account_id': %d,\
                               'default_branch_id': %d,\
                               'default_department_id': %d,\
                               'default_truck_id': %d,\
                               'default_label': '%s',\
                               'default_attach_files_ids': %s,\
                               }" % (self.user_id.id, self.name, False,
                                     self.analytic_account_id.id, self.env.user.user_branch_id.id,
                                     employee.department_id.id, self.vehicle_id.id, self._get_label(), attach_ids.ids)

            return action

    # @api.multi
    @api.constrains('exp_date', 'renewal_exp_date')
    def date_constrains(self):
        for rec in self:
            if rec.exp_date and rec.renewal_exp_date and rec.renewal_exp_date <= rec.exp_date:
                raise UserError(_('Sorry, Renewal Expiry Date Must be greater Than Expiry Date...'))
