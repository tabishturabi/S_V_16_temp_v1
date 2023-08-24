from odoo import api, models, fields
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
import re
from calendar import monthrange
from odoo.exceptions import ValidationError
from pytz import timezone, UTC


class SaleRveneueByBranchReport(models.AbstractModel):
    _name = 'report.bassami_sale_revenue_branch_report.revenue_branch'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = 'sale.revenue.by.branch'
        record_wizard = self.env[model].browse(self.env.context.get('active_id'))
        form = record_wizard.form
        to = record_wizard.to
        is_satha = record_wizard.satha_only
        cargo_sale_type = record_wizard.cargo_sale_type
        report_type = record_wizard.report_type
        cash_pod_total_rec = 0.0
        cash_pod_total_amt_without_tax = 0.0
        credit_total_rec = 0.0
        credit_total_amt_without_tax = 0.0
        exhibit_total_rec = 0.0
        exhibit_total_amt_without_tax = 0.0
        other_total_rec = 0
        other_total_amt_without_tax = 0.0
        cash_method_total_rec = 0.0
        cash_method_total_amt_without_tax = 0.0
        credit_method_total_rec = 0.0
        credit_method_total_amt_without_tax = 0.0
        pod_method_total_rec = 0.0
        pod_method_total_amt_without_tax = 0.0
        none_method_total_rec = 0.0
        none_method_total_amt_without_tax = 0.0
        revenue_total_cars = 0
        revenue_total_amount = 0
        unshipped_total_cars = 0
        unshipped_total_amount = 0
        all_cars = 0
        all_reveneue = 0
        all_web_total_cars = 0
        all_web_total_revenue = 0

        grouped_by_date = {}

        en_arbic_weekday = {
            'Friday': 'الجمعة',
            'Saturday': 'السبت',
            'Sunday': 'الأحد',
            'Monday': 'الاثنين',
            'Tuesday': 'الثلاثاء',
            'Wednesday': 'الأربعاء',
            'Thursday': 'الخميس'
        }
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        form_tz = UTC.localize(form).astimezone(tz).replace(tzinfo=None)
        to_tz = UTC.localize(to).astimezone(tz).replace(tzinfo=None)
        end_date = to_tz.date()
        start_date = form_tz.date()
        num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        domain = [('order_date', '>=', form_tz), ('order_date', '<=', to_tz),('state', '!=', 'cancel')]
        if is_satha:
            domain.append(('shipment_type.is_satha', '=', True))

        if cargo_sale_type != 'all':
            domain.append(('bsg_cargo_sale_id.cargo_sale_type', '=', cargo_sale_type))
        if record_wizard.with_cc == 'add_to_cc':
            domain.append(('add_to_cc', '=', True))
        if record_wizard.with_cc == 'not_add_to_cc':
            domain.append(('add_to_cc', '=', False))
        if record_wizard.create_from == "mobile_app":
            domain.append(('is_from_app', '=', True))
        if record_wizard.create_from == "portal":
            domain.append(('is_from_portal', '=', True))
        if record_wizard.create_from == "branch":
            domain.append(('is_from_portal', '=', False))
            domain.append(('is_from_app', '=', False))
        if record_wizard.partner_type_filter == 'specific':
            domain.append(('bsg_cargo_sale_id.partner_types', 'in', record_wizard.Partner_type_ids.ids))
        if record_wizard.shipment_type_filter == 'specific':
            domain.append(('shipment_type', 'in', record_wizard.shipment_type_ids.ids))
        if record_wizard.car_size_filter == 'specific':
            domain.append(('car_size', 'in', record_wizard.car_size_ids.ids))
        if record_wizard.branch_type == 'specific':
            domain.append(('loc_from', 'in', record_wizard.ship_loc.ids))
        if record_wizard.branch_type_to == 'specific':
            domain.append(('loc_to', 'in', record_wizard.drop_loc.ids))
        if record_wizard.payment_method_filter == 'specific':
            domain.append(('payment_method', 'in', record_wizard.payment_method_ids.ids))
        if record_wizard.pay_case == 'paid':
            domain.append(('invoice_state_stored', '=','paid'))
        if record_wizard.pay_case == 'not_paid':
            domain.append(('invoice_state_stored', '!=','paid'))
        if record_wizard.user_type == 'specific':
            domain.append(('create_uid', 'in', record_wizard.users.ids))
        if record_wizard.customer_filter == 'specific':
            domain.append(('customer_id', 'in', record_wizard.customer_ids.ids))
        if record_wizard.state not in ['all', 'received', 'not_received', 'shipping', 'unshipping', 'both_shipping_unshipping']:
            domain.append(('state', '=', record_wizard.state))
        if record_wizard.state == 'received':
            domain.append(('delivery_report_history_ids', '!=', False))
        if record_wizard.state == 'not_received':
            domain.append(('delivery_report_history_ids', '=', False))
        if record_wizard.state == 'shipping':
            domain.append(('state', 'in', ['shipped', 'on_transit', 'Delivered', 'released', 'done']))
        if record_wizard.state == 'unshipping':
            domain.append(('state', 'in', ['draft', 'confirm']))
        if record_wizard.state == 'both_shipping_unshipping':
            domain.append(
                ('state', 'in', ['draft', 'confirm', 'shipped', 'on_transit', 'Delivered', 'released', 'done']))
        if record_wizard.invoicep_line_filter == 'paid':
            domain.append(('bsg_cargo_sale_id.refund_invoice_count', '!=', 0))
        if record_wizard.invoicep_line_filter == 'unpaid':
            domain.append(('bsg_cargo_sale_id.refund_invoice_count', '=', 0))
        if record_wizard.so_line_state == 'paid':
            domain.append(('is_paid', '=',True))
        if record_wizard.so_line_state == 'unpaid':
            domain.append(('is_paid', '=',False))
        if record_wizard.sale_order_state == 'all':
            domain.append(('sale_order_state', 'in',['done','pod','Delivered','confirm']))
        if record_wizard.sale_order_state == 'confirm':
            domain.append(('sale_order_state', 'in',['confirm']))
        if record_wizard.sale_order_state == 'pod':
            domain.append(('sale_order_state', 'in',['pod']))
        if record_wizard.sale_order_state == 'done':
            domain.append(('sale_order_state', 'in',['done']))
        if record_wizard.sale_order_state == 'Delivered':
            domain.append(('sale_order_state', 'in',['Delivered']))
        if record_wizard.cargo_sale_type == 'local':
            domain.append(('bsg_cargo_sale_id.cargo_sale_type', '=','local'))
        if record_wizard.cargo_sale_type == 'international':
            domain.append(('bsg_cargo_sale_id.cargo_sale_type', '=','international'))
        if record_wizard.trip_type != 'all':
            domain.append(('fleet_trip_id.trip_type', '=',record_wizard.trip_type))


        trans = self.env['bsg_vehicle_cargo_sale_line'].search(domain, order='order_date')
        if trans:
            trans = trans.filtered(lambda order:(order.bsg_cargo_sale_id.partner_types != False and not str(
                order.sale_line_rec_name).startswith(('*', 'P')) and not (order.is_from_portal or order.is_from_app)) or  ((order.is_from_portal or order.is_from_app) and order.is_paid == True))
        if trans:
            unshipped_trans = trans.filtered(lambda t: t.state != 'cancel' and (
                    not t.fleet_trip_id or (t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                       (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                   all(trip_type == 'local' for
                                                                                       trip_type in
                                                                                       [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))))

            if report_type == 'cash_flow':
                all_trans = trans

            trans = trans - unshipped_trans

            # .filtered(lambda t: (t.fleet_trip_id  and t.fleet_trip_id.trip_type != 'local') or\
            #         (t.trip_history_ids and\
            #             not all(trip_type == 'local' for trip_type in [trip_id.trip_type for trip_id in  t.trip_history_ids.mapped('fleet_trip_id')])))
        grouped_by_branch = {}
        if trans:
            #group by loc_fom
            mapped_branch = trans.mapped('loc_from')
            mapped_branch = [d for d in mapped_branch]
            print('............mapped_date.............', mapped_branch)
            print('............mapped_date set .............', set(mapped_branch))
            print('............mapped_date index .............', mapped_branch.index)
            branch_list = sorted(set(mapped_branch), key=mapped_branch.index)
            for branch_id in branch_list:
                # if report_type == 'cash_flow':
                #     order_lines = all_trans.filtered(lambda line: line.loc_from == branch_id)
                #     shipped_lines = trans.filtered(lambda line: line.loc_from == branch_id)
                # else:
                order_lines = trans.filtered(lambda line: line.loc_from == branch_id)
                webiste_sale = order_lines.filtered(lambda l: l.bsg_cargo_sale_id.is_from_portal or l.is_from_app)
                web_total_cars = len(webiste_sale)
                web_total_revenue = round(sum(webiste_sale.mapped('net_revenue')))
                all_web_total_cars += web_total_cars
                all_web_total_revenue += web_total_revenue
                unshipped_lines = unshipped_trans.filtered(lambda line: line.loc_from == branch_id)

                cash_pod_sale_ids = order_lines.filtered(lambda
                                                             order: order.bsg_cargo_sale_id.partner_types.id == 5)  # or order.bsg_cargo_sale_id.partner_types.id not in [2,3]
                credit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 2)
                exhibit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 3)
                other_sale_ids = order_lines.filtered(
                    lambda order: order.bsg_cargo_sale_id.partner_types.id not in [2, 3, 5])

                cash_method_sale_ids = order_lines.filtered(lambda
                                                                order: order.bsg_cargo_sale_id.payment_method and order.bsg_cargo_sale_id.payment_method.payment_type == 'cash')  # or order.bsg_cargo_sale_id.partner_types.id not in [2,3]
                credit_method_sale_ids = order_lines.filtered(lambda
                                                                  order: order.bsg_cargo_sale_id.payment_method and order.bsg_cargo_sale_id.payment_method.payment_type == 'credit')
                pod_method_sale_ids = order_lines.filtered(lambda
                                                               order: order.bsg_cargo_sale_id.payment_method and order.bsg_cargo_sale_id.payment_method.payment_type == 'pod')
                none_method_sale_ids = order_lines.filtered(lambda order: not order.bsg_cargo_sale_id.payment_method)

                cash_pod_rec, cash_pod_amt_without_tax = len(cash_pod_sale_ids), round(
                    sum(cash_pod_sale_ids.mapped('net_revenue')), 2)
                credit_rec, credit_amt_without_tax = len(credit_sale_ids), round(
                    sum(credit_sale_ids.mapped('net_revenue')), 2)
                exhibit_rec, exhibit_amt_without_tax = len(exhibit_sale_ids), round(
                    sum(exhibit_sale_ids.mapped('net_revenue')), 2)
                other_rec, other_amt_without_tax = len(other_sale_ids), round(
                    sum(other_sale_ids.mapped('net_revenue')), 2)

                cash_method_rec, cash_method_amt_without_tax = len(cash_method_sale_ids), round(
                    sum(cash_method_sale_ids.mapped('net_revenue')), 2)
                credit_method_rec, credit_method_amt_without_tax = len(credit_method_sale_ids), round(
                    sum(credit_method_sale_ids.mapped('net_revenue')), 2)
                pod_method_rec, pod_method_amt_without_tax = len(pod_method_sale_ids), round(
                    sum(pod_method_sale_ids.mapped('net_revenue')), 2)
                none_method_rec, none_method_amt_without_tax = len(none_method_sale_ids), round(
                    sum(none_method_sale_ids.mapped('net_revenue')), 2)
                # accumulating total per date range
                cash_pod_total_rec += cash_pod_rec
                cash_pod_total_amt_without_tax += cash_pod_amt_without_tax

                credit_total_rec += credit_rec
                credit_total_amt_without_tax += credit_amt_without_tax

                exhibit_total_rec += exhibit_rec
                exhibit_total_amt_without_tax += exhibit_amt_without_tax

                other_total_rec += other_rec
                other_total_amt_without_tax += other_amt_without_tax

                cash_method_total_rec += cash_method_rec
                cash_method_total_amt_without_tax += cash_method_amt_without_tax

                credit_method_total_rec += credit_method_rec
                credit_method_total_amt_without_tax += credit_method_amt_without_tax

                pod_method_total_rec += pod_method_rec
                pod_method_total_amt_without_tax += pod_method_amt_without_tax

                none_method_total_rec += none_method_rec
                none_method_total_amt_without_tax += none_method_amt_without_tax

                # total_day_no_cars = len(order_lines)
                # total_day_revenue = round(sum(order_lines.mapped('total_without_tax')))

                unshipped_day_no_cars = len(unshipped_lines)
                unshipped_day_revenue = round(sum(unshipped_lines.mapped('net_revenue')), 2)
                # if report_type == 'cash_flow':
                #     total_day_no_cars = len(shipped_lines)
                #     total_day_revenue = round(sum(shipped_lines.mapped('net_revenue')), 2)
                # else:
                total_day_no_cars = len(order_lines)
                total_day_revenue = round(sum(order_lines.mapped('net_revenue')), 2)
                daily_shipped_unshipped_total_cars = total_day_no_cars + unshipped_day_no_cars
                daily_shipped_unshipped_total_revenue = total_day_revenue + unshipped_day_revenue
                branch_key = branch_id.route_waypoint_name
                # date_key = en_arbic_weekday[date.strftime('%A', )] + date.strftime(', %d-%m-%Y', )
                grouped_by_branch[branch_key] = {
                    'cash_pod_rec': cash_pod_rec,
                    'cash_pod_amt_without_tax': cash_pod_amt_without_tax,
                    'credit_rec': credit_rec,
                    'credit_amt_without_tax': credit_amt_without_tax,
                    'exhibit_rec': exhibit_rec,
                    'exhibit_amt_without_tax': exhibit_amt_without_tax,
                    'other_rec': other_rec,
                    'other_amt_without_tax': other_amt_without_tax,
                    'total_day_no_cars': total_day_no_cars,
                    'total_day_revenue': total_day_revenue,
                    'unshipped_day_no_cars': unshipped_day_no_cars,
                    'unshipped_day_revenue': unshipped_day_revenue,
                    'daily_shipped_unshipped_total_cars': daily_shipped_unshipped_total_cars,
                    'daily_shipped_unshipped_total_revenue': daily_shipped_unshipped_total_revenue,
                    'web_total_cars': web_total_cars,
                    'web_total_revenue': web_total_revenue,
                    'by_payment_method': {
                        'cash_method_rec': cash_method_rec,
                        'cash_method_amt_without_tax': cash_method_amt_without_tax,
                        'credit_method_rec': credit_method_rec,
                        'credit_method_amt_without_tax': credit_method_amt_without_tax,
                        'pod_method_rec': pod_method_rec,
                        'pod_method_amt_without_tax': pod_method_amt_without_tax,
                        'none_method_rec': none_method_rec,
                        'none_method_amt_without_tax': none_method_amt_without_tax,
                    }
                }
            # #group by order date
            # mapped_date = trans.mapped('order_date')
            # mapped_date =[d.date() for d in mapped_date]
            # print('............mapped_date.............',mapped_date)
            # print('............mapped_date set .............',set(mapped_date))
            # print('............mapped_date index .............',mapped_date.index)
            # date_list = sorted(set(mapped_date), key=mapped_date.index)
            # grouped_by_date = {}
            # for date in date_list:
            #     if report_type == 'cash_flow':
            #         order_lines = all_trans.filtered(lambda line: line.order_date.date() == date)
            #         shipped_lines = trans.filtered(lambda line: line.order_date.date()  == date)
            #     else:
            #         order_lines = trans.filtered(lambda line: line.order_date.date()  == date)
            #     webiste_sale = order_lines.filtered(lambda l: l.bsg_cargo_sale_id.is_from_portal or l.is_from_app)
            #     web_total_cars = len(webiste_sale)
            #     web_total_revenue = round(sum(webiste_sale.mapped('revenue_amount')))
            #     all_web_total_cars += web_total_cars
            #     all_web_total_revenue += web_total_revenue
            #     unshipped_lines = unshipped_trans.filtered(lambda line: line.order_date.date()  == date)
            #
            #     cash_pod_sale_ids = order_lines.filtered(lambda
            #                                                  order: order.bsg_cargo_sale_id.partner_types.id == 5)  # or order.bsg_cargo_sale_id.partner_types.id not in [2,3]
            #     credit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 2)
            #     exhibit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 3)
            #     other_sale_ids = order_lines.filtered(
            #         lambda order: order.bsg_cargo_sale_id.partner_types.id not in [2, 3, 5])
            #
            #     cash_method_sale_ids = order_lines.filtered(lambda
            #                                                     order: order.bsg_cargo_sale_id.payment_method and order.bsg_cargo_sale_id.payment_method.payment_type == 'cash')  # or order.bsg_cargo_sale_id.partner_types.id not in [2,3]
            #     credit_method_sale_ids = order_lines.filtered(lambda
            #                                                       order: order.bsg_cargo_sale_id.payment_method and order.bsg_cargo_sale_id.payment_method.payment_type == 'credit')
            #     pod_method_sale_ids = order_lines.filtered(lambda
            #                                                    order: order.bsg_cargo_sale_id.payment_method and order.bsg_cargo_sale_id.payment_method.payment_type == 'pod')
            #     none_method_sale_ids = order_lines.filtered(lambda order: not order.bsg_cargo_sale_id.payment_method)
            #
            #     cash_pod_rec, cash_pod_amt_without_tax = len(cash_pod_sale_ids), round(sum(cash_pod_sale_ids.mapped('revenue_amount')),2)
            #     credit_rec, credit_amt_without_tax = len(credit_sale_ids), round(sum(credit_sale_ids.mapped('revenue_amount')), 2)
            #     exhibit_rec, exhibit_amt_without_tax = len(exhibit_sale_ids), round(sum(exhibit_sale_ids.mapped('revenue_amount')), 2)
            #     other_rec, other_amt_without_tax = len(other_sale_ids), round(sum(other_sale_ids.mapped('revenue_amount')), 2)
            #
            #     cash_method_rec, cash_method_amt_without_tax = len(cash_method_sale_ids), round(
            #         sum(cash_method_sale_ids.mapped('revenue_amount')), 2)
            #     credit_method_rec, credit_method_amt_without_tax = len(credit_method_sale_ids), round(
            #         sum(credit_method_sale_ids.mapped('revenue_amount')), 2)
            #     pod_method_rec, pod_method_amt_without_tax = len(pod_method_sale_ids), round(
            #         sum(pod_method_sale_ids.mapped('revenue_amount')), 2)
            #     none_method_rec, none_method_amt_without_tax = len(none_method_sale_ids), round(
            #         sum(none_method_sale_ids.mapped('revenue_amount')), 2)
            #     # accumulating total per date range
            #     cash_pod_total_rec += cash_pod_rec
            #     cash_pod_total_amt_without_tax += cash_pod_amt_without_tax
            #
            #     credit_total_rec += credit_rec
            #     credit_total_amt_without_tax += credit_amt_without_tax
            #
            #     exhibit_total_rec += exhibit_rec
            #     exhibit_total_amt_without_tax += exhibit_amt_without_tax
            #
            #     other_total_rec += other_rec
            #     other_total_amt_without_tax += other_amt_without_tax
            #
            #     cash_method_total_rec += cash_method_rec
            #     cash_method_total_amt_without_tax += cash_method_amt_without_tax
            #
            #     credit_method_total_rec += credit_method_rec
            #     credit_method_total_amt_without_tax += credit_method_amt_without_tax
            #
            #     pod_method_total_rec += pod_method_rec
            #     pod_method_total_amt_without_tax += pod_method_amt_without_tax
            #
            #     none_method_total_rec += none_method_rec
            #     none_method_total_amt_without_tax += none_method_amt_without_tax
            #
            #     # total_day_no_cars = len(order_lines)
            #     # total_day_revenue = round(sum(order_lines.mapped('total_without_tax')))
            #
            #     unshipped_day_no_cars = len(unshipped_lines)
            #     unshipped_day_revenue =  round(sum(unshipped_lines.mapped('revenue_amount')), 2)
            #     if report_type == 'cash_flow':
            #         total_day_no_cars = len(shipped_lines)
            #         total_day_revenue =  round(sum(shipped_lines.mapped('revenue_amount')), 2)
            #     else:
            #         total_day_no_cars = len(order_lines)
            #         total_day_revenue =  round(sum(order_lines.mapped('revenue_amount')), 2)
            #     daily_shipped_unshipped_total_cars = total_day_no_cars + unshipped_day_no_cars
            #     daily_shipped_unshipped_total_revenue = total_day_revenue + unshipped_day_revenue
            #     date_key = en_arbic_weekday[date.strftime('%A', )] + date.strftime(' %d ', )
            #     # date_key = en_arbic_weekday[date.strftime('%A', )] + date.strftime(', %d-%m-%Y', )
            #     grouped_by_date[date_key] = {
            #         'cash_pod_rec': cash_pod_rec,
            #         'cash_pod_amt_without_tax': cash_pod_amt_without_tax,
            #         'credit_rec': credit_rec,
            #         'credit_amt_without_tax': credit_amt_without_tax,
            #         'exhibit_rec': exhibit_rec,
            #         'exhibit_amt_without_tax': exhibit_amt_without_tax,
            #         'other_rec': other_rec,
            #         'other_amt_without_tax': other_amt_without_tax,
            #         'total_day_no_cars': total_day_no_cars,
            #         'total_day_revenue': total_day_revenue,
            #         'unshipped_day_no_cars': unshipped_day_no_cars,
            #         'unshipped_day_revenue': unshipped_day_revenue,
            #         'daily_shipped_unshipped_total_cars': daily_shipped_unshipped_total_cars,
            #         'daily_shipped_unshipped_total_revenue': daily_shipped_unshipped_total_revenue,
            #         'web_total_cars': web_total_cars,
            #         'web_total_revenue': web_total_revenue,
            #         'by_payment_method': {
            #             'cash_method_rec': cash_method_rec,
            #             'cash_method_amt_without_tax': cash_method_amt_without_tax,
            #             'credit_method_rec': credit_method_rec,
            #             'credit_method_amt_without_tax': credit_method_amt_without_tax,
            #             'pod_method_rec': pod_method_rec,
            #             'pod_method_amt_without_tax': pod_method_amt_without_tax,
            #             'none_method_rec': none_method_rec,
            #             'none_method_amt_without_tax': none_method_amt_without_tax,
            #         }
            #     }

            revenue_total_cars = len(trans)
            revenue_total_amount = round(sum(trans.mapped('net_revenue')), 2)
            unshipped_total_cars = len(unshipped_trans)
            unshipped_total_amount = round(sum(unshipped_trans.mapped('net_revenue')), 2)
            all_cars = revenue_total_cars + unshipped_total_cars
            all_reveneue = round(revenue_total_amount + unshipped_total_amount)

        # Sale Targets
        month_total_days = monthrange(form.year, form.month)[1]
        sale_taget_id = self.env['bsg_branch_sales_target'].search([]).filtered(
            lambda tagret: tagret.financial_year.name == str(form.year))
        sale_taget_filtered_id = sale_taget_id.br_sl_tr_line_ids.filtered(lambda l: l.bsg_br_sl_tr_mon == form.month)
        sale_month_target = 1.0
        if sale_taget_filtered_id:
            sale_month_target = sale_taget_filtered_id[0].bsg_br_sl_tr_for_tar
        shipped_month_target = (revenue_total_amount / sale_month_target) * 100
        unshipped_month_target = (unshipped_total_amount / sale_month_target) * 100
        overall_month_target = (all_reveneue / sale_month_target) * 100
        sale_today_target = round((sale_month_target / month_total_days) * to.day)
        shipped_today_target = (revenue_total_amount / sale_today_target) * 100
        unshipped_today_target = (unshipped_total_amount / sale_today_target) * 100
        overall_today_target = (all_reveneue / sale_today_target) * 100

        avarge_daily_revenue = round(all_reveneue / to.day)
        expected_monthly_revenue = avarge_daily_revenue * month_total_days
        if num_months > 1:
            sale_month_target = sale_month_target * num_months

        return {
            'doc_ids': docids,
            'doc_model': 'bsg_vehicle_cargo_sale',
            'form': en_arbic_weekday[form.strftime('%A', )] + form.strftime(', %d-%m-%Y', ),
            'to': en_arbic_weekday[to.strftime('%A', )] + to.strftime(', %d-%m-%Y', ),
            'cargo_sale_type': cargo_sale_type,
            'cash_pod_total_rec': cash_pod_total_rec,
            'cash_pod_total_amt_without_tax': round(cash_pod_total_amt_without_tax),
            'credit_total_rec': credit_total_rec,
            'credit_total_amt_without_tax': round(credit_total_amt_without_tax),
            'exhibit_total_rec': exhibit_total_rec,
            'exhibit_total_amt_without_tax': round(exhibit_total_amt_without_tax),
            'other_total_rec': other_total_rec,
            'other_total_amt_without_tax': round(other_total_amt_without_tax),
            'grouped_by_date': grouped_by_date,
            'grouped_by_branch': grouped_by_branch,
            'revenue_total_cars': revenue_total_cars,
            'revenue_total_amount': revenue_total_amount,
            'unshipped_total_cars': unshipped_total_cars,
            'unshipped_total_amount': unshipped_total_amount,
            'all_cars': all_cars,
            'all_reveneue': all_reveneue,
            'all_web_total_cars': all_web_total_cars,
            'all_web_total_revenue': all_web_total_revenue,
            'sale_month_target': sale_month_target,
            'shipped_month_target': shipped_month_target,
            'unshipped_month_target': unshipped_month_target,
            'overall_month_target': overall_month_target,
            'sale_today_target': sale_today_target,
            'shipped_today_target': shipped_today_target,
            'unshipped_today_target': unshipped_today_target,
            'overall_today_target': overall_today_target,
            'avarge_daily_revenue': avarge_daily_revenue,
            'expected_monthly_revenue': expected_monthly_revenue,
            'report_type': report_type,
            'cash_method_total_rec': cash_method_total_rec,
            'cash_method_total_amt_without_tax': cash_method_total_amt_without_tax,
            'credit_method_total_rec': credit_method_total_rec,
            'credit_method_total_amt_without_tax': credit_method_total_amt_without_tax,
            'pod_method_total_rec': pod_method_total_rec,
            'pod_method_total_amt_without_tax': pod_method_total_amt_without_tax,
            'none_method_total_rec': none_method_total_rec,
            'none_method_total_amt_without_tax': none_method_total_amt_without_tax
        }


