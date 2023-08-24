# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class ReasonToRefuse(models.TransientModel):
    _name = 'penalty.refusal.reason'

    penalty_id = fields.Many2one('employee.penalty',string="Penalty")
    refusal_reason = fields.Text(string="Refuse Reason",required=True)


    def click_refuse(self):
        self.penalty_id.refuse_reason = self.refusal_reason
        if self.penalty_id.state == 'applied':

            self.penalty_id.state = 'hr_salary_accountant'

        elif self.penalty_id.state == 'hr_salary_accountant':

            if not self.penalty_id.employee_id.branch_id.is_hq_branch:

                self.penalty_id.state = 'branch_supervisor'

            else:

                self.penalty_id.state = 'direct_manager'

        elif self.penalty_id.state in ['direct_manager','branch_supervisor']:

            self.penalty_id.state = 'hr_supervisor'

        elif self.penalty_id.state == 'hr_supervisor':

            self.penalty_id.state = 'draft'








class ReasonToCancel(models.TransientModel):
    _name = 'penalty.cancel.reason'

    penalty_id = fields.Many2one('employee.penalty',string="Penalty")
    cancel_reason = fields.Text(string="Cancel Reason",required=True)



    def click_cancel(self):
        self.penalty_id.cancel_reason = self.cancel_reason
        self.penalty_id.state = 'cancel'
















