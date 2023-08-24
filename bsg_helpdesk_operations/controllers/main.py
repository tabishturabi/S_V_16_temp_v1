# -*- coding: utf-8 -*-
 
import base64
from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as df
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import http, fields as odoo_fields, _
import os
# from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.website.controllers import form
from odoo.addons.base.models.ir_qweb_fields import nl2br

class WebsiteForm(form.WebsiteForm):

    def insert_record(self, request, model, values, custom, meta=None):
        model_name = model.sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).model
        record = request.env[model_name].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).with_context({'mail_create_nosubscribe': True, 'default_company_id': request.website.company_id.id}).create(values)

        if custom or meta:
            default_field = model.website_form_default_field_id
            default_field_data = values.get(default_field.name, '')
            custom_content = (default_field_data + "\n\n" if default_field_data else '') \
                           + (self._custom_label + custom + "\n\n" if custom else '') \
                           + (self._meta_label + meta if meta else '')

            # If there is a default field configured for this model, use it.
            # If there isn't, put the custom data in a message instead
            if default_field.name:
                if default_field.ttype == 'html' or model_name == 'mail.mail':
                    custom_content = nl2br(custom_content)
                record.update({default_field.name: custom_content})
            else:
                values = {
                    'body': nl2br(custom_content),
                    'model': model_name,
                    'message_type': 'comment',
                    'no_auto_thread': False,
                    'res_id': record.id,
                }
                mail_id = request.env['mail.message'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).with_context({'default_company_id': request.website.company_id.id}).create(values)

        return record.id
 
class CustomersPortal(CustomerPortal):
    

    @http.route('/ticket/re-open/<int:ticket_id>', type='http', auth="user", website=True)
    def portal_ticket_reopen(self,ticket_id):
        ticket = request.env['helpdesk.ticket'].sudo().search([('id','=',ticket_id)])
        if ticket and ticket.stage_id.is_closed:
            state = request.env['helpdesk.stage'].sudo().search([('is_re_open','=',True)])
            if state:
                try:
                    ticket.write({'stage_id':state.id})
                except:
                    ticket.sudo().write({'stage_id':state.id})
        return request.redirect('/helpdesk/ticket/%s'%ticket_id)

    def _prepare_portal_layout_values(self):
        values = super(CustomersPortal, self)._prepare_portal_layout_values()
        helpdesk = request.env['helpdesk.ticket'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id)
        values['ticket_count'] = request.env['helpdesk.ticket'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search_count([('partner_id','=',request.env.user.partner_id.id)])
        return values


    def _get_archive_groups(self, model, domain=None, fields=None, groupby="create_date", order="create_date desc"):
        if not model:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'create_date']
        groups = []
        for group in request.env[model].sudo()._read_group_raw(domain, fields=fields, groupby=groupby, orderby=order):
            dates, label = group[groupby]
            date_begin, date_end = dates.split('/')
            groups.append({
                'date_begin': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_begin)),
                'date_end': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_end)),
                'name': label,
                'item_count': group[groupby + '_count']
            })
        return groups
    
    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', **kw):
