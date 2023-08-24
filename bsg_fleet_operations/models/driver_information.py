from odoo import fields, models, api, _
from datetime import datetime,date
from odoo.exceptions import UserError


class DriverInformation(models.Model):
    _name = 'driver.information'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'All About Driver'
    _rec_name = 'employee_id'


    employee_id = fields.Many2one('hr.employee',string="Driver",domain=[('is_driver', '=', True)],required=True)
    mobile = fields.Char(string="Mobile",related="employee_id.mobile_phone")
    taq_number = fields.Char(string="Sticker NO",readonly=True)
    trailer_id = fields.Char(string="Trailer",readonly=True)
    card_expire_date = fields.Date(string="Card Expire Date",required=True)
    card_no = fields.Char(string="Card NO")
    left_days = fields.Integer(string="Left Days", compute="get_left_days")

    @api.depends('card_expire_date')
    def get_left_days(self):
        for rec in self:
            if rec.card_expire_date and rec.card_expire_date > date.today():
                days_left_timedelta = rec.card_expire_date - date.today()
                days_left = days_left_timedelta.days
                rec.left_days = days_left
            else:
                rec.left_days = 0

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            args = [('driver_code', operator, name)]
        bsg_vehicle_cargo_sale_ids = self._search(args, limit=limit, access_rights_uid=None)
        return super(DriverInformation, self).name_search(name=name, args=args, operator=operator, limit=limit)


    @api.onchange('employee_id')
    def onchange_driver(self):
        if self.employee_id:
            vehicle_id = self.env['fleet.vehicle'].search([('bsg_driver','=',self.employee_id.id)],limit=1)
            if vehicle_id:
                self.taq_number = vehicle_id.taq_number
                self.trailer_id = vehicle_id.trailer_id.trailer_config_name