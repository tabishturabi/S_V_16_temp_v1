# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CustomerContractUsers(models.Model):
    _name = 'contract.public.users'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Customer Contract Public Users"

    
    def name_get(self):
        return [(record.id, record.customer_id.name) for record in self]

    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    car_make_ids = fields.Many2many(comodel_name="bsg_car_make", string="Car Makes")

    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)

    location_ids = fields.Many2many('bsg_route_waypoints', string='Locations')
    user_lines = fields.One2many("contract.users.line", "contract_users_id", string="Allowed Users")

    _sql_constraints = [
        ('customer_id_uniq', 'unique (customer_id)', "This customer configuration already exists !"),
    ]

    
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {
            'customer_id': self.customer_id.name if self.customer_id else '',
            'user_id': self.user_id.name if self.user_id else '',
            'car_make_ids': self.car_make_ids.mapped("car_make_name") if self.car_make_ids else '',
            'location_ids': self.location_ids.mapped("route_waypoint_name") if self.location_ids else '',}
        res = super(CustomerContractUsers, self).write(values)
        data_dict = {}
        reference = self.display_name if self.customer_id else ''
        if values.get('user_id'):
            data_dict['user_id'] = {'name': 'User', 'old': old_dict['user_id'],
                                    'new': self.user_id.name if self.user_id else ''}
        if values.get('customer_id'):
            data_dict['customer_id'] = {'name': 'Customer', 'old': old_dict['customer_id'],
                                    'new': self.customer_id.name if self.customer_id else ''}
        if values.get('car_make_ids'):
            data_dict['car_make_ids'] = {'name': 'Car Makes', 'old': old_dict['car_make_ids'],
                                         'new': self.car_make_ids.mapped("car_make_name")}
        if values.get('location_ids'):
            data_dict['location_ids'] = {'name': 'Locations', 'old': old_dict['location_ids'],
                                         'new': self.location_ids.mapped("route_waypoint_name")}

        log_body = "<p>Reference/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': "contract.public.users", 'res_id': self.id,
             'subtype_id': '2'})
        return res


#################################################################


class ContractUsersLines(models.Model):
    _name = 'contract.users.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Customer Contract Public Users Lines"

    user_id = fields.Many2one("res.users", string="User", domain="[('share','=',True)]")
    contract_ids = fields.Many2many("bsg_customer_contract", string="Contracts",
                                    domain="[('cont_customer', '=', customer_id)]")
    contract_users_id = fields.Many2one("contract.public.users", required=True)
    customer_id = fields.Many2one("res.partner", string="Customer",
                                  compute="get_contracts_domain")

    date_from = fields.Date(string="Active From")
    date_to = fields.Date(string="Active To")

    @api.onchange('customer_id')
    @api.depends("contract_users_id.customer_id")
    def get_contracts_domain(self):
        contract_ids = []
        for rec in self:
            rec.customer_id = False
            customer = rec.contract_users_id.customer_id
            if customer:
                rec.customer_id = customer.id
                print(" rec.customer_id",  rec.customer_id)
            contracts = self.env['bsg_customer_contract'].search([('cont_customer', '=',  rec.customer_id.id)]).ids
            contract_ids += contracts
            print("===== ids", contract_ids)
        return {'domain': {'contract_ids': [('id', 'in', contract_ids)]}}

    @api.constrains('date_start', 'date_stop', 'company_id')
    def _check_dates(self):
        for line in self:
            # Starting date must be prior to the ending date
            date_from = line.date_from
            date_to = line.date_to
            if date_to < date_from:
                raise ValidationError(_('The ending date must not be prior to the starting date.'))

    def is_active(self):
        today = fields.Date.today()
        if self.date_from <= today <= self.date_to:
            return True
        else:
            return False

    
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'user_id': self.user_id.name if self.user_id else '',
                    'contract_ids': self.contract_ids.mapped("contract_name") if self.contract_ids else '',
                    'date_from': self.date_from if self.date_from else '',
                    'date_to': self.date_to if self.date_to else ''}
        res = super(ContractUsersLines, self).write(values)
        data_dict = {}
        reference = self.contract_users_id.display_name if self.contract_users_id else ''
        if values.get('user_id'):
            data_dict['user_id'] = {'name': 'User', 'old': old_dict['user_id'], 'new': self.user_id.name if self.user_id else ''}
        if values.get('contract_ids'):
            data_dict['contract_ids'] = {'name': 'Contracts', 'old': old_dict['contract_ids'], 'new': self.contract_ids.mapped("contract_name")}
        if values.get('date_from'):
            data_dict['date_from'] = {'name': 'Active From', 'old': old_dict['date_from'], 'new': values.get('date_from')}
        if values.get('date_to'):
            data_dict['date_to'] = {'name': 'Active To', 'old': old_dict['date_to'],
                                        'new': values.get('date_to')}
        log_body = "<p>Reference/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': "contract.public.users", 'res_id': self.contract_users_id.id, 'subtype_id': '2'})
        return res
