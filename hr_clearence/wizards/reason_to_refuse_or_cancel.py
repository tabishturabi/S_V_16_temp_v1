# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class ReasonToRefuse(models.TransientModel):
    _name = 'clearance.refusal.reason'

    clearance_id = fields.Many2one('hr.clearance',string="Clearance")
    refusal_reason = fields.Text(string="Refuse Reason",required=True)



    # @api.multi
    def click_refuse(self):
        self.clearance_id.refuse_reason = self.refusal_reason
        self.clearance_id.state = 'draft'
        # if self.clearance_id.state == 'technical_support':
        #     self.clearance_id.state = 'department_manager'
        # if self.clearance_id.state == 'department_manager':
        #     self.clearance_id.state = 'draft'
        # if self.clearance_id.state == 'internal_auditor':
        #     if self.clearance_id.employee_id.job_id.is_driver:
        #         self.clearance_id.state = 'technical_support'
        #     else:
        #         self.clearance_id.state = 'department_manager'
        # if self.clearance_id.state == 'finance_manager':
        #     self.clearance_id.state = 'internal_auditor'
        # if self.clearance_id.state == 'hr_salary_accountant':
        #     self.clearance_id.state = 'finance_manager'




class ReasonToCancel(models.TransientModel):
    _name = 'clearance.cancel.reason'

    clearance_id = fields.Many2one('hr.clearance',string="Clearance")
    cancel_reason = fields.Text(string="Cancel Reason",required=True)



    # @api.multi
    def click_cancel(self):
        self.clearance_id.cancel_reason = self.cancel_reason
        self.clearance_id.state = 'cancel'
















