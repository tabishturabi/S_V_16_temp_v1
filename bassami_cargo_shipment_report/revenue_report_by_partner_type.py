from odoo import api, models, fields
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
import re
from calendar import monthrange
from odoo.exceptions import ValidationError


class SaleRveneueByPartnerTypeReport(models.AbstractModel):
    _name = 'report.bassami_cargo_shipment_report.revenue_partner_temp'

    @api.model
    def _get_report_values(self, docids, data=None):

        model = 'sale.revenue.by.partner.type'
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
        domain = [('order_date', '>=', form), ('order_date', '<=', to), ('state', 'not in', ['cancel'])]
        if is_satha:
            domain.append(('shipment_type.is_satha', '=', True))

        if cargo_sale_type:
            domain.append(('bsg_cargo_sale_id.cargo_sale_type', '=', cargo_sale_type))

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

        if trans:
            mapped_date = trans.mapped('order_date')
            mapped_date =[d.date() for d in mapped_date]
            date_list = sorted(set(mapped_date), key=mapped_date.index)
            grouped_by_date = {}
            for date in date_list:
                if report_type == 'cash_flow':
                    order_lines = all_trans.filtered(lambda line: line.order_date.date() == date)
                    shipped_lines = trans.filtered(lambda line: line.order_date.date()  == date)
                else:
                    order_lines = trans.filtered(lambda line: line.order_date.date()  == date)
                webiste_sale = order_lines.filtered(lambda l: l.bsg_cargo_sale_id.is_from_portal or l.is_from_app)
                web_total_cars = len(webiste_sale)
                web_total_revenue = round(sum(webiste_sale.mapped('revenue_amount')))
                all_web_total_cars += web_total_cars
                all_web_total_revenue += web_total_revenue
                unshipped_lines = unshipped_trans.filtered(lambda line: line.order_date.date()  == date)

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

                cash_pod_rec, cash_pod_amt_without_tax = len(cash_pod_sale_ids), round(sum(cash_pod_sale_ids.mapped('revenue_amount')),2) 
                credit_rec, credit_amt_without_tax = len(credit_sale_ids), round(sum(credit_sale_ids.mapped('revenue_amount')), 2) 
                exhibit_rec, exhibit_amt_without_tax = len(exhibit_sale_ids), round(sum(exhibit_sale_ids.mapped('revenue_amount')), 2) 
                other_rec, other_amt_without_tax = len(other_sale_ids), round(sum(other_sale_ids.mapped('revenue_amount')), 2) 

                cash_method_rec, cash_method_amt_without_tax = len(cash_method_sale_ids), round(
                    sum(cash_method_sale_ids.mapped('revenue_amount')), 2)
                credit_method_rec, credit_method_amt_without_tax = len(credit_method_sale_ids), round(
                    sum(credit_method_sale_ids.mapped('revenue_amount')), 2) 
                pod_method_rec, pod_method_amt_without_tax = len(pod_method_sale_ids), round(
                    sum(pod_method_sale_ids.mapped('revenue_amount')), 2) 
                none_method_rec, none_method_amt_without_tax = len(none_method_sale_ids), round(
                    sum(none_method_sale_ids.mapped('revenue_amount')), 2) 
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
                unshipped_day_revenue =  round(sum(unshipped_lines.mapped('revenue_amount')), 2)
                if report_type == 'cash_flow':
                    total_day_no_cars = len(shipped_lines)
                    total_day_revenue =  round(sum(shipped_lines.mapped('revenue_amount')), 2)
                else:
                    total_day_no_cars = len(order_lines)
                    total_day_revenue =  round(sum(order_lines.mapped('revenue_amount')), 2)
                daily_shipped_unshipped_total_cars = total_day_no_cars + unshipped_day_no_cars
                daily_shipped_unshipped_total_revenue = total_day_revenue + unshipped_day_revenue
                date_key = en_arbic_weekday[date.strftime('%A', )] + date.strftime(' %d ', )
                # date_key = en_arbic_weekday[date.strftime('%A', )] + date.strftime(', %d-%m-%Y', )
                grouped_by_date[date_key] = {
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

            revenue_total_cars = len(trans)
            revenue_total_amount = round(sum(trans.mapped('revenue_amount')), 2)
            unshipped_total_cars = len(unshipped_trans)
            unshipped_total_amount = round(sum(unshipped_trans.mapped('revenue_amount')), 2)
            all_cars = revenue_total_cars + unshipped_total_cars
            all_reveneue = round(revenue_total_amount + unshipped_total_amount)

        # Sale Targets
        month_total_days = monthrange(form.year, form.month)[1]
        sale_taget_id = self.env['bsg_branch_sales_target'].search([]).filtered(
            lambda tagret: tagret.financial_year.name == str(form.year))
        filtred_br_tr_line = sale_taget_id.br_sl_tr_line_ids.filtered(lambda l: l.bsg_br_sl_tr_mon == form.month)
        sale_month_target = (filtred_br_tr_line and filtred_br_tr_line[0].bsg_br_sl_tr_for_tar) or 0
        shipped_month_target = (sale_month_target and (revenue_total_amount / sale_month_target) * 100) or 0
        unshipped_month_target = (sale_month_target and (unshipped_total_amount / sale_month_target) * 100) or 0
        overall_month_target = (sale_month_target and (all_reveneue / sale_month_target) * 100) or 0
        sale_today_target = round((sale_month_target / month_total_days) * to.day)
        shipped_today_target = (sale_today_target and (revenue_total_amount / sale_today_target) or 0) * 100
        unshipped_today_target = (sale_today_target and (unshipped_total_amount / sale_today_target) or 0) * 100
        overall_today_target = (sale_today_target and (all_reveneue / sale_today_target) or 0) * 100

        avarge_daily_revenue = round(all_reveneue / to.day)
        expected_monthly_revenue = avarge_daily_revenue * month_total_days

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


class SaleRveneueByPartnerTypeReportExcel(models.AbstractModel):
    _name = 'report.bassami_cargo_shipment_report.sale_revenue_partner_xlsx'
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
        is_satha = data.satha_only
        cargo_sale_type = data.cargo_sale_type
        report_type = data.report_type
        worksheet.merge_range(rows, 0, rows, 8, 'تقرير ايرادات تفصيلي بنوع العميل', main_heading_right_side)
        worksheet.write(3, 5, 'من تاريخ', main_heading_right_side)
        worksheet.write(3, 4, str(date_from), main_heading_right_side)
        worksheet.write(4, 5, 'الى تاريخ', main_heading_right_side)
        worksheet.write(4, 4, str(date_to), main_heading_right_side)

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
        domain = [('order_date', '>=', date_from), ('order_date', '<=', date_to), ('state', 'not in', ['cancel'])]
        if is_satha:
            domain.append(('shipment_type.is_satha', '=', True))
        if cargo_sale_type:
            domain.append(('bsg_cargo_sale_id.cargo_sale_type', '=', cargo_sale_type))
        CargoSaleLine = self.env['bsg_vehicle_cargo_sale_line'].search(domain, order='order_date')
        CargoSaleLine = CargoSaleLine.filtered(lambda order:(order.bsg_cargo_sale_id.partner_types != False and not str(
                order.sale_line_rec_name).startswith(('*', 'P')) and not (order.is_from_portal or order.is_from_app)) or  ((order.is_from_portal or order.is_from_app) and order.is_paid == True))
        rows += 1
        mapped_date = CargoSaleLine.mapped('order_date')
        mapped_date = [d.date() for   d in mapped_date]
        date_list = sorted(set(mapped_date), key=mapped_date.index)
        grouped_by_date = {}
        order_lines = []
        date_key =''

        if CargoSaleLine:
            for ddate in date_list:
                rows+2
                order_lines = CargoSaleLine.filtered(lambda line: line.order_date.date()  == ddate)
                cash_pod_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 5)
                credit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 2)
                exhibit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 3)
                other_sale_ids = order_lines.filtered(
                    lambda order: order.bsg_cargo_sale_id.partner_types.id not in [2, 3, 5])
                cash_pod_rec, cash_pod_amt_without_tax = len(cash_pod_sale_ids), sum(
                    cash_pod_sale_ids.mapped('revenue_amount'))
                credit_rec, credit_amt_without_tax = len(credit_sale_ids), sum(
                    credit_sale_ids.mapped('revenue_amount'))
                exhibit_rec, exhibit_amt_without_tax = len(exhibit_sale_ids), sum(
                    exhibit_sale_ids.mapped('revenue_amount'))
                other_rec, other_amt_without_tax = len(other_sale_ids), sum(
                    other_sale_ids.mapped('revenue_amount'))

                # accumulating total per date range
                cash_pod_total_rec += cash_pod_rec
                cash_pod_total_amt_without_tax += cash_pod_amt_without_tax

                credit_total_rec += credit_rec
                credit_total_amt_without_tax += credit_amt_without_tax

                exhibit_total_rec += exhibit_rec
                exhibit_total_amt_without_tax += exhibit_amt_without_tax

                other_total_rec += other_rec
                other_total_amt_without_tax += other_amt_without_tax

                date_key = en_arbic_weekday[ddate.strftime('%A', )] + ddate.strftime(' %d ', )
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
                worksheet.write(rows, 3, 'التاريخ', main_heading_right_side)
                worksheet.write(rows, 2, str(date_key), main_heading_right_side)
                worksheet.write(rows+1, 3, 'اجمالي عدد السيارات', main_heading_right_side)
                total_day = sum(order_lines.mapped('revenue_amount'))
                worksheet.write(rows+2, 3, 'اجمالي الايراد', main_heading_right_side)
                worksheet.write(rows+2, 2, str(total_day), main_heading_right_side)
                rows += 4
                worksheet.merge_range(rows + 1, 0, rows, 8, 'عملاء نقدي او اجل', main_heading_right_side)
                rows += 3
                for x in cash_pod_sale_ids:
                    worksheet.write(rows, 0, '{0:,.2f}'.format(float(x.revenue_amount)), header_data_format)
                    worksheet.write(rows, 1, ' / '.join([trip.name for trip in x.trip_history_ids.mapped('fleet_trip_id')]),
                                    header_data_format)
                    worksheet.write(rows, 2, x.fleet_trip_id.name, header_data_format)
                    worksheet.write(rows, 3, x.plate_no, header_data_format)
                    worksheet.write(rows, 4, str(x.bsg_cargo_sale_id.partner_types.name), header_data_format)
                    worksheet.write(rows, 5, str(x.customer_id.name), header_data_format)
                    worksheet.write(rows, 6, str(x.sale_line_rec_name), header_data_format)
                    worksheet.write(rows, 7, str(x.bsg_cargo_sale_id.name), header_data_format)
                    worksheet.write(rows, 8, str(ddate), header_data_format)
                    rows += 1
                rows += 1
                worksheet.write(rows, 1, str(cash_pod_rec) + ' : عدد السيارات', header_data_format)
                worksheet.write(rows, 0, '{0:,.2f}'.format(float(cash_pod_amt_without_tax)), header_data_format)
                rows += 1

                worksheet.merge_range(rows + 1, 0, rows, 8, 'عملاء على الحساب', main_heading_right_side)
                rows += 3
                for x in credit_sale_ids:
                    worksheet.write(rows, 0, '{0:,.2f}'.format(float(x.revenue_amount)), header_data_format)
                    worksheet.write(rows, 1, ' / '.join([trip.name for trip in x.trip_history_ids.mapped('fleet_trip_id')]),
                                    header_data_format)
                    worksheet.write(rows, 2, x.fleet_trip_id.name, header_data_format)
                    worksheet.write(rows, 3, x.plate_no, header_data_format)
                    worksheet.write(rows, 4, str(x.bsg_cargo_sale_id.partner_types.name), header_data_format)
                    worksheet.write(rows, 5, str(x.customer_id.name), header_data_format)
                    worksheet.write(rows, 6, str(x.sale_line_rec_name), header_data_format)
                    worksheet.write(rows, 7, str(x.bsg_cargo_sale_id.name), header_data_format)
                    worksheet.write(rows, 8, str(ddate), header_data_format)
                    rows += 1
                worksheet.write(rows, 1, str(credit_rec) + ' :  عدد السيارات', header_data_format)
                worksheet.write(rows, 0, '{0:,.2f}'.format(float(credit_amt_without_tax)), header_data_format)
                rows += 1
                worksheet.merge_range(rows + 1, 0, rows, 8, ' عملاء  معارض', main_heading_right_side)
                rows += 3
                for x in exhibit_sale_ids:
                    worksheet.write(rows, 0, '{0:,.2f}'.format(float(x.revenue_amount)), header_data_format)
                    worksheet.write(rows, 1, ' / '.join([trip.name for trip in x.trip_history_ids.mapped('fleet_trip_id')]),
                                    header_data_format)
                    worksheet.write(rows, 2, x.fleet_trip_id.name, header_data_format)
                    worksheet.write(rows, 3, x.plate_no, header_data_format)
                    worksheet.write(rows, 4, str(x.bsg_cargo_sale_id.partner_types.name), header_data_format)
                    worksheet.write(rows, 5, str(x.customer_id.name), header_data_format)
                    worksheet.write(rows, 6, str(x.sale_line_rec_name), header_data_format)
                    worksheet.write(rows, 7, str(x.bsg_cargo_sale_id.name), header_data_format)
                    worksheet.write(rows, 8, str(ddate), header_data_format)
                    rows += 1
                worksheet.write(rows, 1, str(exhibit_rec) + ' : عدد السيارات', header_data_format)
                worksheet.write(rows, 0, '{0:,.2f}'.format(float(exhibit_amt_without_tax)), header_data_format)
                rows += 1
                worksheet.merge_range(rows + 1, 0, rows, 8, '  عملاء اخرين', main_heading_right_side)
                rows += 3
                for x in other_sale_ids:
                    worksheet.write(rows, 0, '{0:,.2f}'.format(float(x.revenue_amount)), header_data_format)
                    worksheet.write(rows, 1, ' / '.join([trip.name for trip in x.trip_history_ids.mapped('fleet_trip_id')]),
                                    header_data_format)
                    worksheet.write(rows, 2, x.fleet_trip_id.name, header_data_format)
                    worksheet.write(rows, 3, x.plate_no, header_data_format)
                    worksheet.write(rows, 4, str(x.bsg_cargo_sale_id.partner_types.name), header_data_format)
                    worksheet.write(rows, 5, str(x.customer_id.name), header_data_format)
                    worksheet.write(rows, 6, str(x.sale_line_rec_name), header_data_format)
                    worksheet.write(rows, 7, str(x.bsg_cargo_sale_id.name), header_data_format)
                    worksheet.write(rows, 8, str(ddate), header_data_format)
                    rows += 1
                worksheet.write(rows, 1, str(other_rec) + ': عدد السيارات', header_data_format)
                worksheet.write(rows, 0, '{0:,.2f}'.format(float(other_amt_without_tax)), header_data_format)

            rows += 3
            revenue_total_cars = len(CargoSaleLine)
            revenue_total_amount = sum(CargoSaleLine.mapped('revenue_amount')) 
            worksheet.write(rows, 5, 'اجمالي الايراد', main_heading_right_side)
            worksheet.write(rows, 4, 'اجمالي عددالسيارات', main_heading_right_side)
            rows += 1
            worksheet.write(rows, 5, str(round(revenue_total_amount, 2)), main_heading_right_side)
            worksheet.write(rows, 4, str(revenue_total_cars), main_heading_right_side)


