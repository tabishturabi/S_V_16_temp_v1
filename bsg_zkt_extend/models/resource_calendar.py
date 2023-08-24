# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResourceCalendar(models.Model):
    _inherit= 'resource.calendar'
    
    max_early_muintes = fields.Float('Max Early Munites')

class ResourceCalendarAttendance(models.Model):
    _inherit= 'resource.calendar.attendance'

    begin_in = fields.Float('Beginning In')
    end_in = fields.Float('Ending In')
    begin_out = fields.Float('Beginning Out')
    end_out = fields.Float('Ending Out')




