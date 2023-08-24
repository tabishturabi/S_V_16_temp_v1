# -*- coding: utf-8 -*-
 
import base64
from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as df
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
 
 
class CustomersPortal(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        values = super(CustomersPortal, self)._prepare_portal_layout_values()
        invoice = request.env['account.move'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id)
        values['invoice_count'] = request.env['account.move'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search_count([('partner_id','=',request.env.user.partner_id.id)])
        return values
 
 
    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']
        user = request.env.user
        domain = []
#         domain = [('user_id','=',request.env.user.id)]
        domain = [('partner_id','=',request.env.user.partner_id.id)]
 
        searchbar_sortings = {
            'date': {'label': _('Invoice Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Invoice Due Date'), 'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
 
        archive_groups = self._get_archive_groups('account.move', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
 
        # count for pager
        invoice_count = request.env['account.move'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_invoices_history'] = invoices.ids[:100]
 
        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("account.portal_my_invoices", values)
