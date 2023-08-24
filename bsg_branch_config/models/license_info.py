# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError

class BsgLicenseInfo(models.Model):
    _name = 'bsg.license.info'
    _inherit = ['mail.thread']
    _description = "License Info"
    _rec_name = 'branch_id'

    doc_type = fields.Many2one('bsg.branch.doc.type',string="Doc Type",required=True, tracking=True)
    document_no = fields.Char(string='Document No', tracking=True)
    issue_date = fields.Date("Issue Date", required=True, tracking=True)
    latest_renewal_date = fields.Date("Latest Renewal Date", tracking=True)
    expiry_date = fields.Date("Expiry Date", required=True, tracking=True)
    renewal = fields.Date("Due for Renewal", tracking=True)
    branch_id = fields.Many2one('bsg_branches.bsg_branches',string='Branch Name', tracking=True)
    active = fields.Boolean(string="Active", tracking=True, default=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Attachment")

    #
    @api.constrains('doc_type')
    def check_license_line(self):
        if self.doc_type:
            record_id = self.env['bsg.license.info'].search([('doc_type','=',self.doc_type.id),('id','!=',self.id),('branch_id','=',self.branch_id.id)])
            if record_id:
                raise UserError(_("Doc Type must Be Unique...!"))

    @api.model_create_multi
    def create(self, values):
        res =  super(BsgLicenseInfo, self).create(values)
        msg = _(
            """<div class="o_thread_message_content">
                <p>Bsg License Info Created</p>
                <ul class="o_mail_thread_message_tracking">
                <li>Doc Type : <span>{doc_type}</span></li>
                <li>Document No : <span>{document_no}</span></li>
                <li>Issue Date : <span>{issue_date}</span></li>
                <li>Latest Renewal Date : <span>{latest_renewal_date}</span></li>
                <li>Expiry Date : <span>{expiry_date}</span></li>
                <li>Due for Renewal : <span>{renewal}</span></li>
                </ul>
                </div>
                """.format(
                    doc_type=res.doc_type.branch_doc_type,
                    document_no=res.document_no,
                    issue_date=res.issue_date,
                    latest_renewal_date=res.latest_renewal_date,
                    expiry_date=res.expiry_date,
                    renewal=res.renewal
                )
            )
        res.branch_id.message_post(body=msg)
        return res

    #
    def write(self, vals):
        msg = _(
            """<div class="o_thread_message_content">
                <p>Bsg License Info Old Value</p>
                <ul class="o_mail_thread_message_tracking">
                <li>Doc Type : <span>{doc_type}</span></li>
                <li>Document No : <span>{document_no}</span></li>
                <li>Issue Date : <span>{issue_date}</span></li>
                <li>Latest Renewal Date : <span>{latest_renewal_date}</span></li>
                <li>Expiry Date : <span>{expiry_date}</span></li>
                <li>Due for Renewal : <span>{renewal}</span></li>
                </ul>
                </div>
                """.format(
                    doc_type=self.doc_type.branch_doc_type,
                    document_no=self.document_no,
                    issue_date=self.issue_date,
                    latest_renewal_date=self.latest_renewal_date,
                    expiry_date=self.expiry_date,
                    renewal=self.renewal
                )
            )
        self.branch_id.message_post(body=msg)
        res = super(BsgLicenseInfo, self).write(vals)
        msg = _(
            """<div class="o_thread_message_content">
                <p>Bsg License Info Modified</p>
                <ul class="o_mail_thread_message_tracking">
                <li>Doc Type : <span>{doc_type}</span></li>
                <li>Document No : <span>{document_no}</span></li>
                <li>Issue Date : <span>{issue_date}</span></li>
                <li>Latest Renewal Date : <span>{latest_renewal_date}</span></li>
                <li>Expiry Date : <span>{expiry_date}</span></li>
                <li>Due for Renewal : <span>{renewal}</span></li>
                </ul>
                </div>
                """.format(
                    doc_type=self.doc_type.branch_doc_type,
                    document_no=self.document_no,
                    issue_date=self.issue_date,
                    latest_renewal_date=self.latest_renewal_date,
                    expiry_date=self.expiry_date,
                    renewal=self.renewal
                )
            )
        self.branch_id.message_post(body=msg)
        return res

    #
    def unlink(self):
        for res in self:
            msg = _(
            """<div class="o_thread_message_content">
                <p>Bsg License Info Deleted</p>
                <ul class="o_mail_thread_message_tracking">
                <li>Doc Type : <span>{doc_type}</span></li>
                <li>Document No : <span>{document_no}</span></li>
                <li>Issue Date : <span>{issue_date}</span></li>
                <li>Latest Renewal Date : <span>{latest_renewal_date}</span></li>
                <li>Expiry Date : <span>{expiry_date}</span></li>
                <li>Due for Renewal : <span>{renewal}</span></li>
                </ul>
                </div>
                """.format(
                    doc_type=res.doc_type.branch_doc_type,
                    document_no=res.document_no,
                    issue_date=res.issue_date,
                    latest_renewal_date=res.latest_renewal_date,
                    expiry_date=res.expiry_date,
                    renewal=res.renewal
                )
            )
            res.branch_id.message_post(body=msg)
        return super(BsgLicenseInfo, self).unlink()