class SaleRveneueDetail(models.AbstractModel):
    _name = 'report.bassami_cargo_shipment_report.revenue_details_temp'

    @api.model
    def _get_report_values(self, docids, data=None):

        model = self.env.context.get('active_model')
        record_wizard = self.env[model].browse(self.env.context.get('active_id'))
        form = record_wizard.form
        to = record_wizard.to
        is_satha = record_wizard.satha_only
        report_type = record_wizard.report_type
        cash_pod_total_rec = 0.0
        cash_pod_total_amt_without_tax = 0.0
        credit_total_rec = 0.0
        credit_total_amt_without_tax = 0.0
        exhibit_total_rec = 0.0
        exhibit_total_amt_without_tax = 0.0
        other_total_amt_without_tax = 0
        other_total_rec = 0
        revenue_total_cars = 0
        revenue_total_amount = 0

        grouped_by_date = {}

        en_arbic_weekday= {
                'Friday': 'الجمعة',
                'Saturday':'السبت',
                'Sunday':'الأحد',
                'Monday':'الاثنين',
                'Tuesday':'الثلاثاء',
                'Wednesday':'الأربعاء',
                'Thursday': 'الخميس'
            }

        domain = [('order_date', '>=', form), ('order_date', '<=', to), ('state', 'not in', ['cancel'])]
        if is_satha:
            domain.append(('shipment_type.is_satha', '=', True))

        trans = self.env['bsg_vehicle_cargo_sale_line'].search(domain, order='order_date')
        if trans:
            trans = trans.filtered(lambda order:(order.bsg_cargo_sale_id.partner_types != False and not str(
                order.sale_line_rec_name).startswith(('*', 'P')) and not (order.is_from_portal or order.is_from_app)) or  ((order.is_from_portal or order.is_from_app) and order.is_paid == True))
        if trans and report_type:
            if report_type == 'details_shipped':
                trans = trans.filtered(lambda t: (t.fleet_trip_id and t.fleet_trip_id.trip_type != 'local') or \
                                                 (t.trip_history_ids and \
                                                  not all(trip_type == 'local' for trip_type in
                                                          [trip_id.trip_type for trip_id in
                                                           t.trip_history_ids.mapped('fleet_trip_id')])))
            if report_type == 'details_not_shipped':
                trans = trans.filtered(lambda t: t.state != 'cancel' and (
                        not t.fleet_trip_id or (t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                 (not t.trip_history_ids or (t.trip_history_ids and \
                                                                             all(trip_type == 'local' for trip_type in
                                                                                 [trip_id.trip_type for trip_id in
                                                                                  t.trip_history_ids.mapped(
                                                                                      'fleet_trip_id')]))))
        if trans:
            mapped_date = trans.mapped('order_date')
            date_list = sorted(set(mapped_date), key=mapped_date.index)
            grouped_by_date = {}
            for date in date_list:
                order_lines = trans.filtered(lambda line: line.order_date.date()  == date.date())

                cash_pod_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 5)
                credit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 2)
                exhibit_sale_ids = order_lines.filtered(lambda order: order.bsg_cargo_sale_id.partner_types.id == 3)
                other_sale_ids = order_lines.filtered(
                    lambda order: order.bsg_cargo_sale_id.partner_types.id not in [2, 3, 5])

                cash_pod_rec, cash_pod_amt_without_tax = len(cash_pod_sale_ids), sum(
                    cash_pod_sale_ids.mapped('revenue_amount'))
                credit_rec, credit_amt_without_tax = len(credit_sale_ids), sum(
                    credit_sale_ids.mapped('revenue_amount'))
                exhibit_rec, exhibit_amt_without_tax = len(exhibit_sale_ids), sum(
                    exhibit_sale_ids.mapped('revenue_amount'))
                other_rec, other_amt_without_tax = len(other_sale_ids), sum(other_sale_ids.mapped('revenue_amount'))

                # accumulating total per date range
                cash_pod_total_rec += cash_pod_rec
                cash_pod_total_amt_without_tax += cash_pod_amt_without_tax

                credit_total_rec += credit_rec
                credit_total_amt_without_tax += credit_amt_without_tax

                exhibit_total_rec += exhibit_rec
                exhibit_total_amt_without_tax += exhibit_amt_without_tax

                other_total_rec += other_rec
                other_total_amt_without_tax += other_amt_without_tax

                date_key = en_arbic_weekday[date.strftime('%A', )] +  date.strftime(' %d ', )
                grouped_by_date[date_key] = {
                    'cash_pod_sale_ids': cash_pod_sale_ids,
                    'cash_pod_rec': cash_pod_rec,
                    'cash_pod_amt_without_tax': cash_pod_amt_without_tax,
                    'credit_sale_ids': credit_sale_ids,
                    'credit_rec': credit_rec,
                    'credit_amt_without_tax': credit_amt_without_tax,
                    'exhibit_sale_ids': exhibit_sale_ids,
                    'exhibit_rec': exhibit_rec,
                    'exhibit_amt_without_tax': exhibit_amt_without_tax,
                    'other_sale_ids': other_sale_ids,
                    'other_rec': other_rec,
                    'other_amt_without_tax': other_amt_without_tax,
                    'total_day_no_cars': len(order_lines),
                    'total_day_revenue': sum(order_lines.mapped('revenue_amount'))
                }

            revenue_total_cars = len(trans)
            revenue_total_amount = sum(trans.mapped('revenue_amount'))

        else:
            raise ValidationError('No records found!')

        return {
            'doc_ids': docids,
            'doc_model': 'bsg_vehicle_cargo_sale',
            'form': en_arbic_weekday[form.strftime('%A', )] + form.strftime(', %d-%m-%Y', ),
            'to': en_arbic_weekday[to.strftime('%A', )] + to.strftime(', %d-%m-%Y', ),
            'cash_pod_total_rec': cash_pod_total_rec,
            'cash_pod_total_amt_without_tax': cash_pod_total_amt_without_tax,
            'credit_total_rec': credit_total_rec,
            'credit_total_amt_without_tax': credit_total_amt_without_tax,
            'exhibit_total_rec': exhibit_total_rec,
            'exhibit_total_amt_without_tax': exhibit_total_amt_without_tax,
            'other_total_rec': other_total_rec,
            'other_total_amt_without_tax': other_total_amt_without_tax,
            'grouped_by_date':grouped_by_date,
            'revenue_total_cars': revenue_total_cars,
            'revenue_total_amount': revenue_total_amount,
            'report_type': report_type

        }
