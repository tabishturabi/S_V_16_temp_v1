# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SendMobileSmsSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	sms_username = fields.Char(string='User Name')
	sms_password = fields.Char(string='Password')
	api_url = fields.Char(string='API Url')
	# http://www.mobily.ws/api/msgSend.php?mobile={username}&password={password}&numbers={numbers}&sender={sender}&msg={message}&applicationType=68


	@api.model
	def get_values(self):
		res = super(SendMobileSmsSettings, self).get_values()
		sms_username = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).\
		get_param('send_mobile_sms.sms_username')
		sms_password = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).\
		get_param('send_mobile_sms.sms_password')
		api_url = self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).\
		get_param('send_mobile_sms.api_url')
		res.update({
					'sms_username' : sms_username,
					'sms_password' : sms_password,
					'api_url' : api_url,

					}) 	
		return res

	
	def set_values(self):
		super(SendMobileSmsSettings, self).set_values()
		self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).\
		set_param('send_mobile_sms.sms_username', self.sms_username)
		self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).\
		set_param('send_mobile_sms.sms_password', self.sms_password)
		self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).\
		set_param('send_mobile_sms.api_url', self.api_url)


