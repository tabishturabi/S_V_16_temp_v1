# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from cryptography.fernet import Fernet
import logging
_logger = logging.getLogger(__name__)

class EmployeeServiceRequestPortal(http.Controller):

    # @http.route(['/requests/get_request/<int:service_id>'], type='http', auth="public", website=True)
    @http.route(['/requests/get_request/<string:service_id>/<string:fernet_key>/'], type='http', auth="public", website=True)
    def get_service(self, service_id,fernet_key, access_token=None, report_type=None, download=True, **kw):
        # API to get employee data
        # key = Fernet.generate_key()
        f = Fernet(fernet_key.encode())

        _logger.info(">>>>>>>>>>>>>>>>service_id ", service_id)
        _logger.info(">>>>>>>>>>>>>>>>service_id type ", type(service_id))

        byte_service_id = service_id.encode()

        _logger.info(">>>>>>>>>>>>>>>>byte_service_id ", byte_service_id)
        _logger.info(">>>>>>>>>>>>>>>>byte_service_id type ", type(byte_service_id))

        byte_decrypted_service_id = f.decrypt(byte_service_id)
        str_decrypted_service_id = byte_decrypted_service_id.decode()
        int_decrypted_service_id = int(str_decrypted_service_id)
        # service_data = request.env['employee.service'].sudo().search([('id', '=', service_id)])
        pdf, _ = request.env.ref('employee_service.employee_service_report').sudo().render_qweb_pdf([int_decrypted_service_id])
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

        # return request.render('employee_service.employee_service_pdf',
        #                       {
        #                           "docs": service_data,
        #                           "is_portal":True
        #                       })
