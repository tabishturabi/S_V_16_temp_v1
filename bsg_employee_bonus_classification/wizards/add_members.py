# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError



class WizardAddMembers(models.TransientModel):
    _name = 'wizard.add.members'

    bonus_cls_id = fields.Many2one('employee.bonus.classification',string='Bonus Classification')
    employee_ids = fields.Many2many('hr.employee',string='Add Members')


    def action_add_members(self):
        if self.bonus_cls_id:
            self.bonus_cls_id.employee_ids = [(6,0,self.employee_ids.ids)]























