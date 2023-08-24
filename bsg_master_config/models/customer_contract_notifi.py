# -*- coding: utf-8 -*-

from odoo import fields,api,models,_
from datetime import date
from odoo.exceptions import UserError


class CustomerContractNotification(models.Model):
    _name = 'customer.contract.notification'
    _inherit = ['mail.thread']
    _description = 'All About Customer Contract Notification Configuration'
    _rec_name='notification_per'
    
    name = fields.Char(string='Name')
    receiver_user_ids = fields.Many2many('res.users',string='Receiver Users')
    notification_per = fields.Integer('Notification Period')
    active = fields.Boolean(string="Active", tracking=True, default=True)
    
    def _send_mail_to_customer(self):
        customer_contracts = self.env['customer.contract.notification'].search([])
        mail_pool = self.env['mail.mail']
        for rec in customer_contracts:
            partner_ids = [user_id.partner_id.id for user_id in rec.receiver_user_ids]
            contract_ids = self.env['bsg_customer_contract'].search([('cont_customer','in',partner_ids),('mail_sended','=',False)])
            enable_to_contract_ids = []
            for contract_id in contract_ids:
                if not contract_id.cont_customer.email:
                    raise UserError('Please enter Email for Partner')
                else:
                    end_date = contract_id.cont_end_date
                    current_date = date.today()
                    total_days = end_date - current_date
                    tot = total_days.days
                    if rec.notification_per <= tot:
                        enable_to_contract_ids.append(contract_id.id)
            if enable_to_contract_ids:
                html_body = '<div style="margin: 0px; padding: 0px;">'
                html_body += '<p style="margin: 0px; padding: 0px; font-size: 13px;">'
                html_body += 'Dear All,' 
                for partner in self.env['res.partner'].search([('id','in',partner_ids)]):
                    html_body += '<strong>'+ partner.name + '</strong>,'
                html_body += '<br /><br />The following list of customer contracts will expire after (<strong>'+str(rec.notification_per)+'</strong>) or Less Days ,you need to take action on that.<table cellspacing="0" cellpadding="1" style="width:600px;background:inherit;color:inherit" border="1"><tbody><tr> <th style="width:135px">Customer Name</th><th style="width: 135px;">Customer Contract</td>'
                for res in self.env['bsg_customer_contract'].search([('id','in',enable_to_contract_ids)]):
                    if res.cont_customer and res.contract_name:
                        html_body += '</tr> <tr><td>'+res.cont_customer.name+'</td><td>'+res.contract_name+'</td></tr></tbody>'
                        res.mail_sended = True
                html_body += "Thank's,"
                html_body += '</p></div>'
                for partner in self.env['res.partner'].search([('id','in',partner_ids)]):
                    values={
                        'subject': str(self.env.user.company_id.name) + 'Contract (Ref ' ')',
                        'email_to':(partner.email) or False,
                        'body_html':html_body,
                        'email_from': str(self.env.user.email)
                    }
                    msg_id = mail_pool.create(values)
                    if msg_id:
                        msg_id.send()
    
