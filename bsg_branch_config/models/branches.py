# -*- coding: utf-8 -*-
import datetime
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class BsgBranches(models.Model):
    _name = 'bsg_branches.bsg_branches'
    _inherit = ['mail.thread']
    _description = "BsgBranches"

    logo = fields.Binary(string="Image")
    branch_no = fields.Char(string="Branch No", tracking=True)
    branch_name = fields.Char(string="Branch", tracking=True)
    branch_ar_name = fields.Char(string="Arabic Name", tracking=True)
    branch_cp_name = fields.Char(string="Contact Person")
    branch_phone = fields.Char(tracking=True)
    branch_long = fields.Char(string="Longitude", tracking=True)
    branch_lat = fields.Char(string="Latitude", tracking=True)
    branch_div = fields.Char(string="Division", tracking=True)
    rml_header1 = fields.Char(string="Branch Tagline", tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    city = fields.Char("City", tracking=True)
    state_id = fields.Many2one('res.country.state', string='State', tracking=True)
    state_zip = fields.Char(tracking=True)
    country_id = fields.Many2one('res.country', string="Country", tracking=True)
    mobile = fields.Char(tracking=True)
    fax = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    vat = fields.Char(string="Tax ID", tracking=True)
    company_registry = fields.Char(string="Company Registry", tracking=True)
    region = fields.Many2one('region.config', string="Region", tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", tracking=True)
    po_box_no = fields.Char(string="P.O Box No", tracking=True)
    location_code = fields.Char(string="LocationCode", tracking=True)
    record_name = fields.Char(compute="_compute_name", string="Name", tracking=True)
    bsg_license_info_ids = fields.One2many('bsg.license.info', 'branch_id', string="License Documents")
    bsg_sponsor_info_ids = fields.One2many('bsg.sponsor.info', 'branch_id', string="Sponsors")
    member_ids = fields.One2many(string="Members", comodel_name="hr.employee", inverse_name="bsg_branch_id")
    branch_type = fields.Selection(string="Branch Type", selection=[
        ('pickup', 'Pickup'),
        ('shipping', 'Shipping'),
        ('both', 'Both')], tracking=True, default="")
    branch_operation = fields.Selection(string="Branch Operation", tracking=True, selection=[
        ('domestic', 'Domestic'),
        ('international', 'International'), ], default="")
    branch_classifcation = fields.Many2one(string="Sales Classifcation", comodel_name="bsg.branch.classification",
                                           tracking=True)
    hr_classifcation = fields.Many2one(string="HR Classifcation", comodel_name="bsg.branch.classification",
                                       tracking=True)
    active = fields.Boolean(string="Active", tracking=True, default=True)
    activation_date = fields.Date('Activation Date', tracking=True)
    deactivation_date = fields.Date('Deactivation Date', readonly=True, tracking=True)
    account_id = fields.Many2one(string="Old Analytic Account", tracking=True,
                                 comodel_name="account.analytic.account")
    account_analytic_id = fields.Many2one("account.analytic.account", tracking=True, string="Analytic Account")
    is_closed_branch = fields.Boolean('Is Closed Brnach')
    is_hq_branch = fields.Boolean('Is HQ Brnach')
    supervisor_id = fields.Many2one('hr.employee', string="Branch Supervisor")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, store=True,
                                 string="Company", track_visibility='always')

    region = fields.Many2one(readonly=True)
    region_city = fields.Many2one('region.config.line', string='Region City', readonly=True)
    zone_id = fields.Many2one('branches.zones', string='Zone', track_visibility='always', readonly=True)
    check = fields.Boolean(string='Check')
    weekly_working_hours = fields.Char(string="Weekly Working Hours", track_visibility='always')
    friday_working_hours = fields.Char(string="Friday Working Hours", track_visibility='always')
    description = fields.Char(string='Description', track_visibility='always')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('branch_no', operator, name)] + args, limit=limit)
            if not recs:
                recs = self.search([('branch_name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('branch_ar_name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.model_create_multi
    def create(self, vals):
        res = super(BsgBranches, self).create(vals)
        WaypointObj = self.env['bsg_route_waypoints']
        WaypointObj.create({
            'route_waypoint_name': res.branch_name,
            'location_type': 'albassami_loc',
            'loc_branch_id': res.id,
            'location_long': res.branch_long,
            'location_lat': res.branch_lat,
            'region': res.region.id,
        })
        return res

    # compute and search fields, in the same order of fields declaration
    #
    def _compute_name(self):
        self.record_name = self.branch_name or self.branch_ar_name or 'Name not defined'

    #
    def toggle_active(self):
        _logger.info(">>>>>>>>>>>>>>>>>bsg_branches.bsg_branches, toggle_active ", str(self))
        for rec in self:
            if rec.active:
                rec.deactivation_date = str(datetime.now())
        return super(BsgBranches, self).toggle_active()

    #
    @api.constrains('bsg_license_info_ids')
    def validation_expiry(self):
        for res in self.bsg_license_info_ids:
            if res.latest_renewal_date and res.latest_renewal_date <= res.issue_date:
                raise UserError(_("Latest Renewal Date Should be greater Than Issue Date"))
            elif res.expiry_date and res.expiry_date <= res.issue_date:
                raise UserError(_("Expiry Date Should be greater Than Issue Date"))
            elif res.renewal and res.renewal <= res.issue_date:
                raise UserError(_("Due for Renewal Should be greater Than Issue Date"))
