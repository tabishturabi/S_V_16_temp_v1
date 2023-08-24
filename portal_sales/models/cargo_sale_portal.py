# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta, date
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class shipTypeWebsiteDescription(models.Model):
    _name = 'ship.type.website.description'

    name = fields.Char(translated=True,required=True)
    shipment_id = fields.Many2one('bsg.car.shipment.type')

class BsgCarShipmentType(models.Model):
    _inherit = 'bsg.car.shipment.type'

    available_in_upgrade = fields.Boolean("Available In Upgrade")
    website_description_ids = fields.One2many('ship.type.website.description','shipment_id','Features')

class ProductPricelist(models.Model):
	_inherit = 'product.pricelist'

	default_in_portal = fields.Boolean(default=False)

class BsgVehicleCargoSale(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale'

    shipment_date = fields.Datetime(default=fields.Datetime.now, copy=False)
    is_from_portal = fields.Boolean()
    cancel_reason = fields.Text()
    to_confirm = fields.Boolean(compute='_compute_so_to_confirm',store=True)
    online_pay_error = fields.Char("Pay Issue#")
    payment_transaction_ids = fields.Many2many('payment.transaction', 'cargo_sale_transaction_rel', 'cargo_sale_id', 'transaction_id',
                                   string='Online Transactions',domain=[('is_tamara','=', False)], copy=False, readonly=True)
    lead_id = fields.Many2one('crm.lead')

    # for calculating value
    def geting_portal_order_due_amount(self):
        due_amount = 0
        for line in self.order_line_ids:
            due_amount += line.sudo().getting_portal_due_amount()
        return due_amount

    
    def confirm_btn(self):
        super(BsgVehicleCargoSale,self).confirm_btn()
        if self.is_from_portal:
            self.state = 'registered'
        return True


    @api.depends('transaction_ids','state','order_line_ids.transaction_ids')
    def _compute_so_to_confirm(self):
        for rec in self:
            if (rec.is_from_portal or rec.is_from_app) and (rec.state == 'draft'):
                if rec.transaction_ids.filtered(lambda l: l.state == 'done') or any(rec.order_line_ids.mapped('transaction_ids').filtered(lambda l: l.state == 'done')):
                    rec.to_confirm = True

    @api.model
    def _search_to_refund_order(self, operator, operand):
        #Users search uning mobile with/out 0 prefix
        orders = []
        ges_orders = self.env['bsg_vehicle_cargo_sale'].sudo().search([
            ('state', '=', 'cancel'),'|',('is_from_portal', '=', True),('is_from_app', '=', True),
        ])
        if ges_orders:
            for order in ges_orders:
                if order.invoice_ids.filtered(lambda s:s.state == 'paid' and s.payment_ids):
                    orders.append(order.id)
        return [('id', 'in', orders)]

    @api.model
    def portal_start_return_process(self,bsg_cargo_sale_id,new_ret_loc_to):
        values = {'return_id' :False,'rtu_masg':False,'return_url':False}
        bsg_cargo_sale_id = self.sudo().browse(bsg_cargo_sale_id)
        try:
            if bsg_cargo_sale_id.order_line_ids:
                order_lines = bsg_cargo_sale_id.order_line_ids
                if any(st != 'done' for st in order_lines.mapped('state')):
                    values['rtu_masg'] = _("The outbound sale line must be processed first!")
                    return values
                if all(order_lines.mapped('return_intiated')):
                    values['rtu_masg'] = _("All return trips for this order already intiated")
                    return values
                _logger.info("start_return_process: starting copy")
                so_vals = {'order_line_ids': False, 'order_date': datetime.now(),
                        'shipment_type': 'oneway',
                        'recieved_from_customer_date':datetime.now(),'shipment_date':datetime.now(),
                        'loc_from': bsg_cargo_sale_id.loc_to.id,'loc_to': bsg_cargo_sale_id.loc_from.id,
                        'return_loc_from': bsg_cargo_sale_id.loc_to.id,'payment_method': bsg_cargo_sale_id.payment_method.id}
                new_so = bsg_cargo_sale_id.sudo().with_context(
                    {'is_return_process': True}).copy(default=so_vals)
                _logger.info("start_return_process: end copy")
                loc_to = False
                if new_ret_loc_to:
                    loc_to = new_ret_loc_to
                else:
                    loc_to = bsg_cargo_sale_id.loc_from.id
                new_so.sudo().write({
                    'loc_to': loc_to,
                    'loc_from' : bsg_cargo_sale_id.loc_to.id,
                })
                # new_so.loc_to = self._context.get('new_ret_loc_to', self.loc_from.id)
                bsg_cargo_sale_id.sudo().write({'return_so_id' : new_so.id})
                new_so.sudo().write({'is_return_so': True})
                new_so.sudo()._onchange_loc_from_to()
                # new_so.name = 'R' + new_so.name
                _logger.info("start_return_process: new order %s" % new_so.id)
                for line in order_lines:
                    _logger.info("start_return_process: in order_line_ids loop")
                    if line.state == 'done':
                        _logger.info("start_return_process:line is draft")
                        return_line = line.sudo().duplicate_record(new_so.id)
                        _logger.info(
                            "start_return_process: duplicated line %s" % return_line.id)
                        # for updating data when return the procee

                        return_line.sudo().write({'bsg_cargo_sale_id' : new_so.id})
                        # return_line.bsg_cargo_return_sale_id = new_so.id
                        bsg_cargo_return_sale_id = new_so
                        vals = {'order_date': bsg_cargo_return_sale_id.order_date,
                                'account_id': bsg_cargo_return_sale_id.account_id.id,
                                'receiver_name': bsg_cargo_return_sale_id.receiver_name,
                                'receiver_mob_no': bsg_cargo_return_sale_id.receiver_mob_no,
                                #  'payment_method' : line.payment_method.id,
                                'deliver_date': False,
                                'delivery_date': False,
                                'customer_id': bsg_cargo_return_sale_id.customer.id,
                                'receiver_type': bsg_cargo_return_sale_id.receiver_type,
                                'receiver_nationality': bsg_cargo_return_sale_id.receiver_nationality.id,
                                'receiver_id_type': bsg_cargo_return_sale_id.receiver_id_type,
                                'receiver_id_card_no': bsg_cargo_return_sale_id.receiver_id_card_no,
                                'receiver_visa_no': bsg_cargo_return_sale_id.receiver_visa_no,
                                'receiver_mob_no': bsg_cargo_return_sale_id.receiver_mob_no,
                                'no_of_copy': bsg_cargo_return_sale_id.no_of_copy,
                                'cargo_sale_state': 'draft',
                                'unit_charge': 0,
                                'discount': 0,
                                'tax_ids': False,
                                'price_line_id': False,
                                'return_loc_from': return_line.loc_from.id,
                                'return_loc_to': return_line.loc_to.id,
                                'so_line_revenue_technical': line.so_line_revenue_technical,
                                'shipping_source_id': bsg_cargo_sale_id.id,
                                'recieved_from_customer_date':datetime.now(),
                                }
                        return_line.sudo().write(vals)
                        if line.shipment_type.is_normal:
                            exp_delivery_date_status = return_line.set_exp_delivery_date_json(
                                                        loc_from=new_so.loc_from.id,
                                                        loc_to=new_so.loc_to.id,
                                                        shipment_type=line.shipment_type.id,
                                                        car_size=line.car_size.id,
                                                        shipment_date=new_so.shipment_date)
                            if not exp_delivery_date_status.get('error'):
                                return_line.sudo().write({
                                    'expected_delivery': exp_delivery_date_status.get('expected_delivery'),
                                    'est_no_delivery_days': exp_delivery_date_status.get('est_no_delivery_days'),
                                    'est_max_no_delivery_days': exp_delivery_date_status.get('est_max_no_delivery_days'),
                                            })
                            else:
                                raise UserError(exp_delivery_date_status.get('error'))

                        else:
                            exp_delivery_date_status = return_line.set_exp_delivery_date_json(
                                                        loc_from=new_so.loc_from.id,
                                                        loc_to=new_so.loc_to.id,
                                                        shipment_type=line.shipment_type.id,
                                                        car_size=line.shipment_type.car_size.id,
                                                        shipment_date=new_so.shipment_date)
                            if not exp_delivery_date_status.get('error'):
                                return_line.sudo().write({
                                    'expected_delivery': exp_delivery_date_status.get('expected_delivery'),
                                    'est_no_delivery_days': exp_delivery_date_status.get('est_no_delivery_days'),
                                    'est_max_no_delivery_days': exp_delivery_date_status.get('est_max_no_delivery_days'),
                                            })
                            else:
                                raise UserError(exp_delivery_date_status.get('error'))
                        line.sudo().write({'return_intiated': True})
                        line.sudo().write({'return_source_id': new_so.id})
                    else:
                        values['rtu_masg'] = _("The outbound sale line must be processed first!")
                        return values
                new_so.sudo().write({
                    'total_amount': 0,
                    'state': 'draft',
                })
                #self.create_trip_picking(new_so.order_line_ids, new_so.loc_from, new_so.loc_to, False)
                all_return_intiated = all(
                    bsg_cargo_sale_id.order_line_ids.mapped('return_intiated'))
                to_write_vals = {
                    'return_intiated': all_return_intiated
                }
                if all_return_intiated:
                    to_write_vals.update({
                        'state': 'done'
                    })
                if new_ret_loc_to:
                    to_write_vals.update({'return_loc_to' : new_ret_loc_to})
                bsg_cargo_sale_id.sudo().write(to_write_vals)
                values['return_id'] = new_so.name
                values['return_url'] = new_so.get_portal_url()
                return values

            else:
                values['rtu_masg'] = _("No Car To Return!")
                return values

        except:
            values['rtu_masg'] = _("Can't Complete This Process Now ,Try Later!")
            return values


    # Get Price For Portal>>>>>>>>>>>>>>>>>>>>>>>>>>
    @api.model
    def get_all_shipment_price_for_portal(self,company_id,partner_type,loc_from,loc_to, car_model, car_size):
        '''
                @param:shipment_type,car_model,car_size,service_type,bsg_cargo_sale_id,car_classfication
                @return: Price For The Trip
        '''

        PriceLine = False
        with_tax = True
        PinConfig = False

        values_list = []
        shipment_types = self.env['bsg.car.shipment.type'].sudo().search(
            [('company_id', '=', company_id),('is_public','=',True)])
        loc_from_rec = self.env['bsg_route_waypoints'].sudo().browse(int(loc_from))
        loc_to_rec = self.env['bsg_route_waypoints'].sudo().browse(int(loc_to))
        car_size = self.env['bsg_car_size'].sudo().browse(car_size).id
        car_model = self.env['bsg_car_model'].sudo().browse(car_model).id
        portal_car_size = car_size
        #SET Discount
        default_customer_price_list = False
        if not loc_from_rec.is_international and not loc_to_rec.is_international:
            default_customer_price_list = self.env['product.pricelist'].sudo().search(
            [('default_in_portal', '=', True),'|', ('agreement_type', '=', False), ('agreement_type', '=', 'oneway')], limit=1)

        if loc_from_rec.is_international or loc_to_rec.is_international:
            with_tax = False
            PinConfig = self.company_id.browse(company_id)

        if shipment_types:

            for ship_type in shipment_types:
                values = {}
                if not ship_type.is_normal:
                    car_size = ship_type.car_size.id
                PriceConfig = self.env['bsg_price_config'].sudo().search([
                    ('waypoint_from', '=', loc_from_rec.id),
                    ('company_id', '=', company_id),
                    ('waypoint_to', '=', loc_to_rec.id),
                    ('customer_type', '=', partner_type)
                ], limit=1)
                if PriceConfig:
                    PriceLine = self.env['bsg_price_line'].sudo().search([
                        ('price_config_id', '=', PriceConfig.id),
                        ('company_id', '=', company_id),
                        ('car_size', '=', car_size),
                    ], limit=1)
                    if PriceLine:
                        est_delivery_day_id = self.env['bsg.estimated.delivery.days'].search(
                            [('loc_from_id', '=', loc_from_rec.zone_id.id), ('loc_to_id', '=', loc_to_rec.zone_id.id)],
                            limit=1)
                        values[ship_type] = {
                            'service_type' : False,
                            'unit_charge': 0.00,
                            'tax_amount': 0.00,
                            'total_without_tax': 0.00,
                            'charges': 0.00,
                            'discount_perc':0.00,
                            'discount_amount':0.00,

                            'round_unit_charge': 0.00,
                            'round_tax_amount': 0.00,
                            'round_total_without_tax': 0.00,
                            'round_charges': 0.00,
                            'round_discount_perc':0.00,
                            'round_discount_amount':0.00,
                            'expected_delivery_days': 0.00,
                            'est_max_no_delivery_days':0.00,
                            'error': '',
                        }
                        _logger.warning("Shipment Prices Logs $$$$$$$$ above......")
                        if est_delivery_day_id:
                            _logger.warning("Shipment Prices Logs $$$$$$$$ above......est_delivery_day_id")
                            if est_delivery_day_id.est_depend_car_size:
                                _logger.warning("Shipment Prices Logs $$$$$$$$ above......est_delivery_day_id.est_depend_car_size")
                                if est_delivery_day_id.car_size_line:
                                    _logger.warning("Shipment Prices Logs $$$$$$$$ above......est_delivery_day_id.car_size_line")
                                    for est_deliv_line_id in est_delivery_day_id.car_size_line:
                                        if ship_type.id in est_deliv_line_id.shipemnt_type.ids and portal_car_size in est_deliv_line_id.car_size_ids.ids:
                                            values[ship_type]['expected_delivery_days'] = est_deliv_line_id.est_min_days
                                            values[ship_type]['est_max_no_delivery_days'] = est_deliv_line_id.est_max_days + est_deliv_line_id.increment
                            else:
                                _logger.error(
                                    "Shipment Prices Logs $$$$$$$$ above......est_delivery_day_id.est_depend_car_size else part")
                                values[ship_type]['expected_delivery_days'] = est_delivery_day_id.est_no_delivery_days
                                values[ship_type]['est_max_no_delivery_days'] = est_delivery_day_id.est_max_no_delivery_days

                        if PriceLine.service_type:
                            values[ship_type]['service_type'] = PriceLine.service_type
                            if default_customer_price_list:
                                if default_customer_price_list.item_ids:
                                    for data in default_customer_price_list.item_ids:
                                        if data.product_tmpl_id.id == PriceLine.service_type.id:
                                            values[ship_type]['discount_perc'] = data.percent_price

                        #Get OneWay
                        values[ship_type]['unit_charge'] = PriceLine.price if PriceLine else 0.0
                        values[ship_type]['discount_amount'] = values[ship_type]['unit_charge'] * (values[ship_type]['discount_perc'] / 100.0)
                        values[ship_type]['charges'] = values[ship_type]['unit_charge'] - values[ship_type]['discount_amount']
                        values[ship_type]['total_without_tax'] = values[ship_type]['charges']
                        #Get RoundTrip
                        values[ship_type]['round_unit_charge'] = PriceLine.price*2 if PriceLine else 0.0
                        values[ship_type]['round_discount_perc'] = 10
                        values[ship_type]['round_discount_amount'] = values[ship_type]['round_unit_charge'] * (values[ship_type]['round_discount_perc'] / 100.0)
                        values[ship_type]['round_charges'] = values[ship_type]['round_unit_charge'] - values[ship_type]['round_discount_amount']
                        values[ship_type]['round_total_without_tax'] = values[ship_type]['round_charges']
                        if with_tax:
                            tax_ids = PinConfig and PinConfig.sudo().tax_ids or PriceLine.service_type.taxes_id
                            if tax_ids:
                                currency = None
                                quantity = 1
                                product = PriceLine.service_type
                                one_way_taxes = tax_ids.compute_all((values[ship_type]['charges']), currency, quantity,
                                                product=product)
                                round_taxes = tax_ids.compute_all((values[ship_type]['round_charges']), currency, quantity,
                                                product=product)
                                values[ship_type]['charges'] = one_way_taxes['total_included']
                                values[ship_type]['total_without_tax'] = one_way_taxes['total_excluded']
                                values[ship_type]['tax_amount'] = one_way_taxes['total_included'] - one_way_taxes['total_excluded']


                                values[ship_type]['round_charges'] = round_taxes['total_included']
                                values[ship_type]['round_tax_amount'] = round_taxes['total_included'] - round_taxes['total_excluded']
                                values[ship_type]['round_total_without_tax'] = round_taxes['total_excluded']

                        values[ship_type]['unit_charge'] = round(values[ship_type]['unit_charge'],2)
                        values[ship_type]['discount_amount'] = round(values[ship_type]['discount_amount'],2)
                        values[ship_type]['tax_amount']  = round(values[ship_type]['tax_amount'],2)
                        values[ship_type]['total_without_tax'] = round(values[ship_type]['total_without_tax'],2)
                        values[ship_type]['charges'] = round(values[ship_type]['charges'],2)

                        values[ship_type]['round_unit_charge'] = round(values[ship_type]['round_unit_charge'],2)
                        values[ship_type]['round_discount_amount'] = round(values[ship_type]['round_discount_amount'],2)
                        values[ship_type]['round_tax_amount']  = round(values[ship_type]['round_tax_amount'],2)
                        values[ship_type]['round_total_without_tax'] = round(values[ship_type]['round_total_without_tax'],2)
                        values[ship_type]['round_charges'] = round(values[ship_type]['round_charges'],2)

                        values_list.append(values)
        return values_list



class bsg_vehicle_cargo_sale_line(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    shipment_date = fields.Datetime(related='bsg_cargo_sale_id.shipment_date',store=True)
    is_from_portal = fields.Boolean(related='bsg_cargo_sale_id.is_from_portal',store=True)


    # Get Price For Portal>>>>>>>>>>>>>>>>>>>>>>>>>>
    @api.model
    def get_price_for_portal(self, shipment_type, car_model, car_size, service_type, car_classfication, bsg_cargo_sale_id,discount_perc=0.0):
        '''
                @param:shipment_type,car_model,car_size,service_type,bsg_cargo_sale_id,car_classfication
                @return: Price For The Trip
        '''
        if not discount_perc:
            discount_perc = 0.0

        bsg_cargo_sale_id = self.bsg_cargo_sale_id.sudo().browse(bsg_cargo_sale_id)
        shipment_type = self.shipment_type.sudo().browse(shipment_type)
        car_model = self.car_model.sudo().browse(car_model)
        car_size = self.car_size.sudo().browse(car_size)
        service_type = self.service_type.sudo().browse(service_type)
        car_classfication = self.car_classfication.browse(car_classfication)
        PriceLine = False
        ContractLine = False
        values = {
            'discount': discount_perc,
            'service_type' : service_type.id,
            'unit_charge': 0.00,
            'tax_amount': 0.00,
            'amount_with_satah': 0.00,
            'total_without_tax': 0.00,
            'charges': 0.00,
            'fixed_discount' :0.00,
            'error': '',
        }

        if bsg_cargo_sale_id.partner_types.is_construction:
            values['discount'] += bsg_cargo_sale_id.partner_types.discount

        if shipment_type and car_size and car_model and bsg_cargo_sale_id:
            if not shipment_type.is_normal:
                car_size = shipment_type.car_size

            if bsg_cargo_sale_id.customer_contract:
                ContractLine = self.env['bsg_customer_contract_line'].sudo().search([
                    ('cust_contract_id', '=', bsg_cargo_sale_id.customer_contract.id),
                    ('service_type', '=', service_type.id),
                    ('company_id', '=', bsg_cargo_sale_id.company_id.id),
                    ('loc_from', '=', bsg_cargo_sale_id.loc_from.id),
                    ('loc_to', '=', bsg_cargo_sale_id.loc_to.id),
                    ('car_size', '=', car_size.id),
                ], limit=1)
                if ContractLine:
                    values['unit_charge'] = ContractLine.price if ContractLine else 0.0
                    # Total
                    values['charges'] = values['unit_charge'] * \
                        (1.0 - values['discount'] / 100.0)
                else:
                    values['error'] = _(
                        'No pricing found for this shipment type.')
            else:
                PriceConfig = self.env['bsg_price_config'].sudo().search([
                    ('waypoint_from', '=', bsg_cargo_sale_id.loc_from.id),
                    ('company_id', '=', bsg_cargo_sale_id.company_id.id),
                    ('waypoint_to', '=', bsg_cargo_sale_id.loc_to.id),
                    # ('customer_type', '=', bsg_cargo_sale_id.customer_type),
                ], limit=1)
                if PriceConfig:
                    PriceLine = self.env['bsg_price_line'].sudo().search([
                        # ('price_config_id', '=', PriceConfig.id),
                        # ('service_type','=',self.service_type.id),
                        ('company_id', '=', bsg_cargo_sale_id.company_id.id),
                        # ('car_classfication', '=', car_classfication.id),
                        # ('car_size', '=', car_size.id),
                    ], limit=1)
                    if PriceLine:
                        if PriceLine.service_type:
                            service_type = PriceLine.service_type
                        if bsg_cargo_sale_id.shipment_type == 'return':
                            values['unit_charge'] = PriceLine.price*2 if PriceLine else 0.0
                            if values['discount'] < 10:
                                values['discount'] = 10
                        else:
                            values['unit_charge'] = PriceLine.price if PriceLine else 0.0
                        # Check if amount less than min amount (not allowed) then take min
                        if values['charges'] < PriceLine.min_price:
                            if values['discount'] <= 80:
                                values['charges'] = PriceLine.min_price * \
                                    (1.0 - values['discount'] / 100.0)
                            else:
                                values['charges'] = PriceLine.min_price
                        values['charges'] = values['unit_charge'] * \
                            (1.0 - values['discount'] / 100.0)

                    else:
                        values['error'] = _(
                            'No pricing found for this shipment type.')
                else:
                    values['error'] = _(
                            'No pricing found for this shipment type.')

            if PriceLine or ContractLine:
                PinConfig = bsg_cargo_sale_id.company_id
                if bsg_cargo_sale_id.loc_from.is_international or bsg_cargo_sale_id.loc_to.is_international:
                    tax_ids = False
                else:
                    tax_ids = PinConfig.sudo().tax_ids or service_type.taxes_id
                if tax_ids:
                    currency = bsg_cargo_sale_id.currency_id or None
                    quantity = 1
                    product = service_type.product_variant_id
                    taxes = tax_ids.compute_all((values['charges'] + values['amount_with_satah']), currency, quantity,
                                                product=product, partner=bsg_cargo_sale_id.customer)
                    values['charges'] = taxes['total_included']
                    if bsg_cargo_sale_id.loc_from.is_international or bsg_cargo_sale_id.loc_to.is_international:
                        values['tax_amount'] = 0
                    else:
                        values['tax_amount'] = taxes['total_included'] - \
                            taxes['total_excluded']
                values['total_without_tax'] = values['charges'] - \
                    values['tax_amount']

            values['fixed_discount'] = values['unit_charge'] * (values['discount'] / 100.0)
            shipment_extra_charges = 0.0
            extra_amount = 0.0
            if shipment_type.is_express_shipment and shipment_type.shipment_extra_charges > 0:
                shipment_extra_charges = shipment_type.shipment_extra_charges
            if shipment_type.is_express_shipment and shipment_type.calculation_type == 'percentage' and shipment_type.is_normal:
                unit_charge = values['charges']
                val_express_shipment = shipment_type.percentage_express_shipment / 100 * unit_charge
                extra_amount = val_express_shipment + unit_charge + shipment_extra_charges
            elif shipment_type.is_express_shipment and shipment_type.calculation_type == 'fixed_amount' and shipment_type.is_normal:
                fixed_amount = shipment_type.percentage_express_shipment + values['charges']
                extra_amount = fixed_amount + shipment_extra_charges
            values['unit_charge'] = values['unit_charge'] + extra_amount
            values['unit_charge'] = round(values['unit_charge'],2)
            values['tax_amount']  = round(values['tax_amount'],2)
            values['amount_with_satah'] = round(values['amount_with_satah'],2)
            values['total_without_tax'] = round(values['total_without_tax'],2)
            values['charges'] = round(values['charges'],2)
            values['fixed_discount'] = round(values['fixed_discount'],2)
            values['service_type'] = service_type.id
            return values


    @api.model
    def check_chassis_palto_constarin_portal(self, bsg_cargo_sale_id, chassis_no, plate_no):
        values = {'count': 0.0}
        if bsg_cargo_sale_id and chassis_no and plate_no:
            values['count'] = self.sudo().search_count(
                [('bsg_cargo_sale_id', '=', bsg_cargo_sale_id), ('chassis_no', '=', chassis_no),
                 ('plate_no', '=', plate_no)])
            return values

    @api.model
    def check_saudi_palto_constarin_portal(self, bsg_cargo_sale_id, plate_no, palte_one, palte_second, palte_third):
        values = {'count': 0.0}
        if bsg_cargo_sale_id and plate_no and palte_one and palte_second and palte_third:
            values['count'] = self.sudo().search_count(
                [('bsg_cargo_sale_id', '=', bsg_cargo_sale_id), ('plate_no', '=', plate_no),
                 ('palte_one', '=', palte_one), ('palte_second', '=', palte_second), ('palte_third', '=', palte_third)])
            return values

    @api.model
    def check_non_saudi_palto_constarin_portal(self, bsg_cargo_sale_id, non_saudi_plate_no,plate_no):
        values = {'count': 0.0}
        if bsg_cargo_sale_id and non_saudi_plate_no:
            values['count'] = self.sudo().search_count(
                [('bsg_cargo_sale_id', '=', bsg_cargo_sale_id), ('non_saudi_plate_no', '=', non_saudi_plate_no),
                 ('plate_no', '=', plate_no)])
            return values
    @api.model
    def get_portal_expected_delivery_date(self, loc_from_id, loc_to_id,shipment_type, car_size,shipment_date):
        if shipment_date:
            date_from = fields.Datetime.from_string(shipment_date)
        else:
            date_from = fields.Datetime.now()
        loc_from = self.env['bsg_route_waypoints'].browse(int(loc_from_id))
        loc_to = self.env['bsg_route_waypoints'].browse(int(loc_to_id))

        shipment_types = self.env['bsg.car.shipment.type'].sudo().search([('id','=',int(shipment_type))])
        #if shipment_types.is_normal:
        #    shipment_type = int(car_size)
        #else:
        shipment_type = shipment_types.car_size and shipment_types.car_size.id or False




        shipment_date = datetime.strptime(datetime.strftime(
            date_from, '%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
        record = self.env['bsg.estimated.delivery.days'].sudo().search(
            [('loc_from_id', '=', loc_from.id),
             ('loc_to_id', '=', loc_to.id),
             ('shipemnt_type.car_size', '=', shipment_type),
             ], limit=1)
        max_so_per_branch = self.env['max_daily_so_per_branch'].search(
            [('name', '=', loc_from.loc_branch_id.id), ('branch_to_ids', 'in', loc_to.loc_branch_id.id),
             ('shipment_type_ids', 'in', shipment_type)], limit=1)
        cargo_sale_count = False
        max_per_day_count = False
        if max_so_per_branch:
            max_per_day_count = max_so_per_branch.max_so_per_day
            cargo_sale_count = self.search_count([('loc_from.loc_branch_id', '=', max_so_per_branch.name.id),
                                                  ('loc_to.loc_branch_id', 'in',
                                                   max_so_per_branch.branch_to_ids.ids),
                                                  ('shipment_type', 'in',
                                                   max_so_per_branch.shipment_type_ids.ids),
                                                  ('order_date_date', '=', date.today())])
        if record:
            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                days = record.est_max_no_delivery_days  # + max_so_per_branch.number_of_day
                shipment_date = str(
                    shipment_date + timedelta(days=max_so_per_branch.number_of_day))
                expected_delivery = str(
                    shipment_date + timedelta(days=days, hours=record.est_no_hours))
                return {'shipment_date': str(shipment_date), 'expected_delivery_date': expected_delivery}
            else:
                expected_delivery = str(
                    shipment_date + timedelta(days=record.est_no_delivery_days, hours=record.est_no_hours))
                return {'shipment_date': str(shipment_date), 'expected_delivery_date': expected_delivery,
                        'est_no_delivery_days': record.est_no_delivery_days,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days,
                        'est_max_no_hours': record.est_max_no_hours
                        }
        elif not record:
            record = self.env['bsg.estimated.delivery.days'].sudo().search(
                [('loc_from_id', '=', loc_from.id),
                 ('loc_to_id', '=', loc_to.id),
                 ('shipemnt_type.car_size', '=', False),
                 ], limit=1)
            if max_per_day_count and cargo_sale_count and cargo_sale_count >= max_per_day_count:
                days = record.est_max_no_delivery_days  # + max_so_per_branch.number_of_day
                shipment_date = str(
                    shipment_date + timedelta(days=max_so_per_branch.number_of_day))
                expected_delivery = str(
                    shipment_date + timedelta(days=days, hours=record.est_no_hours))
                return {'shipment_date': shipment_date, 'expected_delivery_date': expected_delivery,
                'est_no_delivery_days': record.est_no_delivery_days,
                'est_no_hours': record.est_no_hours,
                'est_max_no_delivery_days': record.est_max_no_delivery_days,
                'est_max_no_hours': record.est_max_no_hours
                }
            else:
                expected_delivery = str(
                    shipment_date + timedelta(days=record.est_max_no_delivery_days, hours=record.est_no_hours))
                return {'shipment_date': str(shipment_date), 'expected_delivery_date': expected_delivery,
                        'est_no_delivery_days': record.est_no_delivery_days,
                        'est_no_hours': record.est_no_hours,
                        'est_max_no_delivery_days': record.est_max_no_delivery_days,
                        'est_max_no_hours': record.est_max_no_hours}

        else:
            return {'shipment_date': False, 'expected_delivery_date': False,
                        'est_no_delivery_days': 0,
                        'est_no_hours': 0,
                        'est_max_no_delivery_days': 0,
                        'est_max_no_hours': 0}



    def get_portal_url(self):
        portal_link = "%s/track-shipment?so_id=%s&rec_mo=%s" % (self.env['ir.config_parameter'].sudo().get_param('web.base.url'), self.sale_line_rec_name,self.receiver_mob_no)
        return portal_link


    # for calculating value
    # Customer In All Casses Pay In SAR =>
    # So Convert Amount's To Company Currencies
    def getting_portal_due_amount(self):
        due_amount = 0
        if self.state not in ['cancel','cancel_request']:
            if self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
                if self.invoice_line_ids.filtered(lambda l: l.currency_id.id == l.company_id.currency_id.id):
                    due_amount += sum(
                        self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_demurrage_line and s.move_id.state not in ['paid','cancel']).mapped(
                            'price_total')) - sum(
                        self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_demurrage_line and s.move_id.state not in ['paid','cancel']).mapped(
                            'paid_amount'))
                elif self.invoice_line_ids.filtered(lambda l: l.currency_id.id != l.company_id.currency_id.id):
                    forign_amount = 0
                    for inv_line in self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_demurrage_line and s.move_id.state not in ['paid','cancel']):
                        forign_amount = inv_line.price_total - inv_line.paid_amount

                        due_amount += inv_line.company_id.currency_id._convert(
                        forign_amount, inv_line.currency_id, inv_line.company_id,fields.Date.today())
                else:
                    if self.bsg_cargo_sale_id.currency_id.id == self.bsg_cargo_sale_id.company_id.currency_id.id:
                        due_amount += self.charges
                    elif self.bsg_cargo_sale_id.currency_id.id != self.bsg_cargo_sale_id.company_id.currency_id.id:
                        due_amount += self.original_charges
            elif self.bsg_cargo_sale_id.payment_method.payment_type in ['credit'] and not self.add_to_cc:
                if self.invoice_line_ids.filtered(lambda l: l.currency_id.id == l.company_id.currency_id.id):
                    due_amount += sum(
                        self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_demurrage_line and s.move_id.state not in ['paid','cancel']).mapped(
                            'price_total')) - sum(
                        self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_demurrage_line and s.move_id.state not in ['paid','cancel']).mapped(
                            'paid_amount'))
                elif self.invoice_line_ids.filtered(lambda l: l.currency_id.id != l.company_id.currency_id.id):
                    forign_amount = 0
                    for inv_line in self.invoice_line_ids.filtered(lambda s: not s.is_refund and not s.is_demurrage_line and s.move_id.state not in ['paid','cancel']):
                        forign_amount = inv_line.price_total - inv_line.paid_amount

                        due_amount += inv_line.company_id.currency_id._convert(
                        forign_amount, inv_line.currency_id, inv_line.company_id,fields.Date.today())
                else:
                    if self.bsg_cargo_sale_id.currency_id.id == self.bsg_cargo_sale_id.company_id.currency_id.id:
                        due_amount += self.charges
                    elif self.bsg_cargo_sale_id.currency_id.id != self.bsg_cargo_sale_id.company_id.currency_id.id:
                        due_amount += self.original_charges
            if self.bsg_cargo_return_sale_id and self.bsg_cargo_return_sale_id.payment_method.payment_type in ['cash',
                                                                                                            'pod']:
                for data in self.bsg_cargo_return_sale_id.invoice_ids:
                    if data.payment_sate != 'reversed':
                        if data.currency_id.id == data.company_id.currency_id.id:
                            due_amount += data.amount_residual
                        elif data.currency_id.id != data.company_id.currency_id.id:
                            due_amount += data.company_id.currency_id._convert(
                        data.amount_residual, data.currency_id, data.company_id,fields.Date.today())

            if self.demurrage_invoice_id:
                if self.demurrage_invoice_id.currency_id.id == self.demurrage_invoice_id.company_id.currency_id.id:
                    due_amount += self.demurrage_invoice_id.amout_residual
                elif self.demurrage_invoice_id.currency_id.id != self.demurrage_invoice_id.company_id.currency_id.id:
                    due_amount += self.demurrage_invoice_id.company_id.currency_id._convert(
                        self.demurrage_invoice_id.residual, self.demurrage_invoice_id.currency_id, self.demurrage_invoice_id.company_id,fields.Date.today())
                    due_amount += self.demurrage_invoice_id.amount_residual
            else:
                if self.bsg_cargo_sale_id.currency_id.id == self.bsg_cargo_sale_id.company_id.currency_id.id:
                    due_amount += self.final_price
                elif self.bsg_cargo_sale_id.currency_id.id != self.bsg_cargo_sale_id.company_id.currency_id.id:
                    due_amount += self.bsg_cargo_sale_id.company_id.currency_id._convert(
                        self.final_price , self.bsg_cargo_sale_id.currency_id, self.bsg_cargo_sale_id.company_id,fields.Date.today())
        return due_amount




    # returning only so amount
    def _getting_portal_so_amount(self):
        so_amount = 0
        if self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            so_amount = sum(self.invoice_line_ids.filtered(lambda s: not s.is_other_service_line and not s.is_refund and not s.is_demurrage_line).mapped('price_total'))
        if self.bsg_cargo_return_sale_id and self.bsg_cargo_return_sale_id.payment_method.payment_type in ['cash', 'pod']:
            for data in self.bsg_cargo_return_sale_id.invoice_ids:
                so_amount += data.amount_total
        return so_amount

    # returning only demurrage amount
    def _getting_portal_demurrage_amount(self):
        demurrage_amount = 0
        if self.demurrage_invoice_id:
            demurrage_amount += self.demurrage_invoice_id.amount_total
        else:
            demurrage_amount += self.final_price
        return demurrage_amount

    # returning only other service amount
    def _getting_portal_other_service_amount(self):
        other_service_amount = 0
        if self.bsg_cargo_sale_id.payment_method.payment_type in ['cash', 'pod']:
            other_service_amount += sum(self.invoice_line_ids.filtered(lambda s: s.is_other_service_line and not s.is_refund).mapped('price_total'))
        if self.bsg_cargo_return_sale_id and self.bsg_cargo_return_sale_id.payment_method.payment_type in ['cash', 'pod']:
            for other_service_invoice_data in self.env['account.move'].search([('invoice_origin', '=', self.bsg_cargo_return_sale_id.name), ('is_other_service_invoice', '=', True)]):
                if other_service_invoice_data:
                    other_service_amount += other_service_invoice_data.amount_total
        return other_service_amount



    def portal_onchange_shipment_type(self):
        if self.bsg_cargo_sale_id.partner_types.is_construction:
            self.discount = self.bsg_cargo_sale_id.partner_types.discount

        if self.shipment_type and self.car_size and self.car_model:
            if self.shipment_type.is_normal:
                valid_car_size = self.car_size
            else:
                valid_car_size = self.shipment_type.car_size

            if self.bsg_cargo_sale_id.customer_contract:
                ContractLine = self.env['bsg_customer_contract_line'].search([
                    ('cust_contract_id', '=',
                        self.bsg_cargo_sale_id.customer_contract.id),
                    ('service_type', '=', self.service_type.id),
                    ('loc_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                    ('loc_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                    ('car_size', '=', valid_car_size.id),
                ], limit=1)
                if ContractLine:
                    self.unit_charge = ContractLine.price if ContractLine else 0.0
                else:
                    self.raise_price_warning()
            else:
                PriceConfig = self.env['bsg_price_config'].search([
                    ('waypoint_from', '=', self.bsg_cargo_sale_id.loc_from.id),
                    ('company_id', '=', self.env.user.company_id.id),
                    ('waypoint_to', '=', self.bsg_cargo_sale_id.loc_to.id),
                    ('customer_type', '=',
                        self.bsg_cargo_sale_id.customer_type),
                ], limit=1)
                if PriceConfig:
                    PriceLine = self.env['bsg_price_line'].search([
                        ('price_config_id', '=', PriceConfig.id),
                        ('company_id', '=', self.env.user.company_id.id),
                        # ('service_type','=',self.service_type.id),
                        ('car_classfication', '=',
                            self.car_classfication.id),
                        ('car_size', '=', valid_car_size.id),
                    ], limit=1)
                    if PriceLine:
                        self.price_line_id = PriceLine.id
                        if self.bsg_cargo_sale_id.shipment_type == 'return':
                            self.unit_charge = PriceLine.price*2 if PriceLine else 0.0
                            self.bsg_cargo_sale_id.sudo().write({'qitaf_coupon':False, 'coupon_readonly': False})
                            self.discount = 10
                            self._onchange_discount()
                        else:
                            self.unit_charge = PriceLine.price if PriceLine else 0.0
                        # self.service_type = PriceLine.service_type.id if PriceLine else self.env[
                        #     'product.template'].search([('name', 'in', ['Cargo Service', 'Cargo'])], limit=1).id
                        self.service_type = PriceLine.service_type.id if PriceLine else self._default_cargo_service()
                    else:
                        self.raise_price_warning()
            default_customer_price_list = self.env['product.pricelist'].sudo().search(
            [('default_in_portal', '=', True),'|', ('agreement_type', '=', False), ('agreement_type', '=', self.shipment_type.id)], limit=1)
            if not default_customer_price_list:
                default_customer_price_list = self.env['product.pricelist'].sudo().search([('is_public', '=', True)], limit=1).id
            if self.bsg_cargo_sale_id.loc_from.is_international or self.bsg_cargo_sale_id.loc_to.is_international:
                self.bsg_cargo_sale_id.cargo_sale_type = 'international'
                self.bsg_cargo_sale_id.currency_id = self.bsg_cargo_sale_id.loc_from.loc_branch_id.currency_id.id
                self.customer_price_list = self.env['product.pricelist'].sudo().search([('is_public', '=', True)], limit=1).id
                self.bsg_cargo_sale_id.sudo().write({'qitaf_coupon':False, 'coupon_readonly': False})
                self.discount = 0
                if self.bsg_cargo_sale_id.shipment_type == 'return':
                    self.discount = 10
                self._onchange_discount()
            else:
                self.bsg_cargo_sale_id.cargo_sale_type = 'local'
                self.bsg_cargo_sale_id.currency_id = self.env.user.company_id.currency_id.id
                self.customer_price_list = default_customer_price_list.id
                for data in self.customer_price_list.item_ids:
                    if data.product_tmpl_id.id == self.service_type.id:
                        if self.discount < data.percent_price:
                            self.bsg_cargo_sale_id.sudo().write({'qitaf_coupon':False, 'coupon_readonly': False})
                            self.discount = data.percent_price
                if self.bsg_cargo_sale_id.shipment_type == 'return':
                    self.discount = 10
                self._onchange_discount()
            if not self.bsg_cargo_sale_id.currency_id:
                self.bsg_cargo_sale_id.currency_id = self.env.user.company_id.currency_id.id
            if self.service_type:
                PinConfig = self.env.user.company_id

            if self.bsg_cargo_sale_id.loc_from.is_international or self.bsg_cargo_sale_id.loc_to.is_international:
                self.tax_ids = [(6, 0, [])]
            else:
                self.tax_ids = PinConfig.sudo().tax_ids.ids or self.service_type.taxes_id.ids





