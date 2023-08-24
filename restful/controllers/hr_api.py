"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import logging
from odoo.exceptions import AccessError,AccessDenied
import ast
import re

from odoo import http, _, fields
from odoo.addons.restful.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request

_logger = logging.getLogger(__name__)
import base64
import datetime
import requests
import werkzeug.wrappers
import json
import logging
_logger = logging.getLogger(__name__)


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

class APIController(http.Controller):

    @http.route('/api/hr/auth', auth='none', methods=["POST"], csrf=False)
    def authenticate(self, db, login, password):
        # Before calling /api/auth, call /web?db=*** otherwise web service is not found
        try:
            request.session.authenticate(db, login, password)
        except AccessError as aee:
            data = {'status':500, 'message':'Access Error'}
            return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            response=json.dumps(data, default=default),)
        except AccessDenied as ade:
            data = {'status':500, 'message':'Invalid Username Or Password'}
            return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            response=json.dumps(data, default=default))
        except Exception as e:
            # Invalid database:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            data = {'status':500, 'message': 'Invalid Database Name'}
            return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            response=json.dumps(data, default=default))
        info = request.env['ir.http'].session_info()
        data = {'status':200,'session_id': info['session_id'], 'user_context': info['user_context'], 'expiration_date': info['expiration_date'], 'name': info['name'],'username': info['username'], 'db': info['db']}
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            response=json.dumps(data, default=default),
        )

    @http.route('/api/hr/payroll/slips', auth='user', methods=["POST"], csrf=False)
    def hr_employee_payroll_slips(self):
        uid = request.session.uid
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)
        recs = request.env['hr.payslip'].search([('employee_id', '=', employee.id),('state','=','paid')],order='date_from desc',limit=1)
        data = {'employee_code': employee.driver_code, 'employee_name':employee.name}
        slips = []
        for rec in recs:
            slips.append({
                'salary_payment_method': rec.salary_payment_method,
                'contract': rec.contract_id.name,
                'lines': rec.line_ids.read(['name', 'amount']),
                'net_total': rec.total_net,
                'state': rec.state

            })
        data['slips'] = slips 
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            response=json.dumps(data, default=default),
        )

    @http.route('/api/hr/employee/info', auth='user', methods=["POST"], csrf=False)
    def hr_employee_info(self):
        uid = request.session.uid
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)
        data = {
                'code': employee.driver_code,
                'name': employee.name, 
                'mobile':employee.mobile_phone,
                'job':employee.job_id.name,
                'department': employee.department_id.name,
                'manager': employee.parent_id.name,
                'email': employee.work_email,
                'join_date':employee.bsgjoining_date,
                'service_years':employee.bsg_totalyears,
                'leave_balance':employee.remaining_leaves,
                }
        recs = request.env['hr.leave'].sudo().search([('employee_id', '=', employee.id),('state','=','validate'),('request_unit_half', '=', False), ('request_unit_hours', '=', False)],order='request_date_from desc',limit=10)        
        leaves = []
        for rec in recs:
            leaves.append({
                'type': rec.holiday_status_id.name,
                'number_of_days': rec.number_of_days,
                'start_date': rec.request_date_from,
                'end_date': rec.request_date_to,
                'state' : rec.state,
            })
        data['leaves'] = leaves 
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            response=json.dumps(data, default=default),
        )
