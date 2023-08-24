# -*- coding: utf-8 -*-

from odoo import http, fields as odoo_fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import werkzeug
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, groupby as groupbyelem
from datetime import datetime, timedelta
import pytz 
import collections, functools, operator
import requests
from odoo.osv.expression import AND
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils
from operator import itemgetter
import werkzeug




class VechialPortalSale(CustomerPortal):
    
    @http.route(['/custom_clearance/',  '/custom_clearance/page/<int:page>'], auth='user', website=True)
    def custom_clearance_orders(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='location_from', **kw):
        if not request.env.user.has_group('portal_sales.group_custom_clearance_user'):
            return werkzeug.utils.redirect('/', 303)

        line_sudo = request.env['bsg_vehicle_cargo_sale_line'].sudo()
        domain = [('loc_to', 'in',[1016, 928]), ('state', 'not in', ['cancel', 'draft'])]
        values = self._prepare_portal_layout_values()
        today = odoo_fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'order_date desc'},
            'name': {'label': _('Number'), 'order': 'sale_line_rec_name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        searchbar_inputs = {
            'sale_line_rec_name': {'input': 'sale_line_rec_name', 'label': _('Search in order number')},
            'general_plate_no': {'input': 'general_plate_no', 'label': _('Search in plate number')},
            'chassis_no': {'input': 'chassis_no', 'label': _('Search in chassis  number')},
            'sender_reciever': {'input': 'sender_reciever', 'label': _('Search in Sender / Reciever')},
            'car_color': {'input': 'car_color', 'label': _('Search in color')},
            'year': {'input': 'year', 'label': _('Search in year')}
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'location_from': {'input': 'location_from', 'label': _('Location From')},
            'location_to': {'input': 'location_to', 'label': _('Location To')},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'last_year': {'label': _('Last Year'), 'domain': [('order_date', '>=',last_year)]},
            'last_month': {'label': _('Last Month'), 'domain': [('order_date', '>=',last_month )]},
            'last_week': {'label': _('Last Week'), 'domain': [('order_date', '>=',last_week )]},
            'today': {'label': _('Today'), 'domain': [("order_date", "=", today)]},
    
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if not filterby:
            filterby = 'all'
        # domain = AND([domain, searchbar_filters[filterby]['domain']])
        if search and search_in:
            if search_in == 'all':
                domain = AND([domain, [('sale_line_rec_name', 'ilike', search)]])
            elif search_in == 'sender_reciever':
                domain = AND([domain, ['|', '|','|',
                                        ('bsg_cargo_sale_id.sender_id_card_no', 'ilike', search),('bsg_cargo_sale_id.sender_name', 'ilike', search),
                                        ('receiver_id_card_no', 'ilike', search), ('receiver_name', 'ilike', search)]])
            else:
                domain = AND([domain, [(search_in, 'ilike', search)]])
        sale_line_count = line_sudo.search_count(domain)
        pager = portal_pager(
            url="/custom_clearance/",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=sale_line_count,
            page=page,
            step=self._items_per_page
        )
        if groupby == 'location_from':
            order = "loc_from, %s" % order
        if groupby == 'location_to':
            order = "loc_to, %s" % order
        lines = line_sudo.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'location_from':
            grouped_lines = [line_sudo.concat(*g) for k, g in groupbyelem(lines, itemgetter('loc_from'))]
        if groupby == 'location_to':
            grouped_lines = [line_sudo.concat(*g) for k, g in groupbyelem(lines, itemgetter('loc_to'))]
        else:
            grouped_lines = [lines]

        values = {
            'sale_line_ids': lines,
            'grouped_lines': grouped_lines,
            'page_name': 'drug',
            'default_url': '/custom_clearance/',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'is_helpdesk': False
        }
        return http.request.render('portal_sales.portal_custom_clearance', values)