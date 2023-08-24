# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from lxml import etree
# from odoo.osv.orm import setup_modifiers


class BsgTruckAccident(models.Model):
    _name = 'bsg.truck.accident'
    _inherit = ['mail.thread']
    _description = 'All About Bsg Truck Accidents'
    _rec_name = 'name'

    @api.model
    def default_get(self, fields):
        result = super(BsgTruckAccident, self).default_get(fields)
        if self._context.get('default_claim_type') == 'shaamil_claim' and self.env.user.has_group(
                'bsg_truck_accidents.group_shaamil_claims_state_1'):
            result.update({
                'bool_group_check': True,
            })
        if self._context.get('default_claim_type') == 'third_party_claim' and self.env.user.has_group(
                'bsg_truck_accidents.group_third_party_claims'):
            result.update({
                'bool_group_check': True,
            })
        return result

    fleet_driver_name = fields.Many2one('hr.employee', related='fleet_id.bsg_driver', string='Driver Name',
                                        track_visibility='onchange')
    fleet_driver_code = fields.Char(related='fleet_id.driver_code', string='Driver Code', track_visibility='onchange')
    fleet_driver_mobile = fields.Char(related='fleet_id.mobile_phone', string='Driver Mobile',
                                      track_visibility='onchange')

    expected_start_date = fields.Datetime(string="Scheduled Start Date", related="trip_id.expected_start_date",
                                          track_visibility='onchange')
    name = fields.Char('Reference', copy=False, default=lambda self: _('New'), readonly=True,
                       track_visibility='onchange')
    driver_code = fields.Char(related='driver_name.driver_code', string='Driver Code', track_visibility='onchange',store=True)
    driver_mobile = fields.Char(related='driver_name.mobile_phone', string='Driver Mobile', track_visibility='onchange')
    licence_plate = fields.Char(related='fleet_id.license_plate', string='License Plate', track_visibility='onchange')
    accident_location = fields.Char(string='Accident Location', track_visibility='onchange')
    estimate_before_accident = fields.Char(string='Estimate Before Accident', track_visibility='onchange')
    internal_note = fields.Char(string='Internal Note', track_visibility='onchange')
    note = fields.Char(string='Note', track_visibility=True)
    chassis_no = fields.Char(string='Plate Number', readonly=False, track_visibility='onchange')
    kilometer = fields.Char(string='Kilometer', readonly=False, track_visibility='onchange')
    owner_name = fields.Char(string="Owner Name", related="shipment_no_id.bsg_cargo_sale_id.owner_name",
                             track_visibility=True)
    label = fields.Char(string='Label', track_visibility='onchange')
    so_line_general_plate_no = fields.Char(
        string="Plate No#", store=True, track_visibility='onchange', related="shipment_no_id.general_plate_no")
    so_line_chassis_no = fields.Char(
        string="Chassis No#", store=True, track_visibility='onchange', related="shipment_no_id.chassis_no")
    move_id = fields.Many2one('account.move', string='Journal Entry',
                              readonly=True, index=True, ondelete='restrict', copy=False,
                              help="Link to the automatically generated Journal Items.", track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg Truck Accident", track_visibility='onchange')
    fleet_id = fields.Many2one('fleet.vehicle', string='Vehicle No', track_visibility='onchange')
    vendor_bill_id = fields.Many2one('account.move', string='Bill', track_visibility='onchange')
    compensation_bill_id = fields.Many2one('account.move', string='Compensation Bill', track_visibility='onchange')
    last_accident = fields.Many2one('bsg.truck.accident', string='Last Accident', compute='_compute_last_accident',
                                    store=True, track_visibility='onchange')
    truck_id = fields.Many2one('fleet.vehicle.model', related='fleet_id.model_id', string='Truck Name',
                               track_visibility='onchange')
    invoice_to_other = fields.Many2one('res.partner', string="Invoice To Other Customer", track_visibility='onchange')

    insurance_partner = fields.Many2one('res.partner', string="Insurance Customer", track_visibility='onchange')

    driver_name = fields.Many2one('hr.employee', related='trip_id.driver_id', string='Driver Name',
                                  track_visibility='onchange')
    trailer_id = fields.Many2one('bsg_fleet_trailer_config', related='trip_id.trailer_id', string='Trailer',
                                 track_visibility='onchange')
    fleet_trailer_id = fields.Many2one('bsg_fleet_trailer_config', related='fleet_id.trailer_id',
                                       string='Fleet Trailer',
                                       track_visibility='onchange')
    insurance_company_name = fields.Char(related='fleet_id.insurance_company_name',
                                         string='Insurance Company',
                                         track_visibility='onchange')
    accident_date = fields.Date(string='Accident Date', track_visibility='onchange')
    invoice_to_other_date = fields.Date(string='Invoice To Other Date', track_visibility='onchange')
    reverse_entry_id = fields.Many2one('account.move', String="Reverse entry", store=True, readonly=True,
                                       related='move_id.reversed_entry_id', track_visibility='onchange')
    inv_reverse_entry_id = fields.Many2one('account.move', String="INV Reverse entry", store=True, readonly=True,
                                           related='vendor_bill_id.reversed_entry_id', track_visibility='onchange')
    compensation_reverse_entry_id = fields.Many2one('account.move', String="Compensation Reverse entry", store=True,
                                                    readonly=True, track_visibility='onchange',
                                                    related='compensation_bill_id.reversed_entry_id')
    trip_id = fields.Many2one('fleet.vehicle.trip', string='Vehicle Trip', track_visibility='onchange')
    last_trip_id = fields.Many2one('fleet.vehicle.trip', related="fleet_id.trip_id", string='Last Trip',
                                   track_visibility='onchange')
    workshop = fields.Many2one('res.partner', string="Workshop Name",
                               store=True, track_visibility='onchange')
    fleet_car_color = fields.Char(
        string="Color", track_visibility='onchange', related="fleet_id.color")
    fleet_car_chassis = fields.Char(
        string="Chassis", track_visibility='onchange', related="fleet_id.vin_sn")
    fleet_plate_type = fields.Char(string="Plate Type", track_visibility='onchange', related="fleet_id.license_plate")
    fleet_car_make = fields.Many2one(
        string="Car Maker", comodel_name="fleet.vehicle.model", track_visibility='onchange',
        related="fleet_id.model_id")
    fleet_car_model = fields.Char(
        string="Model", track_visibility='onchange', related="fleet_id.model_year")

    so_line_car_color = fields.Many2one(
        string="Color", comodel_name="bsg_vehicle_color", track_visibility='onchange',
        related="shipment_no_id.car_color")

    so_line_plate_type = fields.Many2one(
        string="Plate Type", comodel_name="bsg_plate_config", track_visibility='onchange',
        related="shipment_no_id.plate_type")

    shipment_no_id = fields.Many2one('bsg_vehicle_cargo_sale_line', string="Shipment No", track_visibility='onchange')
    credit_collection_id = fields.Many2one('credit.customer.collection', related='shipment_no_id.credit_collection_id',
                                           string='Credit Collection', track_visibility='onchange')
    cc_partner_id = fields.Many2one('res.partner', related='shipment_no_id.credit_collection_id.invoice_to',
                                    string='Invoice To', track_visibility='onchange')
    so_line_partner_id = fields.Many2one('res.partner', string="Customer", related="shipment_no_id.customer_id",
                                         store=True, track_visibility='onchange')
    so_line_loc_from = fields.Many2one(string="From", comodel_name="bsg_route_waypoints",
                                       related="shipment_no_id.loc_from", store=True, track_visibility='onchange')
    so_line_loc_to = fields.Many2one(string="To", comodel_name="bsg_route_waypoints", related="shipment_no_id.loc_to",
                                     store=True, track_visibility='onchange')
    so_line_car_make = fields.Many2one(
        string="Car Maker", comodel_name="bsg_car_config", track_visibility='onchange',
        related="shipment_no_id.car_make")
    so_line_car_model = fields.Many2one(
        string="Model", comodel_name="bsg_car_model", track_visibility='onchange', related="shipment_no_id.car_model")
    branch_id = fields.Many2one('bsg_branches.bsg_branches', string="Branch", track_visibility='onchange')
    special_customer = fields.Many2one('res.partner', string="Deduction Customer", store=True,
                                       track_visibility='onchange')
    current_user_branch_id = fields.Many2one('bsg_branches.bsg_branches', string='Current User Branch', index=True,
                                             default=lambda self: self.env.user.user_branch_id.id,
                                             help="Current User Branch", track_visibility='onchange')
    estimate_after_accident = fields.Float(string='Estimate After Accident', track_visibility='onchange',
                                           compute='_compute_estimate_after_accident', store=True)
    rfq_price = fields.Float('RFQ Price', track_visibility='onchange')
    compensation_amount = fields.Float('Compensation Amount', track_visibility='onchange')
    spare_parts_amount = fields.Float('Spare Parts Amount', track_visibility='onchange')
    raw_materials_amount = fields.Float('Raw Material Amount', track_visibility='onchange')
    hand_wages_amount = fields.Float('Hand Wages Amount', track_visibility='onchange')
    less_rfq_price = fields.Float('Less Rfq Price', track_visibility='onchange')
    compensation_amount_2 = fields.Float(string='Compensation Amount', track_visibility='onchange')
    number_of_accident = fields.Float(string='Number of Accident', track_visibility='onchange',
                                      compute='_compute_last_accident', store=True)
    mistake_percentage = fields.Float(string='Mistake Percentage', track_visibility='onchange')
    so_line_order_date = fields.Datetime(
        string="Order Date", related="shipment_no_id.order_date", store=True, track_visibility='onchange')
    state = fields.Selection([
        ('1', 'Draft'),
        ('2', 'Insurance Accountant Confirm'),
        ('3', 'Insurance Manager'),
        ('12', 'Waiting Tax Invoice'),
        ('4', 'Audit Confirm'),
        ('5', 'Financial Control Confirm'),
        ('6', 'Financial Manager Confirm'),
        ('7', 'Accountant Confirm'),
        ('11', 'Waiting Payment'),
        ('8', 'Done'),
        ('9', 'Cancelled'),
    ], default='1', store=True, track_visibility='onchange')
    estimated_by = fields.Selection([
        ('sheikh_dealer', 'Sheikh Dealers'),
        ('insurance_workshops', 'Insurance Workshop'),
        ('agency_estimate', 'Agency Estimate')], store=True, track_visibility='onchange')
    accident_agreement_type = fields.Selection(
        [('bassami_truck', 'Bassami Truck'), ('agreement_cus', 'Agreement Customer'),
         ('agreement_comp', 'Agreement Company')], string='Accident Agreement Type', track_visibility='onchange')
    bool_group_check = fields.Boolean('Check Has Group', compute='_compute_group_check', copy=False,
                                      track_visibility='onchange')
    bool_readonly_financials_1 = fields.Boolean('Bool Readonly Financials 1', compute='_compute_readonly_financials',
                                                copy=False, track_visibility='onchange')
    bool_readonly_financials_2 = fields.Boolean('Bool Readonly Financials 2', compute='_compute_readonly_financials',
                                                copy=False, track_visibility='onchange')
    assign_deduction_drivers = fields.Boolean('Assign deduction to other drivers', copy=False,
                                              track_visibility='onchange')
    is_external_maintenance = fields.Boolean(string='Is External Maintenance', track_visibility='onchange', copy=False)
    is_create_compensation = fields.Boolean('Create Compensation', copy=False, track_visibility='onchange')
    rfq_price_paid = fields.Boolean('Is RFQ Paid By Branch', track_visibility='onchange', copy=False)
    is_pics_attach = fields.Boolean('Is Accident Pics Attached', track_visibility='onchange', copy=False)
    is_send_to_audit = fields.Boolean('Is Send To Audit', track_visibility='onchange', copy=False)
    is_path_to_audit = fields.Boolean('Is Path To Audit', track_visibility='onchange', copy=False, default=False)

    # Financial Tax
    is_compensation_amount_tax = fields.Boolean('Is Tax Compensation Amount', track_visibility='onchange', copy=False)
    is_less_rfq_price_tax = fields.Boolean('Is Tax Less Rfq Price', track_visibility='onchange', copy=False)
    is_rfq_price_tax = fields.Boolean('Is Tax RFQ Price', track_visibility='onchange', copy=False)
    is_spare_parts_amount_tax = fields.Boolean('Is Tax Spare Parts Amount', track_visibility='onchange', copy=False)
    is_raw_materials_amount_tax = fields.Boolean('Is Tax Raw Materials Amount', track_visibility='onchange', copy=False)
    is_hand_wages_amount_tax = fields.Boolean('Is Hand Wages Amount Price', track_visibility='onchange', copy=False)
    is_compensation_amount_2 = fields.Boolean('Is Compensation Amount', track_visibility='onchange', copy=False)

    jv_number = fields.Integer('Number of Journal Entry', compute='_compute_jv_number', track_visibility='onchange')
    bill_number = fields.Integer('Number of Bill', compute='_compute_bill_number', track_visibility='onchange')
    compensation_bill_number = fields.Integer('Number of Compensation Bill', track_visibility='onchange',
                                              compute='_compute_compensation_bill_number')
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number',
                                       track_visibility='onchange')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment', track_visibility='onchange')
    branches_ids = fields.Many2many('bsg_branches.bsg_branches', string='Branches', track_visibility='onchange')
    detail_of_accident = fields.Html(string='Details of the accident', track_visibility='onchange')

    claim_type = fields.Selection(
        [('third_party_claim', 'Third Party Claim'), ('shaamil_claim', 'Shaamil Claim'), ('clear_cars', 'Clear Cars')],
        string='Claim Type', track_visibility='onchange')

    # Third Party claims
    insurance_company = fields.Many2one('res.partner', string="Insurance Company", track_visibility='onchange')
    car_places = fields.Many2one('car.places.config', string="Car Places", track_visibility='onchange')
    responsibility_ratio = fields.Integer(string='Responsibility Ratio', track_visibility='onchange')
    claim_amount = fields.Float(string='Claim Amount', track_visibility='onchange')
    ta_claim_ref = fields.Text(string='Claim Ref', track_visibility='onchange')
    tpc_has_damaged = fields.Boolean('Damaged Assessed', track_visibility='onchange', copy=False)
    is_shipped = fields.Boolean('Is Shipped', track_visibility='onchange', copy=False)
    car_amount = fields.Float(string='Car Amount', track_visibility='onchange')
    bassami_representative = fields.Text(string='Bassami Representative', track_visibility='onchange')
    is_consists = fields.Boolean('Is consists', track_visibility='onchange', copy=False)
    state_shaamil = fields.Selection([
        ('1', 'Technical Support'),
        ('2', 'Insurance Manger Transfer'),
        ('3', 'Maintenance Confirm'),
        ('4', 'Operation'),
        ('5', 'Accountant Confirm'),
        ('6', 'Done'),
    ], default='1', store=True,copy=False, track_visibility='onchange')
    state_third_party = fields.Selection([
        ('1', 'Technical Support'),
        ('2', 'Insurance Manger Transfer'),
        ('3', 'Maintenance Confirm'),
        ('4', 'Operation'),
        ('5', 'Accountant Confirm'),
        ('6', 'Done'),
    ], default='1', store=True, track_visibility='onchange')
    state_clear_cars = fields.Selection([
        ('1', 'Insurance Accountant'),
        ('2', 'Insurance Manger'),
        ('3', 'Investment Confirm'),
        ('4', 'Financial Control'),
        ('5', 'Audit Confirm'),
        ('6', 'Financial Manager Confirm'),
        ('7', 'Accountant Confirm'),
        ('8', 'Done'),
    ], default='1', store=True, track_visibility='onchange')

    # @api.multi
    def action_waiting_payment(self):
        self.write({'state': '11'})

    # @api.multi
    def action_waiting_tax_invoice(self):
        self.write({'state': '12'})

    @api.depends('rfq_price', 'spare_parts_amount', 'raw_materials_amount', 'hand_wages_amount', 'rfq_price_paid',
                 'less_rfq_price', 'estimated_by')
    def _compute_estimate_after_accident(self):
        for rec in self:
            if rec.estimated_by == 'agency_estimate':
                if rec.rfq_price_paid:
                    rec.estimate_after_accident = rec.spare_parts_amount + rec.raw_materials_amount + rec.hand_wages_amount
                else:
                    rec.estimate_after_accident = rec.spare_parts_amount + rec.raw_materials_amount + rec.hand_wages_amount + rec.rfq_price
            elif rec.estimated_by == 'insurance_workshops':
                if rec.rfq_price_paid:
                    rec.estimate_after_accident = rec.spare_parts_amount + rec.less_rfq_price
                else:
                    rec.estimate_after_accident = rec.spare_parts_amount + rec.less_rfq_price + rec.rfq_price
            else:
                if rec.rfq_price_paid:
                    rec.estimate_after_accident = rec.compensation_amount
                else:
                    rec.estimate_after_accident = rec.compensation_amount + rec.rfq_price

    @api.depends('driver_name')
    def _compute_last_accident(self):
        truck_accident = self.env['bsg.truck.accident']
        for rec in self:
            rec.number_of_accident = truck_accident.search_count([('driver_name', '=', rec.driver_name.id)])
            rec.last_accident = truck_accident.search([('driver_name', '=', rec.driver_name.id)], limit=1,
                                                      order='create_date DESC').id

    # @api.multi
    @api.onchange('shipment_no_id')
    def get_trips(self):
        if self.shipment_no_id:
            trip_history_ids = self.shipment_no_id.trip_history_ids
            trip_list = []
            if trip_history_ids:
                for rec in trip_history_ids:
                    trip_list.append(rec.fleet_trip_id.id)
            if self.shipment_no_id.fleet_trip_id:
                trip_list.append(self.shipment_no_id.fleet_trip_id.id)
            if self.shipment_no_id.last_fleet_trip_id:
                trip_list.append(self.shipment_no_id.last_fleet_trip_id.id)

            return {'domain': {'trip_id': [('id', 'in', trip_list)]}}
        else:
            if self.accident_agreement_type == 'agreement_cus':
                domain_shipment_no = ['|', ('sale_order_state', 'in', ['done', 'pod', 'Delivered']),
                                      ('bsg_cargo_return_sale_id', '!=', False), ('state', 'in',
                                                                                  ['draft', 'on_transit', 'Delivered',
                                                                                   'shipped', 'done', 'released']),
                                      ('payment_method.payment_type', 'in', ['cash', 'pod'])]
            else:
                domain_shipment_no = ['|', ('sale_order_state', 'in', ['done', 'pod', 'Delivered']),
                                      ('bsg_cargo_return_sale_id', '!=', False), ('state', 'in',
                                                                                  ['draft', 'on_transit', 'Delivered',
                                                                                   'shipped', 'done', 'released']),
                                      ('payment_method.payment_type', 'in', ['credit'])]
            return {'domain': {'shipment_no_id': domain_shipment_no}}

    #
    # @api.multi
    # @api.onchange('fleet_id')
    # def get_vehicle_code_data(self):
    #     if self.fleet_id:
    #         self.driver_name = self.fleet_id.bsg_driver
    #         self.truck_id = self.fleet_id.model_id
    #         self.plate_no = self.fleet_id.license_plate
    #         self.kilometer = self.fleet_id.odometer

    # @api.multi
    @api.onchange('trip_id')
    def get_trip_data(self):
        if self.trip_id:
            self.fleet_id = self.trip_id.vehicle_id.id
            if self.accident_agreement_type == 'bassami_truck':
                for res in self:
                    for re in range(len(res.trip_id.stock_picking_id)):
                        if re == 0:
                            res.detail_of_accident = """<h3>Vehicle : {vehicle_id}</h3>
                                <table class="table">
                                  <thead>
                                    <tr>
                                      <th scope="col">Picking name</th>
                                      <th scope="col">Car Maker</th>
                                      <th scope="col">Model</th>
                                      <th scope="col">Color</th>
                                      <th scope="col">Year</th>
                                      <th scope="col">Plate No</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    <tr>
                                      <td style="width: 18%;">{picking_name}</td>
                                      <td style="width: 17%;">{car_maker_id}</td>
                                      <td style="width: 17%;">{car_model_id}</td>
                                      <td style="width: 15%;">{car_color}</td>
                                      <td style="width: 15%;">{year}</td>
                                      <td style="width: 18%;">{plate_no}</td>
                                    </tr>
                                  </tbody>
                                </table>
                                """.format(
                                vehicle_id=res.trip_id.vehicle_id.taq_number,
                                picking_name=res.trip_id.stock_picking_id[0].picking_name.sale_line_rec_name,
                                car_maker_id=res.trip_id.stock_picking_id[0].car_maker_id.car_maker.car_make_ar_name,
                                car_model_id=res.trip_id.stock_picking_id[0].car_model_id.car_model_name,
                                car_color=res.trip_id.stock_picking_id[0].picking_name.car_color.vehicle_color_name,
                                year=res.trip_id.stock_picking_id[0].picking_name.year.car_year_name,
                                plate_no=res.trip_id.stock_picking_id[0].plate_no
                            )
                        if re > 0:
                            res.detail_of_accident += """
                            <table class="table">
                                  <tbody>
                                    <tr>
                                      <td style="width: 18%;">{picking_name}</td>
                                      <td style="width: 17%;">{car_maker_id}</td>
                                      <td style="width: 17%;">{car_model_id}</td>
                                      <td style="width: 15%;">{car_color}</td>
                                      <td style="width: 15%;">{year}</td>
                                      <td style="width: 18%;">{plate_no}</td>
                                    </tr>
                                  </tbody>
                              </table>
                                """.format(
                                vehicle_id=res.trip_id.vehicle_id.taq_number,
                                picking_name=res.trip_id.stock_picking_id[re].picking_name.sale_line_rec_name,
                                car_maker_id=res.trip_id.stock_picking_id[re].car_maker_id.car_maker.car_make_ar_name,
                                car_model_id=res.trip_id.stock_picking_id[re].car_model_id.car_model_name,
                                car_color=res.trip_id.stock_picking_id[re].picking_name.car_color.vehicle_color_name,
                                year=res.trip_id.stock_picking_id[re].picking_name.year.car_year_name,
                                plate_no=res.trip_id.stock_picking_id[re].plate_no
                            )

    # @api.multi
    def _compute_attachment_number(self):
        for truck in self:
            truck.attachment_number = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'bsg.truck.accident'), ('res_id', '=', truck.id)])

    # @api.multi
    def open_attach_wizard(self):
        view_id = self.env.ref('bsg_truck_accidents.view_attachment_form_for_truck_accident').id
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_res_model': '%s','default_res_id': %d,'default_type': 'binary'}" % (
                self._name, self.id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    # @api.multi
    def action_shipping(self):
        self.write({'state_shaamil': '5', 'is_shipped': True})

    # @api.multi
    def action_receive(self):
        self.write({'state_shaamil': '1'})

    # @api.multi
    def action_driver_deduction(self):
        if self.claim_type == 'third_party_claim':
            if not self.mistake_percentage > 0.0:
                raise ValidationError(_('The mistake amount must be Strictly positive.'))
            if not self.note:
                raise ValidationError(_('Please set note for move line'))
            claims_config = self.env['claims_account_config'].sudo().search(
                [('company_id', '=', self.env.user.company_id.id)], limit=1)
            date = fields.Date.today()
            price_unit = self.mistake_percentage
            journal_id = claims_config.journal_id.id
            debit_account_id = claims_config.driver_mistake_account_id.id
            credit_account_id = claims_config.claim_account_id.id
            analytic_account_id = claims_config.analytic_account_id.id
            partner_id = self.driver_name.partner_id.id
            if self.assign_deduction_drivers:
                partner_id = self.special_customer.id
            if not partner_id:
                raise ValidationError(_('Please select partner.'))
            label = self.note if self.note else ''
            so_line_car_make = self.so_line_car_make.display_name if self.so_line_car_make.display_name else ''
            so_line_car_model = self.so_line_car_model.display_name if self.so_line_car_model.display_name else ''
            so_line_general_plate_no = self.so_line_general_plate_no if self.so_line_general_plate_no else ''
            so_line_chassis_no = self.so_line_chassis_no if self.so_line_chassis_no else ''
            name = label + ' ' + so_line_car_make + ' ' + so_line_car_model + ' ' + so_line_general_plate_no + ' ' + so_line_chassis_no
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'name': '/',
                'journal_id': journal_id,
                'bsg_truck_accident': self.id,
                'date': date,
                'ref': self.name,
                'line_ids': [(0, 0, {
                    'name': name,
                    'partner_id': partner_id,
                    'debit': price_unit,
                    'account_id': debit_account_id,
                    # 'analytic_distribution': analytic_account_id,
                }), (0, 0, {
                    'name': name,
                    'partner_id': partner_id,
                    'credit': price_unit,
                    'account_id': credit_account_id,
                })]
            })
            self.move_id = move.id
            move.action_post()
        else:
            if not self.mistake_percentage > 0.0:
                raise ValidationError(_('The mistake amount must be Strictly positive.'))
            if not self.note:
                raise ValidationError(_('Please set note for move line'))
            if not self.is_send_to_audit:
                raise ValidationError(_('Please send to audit for confirmation'))
            claims_config = self.env['claims_account_config'].sudo().search(
                [('company_id', '=', self.env.user.company_id.id)], limit=1)
            date = fields.Date.today()
            price_unit = self.mistake_percentage
            journal_id = claims_config.journal_id.id
            debit_account_id = claims_config.driver_mistake_account_id.id
            credit_account_id = claims_config.claim_account_id.id
            # analytic_account_id = claims_config.analytic_account_id.id
            partner_id = self.driver_name.partner_id.id
            if self.assign_deduction_drivers:
                partner_id = self.special_customer.id
            if not partner_id:
                raise ValidationError(_('Please select partner.'))
            label = self.note if self.note else ''
            so_line_car_make = self.so_line_car_make.display_name if self.so_line_car_make.display_name else ''
            so_line_car_model = self.so_line_car_model.display_name if self.so_line_car_model.display_name else ''
            so_line_general_plate_no = self.so_line_general_plate_no if self.so_line_general_plate_no else ''
            so_line_chassis_no = self.so_line_chassis_no if self.so_line_chassis_no else ''
            name = label + ' ' + so_line_car_make + ' ' + so_line_car_model + ' ' + so_line_general_plate_no + ' ' + so_line_chassis_no
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'name': '/',
                'journal_id': journal_id,
                'bsg_truck_accident': self.id,
                'date': date,
                'ref': self.name,
                'line_ids': [(0, 0, {
                    'name': name,
                    'partner_id': partner_id,
                    'debit': price_unit,
                    'account_id': debit_account_id,
                    # 'account_analytic_id': analytic_account_id,
                }), (0, 0, {
                    'name': name,
                    'partner_id': partner_id,
                    'credit': price_unit,
                    'account_id': credit_account_id,
                })]
            })
            self.move_id = move.id
            move.action_post()

    # @api.multi
    def action_cancel(self):
        self.write({'state': '9'})

    # @api.multi
    def action_reset(self):
        self.write({'state': '1'})

    def action_confirm(self):
        if self.claim_type == 'third_party_claim':
            state_id = int(self.state_third_party)
            state_id += 1
            if not self.tpc_has_damaged:
                raise ValidationError(_('Cant approve claim until mark damaged assessed'))
            if self.state_third_party == "1" and self.name == _('New'):
                self.write({'name': self.env['ir.sequence'].next_by_code('seq.third.party.claims') or _('New')})
            self.write({'state_third_party': str(state_id)})
        elif self.claim_type == 'shaamil_claim':
            state_id = int(self.state_shaamil)
            state_id += 1
            if self.state_shaamil == "1" and self.name == _('New'):
                self.write({'name': self.env['ir.sequence'].next_by_code('seq.shaamil.claims') or _('New')})
            if self.state_shaamil == "1" and self.vendor_bill_id:
                state_id = 6
            self.write({'state_shaamil': str(state_id)})
        elif self.claim_type == 'clear_cars':
            state_id = int(self.state_clear_cars)
            state_id += 1
            if self.state_clear_cars == "1" and self.name == _('New'):
                self.write({'name': self.env['ir.sequence'].next_by_code('seq.clear.cars.claims') or _('New')})
            self.write({'state_clear_cars': str(state_id)})
        else:
            if self.is_path_to_audit:
                self.write({'state': '7', 'is_send_to_audit': True})
            else:
                state_id = int(self.state)
                if self.accident_agreement_type == 'agreement_comp':
                    if state_id == 1:
                        state_id += 2
                    elif state_id == 3:
                        state_id += 3
                    elif state_id == 12:
                        state_id = 5
                    else:
                        state_id += 1
                else:
                    state_id += 1
                required_attachment_ids = self.env['truck.accident.attachment'].sudo().search(
                    [('is_required', '=', True)]).ids
                attachment_ids = self.env['ir.attachment'].sudo().search(
                    [('res_model', '=', 'bsg.truck.accident'), ('res_id', 'in', self.ids)]).mapped(
                    'truck_accident_attach')
                if attachment_ids and required_attachment_ids:
                    for rec in required_attachment_ids:
                        if rec not in attachment_ids.ids:
                            raise ValidationError("Please add mandatory attachments")
                if self.state == "1" and self.attachment_number == 0 or not self.is_pics_attach:
                    raise ValidationError("Please add mandatory attachments")
                if self.state == "1" and self.name == _('New'):
                    self.write({'name': self.env['ir.sequence'].next_by_code('bsg.truck.accident.seq') or _('New')})
                self.write({'state': str(state_id)})

    # @api.multi
    def action_create_bill(self):
        if self.claim_type == 'third_party_claim':
            if not self.ta_claim_ref:
                raise ValidationError(_('Please set reference for creating bill'))
            claims_config = self.env['claims_account_config'].sudo().search(
                [('company_id', '=', self.env.user.company_id.id)], limit=1)
            if not claims_config:
                raise ValidationError(_('Please make configuration for claims'))
            invoice_date = fields.Date.today()
            product_id = claims_config.claim_product_id.product_variant_id.id
            analytic_account_id = claims_config.analytic_account_id.id
            journal_id = claims_config.journal_id.id
            label = self.ta_claim_ref if self.ta_claim_ref else ''
            inv_type = 'out_invoice'
            journal_type = 'sale'
            invoice_line_data = []
            so_line_car_make = self.so_line_car_make.display_name if self.so_line_car_make.display_name else ''
            so_line_car_model = self.so_line_car_model.display_name if self.so_line_car_model.display_name else ''
            so_line_general_plate_no = self.so_line_general_plate_no if self.so_line_general_plate_no else ''
            so_line_chassis_no = self.so_line_chassis_no if self.so_line_chassis_no else ''
            name = label + ' ' + so_line_car_make + ' ' + so_line_car_model + ' ' + so_line_general_plate_no + ' ' + so_line_chassis_no
            partner_id = self.insurance_company.id
            amount = self.claim_amount
            account_id = claims_config.claim_account_id.id if claims_config.claim_account_id else product_id.product_account_expense_id.id
            tax_id = claims_config.customer_tax_id.id
            line1 = {
                'product_id': product_id,
                'quantity': 1.00,
                'account_id': account_id,
                'name': name,
                'price_unit': amount,
                'analytic_distribution': {analytic_account_id: 100},
                'tax_ids': [(6, 0, [tax_id])],
            }
            invoice_line_data.append((0, 0, line1))
            invoice = self.env['account.move'].create(dict(
                move_type=inv_type,
                name=self.name + ' - ' + self.shipment_no_id.sale_line_rec_name or '',
                partner_id=partner_id,
                l10n_in_journal_type=journal_type,
                invoice_line_ids=invoice_line_data,
                invoice_date=invoice_date,
                truck_accident_id=self.id,
                claims_branch_id=self.env.user.user_branch_id.id,
                invoice_origin=self.name

            ))
            invoice.action_post()
            self.vendor_bill_id = invoice.id
        elif self.claim_type == 'shaamil_claim':
            inv_type = 'in_refund' if self.is_consists else 'in_invoice'
            claims_config = self.env['claims_account_config'].sudo().search(
                [('company_id', '=', self.env.user.company_id.id)], limit=1)
            if not claims_config:
                raise ValidationError(_('Please make configuration for claims'))
            invoice_date = fields.Date.today()
            product_id = claims_config.claim_product_id.id
            analytic_account_id = claims_config.analytic_account_id.id
            journal_id = claims_config.journal_id.id
            label = self.ta_claim_ref if self.ta_claim_ref else ''
            journal_type = 'sale'
            invoice_line_data = []
            so_line_car_make = self.so_line_car_make.display_name if self.so_line_car_make.display_name else ''
            so_line_car_model = self.so_line_car_model.display_name if self.so_line_car_model.display_name else ''
            so_line_general_plate_no = self.so_line_general_plate_no if self.so_line_general_plate_no else ''
            so_line_chassis_no = self.so_line_chassis_no if self.so_line_chassis_no else ''
            name = label + ' ' + so_line_car_make + ' ' + so_line_car_model + ' ' + so_line_general_plate_no + ' ' + so_line_chassis_no
            partner_id = self.workshop.id
            amount = self.claim_amount
            account_id = claims_config.claim_account_id.id if claims_config.claim_account_id else product_id.product_account_expense_id.id
            tax_id = claims_config.vendor_tax_id.id
            line1 = {
                'product_id': product_id,
                'quantity': 1.00,
                'account_id': account_id,
                'name': name,
                'price_unit': amount,
                'analytic_distribution': {analytic_account_id: 100},
                'tax_ids': [(6, 0, [tax_id])],
            }
            invoice_line_data.append((0, 0, line1))
            invoice = self.env['account.move'].create(dict(
                move_type=inv_type,
                name=self.name + ' - ' + self.shipment_no_id.sale_line_rec_name if self.shipment_no_id else '',
                partner_id=partner_id,
                l10n_in_journal_type=journal_type,
                invoice_line_ids=invoice_line_data,
                invoice_date=invoice_date,
                truck_accident_id=self.id,
                claims_branch_id=self.env.user.user_branch_id.id,
                invoice_origin=self.name

            ))
            invoice.action_post()
            self.vendor_bill_id = invoice.id
            self.write({'state_shaamil': '4'})
        elif self.claim_type == 'clear_cars':
            inv_type = 'out_invoice'
            claims_config = self.env['claims_account_config'].sudo().search(
                [('company_id', '=', self.env.user.company_id.id)], limit=1)
            if not claims_config:
                raise ValidationError(_('Please make configuration for claims'))
            invoice_date = fields.Date.today()
            product_id = claims_config.claim_product_id.id
            analytic_account_id = claims_config.analytic_account_id.id
            journal_id = claims_config.journal_id.id
            label = self.internal_note if self.internal_note else ''
            journal_type = 'sale'
            invoice_line_data = []
            so_line_car_make = self.so_line_car_make.display_name if self.so_line_car_make.display_name else ''
            so_line_car_model = self.so_line_car_model.display_name if self.so_line_car_model.display_name else ''
            so_line_general_plate_no = self.so_line_general_plate_no if self.so_line_general_plate_no else ''
            so_line_chassis_no = self.so_line_chassis_no if self.so_line_chassis_no else ''
            name = label + ' ' + so_line_car_make + ' ' + so_line_car_model + ' ' + so_line_general_plate_no + ' ' + so_line_chassis_no
            partner_id = self.so_line_partner_id.id
            amount = self.car_amount
            account_id = claims_config.cars_account_id.id if claims_config.cars_account_id else product_id.product_account_expense_id.id
            tax_id = claims_config.customer_tax_id.id
            line1 = {
                'product_id': product_id,
                'quantity': 1.00,
                'account_id': account_id,
                'name': name,
                'price_unit': amount,
                'analytic_distribution': {analytic_account_id: 100},
                'tax_ids': [(6, 0, [tax_id])],
            }
            invoice_line_data.append((0, 0, line1))
            invoice = self.env['account.move'].create(dict(
                move_type=inv_type,
                name=self.name + ' - ' + self.shipment_no_id.sale_line_rec_name if self.shipment_no_id else '',
                partner_id=partner_id,
                l10n_in_journal_type=journal_type,
                invoice_line_ids=invoice_line_data,
                invoice_date=invoice_date,
                truck_accident_id=self.id,
                claims_branch_id=self.env.user.user_branch_id.id,
                invoice_origin=self.name

            ))
            invoice.action_post()
            self.vendor_bill_id = invoice.id
        else:
            if not self.is_send_to_audit:
                raise ValidationError(_('Please send to audit for confirmation'))
            if not self.estimate_after_accident > 0.0:
                raise ValidationError(_('The amount must be Strictly positive.'))
            if not self.internal_note:
                raise ValidationError(_('Please set note for creating bill'))
            claims_config = self.env['claims_account_config'].sudo().search(
                [('company_id', '=', self.env.user.company_id.id)], limit=1)
            invoice_date = fields.Date.today()
            product_id = claims_config.claim_product_id.id
            analytic_account_id = claims_config.analytic_account_id.id
            journal_id = claims_config.journal_id.id
            label = self.label if self.label else ''
            so_line_car_make = self.so_line_car_make.display_name if self.so_line_car_make.display_name else ''
            so_line_car_model = self.so_line_car_model.display_name if self.so_line_car_model.display_name else ''
            so_line_general_plate_no = self.so_line_general_plate_no if self.so_line_general_plate_no else ''
            so_line_chassis_no = self.so_line_chassis_no if self.so_line_chassis_no else ''
            name = label + ' ' + so_line_car_make + ' ' + so_line_car_model + ' ' + so_line_general_plate_no + ' ' + so_line_chassis_no
            partner_id = self.workshop.id if self.is_external_maintenance else self.so_line_partner_id.id
            if self.is_external_maintenance:
                partner_id = self.workshop.id
            elif not self.is_external_maintenance and self.accident_agreement_type == 'agreement_comp' and self.cc_partner_id:
                partner_id = self.cc_partner_id.id
            elif self.invoice_to_other:
                partner_id = self.invoice_to_other.id
                invoice_date = self.invoice_to_other_date
            else:
                partner_id = self.so_line_partner_id.id
            account_id = claims_config.claim_account_id.id if claims_config.claim_account_id else product_id.product_account_expense_id.id
            tax_id = claims_config.vendor_tax_id.id if self.is_external_maintenance else claims_config.customer_tax_id.id
            inv_type = 'out_refund'
            journal_type = 'sale'
            if self.is_external_maintenance:
                inv_type = 'in_invoice'
                journal_type = 'purchase'
            invoice_line_data = []
            if self.estimated_by == 'sheikh_dealer':
                amount1 = self.compensation_amount
                amount2 = self.rfq_price
                if not amount1 + amount2 > 0.0:
                    raise ValidationError(_('The amount must be Strictly positive.'))
                line1 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount1,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_compensation_amount_tax else False,
                }
                line2 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount2,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_rfq_price_tax else False,
                }
                if self.rfq_price_paid:
                    if line1['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line1))
                else:
                    if line1['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line1))
                    if line2['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line2))
            elif self.estimated_by == 'insurance_workshops':
                amount1 = self.less_rfq_price
                amount2 = self.rfq_price
                amount3 = self.spare_parts_amount
                if not amount1 + amount2 + amount3 > 0.0:
                    raise ValidationError(_('The amount must be Strictly positive.'))
                line1 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount1,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_less_rfq_price_tax else False,
                }
                line2 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount2,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_rfq_price_tax else False,
                }
                line3 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount3,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_spare_parts_amount_tax else False,
                }
                if self.rfq_price_paid:
                    if line1['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line1))
                    if line3['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line3))
                else:
                    if line1['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line1))
                    if line2['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line2))
                    if line3['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line3))
            elif self.estimated_by == 'agency_estimate':
                amount1 = self.rfq_price
                amount2 = self.spare_parts_amount
                amount3 = self.raw_materials_amount
                amount4 = self.hand_wages_amount
                if not amount1 + amount2 + amount3 + amount4 > 0.0:
                    raise ValidationError(_('The amount must be Strictly positive.'))
                line1 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount1,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_rfq_price_tax else False,
                }
                line2 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount2,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_spare_parts_amount_tax else False,
                }
                line3 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount3,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_raw_materials_amount_tax else False,
                }
                line4 = {
                    'product_id': product_id,
                    'quantity': 1.00,
                    'account_id': account_id,
                    'name': name,
                    'price_unit': amount4,
                    'analytic_distribution': {analytic_account_id: 100},
                    'tax_ids': [(6, 0, [tax_id])] if self.is_hand_wages_amount_tax else False,
                }
                if self.rfq_price_paid:
                    if line2['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line2))
                    if line3['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line3))
                    if line4['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line4))
                else:
                    if line1['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line1))
                    if line2['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line2))
                    if line3['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line3))
                    if line4['price_unit'] > 0.0:
                        invoice_line_data.append((0, 0, line4))
            invoice = self.env['account.move'].create(dict(
                move_type=inv_type,
                name=self.name + ' - ' + self.shipment_no_id.sale_line_rec_name if self.shipment_no_id else '',
                partner_id=partner_id,
                branches_ids=self.branches_ids.ids if self.branches_ids else [],
                l10n_in_journal_type=journal_type,
                invoice_line_ids=invoice_line_data,
                invoice_date=invoice_date,
                truck_accident_id=self.id,
                claims_branch_id=self.env.user.user_branch_id.id,
                invoice_origin=self.name

            ))
            invoice.action_post()
            self.vendor_bill_id = invoice.id

    # @api.multi
    def action_create_compensation_bill(self):
        if not self.is_send_to_audit:
            raise ValidationError(_('Please send to audit for confirmation'))
        if not self.compensation_amount_2 > 0.0:
            raise ValidationError(_('The compensation amount must be Strictly positive.'))
        claims_config = self.env['claims_account_config'].sudo().search(
            [('company_id', '=', self.env.user.company_id.id)], limit=1)
        invoice_date = fields.Date.today()
        product_id = claims_config.claim_product_id.id
        price_unit = self.compensation_amount_2
        if not price_unit > 0.0:
            raise ValidationError(_('The amount must be Strictly positive.'))
        analytic_account_id = claims_config.analytic_account_id.id
        journal_id = claims_config.journal_id.id
        label = self.label if self.label else ''
        so_line_car_make = self.so_line_car_make.display_name if self.so_line_car_make.display_name else ''
        so_line_car_model = self.so_line_car_model.display_name if self.so_line_car_model.display_name else ''
        so_line_general_plate_no = self.so_line_general_plate_no if self.so_line_general_plate_no else ''
        so_line_chassis_no = self.so_line_chassis_no if self.so_line_chassis_no else ''
        name = label + ' ' + so_line_car_make + ' ' + so_line_car_model + ' ' + so_line_general_plate_no + ' ' + so_line_chassis_no
        partner_id = self.insurance_partner.id
        account_id = claims_config.claim_account_id.id if claims_config.claim_account_id else product_id.product_account_expense_id.id
        tax_id = claims_config.customer_tax_id.id
        invoice_line_data = [
            (0, 0,
             {
                 'product_id': product_id,
                 'quantity': 1.00,
                 'account_id': account_id,
                 'name': name,
                 'price_unit': price_unit,
                 'account_analytic_id': analytic_account_id,
                 'invoice_line_tax_ids': [(6, 0, [tax_id])] if self.is_compensation_amount_2 else False,

             }
             )
        ]
        invoice = self.env['account.move'].create(dict(
            type='out_invoice',
            name=self.name + ' - ' + self.shipment_no_id.sale_line_rec_name if self.shipment_no_id else '',
            partner_id=partner_id,
            invoice_line_ids=invoice_line_data,
            invoice_date=invoice_date,
            compensation_id=self.id,
            claims_branch_id=self.env.user.user_branch_id.id,

        ))
        invoice.action_post()
        self.compensation_bill_id = invoice.id

    # @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_truck_accidents.action_attachment_for_truck_accident')
        res['domain'] = [('res_model', '=', 'bsg.truck.accident'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'bsg.truck.accident', 'default_res_id': self.id, }
        return res

    # @api.multi
    def _compute_bill_number(self):
        for bill in self:
            bill.bill_number = self.env['account.move'].search_count([('truck_accident_id', '=', bill.id)])

    # @api.multi
    def action_get_bill_view(self):
        self.ensure_one()
        if self.accident_agreement_type in ['agreement_comp', 'agreement_cus']:
            inv_type = 'out_refund'
            journal_type = 'sale'
            if self.is_external_maintenance:
                inv_type = 'in_invoice'
                journal_type = 'purchase'
            # res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_out_refund')
            res = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_refund_type')
            res['domain'] = [('truck_accident_id', 'in', self.ids)]
            res['context'] = {'default_type': inv_type, 'type': inv_type, 'journal_type': journal_type}
        elif self.accident_agreement_type == 'bassami_truck' and self.claim_type == 'third_party_claim':
            inv_type = 'out_invoice'
            journal_type = 'sale'
            # res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_tree1')
            res = self.env['ir.actions.act_window']._for_xml_id('account.action_invoice_tree1')
            res['domain'] = [('truck_accident_id', 'in', self.ids)]
            res['context'] = {'default_type': inv_type, 'type': inv_type, 'journal_type': journal_type}
        elif self.accident_agreement_type == 'bassami_truck' and self.claim_type == 'clear_cars':
            inv_type = 'out_refund'
            journal_type = 'sale'
            # res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_out_refund')
            res = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_refund_type')
            res['domain'] = [('truck_accident_id', 'in', self.ids)]
            res['context'] = {'default_type': inv_type, 'type': inv_type, 'journal_type': journal_type}
        elif self.accident_agreement_type == 'bassami_truck' and self.claim_type == 'shaamil_claim':
            inv_type = 'in_refund' if self.is_consists else 'in_invoice'
            journal_type = 'sale'
            if self.is_consists:
                # res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_in_refund')
                res = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_refund_type')
            else:
                # res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_vendor_bill_template')
                res = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
            res['domain'] = [('truck_accident_id', 'in', self.ids)]
            res['context'] = {'default_type': inv_type, 'type': inv_type, 'journal_type': journal_type}
        return res

    # @api.multi
    def _compute_compensation_bill_number(self):
        for bill in self:
            bill.compensation_bill_number = self.env['account.move'].search_count(
                [('compensation_id', '=', bill.id)])

    # @api.multi
    def action_get_compensation_bill_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('account.action_invoice_tree1')
        res['domain'] = [('compensation_id', 'in', self.ids)]
        res['context'] = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale'}
        return res

    # @api.multi
    def _compute_jv_number(self):
        for jv in self:
            jv.jv_number = self.env['account.move'].search_count([('bsg_truck_accident', '=', jv.id)])

    # @api.multi
    def action_get_jv_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')
        res['domain'] = [('bsg_truck_accident', 'in', self.ids)]
        return res

    @api.model
    def create(self, vals):
        if vals.get('accident_agreement_type') in ['agreement_comp', 'agreement_cus']:
            vals['is_send_to_audit'] = True
        if vals.get('accident_agreement_type') in ['agreement_comp', 'agreement_cus']:
            shipment_no_id = self.env['bsg.truck.accident'].search([('shipment_no_id', '=',vals.get('shipment_no_id')), ('state', 'not in', ['9'])])
            if len(shipment_no_id) > 0:
                raise ValidationError('Claim related to this Shipment No already exists')
        return super(BsgTruckAccident, self).create(vals)

    # @api.multi
    def unlink(self):
        for truck in self:
            if truck.state != '1':
                raise ValidationError(_("You can only delete this record in draft state"))
        return super(BsgTruckAccident, self).unlink()

    # @api.multi
    def _compute_group_check(self):
        for rec in self:
            rec.bool_group_check = False
            if rec.accident_agreement_type in ['agreement_comp', 'agreement_cus']:
                if rec.state == '1':
                    if self.env.user.has_group('bsg_truck_accidents.group_truck_accident') or self.env.user.has_group(
                            'bsg_truck_accidents.group_truck_company_claims') or \
                            self.env.user.has_group(
                                'bsg_truck_accidents.group_individual_claims') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state == '2':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_1') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state == '3':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state == '12':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state == '4':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_3') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state == '5':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_4') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state == '6':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_5') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state == '7' or rec.state == '11':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state == '8':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_group_check = True
            elif rec.accident_agreement_type == 'bassami_truck' and rec.claim_type == 'clear_cars':
                if rec.state_clear_cars == '1':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_1') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_clear_cars == '2':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_clear_cars == '3':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_9') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_clear_cars == '4':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_4') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_clear_cars == '5':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_3') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_clear_cars == '6':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_5') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_clear_cars == '7':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_clear_cars == '8':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_group_check = True
            elif rec.accident_agreement_type == 'bassami_truck' and rec.claim_type == 'third_party_claim':
                if rec.state_third_party == '1':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_shaamil_claims_state_1') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_third_party == '2':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_11') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_third_party == '3':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_10') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_third_party == '4':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_shaamil_claims_4') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_third_party == '5':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_group_check = True
            elif rec.accident_agreement_type == 'bassami_truck' and rec.claim_type == 'shaamil_claim':
                if rec.state_shaamil == '1':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_shaamil_claims_state_1') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_shaamil == '2':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_shaamil == '3':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_10') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_shaamil == '4':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_shaamil_claims_4') or self.env.user._is_admin():
                        rec.bool_group_check = True
                elif rec.state_shaamil == '5':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_group_check = True

    # @api.multi
    def _compute_readonly_financials(self):
        for rec in self:
            rec.bool_readonly_financials_1 = True
            rec.bool_readonly_financials_2 = True
            if rec.accident_agreement_type == 'agreement_comp':
                if rec.state == '1' or rec.state == '3':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_1') or self.env.user.has_group(
                        'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_readonly_financials_1 = False
                        rec.bool_readonly_financials_2 = False
                if rec.state == '7' or rec.state == '8':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                if rec.state == '6':
                    if self.env.user.has_group('bsg_truck_accidents.group_state_accident_state_5') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                if rec.state == '12':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_readonly_financials_1 = False
                        rec.bool_readonly_financials_2 = False
            elif rec.accident_agreement_type == 'agreement_cus':
                if rec.state == '1' or rec.state == '2':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_1') or self.env.user.has_group(
                        'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_readonly_financials_1 = False
                        rec.bool_readonly_financials_2 = False
                if rec.state == '3':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_readonly_financials_1 = False
                        rec.bool_readonly_financials_2 = False
                if rec.state == '7' or rec.state == '8' or rec.state == '11':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
            elif rec.claim_type == 'third_party_claim':
                if self.env.user.has_group(
                        'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                    rec.bool_readonly_financials_2 = False
            elif rec.claim_type == 'shaamil_claim':
                if rec.state_shaamil == '1':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_shaamil_claims_state_1') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_shaamil == '2':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_shaamil == '3':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_10') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_shaamil == '4':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_shaamil_claims_4') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_shaamil == '5':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
            elif rec.claim_type == 'clear_cars':
                if rec.state_clear_cars == '1':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_1') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_clear_cars == '2':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_2') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_clear_cars == '3':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_9') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_clear_cars == '4':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_3') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_clear_cars == '5':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_3') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_clear_cars == '6':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_5') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_clear_cars == '7':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False
                elif rec.state_clear_cars == '8':
                    if self.env.user.has_group(
                            'bsg_truck_accidents.group_state_accident_state_6') or self.env.user._is_admin():
                        rec.bool_readonly_financials_2 = False

    @api.constrains('accident_date')
    def check_accident_date(self):
        if not self.accident_date <= fields.Date.today():
            raise ValidationError(_('You cannot set future accident date'))

    @api.constrains('responsibility_ratio')
    def check_responsibility_ratio(self):
        if self.responsibility_ratio > 100:
            raise ValidationError(_('You cannot set responsibility ratio greater than 100'))

    def action_send_to_audit_confirm(self):
        self.write({'state': '4', 'is_path_to_audit': True})

    # @api.multi
    def action_multi_create_bill_claims(self):
        partner_list = []
        for rec in self:
            partner_list.append(rec.so_line_partner_id.id)
        if set(partner_list).__len__() == 1:
            for claim in self:
                if not claim.vendor_bill_id:
                    claim.action_create_bill()
                else:
                    raise ValidationError(_('Bill already created in one of lines'))
        else:
            raise ValidationError(_('Please select lines having same customer'))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(BsgTruckAccident, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and not self.env.user._is_admin():
            if self.env.user.has_group('bsg_truck_accidents.group_state_accident_state_7') or self.env.user.has_group(
                    'bsg_truck_accidents.group_state_accident_state_7') or self.env.user.has_group(
                    'bsg_truck_accidents.group_state_accident_state_8'):
                doc = etree.XML(result['arch'])
                for t in doc.xpath("//form"):
                    t.set('edit', "false")
                    t.set('create', "false")
                for t in doc.xpath("//button"):
                    t.set('invisible', "1")
                result['arch'] = etree.tostring(doc)
                method_nodes = doc.xpath("//field")
                for node in method_nodes:
                    node.set('readonly', "1")
                    setup_modifiers(node, result['fields'][node.get('name', False)])
                result['arch'] = etree.tostring(doc)
        return result
