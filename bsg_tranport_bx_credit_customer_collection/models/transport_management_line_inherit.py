# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError,Warning
from datetime import datetime


class TransportManagementLine(models.Model):
    _inherit = 'transport.management.line'
    _rec_name = "transport_management"

    #for couting total number of BX credit customer collection
    def _get_total_collection(self):
        self.bx_customer_collection_count = self.env['bx.credit.customer.collection'].search_count([('transport_management_ids','=',self.id)])
    
    #field as need to add it
    payment_method_id = fields.Many2one('cargo_payment_method',string='Payment Method',related='transport_management.payment_method',track_visibility=True, store=True)
    payment_method = fields.Selection(related='transport_management.payment_method.payment_type',string='Payment Method Type', track_visibility=True, store=True)
    transportation_no = fields.Char(related="transport_management.transportation_no", store=True)
    order_date = fields.Date(related="transport_management.order_date", store=True)
    customer_id = fields.Many2one('res.partner', related="transport_management.customer", store=True)
    add_to_cc = fields.Boolean(string="ADD TO CC", default=False)
    bx_customer_collection_count = fields.Integer(string="Total BX Customer Collection", compute="_get_total_collection")
    bx_credit_collection_id = fields.Many2one('bx.credit.customer.collection',string="Bx Credit Customer Collection")
    bx_credit_collection_ids = fields.Many2many('bx.credit.customer.collection',string="Bx Credit Customer Collections")
    bx_credit_sequnce = fields.Integer(string="Collection Report Seq")
    customer_ref = fields.Char(string='Customer Reference')
    route_id = fields.Many2one('bsg_route',string='Route',related='transport_management.route_id',store=True, track_visibility=True)
    transportation_driver = fields.Many2one('hr.employee', string='Transportation Driver',related='transport_management.transportation_driver', store=True, track_visibility=True)
    driver_number = fields.Char(string='Driver Number',related='transport_management.driver_number', store=True, track_visibility=True)
    loading_date = fields.Datetime(string='Loading Date', related='transport_management.loading_date',store=True, track_visibility=True)
    arrival_date = fields.Datetime(string='Arrival Date',related='transport_management.arrival_date', store=True, track_visibility=True)
    agreement_type = fields.Selection([('one_way','One way'),('round_trip','Round trip')],string='Agreement Type',related='transport_management.agreement_type',store=True,track_visibility=True)
    delivery_date = fields.Date(string='Delivery Date',related='transport_management.delivery_date', store=True, track_visibility=True)
    service_type = fields.Selection([('express','Express'),('line_haul','Line Haul'),('intra_city','Intra City'),('cargo','Cargo'),('others','Others')],string='Service Type',related='transport_management.service_type', store=True, track_visibility=True)
    delivery_way = fields.Selection([('dr2dr','Dr2Dr'),('albassami_branch','Albassami Branches')],string='Delivery Way', related='transport_management.delivery_way', store=True,track_visibility=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed Order'),
        ('issue_bill', 'Issue Bill'),
        ('vendor_trip', 'Vendor Trip Money'),
        ('fuel_voucher', 'Fuel Voucher'),
        ('receive_pod', 'Received POD'),
        ('done', 'Invoiced'),
        ('cancel', 'Cancel'),
    ], default='draft',related='transport_management.state',store=True, track_visibility=True)
    ##########NEW#############################################################################
    fleet_type_transport = fields.Many2one('bsg.vehicle.type.table', string="Fleet Type",related='transport_management.fleet_type_transport',store=True, track_visibility=True)
    display_expense_mthod_id = fields.Many2one(string='Fuel Expense Method',related='transport_management.display_expense_mthod_id',store=True, track_visibility=True)
    truck_load = fields.Selection([
        ('full','Full Load'),
        ('empty','Empty Load')
        ], string="Truck Load",related='transport_management.truck_load',store=True,
        track_visibility=True)
    display_expense_type = fields.Selection(string="Fuel Expense Type",related='transport_management.display_expense_type',store=True, track_visibility=True)
    total_fuel_amount = fields.Float(string="Total Fuel Expense",related='transport_management.total_fuel_amount',store=True, track_visibility=True)
    trip_distance = fields.Float(string="Trip Distance",related='transport_management.trip_distance',store=True, track_visibility=True)
    extra_distance = fields.Integer(string="Extra Distance",related='transport_management.extra_distance',store=True, track_visibility=True)
    reason = fields.Text(string="Reason",related='transport_management.reason',store=True, track_visibility=True)
    total_distance = fields.Float(string='Total Distance',related='transport_management.total_distance',store=True,readonly=True, track_visibility=True)
    extra_distance_amount = fields.Float(string="Extra Distance Amount" ,related='transport_management.extra_distance_amount',store=True, track_visibility=True)
    total_reward_amount = fields.Float(string="Total Reward amount Backend",related='transport_management.total_reward_amount',store=True, track_visibility=True)
    return_date = fields.Date(string='Return Date',related='transport_management.return_date',store=True, track_visibility=True)
    stuffing_date = fields.Date(string='Stuffing Date',related='transport_management.stuffing_date',store=True, track_visibility=True)
    arrival_time = fields.Float(string='Est Duration',related='transport_management.arrival_time',store=True, track_visibility=True)
    waybill_date = fields.Date(string='WayBill Date',related='transport_management.waybill_date',store=True, track_visibility=True)
    pod_date = fields.Date(string='POD Date',related='transport_management.pod_date',store=True, track_visibility=True)
    lead_days = fields.Integer(string='Lead Days',related='transport_management.lead_days',store=True, track_visibility=True)
    
    receiver_name = fields.Char(string='Receiver Name',related='transport_management.receiver_name',store=True, track_visibility=True)
    rec_company = fields.Char(string='Company Name',related='transport_management.rec_company',store=True, track_visibility=True)
    rec_customer_number = fields.Char(string='Customer Number',related='transport_management.rec_customer_number',store=True, track_visibility=True)
    rec_phone = fields.Char(string='Phone',related='transport_management.rec_phone',store=True, track_visibility=True)
    rec_mobile = fields.Char(string='Mobile',related='transport_management.rec_mobile',store=True, track_visibility=True)
    rec_street = fields.Char(string='Address',related='transport_management.rec_street',store=True, track_visibility=True)
    rec_street2 = fields.Char(string='Street2',related='transport_management.rec_street2',store=True, track_visibility=True)
    rec_city = fields.Char(string='City',related='transport_management.rec_city',store=True, track_visibility=True)
    rec_state_id = fields.Many2one('res.country.state',string='State',related='transport_management.rec_state_id',store=True, track_visibility=True)
    rec_zip = fields.Char(string='Zip',related='transport_management.rec_zip',store=True, track_visibility=True)
    rec_country_id = fields.Many2one('res.country',string="Country",related='transport_management.rec_country_id',store=True, track_visibility=True)
    receiver_type = fields.Selection(string="Receiver Type", track_visibility=True, selection=[
        ('1', 'Saudi'),
        ('2', 'Non-Saudi'),
        ('3', 'Corporate'),
    ],related='transport_management.receiver_type',store=True,)
    receiver_nationality = fields.Many2one(string="Receiver Nationality", comodel_name="res.country",related='transport_management.receiver_nationality',store=True, track_visibility=True)
    receiver_id_type = fields.Selection(string="Receiver ID Type", track_visibility=True, selection=[
        ('saudi_id_card', 'Saudi ID Card'),
        ('iqama', 'Iqama'),
        ('gcc_national', 'GCC National'),
        ('passport', 'Passport'),
        ('other', 'Other'),
    ],related='transport_management.receiver_id_type',store=True,)
    receiver_id_card_no = fields.Char(string="Receiver ID Card No",related='transport_management.receiver_id_card_no',store=True,track_visibility=True)
    receiver_visa_no = fields.Char(string="Receiver Visa No",related='transport_management.receiver_visa_no',store=True, track_visibility=True)
    check_edit_price = fields.Boolean(string='Check Edit Price', compute="_get_check_edit_price")


    def _get_check_edit_price(self):
        if self.env.user.has_group('bsg_tranport_bx_credit_customer_collection.group_allow_to_edit_bx_price') and (
                self.bx_customer_collection_count != 0 or self.transport_management.invoice_id):
            self.check_edit_price = False
        else:
            self.check_edit_price = True
    
    # # override to create method
    # @api.model
    # def create(self, vals):
    #     res = super(TransportManagementLine, self).create(vals)
    #     res.transport_management._reset_sequence()
    #     return res

    #override to solved key error issue 
    
    def write(self, vals):
        # old_values = {
        # 'product_id':self.product_id,
        # 'add_to_cc' : self.add_to_cc,
        # 'bx_credit_sequnce' : self.bx_credit_sequnce,
        # 'description':self.description,
        # 'weight':self.weight,
        # 'length':self.length,
        # 'width': self.width,
        # 'height': self.height,
        # 'total_pieces': self.total_pieces,
        # 'form' : self.form,
        # 'to' : self.to,
        # 'fleet_type':self.fleet_type,
        # 'product_uom_qty':self.product_uom_qty,
        # 'price' : self.price,
        # 'seal_number':self.seal_number,
        # 'container_number':self.container_number,
        # 'tax_ids':self.tax_ids,
        # 'total_before_taxes': self.total_before_taxes,
        # 'tax_amount':self.tax_amount,
        # 'total_amount':self.total_amount,
        # 'fleet_vehicle_id':self.fleet_vehicle_id,
        # 'car_size_id':self.car_size_id,
        # 'receiver_name': self.receiver_name,
        # 'rec_company': self.rec_company,
        # 'rec_customer_number': self.rec_customer_number,
        # 'rec_phone':  self.rec_phone,
        # 'rec_mobile': self.rec_mobile,
        # 'rec_street': self.rec_street,
        # 'rec_street2':  self.rec_street2,
        # 'rec_city':  self.rec_city,
        # 'rec_state_id':  self.rec_state_id,
        # 'rec_zip': self.rec_zip,
        # 'rec_country_id': self.rec_country_id,
        # 'receiver_type': self.receiver_type,
        # 'receiver_nationality': self.receiver_nationality,
        # 'receiver_id_type': self.receiver_id_type,
        # 'receiver_id_card_no': self.receiver_id_card_no,
        # 'receiver_visa_no': self.receiver_visa_no,
        # 'partner_types': self.partner_types,
        # 'is_overnight': self.is_overnight,
        # 'customer_ref': self.customer_ref,
        # 'transport_bayan_goods_type_id': self.transport_bayan_goods_type_id.id,
        # 'transport_bayan_way_bill_line_id': self.transport_bayan_way_bill_line_id.id,
        #
        #
        # }
        res = super(TransportManagementLine,self).write(vals)
        if self.check_edit_price == False:
            group_e = self.env.ref('bsg_tranport_bx_credit_customer_collection.group_allow_to_edit_bx_price', False)
            group_e.write({'users': [(3, self.env.user.id)]})
        # if not self._context.get('without_track',False):
        #     # tracked_fields = self.env['transport.management.line'].fields_get(vals)
        #     tracked_fields = self.env['transport.management.line']._track_get_fields()
        #     changes, tracking_value_ids = self._message_track(tracked_fields, old_values)
        #     if changes:
        #         self.transport_management.message_post(tracking_value_ids=tracking_value_ids)
        return res

    # View Customer collection
    
    def action_view_bx_customer_collection(self, context):
        bx_credit_collection_id = self.env['bx.credit.customer.collection'].search([('transport_management_ids','=',self.id)])
        action = self.env.ref('bsg_tranport_bx_credit_customer_collection.action_bx_credit_customer_collection').read()[0]
        if len(bx_credit_collection_id) > 1:
            action['domain'] = [('id', 'in', bx_credit_collection_id.ids)]
        elif len(bx_credit_collection_id) == 1:
            action['views'] = [(self.env.ref('bsg_tranport_bx_credit_customer_collection.view_bx_credit_customer_form').id, 'form')]
            action['res_id'] = bx_credit_collection_id.ids[0]
        else:
            action = {'type' : 'ir.actions.act_window_close'}
        return action
