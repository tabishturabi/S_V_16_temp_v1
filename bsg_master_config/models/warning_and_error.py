# -*- coding: utf-8 -*-

from odoo import fields,models,api,_
from odoo.exceptions import ValidationError,UserError

class BsgWarningError(models.Model):
    _name = 'bsg.warning.error'
    _description = 'It s All About Master Data Error and Warnings.'
    _rec_name = 'message_id'
    
    message_id = fields.Char(string='Message ID')
    message_code = fields.Char(string='Message Code')
    message_arabic = fields.Text(string='Message Arabic')
    message_english = fields.Text(string='Message English')
    
    
    
    def get_warning(self,code, **kw):
        if code:
            warning_id = self.search([('message_id','=',code)])
            if warning_id:
                user_lang = self.env.user.lang
                if user_lang == 'en_US':
                    msg = warning_id.message_code+": "+warning_id.message_english
                    return msg
                else:
                    msg = warning_id.message_code+": "+warning_id.message_arabic
                    return msg
            else:
                raise UserError(_("Warning Code not found"))
    
    
