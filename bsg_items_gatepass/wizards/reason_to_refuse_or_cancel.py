# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class ReasonToRefuse(models.TransientModel):
    _name = 'gatepass.refusal.reason'

    gatepass_id = fields.Many2one('item.gatepass',string="GatePass")
    refusal_reason = fields.Text(string="Refuse Reason",required=True)



    # @api.multi
    def click_refuse(self):
        for rec in self:
            if rec.gatepass_id.state == 'done':
                if rec.gatepass_id.pass_to == 'customer':
                    rec.gatepass_id.state = 'finanace_approval'
                else:
                    rec.gatepass_id.state = 'op_manager_approval'
            elif rec.gatepass_id.state in ['finanace_approval','op_manager_approval']:
                rec.gatepass_id.state = 'draft'
            rec.gatepass_id.refusal_reason = rec.refusal_reason






# class ReasonToCancel(models.TransientModel):
#     _name = 'clearance.cancel.reason'
#
#     clearance_id = fields.Many2one('hr.clearance',string="Clearance")
#     cancel_reason = fields.Text(string="Cancel Reason",required=True)
#
#
#
#     @api.multi
#     def click_cancel(self):
#         self.clearance_id.cancel_reason = self.cancel_reason
#         self.clearance_id.state = 'cancel'
















