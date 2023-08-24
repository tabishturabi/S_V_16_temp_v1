# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class ExpenseType(models.Model):
    _name = 'expense.type'
    _rec_name ='name'

    name = fields.Char('Expense Type')
    date_range = fields.Boolean(string='Include Range Of Date')



