from odoo import api, models, fields, _
from odoo.exceptions import UserError
from lxml import etree
# from odoo.osv.orm import setup_modifiers


class TransportManagement(models.Model):
    _inherit = 'transport.management'

    @api.model
    def _get_route_domain(self):
        domain = []
        if self.env.context.get('default_is_government'):
            locations = self.env['bsg_route_waypoints'].search(
                [('user_allowed_locations', 'in', self.env.user.user_branch_id.ids)])
            locations_lines = self.env['bsg_route_line'].search(['|', ('waypoint', 'in', locations.ids), (
                'waypoint.user_allowed_locations', 'in', self.env.user.user_branch_id.ids)])
            route_ids = []
            for rec in locations_lines:
                route_ids.append(rec.route_id.id)
            transport_management = self.env['transport.management'].browse(self.env.context.get('active_id'))
            route = self.env['bsg_route'].search([('waypoint_from', '=', transport_management.form_transport.id)])
            for rec in route:
                route_ids.append(rec.id)
            domain += ['|', ('id', 'in', route_ids)]
        if self.env.user.has_group('bsg_trip_mgmt.group_create_trip_with_all_route_view'):
            id_list = self.env['bsg_route'].search([])
            domain += [('id', 'in', id_list.ids)]
        else:
            id_list = self.env['bsg_route'].search(
                [('waypoint_from.user_allowed_locations', '=', self.env.user.user_branch_id.id)])
            domain += [('id', 'in', id_list.ids)]
        return domain

    @api.onchange('customer_contract')
    def _onchange_get_form_contract(self):
        if self.customer_contract and self.is_government and self.user_has_groups(
                'government_sale.group_create_government_so_all_locations'):
            loc_from_ids = self.env['bsg_customer_contract_line'].search([
                ('cust_contract_id', '=', self.customer_contract.id),
            ]).mapped('loc_from').ids
            return {'domain': {'form_transport': [('id', 'in', loc_from_ids)]}}

    @api.model
    def _default_get_site(self):
        if self.env.context.get('default_is_government'):
            route = self.env['bsg_route_waypoints'].search(
                [('user_allowed_locations', 'in', self.env.user.user_branch_id.id)], limit=1)
            if route:
                return route.id
            else:
                return False
        else:
            if self.env.user and self.env.user.user_branch_id:
                site_import = self.env['bsg_route_waypoints'].search(
                    [('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                    limit=1)
                if site_import:
                    return site_import.id
                else:
                    return False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(TransportManagement, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and res.get('toolbar', False):
            if self.env.context.get('default_is_government'):
                report_id = self.env['ir.actions.report']._get_report_from_name(
                    'government_sale.sale_gov_agreement_report_temp')
                report_list = []
                report_vals = {'id': report_id.id, 'name': report_id.name, 'type': report_id.type,
                               'binding_type': report_id.binding_type,
                               'model': report_id.model, 'report_type': report_id.report_type,
                               'report_name': report_id.report_name,
                               'report_file': report_id.report_file, 'groups_id': report_id.groups_id,
                               'multi': report_id.multi,
                               'paperformat_id': report_id.paperformat_id,
                               'print_report_name': report_id.print_report_name,
                               'attachment_use': report_id.attachment_use,
                               'attachment': report_id.attachment,
                               'help': report_id.help, 'binding_model_id': report_id.binding_model_id,
                               'create_uid': report_id.create_uid,
                               'create_date': report_id.create_date, 'write_uid': report_id.write_uid,
                               'write_date': report_id.write_date, 'xml_id': report_id.xml_id,
                               'display_name': report_id.display_name,
                               'string': report_id.name}
                report_list.append(report_vals)
                res['toolbar']['print'] = report_list
            else:
                report_id = self.env['ir.actions.report']._get_report_from_name(
                    'bx_agreement_report.bx_agreement_report_temp')
                report_list = []
                report_vals = {'id': report_id.id, 'name': report_id.name, 'type': report_id.type,
                               'binding_type': report_id.binding_type,
                               'model': report_id.model, 'report_type': report_id.report_type,
                               'report_name': report_id.report_name,
                               'report_file': report_id.report_file, 'groups_id': report_id.groups_id,
                               'multi': report_id.multi,
                               'paperformat_id': report_id.paperformat_id,
                               'print_report_name': report_id.print_report_name,
                               'attachment_use': report_id.attachment_use,
                               'attachment': report_id.attachment,
                               'help': report_id.help, 'binding_model_id': report_id.binding_model_id,
                               'create_uid': report_id.create_uid,
                               'create_date': report_id.create_date, 'write_uid': report_id.write_uid,
                               'write_date': report_id.write_date, 'xml_id': report_id.xml_id,
                               'display_name': report_id.display_name,
                               'string': report_id.name}
                report_list.append(report_vals)
                res['toolbar']['print'] = report_list

        return res

    @api.model
    def _get_form_transport_domain(self):
        res = [(1, '=', 1)]
        if self.env.context.get('default_is_government'):
            res = [('id', 'in', self.env['bsg_route_waypoints'].search(
                [('user_allowed_locations', 'in', self.env.user.user_branch_id.id)]).ids)]
            if self.user_has_groups('government_sale.group_create_government_so_all_locations'):
                res = [(1, '=', 1)]
        return res

    form_transport = fields.Many2one('bsg_route_waypoints', string="From", store=True, default=_default_get_site,
                                     track_visibility=True, domain=lambda self: self._get_form_transport_domain())
    is_government = fields.Boolean("Is Government")
    is_started_trip = fields.Boolean("Is Started Trip")
    is_multiple = fields.Boolean("Is Multiple Places")
    tender_date = fields.Date(string='Tender Date', store=True, track_visibility=True)
    actual_arrival_date = fields.Datetime(string='Actual Arrival Date', track_visibility=True)
    customer_ref_gs = fields.Char("Customer Ref", related="customer.ref", readonly=True)
    tender_number = fields.Char("Tender Number")
    distance_km = fields.Float(string='Distance KM', store=True, track_visibility=True, compute='_compute_distance_km')
    overnight_percentage = fields.Float(string='Overnight Percentage', store=True, track_visibility=True)
    request_type = fields.Selection([('goods_cargo', 'Goods Cargo'), ('car_cargo', 'Car Cargo')], default='car_cargo',
                                    string='Request Type', track_visibility=True)
    register_arrival_branch_id = fields.Many2one("bsg_branches.bsg_branches", string="Register Arrival Branch")
    fleet_trip_gov_id = fields.Many2one("fleet.vehicle.trip", string="Fleet Trip Gov")
    vehicle_type_domain_name = fields.Char('Domain Name', related='vehicle_type_domain_id.name')
    current_user_branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Current User Branch', store=True,
                                             default=lambda self: self.env.user.user_branch_id.id,
                                             help="Current User Branch",track_visibility='onchange')

    @api.depends('form_transport', 'to_transport', 'customer_contract')
    def _compute_distance_km(self):
        contract_line = self.env['bsg_customer_contract_line']
        for rec in self:
            rec.distance_km = 0.0
            if rec.form_transport and rec.to_transport and rec.customer_contract:
                rec.distance_km = contract_line.search(
                    [('loc_from', '=', rec.form_transport.id), ('loc_to', '=', rec.to_transport.id),
                     ('cust_contract_id', '=', rec.customer_contract.id)], limit=1).distance_km

    @api.onchange('customer_contract')
    def onchange_customer_contract(self):
        if self.customer_contract:
            # as per khaleed told
            payment_method = self.env['cargo_payment_method'].search(
                [('payment_type', '=', 'credit')], limit=1)
            self.payment_method = payment_method.id

    # @api.multi
    def action_start_trip_gov(self):
        trip_id = self.env['fleet.vehicle.trip'].create(
            {'sale_gov_id': self.id, 'trip_type': 'manual', 'vehicle_id': self.transportation_vehicle.id,
             'route_id': self.route_id.id, 'state': 'progress', 'truck_load': 'full', 'actual_revenue': self.total_before_taxes, 'expected_end_date': fields.datetime.now()})
        trip_id._onchange_route_id()
        trip_id.write({'vehicle_id': self.transportation_vehicle.id, 'trailer_id': self.trailer_id.id})
        self.write({'fleet_trip_gov_id': trip_id.id, 'is_started_trip': True})
        self.transportation_vehicle.write({'current_branch_id': False, 'trip_id': trip_id.id})

    # @api.multi
    def action_arrival(self):
        bsg_route = self.env['bsg_route'].browse(self.route_id.id)
        bsg_route_lines_cities = bsg_route.waypoint_to_ids
        check_branch_bool = False
        for rec in bsg_route_lines_cities:
            if rec.waypoint.loc_branch_id.id == self.env.user.user_branch_id.id:
                check_branch_bool = True
        if not bsg_route_lines_cities:
            raise UserError(_("Please contact operation department to add your branch in the route"))
        if not check_branch_bool:
            raise UserError(_("You are not authorized to register arrival"))
        if not self.is_started_trip:
            raise UserError(_("Please make sure to start trip before you register arrival"))
        self.write({'state': 'done', 'actual_arrival_date': fields.datetime.now(),
                    'register_arrival_branch_id': self.env.user.user_branch_id.id})
        self.transportation_vehicle.write({'current_branch_id': self.env.user.user_branch_id.id, 'trip_id': False})
        self.fleet_trip_gov_id.write({'state': 'finished'})

    # @api.multi
    def action_confirm(self):
        if self.is_government:
            if self.transportation_no == "New":
                self.write({'transportation_no': self.env['ir.sequence'].next_by_code('government.sale')})
            if self.payment_method.payment_type == 'credit':
                self.write({'state': 'issue_bill'})
        else:
            self.write({'state': 'confirm'})

    @api.onchange('transportation_vehicle')
    def onchange_government_transportation_vehicle(self):
        if self.is_government:
            if self.transportation_vehicle:
                self.fleet_type_transport = self.transportation_vehicle.vehicle_type


class TransportManagementLine(models.Model):
    _inherit = 'transport.management.line'

    # def get_config_products(self):
    #     domain = [('sale_ok', '=', True), ('categ_id', 'in', self.env.user.company_id.product_category_ids.ids)]
    #     if self.is_government:
    #         domain = [('is_government', '=', True)]
    #     return domain
    #
    # def get_car_size(self):
    #     domain = [('id', 'in', self.env.user.company_id.bsg_car_size_ids.ids)]
    #     if self.is_government:
    #         domain = [('is_government', '=', True)]
    #     return domain

    # @api.one
    @api.depends('price', 'tax_ids', 'product_uom_qty', 'is_overnight', 'customer_contract', 'agreement_type')
    def _get_price(self):
        if self.product_id:
            if self.product_uom_qty:
                self.total_before_taxes = self.product_uom_qty * self.price
            if self.tax_ids:
                currency = self.currency_id or None
                quantity = 1
                product = self.product_id
                taxes = self.tax_ids.compute_all((self.total_before_taxes), currency, quantity,
                                                 product=product)
                self.tax_amount = taxes['total_included'] - taxes['total_excluded']

    @api.onchange('product_id', 'car_size_id', 'form', 'to', 'is_overnight', 'customer_contract')
    def onchange_line_get_contract_price(self):
        for rec in self:
            rec.price = 0
            if rec.product_id and rec.form and rec.to and rec.car_size_id:
                if rec.transport_management.customer_contract:
                    ContractLine = self.env['bsg_customer_contract_line'].sudo().search([
                        ('cust_contract_id', '=', rec.transport_management.customer_contract.id),
                        ('service_type', '=', rec.product_id.product_tmpl_id.id),
                        ('loc_from', '=', rec.form.id),
                        ('loc_to', '=', rec.to.id),
                        ('car_size', '=', rec.car_size_id.id),
                    ], limit=1)
                    if self.transport_management.agreement_type == 'round_trip':
                        rec.price = ContractLine.price * 2 if ContractLine else 0.0
                    else:
                        rec.price = ContractLine.price if ContractLine else 0.0
                else:
                    price_id = self.env['bsg_price_line'].sudo().search([
                        ('price_config_id.waypoint_from', '=', rec.form.id),
                        ('price_config_id.waypoint_to', '=', rec.to.id),
                        ('customer_type', '=', rec.transport_management.customer.partner_types.pricing_type),
                        ('service_type', '=', rec.product_id.product_tmpl_id.id),
                        # ('car_classfication', '=', self.car_classfication.id),
                        ('car_size', '=', rec.car_size_id.id),
                    ], limit=1)
                    if price_id:
                        if self.transport_management.agreement_type == 'round_trip':
                            rec.price = price_id.addtional_price * 2
                        else:
                            rec.price = price_id.price
            if rec.is_government and rec.is_overnight and rec.customer_contract.overnight_percentage > 0:
                overnight_percentage_amount = rec.customer_contract.overnight_percentage / 100 * rec.price
                rec.price = rec.price + overnight_percentage_amount

    is_government = fields.Boolean("Is Government")
    is_overnight = fields.Boolean("Is Overnight", store=True)
    is_multiple = fields.Boolean("Is Multiple Places", store=True)
    distance_km = fields.Float(string='Distance KM', store=True, track_visibility=True,
                               related='transport_management.distance_km')
    agreement_type = fields.Selection([('one_way', 'One way'), ('round_trip', 'Round trip')],
                                      related='transport_management.agreement_type', string='Agreement Type',
                                      track_visibility=True)
    request_type = fields.Selection([('goods_cargo', 'Goods Cargo'), ('car_cargo', 'Car Cargo')], default='car_cargo',
                                    string='Request Type', track_visibility=True)


class PartnerType(models.Model):
    _inherit = 'partner.type'

    is_government = fields.Boolean("Is Government")


class BsgCarSize(models.Model):
    _inherit = 'bsg_car_size'

    is_government = fields.Boolean("Is Government")


class BsgCustomerContractLine(models.Model):
    _inherit = 'bsg_customer_contract_line'

    distance_km = fields.Float(string='Distance KM', store=True, track_visibility=True)


class BsgRouteWaypoints(models.Model):
    _inherit = 'bsg_route_waypoints'

    user_allowed_locations = fields.Many2many(comodel_name='bsg_branches.bsg_branches', string='Allowed Branches')


class BsgCustomerContract(models.Model):
    _inherit = 'bsg_customer_contract'

    overnight_percentage = fields.Float(string='Overnight Percentage', store=True, track_visibility=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_government = fields.Boolean("Is Government")


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_government = fields.Boolean('Is Government', related='product_tmpl_id.is_government', store=True)


class BXCreditCustomerCollection(models.Model):
    _inherit = "bx.credit.customer.collection"

    @api.model
    def create(self, vals):
        self = self.with_context(is_government=False)
        if self.env.context.get('default_is_government'):
            self = self.with_context(is_government=True)
        return super(BXCreditCustomerCollection, self).create(vals)

    # @api.multi
    def confirm_button(self):
        if not self.name and self.customer_id.partner_types.is_government:
            self.write({'name': self.env['ir.sequence'].next_by_code('government.cc.sale')})
        if not self.transport_management_ids:
            raise UserError(_("Please At Least Add One Line To Confirm Order."))
        if self.transport_management_ids:
            update_query = "update transport_management_line set add_to_cc = TRUE where id in %s;"
            self.env.cr.execute(update_query, (tuple(self.transport_management_ids.ids),))
        self.write({'state': 'confirm'})
