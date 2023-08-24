# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug

from odoo.api import Environment
import odoo.http as http
from odoo.http import request


from odoo.http import request
from odoo import SUPERUSER_ID
from odoo import registry as registry_get


class NotifyController(http.Controller):

    @http.route('/notify_inbox/employee_decision_approve/accept', type='http', auth="public")
    def request_approve_manager(self, db, token, id, **kwargs):
        request_employee_decision = request.env['employees.appointment'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if request_employee_decision:
            request_employee_decision.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).approve_mng()
            return self.employee_decision_manager_view(db, id, token)

    @http.route('/notify_inbox/card_approve/view', type='http', auth="public", website=True)
    def employee_decision_manager_view(self, db, id, token):
        employee_decision = request.env['employees.appointment'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})

            response_content = env['ir.ui.view'].with_context().render_template(
                'bsg_hr_employees_decisions.manager_page', {
                    'employee_decision': employee_decision,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])