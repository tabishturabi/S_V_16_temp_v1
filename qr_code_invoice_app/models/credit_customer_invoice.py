from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError,Warning
from datetime import datetime
from itertools import groupby
from num2words import num2words
from .qr_generator import generateQrCode
from odoo.tools import html2plaintext
import base64
from odoo.http import request



class QRCodeCreditCustomerCollection(models.Model):
    _inherit = "credit.customer.collection"


    qr_image = fields.Binary("QR Code", compute='_compute_qr_code_str', compute_sudo=True)

    # @api.one
    def _generate_qr_code(self):
        qr_info = ''
        if self.env.user.company_id.invoice_qr_type != 'by_info':
            qr_info = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            qr_info += self.get_portal_url()
        else:
            if self.env.user.company_id.invoice_field_ids:
                result = self.search_read([('id', 'in', self.ids)],
                                          self.env.user.company_id.invoice_field_ids.mapped('field_id.name'))
                dict_result = {}
                for ffild in self.env.user.company_id.invoice_field_ids.mapped('field_id'):
                    if ffild.ttype == 'many2one':
                        dict_result[ffild.field_description] = self[ffild.name].display_name
                    elif ffild.name == 'access_url':
                        invoice_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        invoice_url += self.get_portal_url()
                        dict_result[ffild.field_description] = invoice_url
                    else:
                        dict_result[ffild.field_description] = self[ffild.name]
                for key, value in dict_result.items():
                    if str(key).__contains__('Partner') or str(key).__contains__(_('Partner')):
                        if self.type in ['out_invoice', 'out_refund']:
                            key = str(key).replace(_('Partner'), _('Customer'))
                        elif self.type in ['in_invoice', 'in_refund']:
                            key = str(key).replace(_('Partner'), _('Vendor'))
                    qr_info += f"{key} : {value} <br/>"
                qr_info = html2plaintext(qr_info)
        self.qr_image = generateQrCode.generate_qr_code(qr_info)

    l10n_sa_qr_code_str = fields.Char(string='Zatka QR Code', compute='_compute_qr_code_str')

    def _compute_qr_code_str(self):
        """ Generate the qr code for Saudi e-invoicing. Specs are available at the following link at page 23
        https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
        """

        def get_qr_encoding(tag, field):
            company_name_byte_array = field.encode('UTF-8')
            company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
            company_name_length_encoding = len(company_name_byte_array).to_bytes(length=1, byteorder='big')
            return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array

        for record in self:
            qr_code_str = ''
            if record.create_date and record.company_id.vat:
                seller_name_enc = get_qr_encoding(1, record.company_id.display_name)
                company_vat_enc = get_qr_encoding(2, record.company_id.vat)
                time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'), record.create_date)
                timestamp_enc = get_qr_encoding(3, time_sa.isoformat())
                invoice_total_enc = get_qr_encoding(4, str(record.amount_total))
                total_vat_enc = get_qr_encoding(5, str(record.currency_id.round(
                    record.amount_total - (record.amount_total - sum(record.cargo_sale_line_ids.mapped('tax_amount'))))))

                str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
                qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
            record.l10n_sa_qr_code_str = qr_code_str
            record.qr_image = generateQrCode.generate_qr_code(record.l10n_sa_qr_code_str)

