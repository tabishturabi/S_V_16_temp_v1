# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
from ast import literal_eval

class BarriersConformityCertificate(models.Model):
    _inherit = 'sale.order'
    _description = 'For Barriers Conformity Certificate'

    # certificate_no = fields.Char(string='Certificate No',readonly=True)
    reference_no = fields.Char(string='Referencef NO')
    notes = fields.Char(string='Notes')
    date = fields.Date(string='Date',default=fields.date.today())
    price = fields.Monetary(string='Price',default=300)
    truck_owner = fields.Char(string="Truck/Trailer's Owner")
    manufacturer = fields.Char(string='Manufacturer', compute="get_settings_data")
    manufacturer_code = fields.Char(string='Manufactuere Code', compute="get_settings_data")
    truck_type = fields.Char(string="Truck/Trailer's Type")
    chasis_no = fields.Char(string='Chasis NO')
    plate_location = fields.Selection([('front', 'Front'),('back', 'Back'),('side', 'Side')],
                                      string='Plat Location')
    truck_serial_no = fields.Char(string='Truck Serial NO')
    bcc_check = fields.Boolean(string="BCC Check", compute="get_bcc_check")

    # @api.multi
    def action_confirm(self):
        res = super(BarriersConformityCertificate, self).action_confirm()
        self.action_invoice_create()
        return res

    @api.depends('manufacturer', 'manufacturer_code')
    def get_settings_data(self):
        saso_config_id = self.env.ref('bsg_barriers_conformity_certificate.saso_settings_data', False)
        if saso_config_id:
            self.manufacturer = saso_config_id.manufacturer
            self.manufacturer_code = saso_config_id.manufacturer_code

    @api.onchange('partner_id')
    def get_trailer_owner(self):
        if self.partner_id:
            self.truck_owner = self.partner_id.name

    def get_bcc_check(self):
        if self.invoice_ids:
            paid_invoice_ids = self.invoice_ids.filtered(lambda l: l.state == 'paid')
            if paid_invoice_ids:
                self.bcc_check = True
            else:
                self.bcc_check = False

    def print_bcc_order(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_barriers_conformity_certificate.bcc_report_pdf_id').report_action(
            self, data=data)


class BarriersConfirmityCertificatePdf(models.AbstractModel):
    _name = 'report.bsg_barriers_conformity_certificate.bcc_report_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs
        }

class SasoAccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = "Add domain to Payment Journal"


    @api.onchange('journal_id')
    def onchange_journal(self):
        if self.env.user.company_id.id == 3 and self.env.user.has_group('bsg_barriers_conformity_certificate.groups_saso_users'):
            saso_config_id = self.env.ref('bsg_barriers_conformity_certificate.saso_settings_data', False)
            journals_list = []
            if saso_config_id:
                bcc_journal_ids = saso_config_id.bcc_journal_ids
                if bcc_journal_ids:
                    journals_list = bcc_journal_ids.ids
            return {'domain': {'journal_id': [('id', '=', journals_list)]}}










