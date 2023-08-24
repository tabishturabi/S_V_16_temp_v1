# -*- coding: utf-8 -*-
from odoo import models,fields, api

class HrJob(models.Model):
    _inherit = 'hr.job'

    active = fields.Boolean('Active', default=True)
    is_driver = fields.Boolean('Is Driver?')

    
    def archive_hr_job(self):
        for rec in self:
            rec.active = not rec.active
