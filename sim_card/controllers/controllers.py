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

    @http.route('/notify_inbox/employee_sim_approve/accept', type='http', auth="public")
    def request_approve_manager(self, db, token, id, **kwargs):
        request_sim_card = request.env['sim.card.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if request_sim_card:
            request_sim_card.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).approve_mng()
            return self.employee_sim_manager_view(db, id, token)

    @http.route('/notify_inbox/card_approve/view', type='http', auth="public", website=True)
    def employee_sim_manager_view(self, db, id, token):
        employee_sim_card = request.env['sim.card.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})

            response_content = env['ir.ui.view'].with_context().render_template(
                'housing.manager_page', {
                    'employee_sim_card': employee_sim_card,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    @http.route('/notify_inbox/request_reject/accept', type='http', auth="public")
    def request_reject_manager(self, db, token, id, **kwargs):
        request_reject_sim_card = request.env['sim.card.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if request_reject_sim_card:
            request_reject_sim_card.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).reject_mng()
            return self.request_reject_view(db, id, token)

    @http.route('/notify_inbox/request_reject_sim_card_reject/view', type='http', auth="public", website=True)
    def request_reject_view(self, db, id, token):
        request_reject_sim_card = request.env['sim.card.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            response_content = env['ir.ui.view'].with_context().render_template(
                'sim_card.manager_reject', {
                    'request_reject_sim_card': request_reject_sim_card,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    @http.route('/notify_inbox/finance/accept', type='http', auth="public")
    def finance_manger(self, db, token, id, **kwargs):
        ssim_card = request.env['sim.card.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if ssim_card:
            ssim_card.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).finance_approve()
            return self.finance_view(db, id, token)

    @http.route('/notify_inbox/finance/view', type='http', auth="public", website=True)
    def finance_view(self, db, id, token):
        ssim_card = request.env['sim.card.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})

            response_content = env['ir.ui.view'].with_context().render_template(
                'sim_card.finance_manager_page', {
                    'sim_card': ssim_card,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    @http.route('/notify_inbox/finance_reject/accept', type='http', auth="public")
    def finance_manger_reject (self, db, token, id, **kwargs):
        ssim_card = request.env['sim.card.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if ssim_card:
            ssim_card.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).finance_reject()
            return self.finance__reject_view(db, id, token)

    @http.route('/notify_inbox/finance_reject/view', type='http', auth="public", website=True)
    def finance__reject_view(self, db, id, token):
        ssim_card = request.env['sim.card.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})

            response_content = env['ir.ui.view'].with_context().render_template(
                'sim_card.finance_manager_reject', {
                    'sim_card': ssim_card,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    @http.route('/notify_inbox/upgrade_approve/accept', type='http', auth="public")
    def upgrade_approve_manager(self, db, token, id, **kwargs):
        sim_card_upgrade = request.env['upgrade.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if sim_card_upgrade:
            sim_card_upgrade.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).approve_mng()
            return self.manager_upgrade_view(db, id, token)

    @http.route('/notify_inbox/card_approve/view', type='http', auth="public", website=True)
    def manager_upgrade_view(self, db, id, token):
        sim_card_upgrade = request.env['upgrade.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})

            response_content = env['ir.ui.view'].with_context().render_template(
                'sim_card.manager_upgrade_page', {
                    'sim_card_upgrade': sim_card_upgrade,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    @http.route('/notify_inbox/upgrade_reject/accept', type='http', auth="public")
    def upgrdae_reject_manger(self, db, token, id, **kwargs):
        sim_card = request.env['upgrade.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if sim_card:
            sim_card.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).reject_mng()
            return self.upgrade_reject_view(db, id, token)

    @http.route('/notify_inbox/card_upgrade_reject/view', type='http', auth="public", website=True)
    def upgrade_reject_view(self, db, id, token):
        sim_card_upgrade_reject = request.env['upgrade.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            response_content = env['ir.ui.view'].with_context().render_template(
                'sim_card.manager_upgrade_reject', {
                    'sim_card_upgrade_reject': sim_card_upgrade_reject,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    @http.route('/notify_inbox/finance_upgrade_approve/accept', type='http', auth="public")
    def approve_manager(self, db, token, id, **kwargs):
        sim_card_finance_upgrade = request.env['upgrade.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if sim_card_finance_upgrade:
            sim_card_finance_upgrade.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).finance_approve()
            return self.finance_manager_upgrade_view(db, id, token)

    @http.route('/notify_inbox/card_approve/view', type='http', auth="public", website=True)
    def finance_manager_upgrade_view(self, db, id, token):
        sim_card_finance_upgrade = request.env['upgrade.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})

            response_content = env['ir.ui.view'].with_context().render_template(
                'sim_card.finance_upgrade_page', {
                    'sim_card_finance_upgrade': sim_card_finance_upgrade,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    @http.route('/notify_inbox/finance_upgrade_reject/accept', type='http', auth="public")
    def rejcet_manger(self, db, token, id, **kwargs):
        sim_card = request.env['upgrade.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)])
        if sim_card:
            sim_card.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).finance_reject()
            return self.finance_upgrade_reject_view(db, id, token)

    @http.route('/notify_inbox/finance_card_upgrade_reject/view', type='http', auth="public", website=True)
    def finance_upgrade_reject_view(self, db, id, token):
        sim_card = request.env['upgrade.request'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('id', '=', id)], limit=1)
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            response_content = env['ir.ui.view'].with_context().render_template(
                'sim_card.finance_manger_upgrade_reject', {
                    'sim_card': sim_card,
                    'id': id,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