#         if request.env.user.has_group('base.group_user'):
            values = self._prepare_portal_layout_values()
             
            user = request.env.user
            domain = [('partner_id','=',request.env.user.partner_id.id)]
     
            searchbar_sortings = {
                'date': {'label': _('Newest'), 'order': 'create_date desc'},
                'name': {'label': _('Subject'), 'order': 'name'},
            }
            searchbar_inputs = {
                'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
                'message': {'input': 'message', 'label': _('Search in Messages')},
                'customer': {'input': 'customer', 'label': _('Search in Customer')},
                'all': {'input': 'all', 'label': _('Search in All')},
            }
     
            # default sort by value
            if not sortby:
                sortby = 'date'
            order = searchbar_sortings[sortby]['order']
     
            # archive groups - Default Group By 'create_date'
            archive_groups = self._get_archive_groups('helpdesk.ticket', domain)
            if date_begin and date_end:
                domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
     
            # search
            if search and search_in:
                search_domain = []
                if search_in in ('content', 'all'):
                    search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
                if search_in in ('customer', 'all'):
                    search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
                if search_in in ('message', 'all'):
                    search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
                domain += search_domain
     
            # pager
            tickets_count = request.env['helpdesk.ticket'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search_count(domain)
            pager = portal_pager(
                url="/my/tickets",
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                total=tickets_count,
                page=page,
                step=self._items_per_page
            )
     
            tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
            request.session['my_tickets_history'] = tickets.ids[:100]
     
            values.update({
                'date': date_begin,
                'grouped_tickets': tickets,
                'page_name': 'ticket',
                'default_url': '/my/tickets',
                'pager': pager,
                'archive_groups': archive_groups,
                'searchbar_sortings': searchbar_sortings,
                'searchbar_inputs': searchbar_inputs,
                'sortby': sortby,
                'search_in': search_in,
                'search': search,
                'is_helpdesk': True
            })
            return request.render("helpdesk.portal_helpdesk_ticket", values)

class Helpdesk(http.Controller):
    
    @http.route(['/updates'], type='http', auth="user", website=True)
    def updatepage(self, **kw):
        
        return request.render('website.updates')
    
    

    @http.route('/my/new/helpdesk', type='http', auth="user", website=True)
    def portal_my_helpdesk_view(self, helpdesk_id=None,message=None, **kw):
        values = {}
        employee_id = request.env['hr.employee'].search([('user_id','=',request.env.user.id)])
#         user = request.env['res.users']
        default_values = {}
        default_values['partner_id'] = request.env.user.partner_id.name
        default_values['email'] = request.env.user.partner_id.email
        default_values['user'] = request.env.user.name
        default_values['emp_id'] = request.env['hr.employee'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('user_id','=',request.env.user.id)],limit=1).driver_code
        default_values['department_id'] = request.env['hr.employee'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('user_id','=',request.env.user.id)],limit=1).department_id.display_name
        if employee_id:
            values['employee_id'] = employee_id
        values['helpdesk_id'] = request.env['helpdesk.ticket'].search([])
        values['app_name_id'] = request.env['app.config'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([])
        values['team_id'] = request.env['helpdesk.team'].with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([])
        team_ids = request.env['helpdesk.team'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('name','=','الدعم الفني IT')])
        values['user_id'] = team_ids.member_ids
        values['type_id'] = request.env['type.config'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([])
        values['page_name'] = 'helpdesk'
        print('...........app_name_id...........',values['app_name_id'])
        return request.render("bsg_helpdesk_operations.portal_helpdesk_modes",{'values':values,'default_values':default_values})
  
    @http.route(['/my/helpdesk/process'], type='http', auth="user",method=['post'], website=True,csrf_token=True)
    def portal_my_helpdesk_process(self, id=None, helpdesk_id=None, **kw):
        values = {}
        attachment_id = kw.get('attachment_id')
        attachment = []
        print('..............helpdesk_id.............',helpdesk_id)
        if attachment_id:
            extension = os.path.splitext(attachment_id.filename)[-1]
            file_vals = {
                'name':attachment_id.filename,
                'store_fname':attachment_id.filename,
                'datas': base64.encodebytes(attachment_id.read()),
                'res_model': 'helpdesk.ticket',
                'res_name':attachment_id.filename,
                'mimetype': 'application/' + extension
            }
            attachment_id = request.env['ir.attachment'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).create(file_vals)
            attachment.append(attachment_id.id)
        print('.............**kw...............',kw.get('team_id'))
        HelpdeskObj = request.env['helpdesk.ticket']

        if kw:
            kw.update({'name':kw.get('name')})
            kw.update({'partner_id':request.env.user.partner_id.id})
            kw.update({'user_id':int(kw.get('user_id') if kw.get('user_id') else False)})
            kw.update({'partner_email':kw.get('partner_email')})
            kw.update({'emp_id':kw.get('emp_id')})
            kw.update({'user':(kw.get('user'))})
            kw.update({'app_name_id':int(kw.get('app_name_id'))})
            kw.update({'team_id':int(kw.get('team_id'))})
            kw.update({'type_id':int(kw.get('type_id'))})
            kw.update({'so':kw.get('so')})
            kw.update({'importance':kw.get('importance')})
            kw.update({'department_id':kw.get('department_id')})
            kw.update({'trip':kw.get('trip')})
            kw.update({'description':kw.get('description')})
            kw.update({'attachment_id':[(6, 0, attachment)] if attachment else []})
        if helpdesk_id:
            res = HelpdeskObj.browse(int(helpdesk_id)).write(kw)
            print('..............helpdesk_id  res.............', res)
        else:
            try: 
                #res = HelpdeskObj.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create(kw) don't use sudo here bc  of['helpdesk.ticket']._default_team_id().. by Gaga
                res = HelpdeskObj.create(kw)
                print('..............try HelpdeskObj  res.............', res)
            
            except Exception as e:
                return str(e)
        return request.redirect('/my/tickets' + '?message=success')
