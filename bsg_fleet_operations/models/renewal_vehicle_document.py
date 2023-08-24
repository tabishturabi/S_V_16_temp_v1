# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ummalqura.hijri_date import HijriDate


class RenewalVehicleDocument(models.Model):
    _name = 'renewal.vehicle.document'
    _inherit = ['mail.thread']
    _description = 'All About Renewal Vehicle Documents'
    _order = 'name asc'
    
    name = fields.Char(string='Name', readonly=True)
    document_type = fields.Many2one('documents.type', string='Document Type')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle Sticker No. #')
    model_id = fields.Many2one('fleet.vehicle.model', related='vehicle_id.model_id', string='Vehicle Name')
    vehicle_type_id = fields.Many2one('bsg.vehicle.type.table', related='vehicle_id.vehicle_type',
                                      string='Vehicle Type Name')
    chassis_no = fields.Char(related='vehicle_id.vin_sn', string='Chassis Number')
    estmaira_serial_no = fields.Integer(related='vehicle_id.estmaira_serial_no', string='Estmaira Serial No.')
    request_date = fields.Date(default=fields.Date.today, string='Request Date')
    sign_to = fields.Char(string='Sign To')
    driver_name = fields.Many2one('hr.employee', related='vehicle_id.bsg_driver', string='Driver Name')
    driver_code = fields.Char(related='vehicle_id.driver_code', string='Driver Code')
    plate_no = fields.Char(related='vehicle_id.license_plate', string='Plate No.')
    vehicle_status = fields.Many2one('bsg.vehicle.status', related='vehicle_id.vehicle_status', string='Vehicle Status')
    model_year = fields.Char(related='vehicle_id.model_year', string='Model Year')

    # Document Information

    exp_date_hajri = fields.Char(string='Expiration Date Hajri')
    exp_date = fields.Date(string='Expiration Date')
    comment = fields.Text(string='Comment')
    renewal_exp_date_hajri = fields.Char(string='Renewal Expiration Date Hajri')
    renewal_exp_date = fields.Date(string='Renewal Expiration Date')
    attechment = fields.Many2many('ir.attachment', string='Attachment')

    # Manager Rejects
    manager_comment = fields.Text(string='Comments')
    manager_date = fields.Date(default=fields.Date.today, string='Date')

    # Expense Line
    renew_expense_line = fields.One2many('renew.expense.line', 'renew_vehicle_id', string='Renew Expense Line')

    # Other Info
    document_info = fields.Char(string='Document Info')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('submit', 'Submit'), ('manager_approval', 'Manager Approval'),
                              ('reject', 'Reject'), ('expense_insurance', 'Expense Insurance'),
                              ('petty_cash', 'Petty Cash'), ('done', 'Done'), ('cancel', 'Cancel')], string='State',
                             default='draft')

    issue_date = fields.Date(string='Issue Date')

    @api.model
    def create(self, vals):
        res = super(RenewalVehicleDocument, self).create(vals)
        if self.env.user.user_branch_id.branch_no:
            res.name = 'VDR-' + self.env.user.user_branch_id.branch_no + self.env['ir.sequence'].next_by_code(
                'renewal.vehicle.document')
        else:
            res.name = 'VDR-' + self.env['ir.sequence'].next_by_code('renewal.vehicle.document')
        return res

    @api.onchange('renewal_exp_date')
    def onchange_renewal_exp_date(self):
        if self.renewal_exp_date:
            self.renewal_exp_date_hajri = HijriDate.get_hijri_date(self.renewal_exp_date)

    @api.onchange('renewal_exp_date_hajri')
    def onchange_renewal_exp_date_hajri(self):
        if self.renewal_exp_date_hajri:
            if len(self.renewal_exp_date_hajri) == 10:
                self.renewal_exp_date = HijriDate.get_georing_date(self.renewal_exp_date_hajri)
            else:
                raise UserError(
                    _('Please input hijri date by using format [1441-02-27,Year-Month-Day]'))

    @api.onchange('exp_date')
    def onchange_exp_date(self):
        if self.exp_date:
            self.exp_date_hajri = HijriDate.get_hijri_date(self.exp_date)

    @api.onchange('exp_date_hajri')
    def onchange_exp_date_hajri(self):
        if self.exp_date_hajri:
            if len(self.exp_date_hajri) == 10:
                self.exp_date = HijriDate.get_georing_date(self.exp_date_hajri)
            else:
                raise UserError(
                    _('Please input hijri date by using format [1441-02-27,Year-Month-Day]'))

    @api.onchange('vehicle_id')
    def get_date_from_document(self):
        if self.vehicle_id.document_ids:
            for docs in self.vehicle_id.document_ids:
                self.exp_date = docs.expiry_date
                self.exp_date_hajri = docs.hijri_date

    # @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    # @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirm'})

    # @api.multi
    def action_submit(self):
        return self.write({'state': 'submit'})

    # @api.multi
    def action_manager_approval(self):
        return self.write({'state': 'manager_approval'})

    # @api.multi
    def action_manager_reject(self):
        return self.write({'state': 'reject'})

    # @api.multi
    def action_expense_insurance(self):

        return self.write({'state': 'expense_insurance'})

    # @api.multi
    def action_petty_cash(self):
        return self.write({'state': 'petty_cash'})

    # @api.multi
    def action_done(self):
        if self.vehicle_id and self.document_type:
            var = self.env['document.info.fleet'].search(
                [('document_id', '=', self.vehicle_id.id), ('document_type_id', '=', self.document_type.id)], limit=1)
            var.write({'issue_date': self.issue_date, 'hijri_issue_date': HijriDate.get_hijri_date(self.exp_date),
                       'expiry_date': self.renewal_exp_date,
                       'hijri_date': HijriDate.get_hijri_date(self.renewal_exp_date)})
        return self.write({'state': 'done'})

    # @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})


class RenewExpenseLine(models.Model):
    _name = 'renew.expense.line'
    _description = 'All About Renew Expense Line'

    renew_vehicle_id = fields.Many2one('renewal.vehicle.document', string='Renew Vehicle')
    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Char(string='Description')
    inv_ref = fields.Char(string='Inv Ref.')
    account_id = fields.Many2one('account.account', string='Account')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Branch')
    department_id = fields.Many2one('hr.department', string='Department')
    truck_id = fields.Many2one('fleet.vehicle', string='Truck')
    account_tag_ids = fields.Many2many('account.account.tag', string='Analytic Tags')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    unit_price = fields.Float(string='Unit Price')
    discount = fields.Float(string='Discount %')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    sub_total = fields.Float(string='Amount')
    attachment = fields.Many2many('ir.attachment', string='Attachment')
