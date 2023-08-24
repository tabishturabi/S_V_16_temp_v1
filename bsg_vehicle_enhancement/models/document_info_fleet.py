# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ummalqura.hijri_date import HijriDate
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date, datetime


class DocumentInfoExt(models.Model):
    _inherit = 'document.info.fleet'

    # @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_vehicle_enhancement.action_attachment_fleet_all_access')
        if self.env.user.has_group('bsg_vehicle_enhancement.group_fleet_attachment_delete') or self.env.user._is_admin():
            res['context'] = {'default_res_model': 'fleet.vehicle', 'default_res_id': self.document_id.id,
                              'default_fleet_doc_type': self.document_type_id.id, 'create': True,
                              'edit': True, 'delete': True}
        elif self.env.user.has_group('bsg_vehicle_enhancement.group_fleet_attachment_view'):
            res['context'] = {'default_res_model': 'fleet.vehicle', 'default_res_id': self.document_id.id,
                              'default_fleet_doc_type': self.document_type_id.id, 'create': False,
                              'edit': False, 'delete': False}
        elif self.env.user.has_group('bsg_vehicle_enhancement.group_fleet_attachment_add'):
            res['context'] = {'default_res_model': 'fleet.vehicle', 'default_res_id': self.document_id.id,
                              'default_fleet_doc_type': self.document_type_id.id, 'create': True,
                              'edit': False, 'delete': False}
        res['domain'] = [('res_model', '=', 'fleet.vehicle'), ('res_id', 'in', self.document_id.ids)]
        return res

    hijri_issue_date = fields.Char(string='Hijri Issue Date', track_visibility=True, )
    name = fields.Char(related='document_type_id.name', string="Name", track_visibility=True, )
    vehicle_name = fields.Many2one('fleet.vehicle.model', string="Vehicle Name", track_visibility=True, )
    licence_plate = fields.Char(string='License Plate', track_visibility=True, )
    chassis_no = fields.Char(string='Chassis No', track_visibility=True, )
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    is_created = fields.Boolean(string="Active")
    descripiton = fields.Text(string="Description")
    renewel_license_date = fields.Date(string='Renewel License Date', default=date.today())
    last_update_date = fields.Date(string='Last Update Date', compute='get_write_date')

    @api.depends('write_date')
    def get_write_date(self):
        for rec in self:
            rec.last_update_date = rec.write_date.date()


    # @api.multi
    def _compute_attachment_number(self):
        for fleet in self:
            fleet.attachment_number = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'fleet.vehicle'), ('res_id', '=', fleet.document_id.id),
                 ('fleet_doc_type', '=', fleet.document_type_id.id)])

    # @api.multi
    def open_attach_wizard(self):
        view_id = self.env.ref('bsg_vehicle_enhancement.view_attachment_fleet_form').id
        default_name = str(self.issue_date)+str(self.document_type_id.document_type_id)+" "+ "الشاحنة رقم" + " " + str(self.document_id.taq_number) + " " + "لصادرة في تاريخ" + " "
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_name': '%s','default_res_model': '%s','default_res_id': %d,'default_fleet_doc_type': %d,'default_check_fleet':True}" % (default_name,"fleet.vehicle", self.document_id.id, self.document_type_id.id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    # @api.one
    @api.constrains('document_type_id')
    def check_document_type_id(self):
        if self.document_type_id:
            record_id = self.env['document.info.fleet'].search(
                [('document_type_id', '=', self.document_type_id.id), ('id', '!=', self.id),
                 ('document_id', '=', self.document_id.id)])
            if record_id:
                raise UserError(_("Doc Type must Be Unique...!"))

    @api.onchange('document_type_id')
    def _onchange_document_type(self):
        if self.document_type_id:
            year_of_renew = self.document_type_id.year_of_renew
            if year_of_renew:
                self.expiry_date = date.today() + relativedelta(years=year_of_renew)
            else:
                self.expiry_date = False

    @api.onchange('document_id')
    def onchange_document_id(self):
        if self.document_id:
            self.licence_plate = self.document_id.license_plate
            self.chassis_no = self.document_id.vin_sn
            self.vehicle_name = self.document_id.model_id
            # self.active = True
        else:
            self.licence_plate = False
            self.chassis_no = False
            self.vehicle_name = False

    @api.model
    def create(self, vals):
        res = super(DocumentInfoExt, self).create(vals)
        res.is_created = True
        res.get_arabic_issue_date()
        res.get_arabic_dates()
        return res

    @api.onchange('issue_date')
    def get_arabic_issue_date(self):
        if self.issue_date:
            self.hijri_issue_date = HijriDate.get_hijri_date(self.issue_date)

    @api.onchange('hijri_issue_date')
    def get_arabic_hijri_issue_date(self):
        if self.hijri_issue_date:
            if len(self.hijri_issue_date) == 10:
                self.issue_date = HijriDate.get_georing_date(self.hijri_issue_date)
            else:
                raise UserError(
                    _('Please input hijri date by using format [1441-07-27,Year-Month-Day]'))

    @api.onchange('hijri_date')
    def get_arabic_exp_hijri_date(self):
        if self.hijri_date:
            if len(self.hijri_date) == 10:
                self.expiry_date = HijriDate.get_georing_date(self.hijri_date)
            else:
                raise UserError(
                    _('Please input hijri date by using format [1441-02-27,Year-Month-Day]'))