class SaleRveneueByBranchReportExcel(models.AbstractModel):
    _name = 'report.bassami_sale_revenue_branch_report.revenue_branch_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):
        main_heading_top = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#00cc44',
            'font_size': '12',
        })
        main_heading_lines = workbook.add_format({
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '12',
        })
        header_data_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_size': 10, 'border': 1})
        main_heading_right_side = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '12',
        })
        worksheet = workbook.add_worksheet('تقرير ايرادات تفصيلي بنوع العميل')
        worksheet.set_column('A:A', 38)
        worksheet.set_column('B:P', 20)
        worksheet.freeze_panes(7, 0)
        rows = 0
        date_from = data.form
        date_to = data.to
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        form_tz = UTC.localize(date_from).astimezone(tz).replace(tzinfo=None)
        to_tz = UTC.localize(date_to).astimezone(tz).replace(tzinfo=None)
        is_satha = data.satha_only
        cargo_sale_type = data.cargo_sale_type
        report_type = data.report_type
        worksheet.merge_range(rows, 0, rows, 8, 'تقرير ايرادات تفصيلي بنوع العميل', main_heading_right_side)
        worksheet.write(3, 5, 'من تاريخ', main_heading_right_side)
        worksheet.write(3, 4, str(form_tz), main_heading_right_side)
        worksheet.write(4, 5, 'الى تاريخ', main_heading_right_side)
        worksheet.write(4, 4, str(to_tz), main_heading_right_side)

        rows += 6
        worksheet.write(rows, 0, 'الايراد', main_heading_top)
        worksheet.write(rows, 1, 'رحلات سابقه', main_heading_top)
        worksheet.write(rows, 2, 'رقم الرحله', main_heading_top)
        worksheet.write(rows, 3, 'رقم اللوحه', main_heading_top)
        worksheet.write(rows, 4, 'نوع العميل', main_heading_top)
        worksheet.write(rows, 5, 'اسم العميل', main_heading_top)
        worksheet.write(rows, 6, 'رقم السجل', main_heading_top)
        worksheet.write(rows, 7, 'رقم الاتفاقيه', main_heading_top)
        worksheet.write(rows, 8, 'التاريخ', main_heading_top)
        worksheet.write(rows, 9, 'فرع الشحن', main_heading_top)
        worksheet.write(rows, 10, 'فرع الوصول', main_heading_top)
        worksheet.write(rows, 11, 'طريقة الدفع', main_heading_top)

        cash_pod_total_rec = 0.0
        cash_pod_total_amt_without_tax = 0.0
        credit_total_rec = 0.0
        credit_total_amt_without_tax = 0.0
        exhibit_total_rec = 0.0
        exhibit_total_amt_without_tax = 0.0
        other_total_amt_without_tax = 0
        other_total_rec = 0
        en_arbic_weekday = {
            'Friday': 'الجمعة',
            'Saturday': 'السبت',
            'Sunday': 'الأحد',
            'Monday': 'الاثنين',
            'Tuesday': 'الثلاثاء',
            'Wednesday': 'الأربعاء',
            'Thursday': 'الخميس'
        }
        domain = [('order_date', '>=', form_tz),('order_date', '<=', to_tz),('state', '!=', 'cancel')]
        if is_satha:
            domain.append(('shipment_type.is_satha', '=', True))
        if cargo_sale_type != 'all':
            domain.append(('bsg_cargo_sale_id.cargo_sale_type', '=', cargo_sale_type))
        if data.with_cc == 'add_to_cc':
            domain.append(('add_to_cc', '=', True))
        if data.with_cc == 'not_add_to_cc':
            domain.append(('add_to_cc', '=', False))
        if data.create_from == "mobile_app":
            domain.append(('is_from_app', '=', True))
        if data.create_from == "portal":
            domain.append(('is_from_portal', '=', True))
        if data.create_from == "branch":
            domain.append(('is_from_portal', '=', False))
            domain.append(('is_from_app', '=', False))
        if data.partner_type_filter == 'specific':
            domain.append(('bsg_cargo_sale_id.partner_types', 'in', data.Partner_type_ids.ids))
        if data.shipment_type_filter == 'specific':
            domain.append(('shipment_type', 'in', data.shipment_type_ids.ids))
        if data.car_size_filter == 'specific':
            domain.append(('car_size', 'in', data.car_size_ids.ids))
        if data.branch_type == 'specific':
            domain.append(('loc_from', 'in', data.ship_loc.ids))
        if data.branch_type_to == 'specific':
            domain.append(('loc_to', 'in', data.drop_loc.ids))
        if data.payment_method_filter == 'specific':
            domain.append(('payment_method', 'in', data.payment_method_ids.ids))
        if data.pay_case == 'paid':
            domain.append(('invoice_state_stored', '=','paid'))
        if data.pay_case == 'not_paid':
            domain.append(('invoice_state_stored', '!=','paid'))
        if data.user_type == 'specific':
            domain.append(('create_uid', 'in', data.users.ids))
        if data.customer_filter == 'specific':
            domain.append(('customer_id', 'in', data.customer_ids.ids))
        if data.state not in ['all','received', 'not_received','shipping','unshipping','both_shipping_unshipping']:
            domain.append(('state', '=', data.state))
        if data.state == 'received':
            domain.append(('delivery_report_history_ids', '!=', False))
        if data.state == 'not_received':
            domain.append(('delivery_report_history_ids', '=', False))
        if data.state == 'shipping':
            domain.append(('state', 'in', ['shipped', 'on_transit', 'Delivered', 'released', 'done']))
        if data.state == 'unshipping':
            domain.append(('state', 'in', ['draft', 'confirm']))
        if data.state == 'both_shipping_unshipping':
            domain.append(
                ('state', 'in', ['draft', 'confirm', 'shipped', 'on_transit', 'Delivered', 'released', 'done']))
        if data.invoicep_line_filter == 'paid':
            domain.append(('bsg_cargo_sale_id.refund_invoice_count', '!=', 0))
        if data.invoicep_line_filter == 'unpaid':
            domain.append(('bsg_cargo_sale_id.refund_invoice_count', '=', 0))
        if data.so_line_state == 'paid':
            domain.append(('is_paid', '=',True))
        if data.so_line_state == 'unpaid':
            domain.append(('is_paid', '=',False))
        if data.sale_order_state == 'all':
            domain.append(('sale_order_state', 'in',['done','pod','Delivered','confirm']))
        if data.sale_order_state == 'confirm':
            domain.append(('sale_order_state', 'in',['confirm']))
        if data.sale_order_state == 'pod':
            domain.append(('sale_order_state', 'in',['pod']))
        if data.sale_order_state == 'done':
            domain.append(('sale_order_state', 'in',['done']))
        if data.sale_order_state == 'Delivered':
            domain.append(('sale_order_state', 'in',['Delivered']))
        if data.cargo_sale_type == 'local':
            domain.append(('bsg_cargo_sale_id.cargo_sale_type', '=','local'))
        if data.cargo_sale_type == 'international':
            domain.append(('bsg_cargo_sale_id.cargo_sale_type', '=','international'))
        if data.trip_type != 'all':
            domain.append(('fleet_trip_id.trip_type', '=',data.trip_type))

        CargoSaleLine = self.env['bsg_vehicle_cargo_sale_line'].search(domain, order='order_date')
        CargoSaleLine = CargoSaleLine.filtered(lambda order:(order.bsg_cargo_sale_id.partner_types != False and not str(
                order.sale_line_rec_name).startswith(('*', 'P')) and not (order.is_from_portal or order.is_from_app)) or  ((order.is_from_portal or order.is_from_app) and order.is_paid == True))
        rows += 1
        # mapped_date = CargoSaleLine.mapped('order_date')
        # mapped_date = [d.date() for   d in mapped_date]
        # date_list = sorted(set(mapped_date), key=mapped_date.index)
        grouped_by_date = {}
        order_lines = []
        date_key =''

        if CargoSaleLine:
            # for ddate in date_list:
            rows+2
            # order_lines = CargoSaleLine.filtered(lambda line: line.order_date.date()  == ddate)
            order_lines = CargoSaleLine
            cash_pod_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 5)
            credit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 2)
            exhibit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 3)
            other_sale_ids = order_lines.filtered(
                lambda order: order.bsg_cargo_sale_id.partner_types.id not in [2, 3, 5])
            cash_pod_rec, cash_pod_amt_without_tax = len(cash_pod_sale_ids), sum(
                cash_pod_sale_ids.mapped('net_revenue'))
            credit_rec, credit_amt_without_tax = len(credit_sale_ids), sum(
                credit_sale_ids.mapped('net_revenue'))
            exhibit_rec, exhibit_amt_without_tax = len(exhibit_sale_ids), sum(
                exhibit_sale_ids.mapped('net_revenue'))
            other_rec, other_amt_without_tax = len(other_sale_ids), sum(
                other_sale_ids.mapped('net_revenue'))

            # accumulating total per date range
            cash_pod_total_rec += cash_pod_rec
            cash_pod_total_amt_without_tax += cash_pod_amt_without_tax

            credit_total_rec += credit_rec
            credit_total_amt_without_tax += credit_amt_without_tax

            exhibit_total_rec += exhibit_rec
            exhibit_total_amt_without_tax += exhibit_amt_without_tax

            other_total_rec += other_rec
            other_total_amt_without_tax += other_amt_without_tax

            # date_key = en_arbic_weekday[ddate.strftime('%A', )] + ddate.strftime(' %d ', )
            # grouped_by_date[date_key] = {
            #     'cash_pod_sale_ids': cash_pod_sale_ids,
            #     'cash_pod_rec': cash_pod_rec,
            #     'cash_pod_amt_without_tax': cash_pod_amt_without_tax,
            #     'credit_sale_ids': credit_sale_ids,
            #     'credit_rec': credit_rec,
            #     'credit_amt_without_tax': credit_amt_without_tax,
            #     'exhibit_sale_ids': exhibit_sale_ids,
            #     'exhibit_rec': exhibit_rec,
            #     'exhibit_amt_without_tax': exhibit_amt_without_tax,
            #     'other_sale_ids': other_sale_ids,
            #     'other_rec': other_rec,
            #     'other_amt_without_tax': other_amt_without_tax,
            #     'total_day_no_cars': len(order_lines),
            #     'total_day_revenue': sum(order_lines.mapped('total_without_tax'))
            # }
            # worksheet.write(rows, 3, 'التاريخ', main_heading_right_side)
            # worksheet.write(rows, 2, str(date_key), main_heading_right_side)
            # worksheet.write(rows+1, 3, 'اجمالي عدد السيارات', main_heading_right_side)
            # total_day = sum(order_lines.mapped('revenue_amount'))
            # worksheet.write(rows+2, 3, 'اجمالي الايراد', main_heading_right_side)
            # worksheet.write(rows+2, 2, str(total_day), main_heading_right_side)
            # rows += 4
            # worksheet.merge_range(rows + 1, 0, rows, 8, 'عملاء نقدي او اجل', main_heading_right_side)
            # rows += 3
            for x in cash_pod_sale_ids:
                worksheet.write_number(rows, 0, round(float(x.revenue_amount),2), header_data_format)
                worksheet.write(rows, 1, ' / '.join([trip.name for trip in x.trip_history_ids.mapped('fleet_trip_id')]),
                                header_data_format)
                worksheet.write(rows, 2, x.fleet_trip_id.name, header_data_format)
                worksheet.write(rows, 3, x.plate_no, header_data_format)
                worksheet.write(rows, 4, str(x.bsg_cargo_sale_id.partner_types.name), header_data_format)
                worksheet.write(rows, 5, str(x.customer_id.name), header_data_format)
                worksheet.write(rows, 6, str(x.sale_line_rec_name), header_data_format)
                worksheet.write(rows, 7, str(x.bsg_cargo_sale_id.name), header_data_format)
                worksheet.write(rows, 8, str(x.order_date), header_data_format)
                worksheet.write(rows, 9, str(x.loc_from.route_waypoint_name), header_data_format)
                worksheet.write(rows, 10, str(x.loc_to.route_waypoint_name), header_data_format)
                worksheet.write(rows, 11, str(x.payment_method.payment_method_name), header_data_format)
                rows += 1
            rows += 1
            # worksheet.write(rows, 1, str(cash_pod_rec) + ' : عدد السيارات', header_data_format)
            # worksheet.write(rows, 0, '{0:,.2f}'.format(float(cash_pod_amt_without_tax)), header_data_format)
            # rows += 1
            #
            # worksheet.merge_range(rows + 1, 0, rows, 8, 'عملاء على الحساب', main_heading_right_side)
            # rows += 3
            for x in credit_sale_ids:
                worksheet.write_number(rows, 0, round(float(x.revenue_amount),2), header_data_format)
                worksheet.write(rows, 1, ' / '.join([trip.name for trip in x.trip_history_ids.mapped('fleet_trip_id')]),
                                header_data_format)
                worksheet.write(rows, 2, x.fleet_trip_id.name, header_data_format)
                worksheet.write(rows, 3, x.plate_no, header_data_format)
                worksheet.write(rows, 4, str(x.bsg_cargo_sale_id.partner_types.name), header_data_format)
                worksheet.write(rows, 5, str(x.customer_id.name), header_data_format)
                worksheet.write(rows, 6, str(x.sale_line_rec_name), header_data_format)
                worksheet.write(rows, 7, str(x.bsg_cargo_sale_id.name), header_data_format)
                worksheet.write(rows, 8, str(x.order_date), header_data_format)
                worksheet.write(rows, 9, str(x.loc_from.route_waypoint_name), header_data_format)
                worksheet.write(rows, 10, str(x.loc_to.route_waypoint_name), header_data_format)
                worksheet.write(rows, 11, str(x.payment_method.payment_method_name), header_data_format)
                rows += 1
            # worksheet.write(rows, 1, str(credit_rec) + ' :  عدد السيارات', header_data_format)
            # worksheet.write(rows, 0, '{0:,.2f}'.format(float(credit_amt_without_tax)), header_data_format)
            # rows += 1
            # worksheet.merge_range(rows + 1, 0, rows, 8, ' عملاء  معارض', main_heading_right_side)
            # rows += 3
            for x in exhibit_sale_ids:
                worksheet.write_number(rows, 0, round(float(x.revenue_amount),2), header_data_format)
                worksheet.write(rows, 1, ' / '.join([trip.name for trip in x.trip_history_ids.mapped('fleet_trip_id')]),
                                header_data_format)
                worksheet.write(rows, 2, x.fleet_trip_id.name, header_data_format)
                worksheet.write(rows, 3, x.plate_no, header_data_format)
                worksheet.write(rows, 4, str(x.bsg_cargo_sale_id.partner_types.name), header_data_format)
                worksheet.write(rows, 5, str(x.customer_id.name), header_data_format)
                worksheet.write(rows, 6, str(x.sale_line_rec_name), header_data_format)
                worksheet.write(rows, 7, str(x.bsg_cargo_sale_id.name), header_data_format)
                worksheet.write(rows, 8, str(x.order_date), header_data_format)
                worksheet.write(rows, 9, str(x.loc_from.route_waypoint_name), header_data_format)
                worksheet.write(rows, 10, str(x.loc_to.route_waypoint_name), header_data_format)
                worksheet.write(rows, 11, str(x.payment_method.payment_method_name), header_data_format)
                rows += 1
            # worksheet.write(rows, 1, str(exhibit_rec) + ' : عدد السيارات', header_data_format)
            # worksheet.write(rows, 0, '{0:,.2f}'.format(float(exhibit_amt_without_tax)), header_data_format)
            # rows += 1
            # worksheet.merge_range(rows + 1, 0, rows, 8, '  عملاء اخرين', main_heading_right_side)
            # rows += 3
            for x in other_sale_ids:
                worksheet.write_number(rows, 0, round(float(x.revenue_amount),2), header_data_format)
                worksheet.write(rows, 1, ' / '.join([trip.name for trip in x.trip_history_ids.mapped('fleet_trip_id')]),
                                header_data_format)
                worksheet.write(rows, 2, x.fleet_trip_id.name, header_data_format)
                worksheet.write(rows, 3, x.plate_no, header_data_format)
                worksheet.write(rows, 4, str(x.bsg_cargo_sale_id.partner_types.name), header_data_format)
                worksheet.write(rows, 5, str(x.customer_id.name), header_data_format)
                worksheet.write(rows, 6, str(x.sale_line_rec_name), header_data_format)
                worksheet.write(rows, 7, str(x.bsg_cargo_sale_id.name), header_data_format)
                worksheet.write(rows, 8, str(x.order_date), header_data_format)
                worksheet.write(rows, 9, str(x.loc_from.route_waypoint_name), header_data_format)
                worksheet.write(rows, 10, str(x.loc_to.route_waypoint_name), header_data_format)
                worksheet.write(rows, 11, str(x.payment_method.payment_method_name), header_data_format)
                rows += 1
            # worksheet.write(rows, 1, str(other_rec) + ': عدد السيارات', header_data_format)
            # worksheet.write(rows, 0, '{0:,.2f}'.format(float(other_amt_without_tax)), header_data_format)

        rows += 3
        revenue_total_cars = len(CargoSaleLine)
        revenue_total_amount = sum(CargoSaleLine.mapped('net_revenue'))
        worksheet.write(rows, 5, 'اجمالي الايراد', main_heading_right_side)
        worksheet.write(rows, 4, 'اجمالي عددالسيارات', main_heading_right_side)
        rows += 1
        worksheet.write(rows, 5, str(round(revenue_total_amount, 2)), main_heading_right_side)
        worksheet.write(rows, 4, str(revenue_total_cars), main_heading_right_side)
