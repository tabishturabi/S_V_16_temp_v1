# -*- coding: utf-8 -*-

from odoo import api, fields, models,_


class RejectReason(models.TransientModel):
	_name = 'reject.reason.purchase.request'
	_description = 'Reject Reason for Purchase Request'

	name = fields.Text(string="Reason for Reject")

	# @api.multi
	def action_reject_apply(self):
		purchase_request = self.env['purchase.req'].browse(self.env.context.get('active_ids'))
		purchase_request.write({'reject_reason': self.name})
		purchase_request.message_post(body="Reject Reason :" + str(self.name))
		purchase_request.message_post(subject=_('Purchase Request Refused'),
                                      body='Hello, Your Purchase Request %s is Refused.' % (self.name))
		return purchase_request.action_reject()


class RejectCommitteeReason(models.TransientModel):
	_name = 'reject.reason.purchase.committee'
	_description = 'Reject Reason for Purchase Order'

	name = fields.Text(string="Reason for Reject")

	# @api.multi
	def action_reject_apply(self):
		purchase_order = self.env['purchase.order'].browse(self.env.context.get('order_id'))
		committee_id = self.env['purchase.order.committee'].browse(self.env.context.get('commite_id'))
		committee_id.sudo().write({'comment': self.name,'decision':'reject'})
		purchase_order.message_post(subject=_('Mebmer Reject Purchase Order '),
                                      body='Member %s Reject Purchase Order In %s' % (str(self.env.user.name),str(fields.Datetime.now())))
		return True
