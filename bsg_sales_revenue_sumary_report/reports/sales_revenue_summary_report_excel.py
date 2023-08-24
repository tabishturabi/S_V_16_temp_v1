from odoo import models
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
import json
from num2words import num2words


class SalesRevenueReportExcel(models.AbstractModel):
    _name = 'report.bsg_sales_revenue_sumary_report.sales_report_xlsx'
    _inherit ='report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,shipment_type,payment_method,loc_from,bsg_cargo_sale_id,revenue_amount,loc_to,create_uid,car_make,company_id,year,customer_price_list,car_model FROM " + table_name + " where is_package = False;")
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(columns={0: 'so_line_id', 1: 'order_date', 2: 'so_shipment_type_id',3:'so_payment_method_id',4:'loc_from_id',5:'so_cargo_sale_id',6:'revenue_amount',7:'loc_to_id',8:'so_creator_id',9:'so_car_make_id',10:'so_company_id',11:'so_manufacture_year_id',12:'so_customer_price_list_id',13:'so_car_model_id'})
        
        company_frame_table = "res_company"
        self.env.cr.execute(
            "select id,name FROM " + company_frame_table + " ")
        result_company_frame = self._cr.fetchall()
        company_frame = pd.DataFrame(list(result_company_frame))
        company_frame = company_frame.rename(columns={0: 'company_id', 1: 'company_name'})
        bsg_cargo_lines = pd.merge(bsg_cargo_lines, company_frame, how='left', left_on='so_company_id',right_on='company_id')


        car_make_frame_table = "bsg_car_make"
        self.env.cr.execute(
            "select id,car_make_ar_name FROM " + car_make_frame_table + " ")
        result_car_make_frame = self._cr.fetchall()
        car_make_frame = pd.DataFrame(list(result_car_make_frame))
        car_make_frame = car_make_frame.rename(columns={0: 'car_make_id', 1: 'car_make_name'})


        car_config_frame_table = "bsg_car_config"
        self.env.cr.execute(
            "select id,car_maker FROM " + car_config_frame_table + " ")
        result_car_config_frame = self._cr.fetchall()
        car_config_frame = pd.DataFrame(list(result_car_config_frame))
        car_config_frame = car_config_frame.rename(columns={0: 'car_config_id', 1: 'config_car_make_id'})
        car_config_frame = pd.merge(car_config_frame,car_make_frame,how='left',left_on='config_car_make_id',
                                   right_on='car_make_id')
        
        bsg_cargo_lines = pd.merge(bsg_cargo_lines, car_config_frame, how='left', left_on='so_car_make_id',
                                   right_on='car_config_id')

        carconfiglines_frame_table = "bsg_car_line"
        self.env.cr.execute("select id,car_config_id,car_model,car_size FROM " + carconfiglines_frame_table + " ")
        result_carconfiglines_frame = self._cr.fetchall()
        carconfiglines_frame = pd.DataFrame(list(result_carconfiglines_frame))
        carconfiglines_frame = carconfiglines_frame.rename(
            columns={0: 'car_configline_id', 1: 'car_configrelated_id', 2: 'car_modelline_id', 3: 'car_sizeline_id'})

        bsg_cargo_lines = pd.merge(bsg_cargo_lines, carconfiglines_frame, how='left', left_on=['so_car_make_id', 'so_car_model_id'],
                                   right_on=['car_configrelated_id', 'car_modelline_id'])

        car_size_frame_table = "bsg_car_size"
        self.env.cr.execute(
            "select id,car_size_name FROM " + car_size_frame_table + " ")
        result_car_size_frame = self._cr.fetchall()
        car_size_frame = pd.DataFrame(list(result_car_size_frame))
        car_size_frame = car_size_frame.rename(columns={0: 'car_size_id', 1: 'car_size_name'})
        bsg_cargo_lines = pd.merge(bsg_cargo_lines, car_size_frame, how='left', left_on='car_sizeline_id',
                                   right_on='car_size_id')


        manufacture_year_frame_table = "bsg_car_year"
        self.env.cr.execute(
            "select id,car_year_name FROM " + manufacture_year_frame_table + " ")
        result_manufacture_year_frame = self._cr.fetchall()
        manufacture_year_frame = pd.DataFrame(list(result_manufacture_year_frame))
        manufacture_year_frame = manufacture_year_frame.rename(columns={0: 'manufacture_year_id', 1: 'manufacture_year_name'})
        bsg_cargo_lines = pd.merge(bsg_cargo_lines, manufacture_year_frame, how='left', left_on='so_manufacture_year_id',
                                   right_on='manufacture_year_id')

        shipment_type_frame_table = "bsg_car_shipment_type"
        self.env.cr.execute(
            "select id,car_shipment_name FROM " + shipment_type_frame_table + " ")
        result_shipment_type_frame = self._cr.fetchall()
        shipment_type_frame = pd.DataFrame(list(result_shipment_type_frame))
        shipment_type_frame = shipment_type_frame.rename(
            columns={0: 'shipment_type_id', 1: 'shipment_type_name'})
        bsg_cargo_lines = pd.merge(bsg_cargo_lines, shipment_type_frame, how='left',left_on='so_shipment_type_id',right_on='shipment_type_id')

        pricelist_frame_table = "product_pricelist"
        self.env.cr.execute(
            "select id,name FROM " + pricelist_frame_table + " ")
        result_pricelist_frame = self._cr.fetchall()
        pricelist_frame = pd.DataFrame(list(result_pricelist_frame))
        pricelist_frame = pricelist_frame.rename(
            columns={0: 'pricelist_id', 1: 'pricelist_name'})
        bsg_cargo_lines = pd.merge(bsg_cargo_lines, pricelist_frame, how='left', left_on='so_customer_price_list_id',
                                   right_on='pricelist_id')

        loc_from_frame_table = "bsg_route_waypoints"
        self.env.cr.execute(
            "select id,loc_branch_id FROM " + loc_from_frame_table + " ")
        result_loc_from_frame = self._cr.fetchall()
        loc_from_frame = pd.DataFrame(list(result_loc_from_frame))
        loc_from_frame = loc_from_frame.rename(columns={0: 'bsg_loc_from_id', 1: 'loc_from_branch_id'})


        branches_frame_table = "bsg_branches_bsg_branches"
        self.env.cr.execute("select id,branch_ar_name,branch_classifcation,region FROM " + branches_frame_table + " ")
        result_branches_frame = self._cr.fetchall()
        branches_frame = pd.DataFrame(list(result_branches_frame))
        branches_frame = branches_frame.rename(columns={0: 'bsg_branch_id', 1: 'bsg_branch_name',2:'branch_cls_id',3:'branch_region_id'})

        branches_cls_frame_table = "bsg_branch_classification"
        self.env.cr.execute("select id,bsg_branch_cls_name FROM " + branches_cls_frame_table + " ")
        result_branches_cls_frame = self._cr.fetchall()
        branches_cls_frame = pd.DataFrame(list(result_branches_cls_frame))
        branches_cls_frame = branches_cls_frame.rename(
            columns={0: 'bsg_branch_cls_id', 1: 'bsg_branch_cls_name'})
        branches_frame = pd.merge(branches_frame, branches_cls_frame, how='left', left_on='branch_cls_id',
                                   right_on='bsg_branch_cls_id')
        region_frame_table = "region_config"
        self.env.cr.execute("select id,bsg_region_name FROM " + region_frame_table + " ")
        result_region_frame = self._cr.fetchall()
        region_frame = pd.DataFrame(list(result_region_frame))
        region_frame = region_frame.rename(
            columns={0: 'region_id', 1: 'bsg_region_name'})
        branches_frame = pd.merge(branches_frame, region_frame, how='left', left_on='branch_region_id',
                                  right_on='region_id')
        loc_from_frame = pd.merge(loc_from_frame, branches_frame, how='left', left_on='loc_from_branch_id',
                                  right_on='bsg_branch_id')
        bsg_cargo_lines = pd.merge(bsg_cargo_lines, loc_from_frame, how='left', left_on='loc_from_id',
                                  right_on='bsg_loc_from_id')

        loc_to_frame_table = "bsg_route_waypoints"
        self.env.cr.execute(
            "select id,loc_branch_id FROM " + loc_to_frame_table + " ")
        result_loc_to_frame = self._cr.fetchall()
        loc_to_frame = pd.DataFrame(list(result_loc_to_frame))
        loc_to_frame = loc_to_frame.rename(columns={0:'bsg_loc_to_id',1:'loc_to_branch_id'})
        bsg_cargo_lines = pd.merge(bsg_cargo_lines,loc_to_frame, how='left', left_on='loc_to_id',
                                   right_on='bsg_loc_to_id')

        payment_method_frame_table = "cargo_payment_method"
        self.env.cr.execute("select id,payment_method_name FROM " + payment_method_frame_table + " ")
        result_payment_method_frame = self._cr.fetchall()
        payment_method_frame = pd.DataFrame(list(result_payment_method_frame))
        payment_method_frame = payment_method_frame.rename(
            columns={0: 'payment_method_id', 1: 'payment_method_name'})
        bsg_cargo_lines = pd.merge(bsg_cargo_lines,payment_method_frame, how='left', left_on='so_payment_method_id',
                                   right_on='payment_method_id')

        cargo_sale_frame_table = "bsg_vehicle_cargo_sale"
        self.env.cr.execute("select id,partner_types,shipment_type,cargo_sale_type FROM " + cargo_sale_frame_table + " ")
        result_cargo_sale_frame = self._cr.fetchall()
        cargo_sale_frame = pd.DataFrame(list(result_cargo_sale_frame))
        cargo_sale_frame = cargo_sale_frame.rename(
            columns={0: 'cargo_sale_id', 1: 'cargo_sale_partner_type_id',2:'agreement_type',3:'cargo_sale_type'})

        partner_type_frame_table = "partner_type"
        self.env.cr.execute("select id,name FROM " + partner_type_frame_table + " ")
        result_partner_type_frame = self._cr.fetchall()
        partner_type_frame = pd.DataFrame(list(result_partner_type_frame))
        partner_type_frame = partner_type_frame.rename(
            columns={0:'partner_type_id', 1:'partner_type_name'})

        cargo_sale_frame = pd.merge(cargo_sale_frame,partner_type_frame, how='left', left_on='cargo_sale_partner_type_id',
                                   right_on='partner_type_id')

        bsg_cargo_lines = pd.merge(bsg_cargo_lines, cargo_sale_frame, how='left', left_on='so_cargo_sale_id',
                                   right_on='cargo_sale_id')
        if docs.region_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['region_id'].isin(docs.region_ids.ids))]
        if docs.from_branch_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['loc_from_branch_id'].isin(docs.from_branch_ids.ids))]
        if docs.to_branch_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['loc_to_branch_id'].isin(docs.to_branch_ids.ids))]
        if docs.branch_cls_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['bsg_branch_cls_id'].isin(docs.branch_cls_ids.ids))]
        if docs.company_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['so_company_id'].isin(docs.company_ids.ids))]
        if docs.partner_type_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['partner_type_id'].isin(docs.partner_type_ids.ids))]
        if docs.shipment_type_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['so_shipment_type_id'].isin(docs.shipment_type_ids.ids))]
        if docs.create_user_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['so_creator_id'].isin(docs.create_user_ids.ids))]
        if docs.payment_method_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['so_payment_method_id'].isin(docs.payment_method_ids.ids))]
        if docs.car_size_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['car_size_id'].isin(docs.car_size_ids.ids))]
        if docs.car_maker_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['so_car_make_id'].isin(docs.car_maker_ids.ids))]
        if docs.manufacture_year_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['so_manufacture_year_id'].isin(docs.manufacture_year_ids.ids))]
        if docs.pricelist_ids:
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['so_customer_price_list_id'].isin(docs.pricelist_ids.ids))]
        if docs.sale_type == 'local':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['cargo_sale_type']=='local')]
        if docs.sale_type == 'international':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['cargo_sale_type']=='international')]
        if docs.agreement_type == 'round_trip':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['agreement_type']=='return')]
        if docs.agreement_type == 'one_way':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['agreement_type']=='oneway')]
        # if docs.shipment_status:
        #     bsg_cargo_lines = bsg_cargo_lines.loc[
        #         (bsg_cargo_lines['so_customer_price_list_id'].isin(docs.pricelist_ids.ids))]
        if docs.include_salath:
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['is_satah']==True)]
        if docs.order_date_condition == 'is_equal_to':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] == (docs.order_date))]
        if docs.order_date_condition == 'is_not_equal_to':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] != (docs.order_date))]
        if docs.order_date_condition == 'is_after':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] > (docs.order_date))]
        if docs.order_date_condition == 'is_before':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] < (docs.order_date))]
        if docs.order_date_condition == 'is_after_or_equal_to':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] >= (docs.order_date))]
        if docs.order_date_condition == 'is_before_or_equal_to':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] <= (docs.order_date))]
        if docs.order_date_condition == 'is_between':
            bsg_cargo_lines = bsg_cargo_lines.loc[
                (bsg_cargo_lines['order_date'] >= (docs.date_from)) & (
                            bsg_cargo_lines['order_date'] <= (docs.date_to))]
        if docs.order_date_condition == 'is_set':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'].notnull())]
        if docs.order_date_condition == 'is_not_set':
            bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'].isnull())]

        bsg_cargo_lines = bsg_cargo_lines.fillna(0)
        bsg_cargo_lines=bsg_cargo_lines.sort_values(by=['payment_method_id'])
        payment_method_dict = OrderedDict.fromkeys(
            (value['payment_method_name'] for index,value in bsg_cargo_lines.iterrows()),{'no_of_cars': 0,'revenue_amount': 0})
        x=0
        for key in list(payment_method_dict.keys()):
            if key == x:
                del payment_method_dict[key]
        main_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '10',
        })
        main_heading2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#999999',
            'font_size': '12',
        })
        main_heading3 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#ffffff',
            'font_size': '13',
        })
        sheet = workbook.add_worksheet('Employee Salary Information Report')
        sheet.set_column('A:Z',15)
        row = 0
        col = 0
        if docs.grouping_by == 'all':
            self.env.ref('bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Reports"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report', main_heading3)
            row = 3
            index=0
            cols_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
            sheet.write(cols_list[index]+str(row), 'الفروع', main_heading2)
            index += 1
            sheet.write(cols_list[index]+str(row), 'المناطق', main_heading2)
            index += 1
            sheet.write(cols_list[index]+str(row), 'فئة الفروع', main_heading2)
            index += 1
            sheet.write(cols_list[index]+str(row), 'نوع الشريك', main_heading2)
            index += 1
            sheet.write(cols_list[index]+str(row), 'نوع الاتفاقية', main_heading2)
            index += 1
            sheet.write(cols_list[index]+str(row), 'نوع الشحن', main_heading2)
            index += 1
            sheet.write(cols_list[index]+str(row), 'تاريخ الشحن', main_heading2)
            index += 1
            for pm_key,pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index]+str(row)+':'+cols_list[index+1]+str(row), str(pm_key), main_heading2)
                index += 2
            sheet.merge_range(cols_list[index]+str(row)+':'+cols_list[index+1]+str(row), 'الاجمالي العام', main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات غير المرحلة',main_heading2)
            index += 2
            pm_index = index
            index = 0
            row += 1
            sheet.merge_range(cols_list[index] + str(row)+':'+cols_list[index] + str(row+1), 'Branches', main_heading2)
            index += 1
            sheet.merge_range(cols_list[index] + str(row)+':'+cols_list[index] + str(row+1), 'Branches Regions', main_heading2)
            index += 1
            sheet.merge_range(cols_list[index] + str(row)+':'+cols_list[index] + str(row+1), 'Branches Classification', main_heading2)
            index += 1
            sheet.merge_range(cols_list[index] + str(row)+':'+cols_list[index] + str(row+1), 'Partner Type', main_heading2)
            index += 1
            sheet.merge_range(cols_list[index] + str(row)+':'+cols_list[index] + str(row+1), 'Agreement Type', main_heading2)
            index += 1
            sheet.merge_range(cols_list[index] + str(row)+':'+cols_list[index] + str(row+1), 'Shipment Type', main_heading2)
            index += 1
            sheet.merge_range(cols_list[index] + str(row)+':'+cols_list[index] + str(row+1), 'Order Date', main_heading2)
            index += 1
            nl_index = index
            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1
            index = nl_index
            row+=1
            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1
            row+=1
            col=0
            bsg_cargo_lines_grouped_all = bsg_cargo_lines.groupby(['bsg_branch_name','bsg_region_name','bsg_branch_cls_name','partner_type_name','agreement_type','shipment_type_name','order_date'])
            grouped_by_all = {}
            for key_all, df_all in bsg_cargo_lines_grouped_all:
                if key_all:
                    payment_method_df_groupby = df_all.groupby(['payment_method_name'])
                    no_of_cars_total = 0
                    revenue_total = 0
                    no_of_cars_shipped=0
                    revenue_shipped = 0
                    no_of_cars_unshipped = 0
                    revenue_unshipped = 0
                    grouped_by_payment_method=OrderedDict.fromkeys((index for index, value in payment_method_dict.items()),{'no_of_cars': 0, 'revenue_amount': 0})
                    # print('...........key_all............',key_all)
                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                    for key_pm,dataframe_pm in payment_method_df_groupby:
                        no_of_cars = 0
                        revenue_amount = 0
                        if key_pm:
                            # print('..........key_pm..........',key_pm)
                            for key,value in dataframe_pm.iterrows():
                                t = self.env['bsg_vehicle_cargo_sale_line'].search([('id','=',int(value['so_line_id']))],limit=1)
                                if t.state != 'cancel' and (not t.fleet_trip_id or (t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                                           (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                       all(trip_type == 'local' for trip_type in [trip_id.trip_type for trip_id in t.trip_history_ids.mapped('fleet_trip_id')]))):
                                    no_of_cars_unshipped += 1
                                    revenue_unshipped += t.revenue_amount
                                else:
                                    no_of_cars_shipped += 1
                                    revenue_shipped += t.revenue_amount
                                no_of_cars += 1
                                revenue_amount += value['revenue_amount']
                            grouped_by_payment_method[key_pm] = {
                                'no_of_cars': no_of_cars,
                                'revenue_amount': revenue_amount
                            }
                            no_of_cars_total += no_of_cars
                            revenue_total += revenue_amount
                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                    grouped_by_all[key_all] = {
                        'grouped_by_payment_method': grouped_by_payment_method,
                        'no_of_cars_total': no_of_cars_total,
                        'revenue_total': revenue_total,
                        'no_of_cars_shipped':no_of_cars_shipped,
                        'revenue_shipped': revenue_shipped,
                        'no_of_cars_unshipped': no_of_cars_unshipped,
                        'revenue_unshipped': revenue_unshipped
                    }
            no_of_cars_shipped_total = 0
            revenue_shipped_total = 0
            no_of_cars_unshipped_total = 0
            revenue_unshipped_total = 0
            payment_method_grand_sum_dict = OrderedDict.fromkeys((index for index, value in payment_method_dict.items()),
                                                             {'no_of_cars': 0, 'revenue_amount': 0})
            payment_method_grand_sum_dict=json.loads(json.dumps(payment_method_grand_sum_dict))
            for all_key,all_value in grouped_by_all.items():
                if all_key[0]:
                    sheet.write_string(row, col,str(all_key[0]), main_heading)
                if all_key[1]:
                    sheet.write_string(row, col+1,str(all_key[1]), main_heading)
                if all_key[2]:
                    sheet.write_string(row, col+2,str(all_key[2]), main_heading)
                if all_key[3]:
                    sheet.write_string(row, col+3,str(all_key[3]), main_heading)
                if all_key[4]:
                    sheet.write_string(row, col+4,str(all_key[4]), main_heading)
                if all_key[5]:
                    sheet.write_string(row, col+5,str(all_key[5]), main_heading)
                if all_key[6]:
                    sheet.write_string(row, col+6, str(all_key[6]), main_heading)
                col = 7
                for pm_key, pm_value in all_value['grouped_by_payment_method'].items():
                    sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                    col += 1
                    sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                    col += 1
                    payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                    payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value['revenue_amount']
                sheet.write_number(row, col,all_value['no_of_cars_total'], main_heading)
                col += 1
                sheet.write_number(row, col, all_value['revenue_total'], main_heading)
                col += 1
                sheet.write_number(row, col, all_value['no_of_cars_shipped'], main_heading)
                no_of_cars_shipped_total+=all_value['no_of_cars_shipped']
                col += 1
                sheet.write_number(row, col, all_value['revenue_shipped'], main_heading)
                revenue_shipped_total += all_value['revenue_shipped']
                col += 1
                sheet.write_number(row, col, all_value['no_of_cars_unshipped'], main_heading)
                no_of_cars_unshipped_total += all_value['no_of_cars_unshipped']
                col += 1
                sheet.write_number(row, col, all_value['revenue_unshipped'], main_heading)
                revenue_unshipped_total += all_value['revenue_unshipped']
                col = 0
                row+=1
            print('...........payment_method_grand_sum_dict..........',payment_method_grand_sum_dict)

            sheet.write(row,col,'الإجمالي الكلي', main_heading2)
            col += 7
            car_nums_grand_sum = 0
            revenue_grand_sum = 0
            for pm_key,pm_value in payment_method_grand_sum_dict.items():
                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                car_nums_grand_sum += pm_value['no_of_cars']
                col += 1
                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                revenue_grand_sum += pm_value['revenue_amount']
                col += 1
            sheet.write_number(row, col, car_nums_grand_sum,main_heading)
            col += 1
            sheet.write_number(row, col, revenue_grand_sum,main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
            col += 1
        if docs.grouping_by == 'by_branches_cls':

            self.env.ref('bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Rep Group By Branches Classification"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب فئات الفروع', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Rep Group By Branches Classification', main_heading3)

            row = 3

            index=0

            cols_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

            sheet.write(cols_list[index]+str(row), 'فئة الفروع', main_heading2)

            index += 1

            for pm_key,pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index]+str(row)+':'+cols_list[index+1]+str(row), str(pm_key), main_heading2)
                index += 2

            sheet.merge_range(cols_list[index]+str(row)+':'+cols_list[index+1]+str(row), 'الاجمالي العام', main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),'السيارات غير المرحلة', main_heading2)

            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row)+':'+cols_list[index] + str(row+1), 'Branches Classification', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row+=1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row+=1

            col=0

            bsg_cargo_lines_grouped_branch_cls = bsg_cargo_lines.groupby(['bsg_branch_cls_name'])

            grouped_by_branch_cls={}

            for key_branch_cls,df_branch_cls in bsg_cargo_lines_grouped_branch_cls:
                if key_branch_cls:
                    payment_method_df_groupby = df_branch_cls.groupby(['payment_method_name'])
                    no_of_cars_total = 0
                    revenue_total = 0
                    no_of_cars_shipped = 0
                    revenue_shipped = 0
                    no_of_cars_unshipped = 0
                    revenue_unshipped = 0
                    grouped_by_payment_method=OrderedDict.fromkeys((index for index, value in payment_method_dict.items()),{'no_of_cars': 0, 'revenue_amount': 0})
                    # print('...........key_all............',key_all)
                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                    for key_pm,dataframe_pm in payment_method_df_groupby:
                        no_of_cars = 0
                        revenue_amount = 0
                        if key_pm:
                            # print('..........key_pm..........',key_pm)
                            for key,value in dataframe_pm.iterrows():
                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                    all(trip_type == 'local' for trip_type in
                                                                        [trip_id.trip_type for trip_id in
                                                                         t.trip_history_ids.mapped('fleet_trip_id')]))):
                                    no_of_cars_unshipped += 1
                                    revenue_unshipped += t.revenue_amount
                                else:
                                    no_of_cars_shipped += 1
                                    revenue_shipped += t.revenue_amount
                                no_of_cars += 1
                                revenue_amount += value['revenue_amount']
                            grouped_by_payment_method[key_pm] = {
                                'no_of_cars': no_of_cars,
                                'revenue_amount': revenue_amount
                            }
                            no_of_cars_total += no_of_cars
                            revenue_total += revenue_amount
                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                    grouped_by_branch_cls[key_branch_cls] = {
                        'grouped_by_payment_method': grouped_by_payment_method,
                        'no_of_cars_total': no_of_cars_total,
                        'revenue_total': revenue_total,
                        'no_of_cars_shipped': no_of_cars_shipped,
                        'revenue_shipped': revenue_shipped,
                        'no_of_cars_unshipped': no_of_cars_unshipped,
                        'revenue_unshipped': revenue_unshipped
                    }
            no_of_cars_shipped_total = 0
            revenue_shipped_total = 0
            no_of_cars_unshipped_total = 0
            revenue_unshipped_total = 0
            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                (index for index, value in payment_method_dict.items()),
                {'no_of_cars': 0, 'revenue_amount': 0})
            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
            for bcls_key, bcls_value in grouped_by_branch_cls.items():
                if bcls_key:
                    sheet.write_string(row,col,str(bcls_key), main_heading)
                    col = 1
                    for pm_key, pm_value in bcls_value['grouped_by_payment_method'].items():
                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                        col += 1
                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                        col += 1
                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value['revenue_amount']
                    sheet.write_number(row, col, bcls_value['no_of_cars_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, bcls_value['revenue_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, bcls_value['no_of_cars_shipped'], main_heading)
                    no_of_cars_shipped_total += bcls_value['no_of_cars_shipped']
                    col += 1
                    sheet.write_number(row, col, bcls_value['revenue_shipped'], main_heading)
                    revenue_shipped_total += bcls_value['revenue_shipped']
                    col += 1
                    sheet.write_number(row, col, bcls_value['no_of_cars_unshipped'], main_heading)
                    no_of_cars_unshipped_total += bcls_value['no_of_cars_unshipped']
                    col += 1
                    sheet.write_number(row, col, bcls_value['revenue_unshipped'], main_heading)
                    revenue_unshipped_total += bcls_value['revenue_unshipped']
                    col = 0
                    row += 1
            print('...........payment_method_grand_sum_dict..........', payment_method_grand_sum_dict)
            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
            col += 1
            car_nums_grand_sum = 0
            revenue_grand_sum = 0
            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                car_nums_grand_sum += pm_value['no_of_cars']
                col += 1
                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                revenue_grand_sum += pm_value['revenue_amount']
                col += 1
            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
            col += 1
        if docs.grouping_by == 'by_company':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Company"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب شركة', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Company', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'شركة', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Company', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_company = bsg_cargo_lines.groupby(['company_name'])

            grouped_by_company = {}

            for key_company, df_company in bsg_cargo_lines_grouped_company:
                if key_company:
                    payment_method_df_groupby = df_company.groupby(['payment_method_name'])
                    no_of_cars_total = 0
                    revenue_total = 0
                    no_of_cars_shipped = 0
                    revenue_shipped = 0
                    no_of_cars_unshipped = 0
                    revenue_unshipped = 0
                    grouped_by_payment_method = OrderedDict.fromkeys(
                        (index for index, value in payment_method_dict.items()), {'no_of_cars': 0, 'revenue_amount': 0})
                    # print('...........key_all............',key_all)
                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                    for key_pm, dataframe_pm in payment_method_df_groupby:
                        no_of_cars = 0
                        revenue_amount = 0
                        if key_pm:
                            # print('..........key_pm..........',key_pm)
                            for key, value in dataframe_pm.iterrows():
                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                    all(trip_type == 'local' for trip_type in
                                                                        [trip_id.trip_type for trip_id in
                                                                         t.trip_history_ids.mapped('fleet_trip_id')]))):
                                    no_of_cars_unshipped += 1
                                    revenue_unshipped += t.revenue_amount
                                else:
                                    no_of_cars_shipped += 1
                                    revenue_shipped += t.revenue_amount
                                no_of_cars += 1
                                revenue_amount += value['revenue_amount']
                            grouped_by_payment_method[key_pm] = {
                                'no_of_cars': no_of_cars,
                                'revenue_amount': revenue_amount
                            }
                            no_of_cars_total += no_of_cars
                            revenue_total += revenue_amount
                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                    grouped_by_company[key_company] = {
                        'grouped_by_payment_method': grouped_by_payment_method,
                        'no_of_cars_total': no_of_cars_total,
                        'revenue_total': revenue_total,
                        'no_of_cars_shipped': no_of_cars_shipped,
                        'revenue_shipped': revenue_shipped,
                        'no_of_cars_unshipped': no_of_cars_unshipped,
                        'revenue_unshipped': revenue_unshipped
                    }
            no_of_cars_shipped_total = 0
            revenue_shipped_total = 0
            no_of_cars_unshipped_total = 0
            revenue_unshipped_total = 0
            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                (index for index, value in payment_method_dict.items()),
                {'no_of_cars': 0, 'revenue_amount': 0})
            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
            for compnay_key, company_value in grouped_by_company.items():
                if compnay_key:
                    sheet.write_string(row, col, str(compnay_key), main_heading)
                    col = 1
                    for pm_key, pm_value in company_value['grouped_by_payment_method'].items():
                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                        col += 1
                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                        col += 1
                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value['revenue_amount']
                    sheet.write_number(row, col, company_value['no_of_cars_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, company_value['revenue_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, company_value['no_of_cars_shipped'], main_heading)
                    no_of_cars_shipped_total += company_value['no_of_cars_shipped']
                    col += 1
                    sheet.write_number(row, col, company_value['revenue_shipped'], main_heading)
                    revenue_shipped_total += company_value['revenue_shipped']
                    col += 1
                    sheet.write_number(row, col, company_value['no_of_cars_unshipped'], main_heading)
                    no_of_cars_unshipped_total += company_value['no_of_cars_unshipped']
                    col += 1
                    sheet.write_number(row, col, company_value['revenue_unshipped'], main_heading)
                    revenue_unshipped_total += company_value['revenue_unshipped']
                    col = 0
                    row += 1
            print('...........payment_method_grand_sum_dict..........', payment_method_grand_sum_dict)
            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
            col += 1
            car_nums_grand_sum = 0
            revenue_grand_sum = 0
            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                car_nums_grand_sum += pm_value['no_of_cars']
                col += 1
                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                revenue_grand_sum += pm_value['revenue_amount']
                col += 1
            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
            col += 1
        if docs.grouping_by == 'by_region':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Regions"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب  المناطق', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Regions', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), ' المناطق', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Region', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_region = bsg_cargo_lines.groupby(['bsg_region_name'])

            grouped_by_region = {}

            for key_region, df_region in bsg_cargo_lines_grouped_region:
                if key_region:
                    payment_method_df_groupby = df_region.groupby(['payment_method_name'])
                    no_of_cars_total = 0
                    revenue_total = 0
                    no_of_cars_shipped = 0
                    revenue_shipped = 0
                    no_of_cars_unshipped = 0
                    revenue_unshipped = 0
                    grouped_by_payment_method = OrderedDict.fromkeys(
                        (index for index, value in payment_method_dict.items()), {'no_of_cars': 0, 'revenue_amount': 0})
                    # print('...........key_all............',key_all)
                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                    for key_pm, dataframe_pm in payment_method_df_groupby:
                        no_of_cars = 0
                        revenue_amount = 0
                        if key_pm:
                            # print('..........key_pm..........',key_pm)
                            for key, value in dataframe_pm.iterrows():
                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                    all(trip_type == 'local' for trip_type in
                                                                        [trip_id.trip_type for trip_id in
                                                                         t.trip_history_ids.mapped('fleet_trip_id')]))):
                                    no_of_cars_unshipped += 1
                                    revenue_unshipped += t.revenue_amount
                                else:
                                    no_of_cars_shipped += 1
                                    revenue_shipped += t.revenue_amount
                                no_of_cars += 1
                                revenue_amount += value['revenue_amount']
                            grouped_by_payment_method[key_pm] = {
                                'no_of_cars': no_of_cars,
                                'revenue_amount': revenue_amount
                            }
                            no_of_cars_total += no_of_cars
                            revenue_total += revenue_amount
                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                    grouped_by_region[key_region] = {
                        'grouped_by_payment_method': grouped_by_payment_method,
                        'no_of_cars_total': no_of_cars_total,
                        'revenue_total': revenue_total,
                        'no_of_cars_shipped': no_of_cars_shipped,
                        'revenue_shipped': revenue_shipped,
                        'no_of_cars_unshipped': no_of_cars_unshipped,
                        'revenue_unshipped': revenue_unshipped
                    }
            no_of_cars_shipped_total = 0
            revenue_shipped_total = 0
            no_of_cars_unshipped_total = 0
            revenue_unshipped_total = 0
            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                (index for index, value in payment_method_dict.items()),
                {'no_of_cars': 0, 'revenue_amount': 0})
            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
            for region_key, region_value in grouped_by_region.items():
                if region_key:
                    sheet.write_string(row, col, str(region_key), main_heading)
                    col = 1
                    for pm_key, pm_value in region_value['grouped_by_payment_method'].items():
                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                        col += 1
                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                        col += 1
                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value['revenue_amount']
                    sheet.write_number(row, col, region_value['no_of_cars_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, region_value['revenue_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, region_value['no_of_cars_shipped'], main_heading)
                    no_of_cars_shipped_total += region_value['no_of_cars_shipped']
                    col += 1
                    sheet.write_number(row, col, region_value['revenue_shipped'], main_heading)
                    revenue_shipped_total += region_value['revenue_shipped']
                    col += 1
                    sheet.write_number(row, col, region_value['no_of_cars_unshipped'], main_heading)
                    no_of_cars_unshipped_total += region_value['no_of_cars_unshipped']
                    col += 1
                    sheet.write_number(row, col, region_value['revenue_unshipped'], main_heading)
                    revenue_unshipped_total += region_value['revenue_unshipped']
                    col = 0
                    row += 1
            print('...........payment_method_grand_sum_dict..........', payment_method_grand_sum_dict)
            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
            col += 1
            car_nums_grand_sum = 0
            revenue_grand_sum = 0
            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                car_nums_grand_sum += pm_value['no_of_cars']
                col += 1
                sheet.write_number(row, col,pm_value['revenue_amount'], main_heading)
                revenue_grand_sum += pm_value['revenue_amount']
                col += 1
            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
            col += 1
        if docs.grouping_by == 'by_branch':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Branch"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب  الفروع', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Branch', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), ' الفروع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branch', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_branch = bsg_cargo_lines.groupby(['bsg_branch_name'])

            grouped_by_branch = {}

            for key_branch, df_branch in bsg_cargo_lines_grouped_branch:
                if key_branch:
                    payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                    no_of_cars_total = 0
                    revenue_total = 0
                    no_of_cars_shipped = 0
                    revenue_shipped = 0
                    no_of_cars_unshipped = 0
                    revenue_unshipped = 0
                    grouped_by_payment_method = OrderedDict.fromkeys(
                        (index for index, value in payment_method_dict.items()), {'no_of_cars': 0, 'revenue_amount': 0})
                    # print('...........key_all............',key_all)
                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                    for key_pm, dataframe_pm in payment_method_df_groupby:
                        no_of_cars = 0
                        revenue_amount = 0
                        if key_pm:
                            # print('..........key_pm..........',key_pm)
                            for key, value in dataframe_pm.iterrows():
                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                    all(trip_type == 'local' for trip_type in
                                                                        [trip_id.trip_type for trip_id in
                                                                         t.trip_history_ids.mapped('fleet_trip_id')]))):
                                    no_of_cars_unshipped += 1
                                    revenue_unshipped += t.revenue_amount
                                else:
                                    no_of_cars_shipped += 1
                                    revenue_shipped += t.revenue_amount
                                no_of_cars += 1
                                revenue_amount += value['revenue_amount']
                            grouped_by_payment_method[key_pm] = {
                                'no_of_cars': no_of_cars,
                                'revenue_amount': revenue_amount
                            }
                            no_of_cars_total += no_of_cars
                            revenue_total += revenue_amount
                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                    grouped_by_branch[key_branch] = {
                        'grouped_by_payment_method': grouped_by_payment_method,
                        'no_of_cars_total': no_of_cars_total,
                        'revenue_total': revenue_total,
                        'no_of_cars_shipped': no_of_cars_shipped,
                        'revenue_shipped': revenue_shipped,
                        'no_of_cars_unshipped': no_of_cars_unshipped,
                        'revenue_unshipped': revenue_unshipped
                    }
            no_of_cars_shipped_total = 0
            revenue_shipped_total = 0
            no_of_cars_unshipped_total = 0
            revenue_unshipped_total = 0
            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                (index for index, value in payment_method_dict.items()),
                {'no_of_cars': 0, 'revenue_amount': 0})
            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
            for branch_key, branch_value in grouped_by_branch.items():
                if branch_key:
                    sheet.write_string(row, col, str(branch_key), main_heading)
                    col = 1
                    for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                        col += 1
                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                        col += 1
                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value['revenue_amount']
                    sheet.write_number(row, col, branch_value['no_of_cars_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col,branch_value['revenue_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                    no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                    col += 1
                    sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                    revenue_shipped_total += branch_value['revenue_shipped']
                    col += 1
                    sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                    no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                    col += 1
                    sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                    revenue_unshipped_total += branch_value['revenue_unshipped']
                    col = 0
                    row += 1
            print('...........payment_method_grand_sum_dict..........', payment_method_grand_sum_dict)
            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
            col += 1
            car_nums_grand_sum = 0
            revenue_grand_sum = 0
            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                car_nums_grand_sum += pm_value['no_of_cars']
                col += 1
                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                revenue_grand_sum += pm_value['revenue_amount']
                col += 1
            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
            col += 1
        if docs.grouping_by == 'by_create_by':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Created By"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب  المستخدم', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Created By', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'المستخدم', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Created By', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_creator = bsg_cargo_lines.groupby(['so_creator_id'])

            grouped_by_creator = {}

            for key_creator, df_creator in bsg_cargo_lines_grouped_creator:
                if key_creator:
                    payment_method_df_groupby = df_creator.groupby(['payment_method_name'])
                    no_of_cars_total = 0
                    revenue_total = 0
                    no_of_cars_shipped = 0
                    revenue_shipped = 0
                    no_of_cars_unshipped = 0
                    revenue_unshipped = 0
                    grouped_by_payment_method = OrderedDict.fromkeys(
                        (index for index, value in payment_method_dict.items()), {'no_of_cars': 0, 'revenue_amount': 0})
                    # print('...........key_all............',key_all)
                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                    for key_pm, dataframe_pm in payment_method_df_groupby:
                        no_of_cars = 0
                        revenue_amount = 0
                        if key_pm:
                            # print('..........key_pm..........',key_pm)
                            for key, value in dataframe_pm.iterrows():
                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                    all(trip_type == 'local' for trip_type in
                                                                        [trip_id.trip_type for trip_id in
                                                                         t.trip_history_ids.mapped('fleet_trip_id')]))):
                                    no_of_cars_unshipped += 1
                                    revenue_unshipped += t.revenue_amount
                                else:
                                    no_of_cars_shipped += 1
                                    revenue_shipped += t.revenue_amount
                                no_of_cars += 1
                                revenue_amount += value['revenue_amount']
                            grouped_by_payment_method[key_pm] = {
                                'no_of_cars': no_of_cars,
                                'revenue_amount': revenue_amount
                            }
                            no_of_cars_total += no_of_cars
                            revenue_total += revenue_amount
                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                    user_id = self.env['res.users'].search([('id','=',int(key_creator))])
                    creator_name = user_id.name
                    grouped_by_creator[creator_name] = {
                        'grouped_by_payment_method': grouped_by_payment_method,
                        'no_of_cars_total': no_of_cars_total,
                        'revenue_total': revenue_total,
                        'no_of_cars_shipped': no_of_cars_shipped,
                        'revenue_shipped': revenue_shipped,
                        'no_of_cars_unshipped': no_of_cars_unshipped,
                        'revenue_unshipped': revenue_unshipped
                    }
            no_of_cars_shipped_total = 0
            revenue_shipped_total = 0
            no_of_cars_unshipped_total = 0
            revenue_unshipped_total = 0
            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                (index for index, value in payment_method_dict.items()),
                {'no_of_cars': 0, 'revenue_amount': 0})
            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
            for creator_key, creator_value in grouped_by_creator.items():
                if creator_key:
                    sheet.write_string(row, col, str(creator_key), main_heading)
                    col = 1
                    for pm_key, pm_value in creator_value['grouped_by_payment_method'].items():
                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                        col += 1
                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                        col += 1
                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value['revenue_amount']
                    sheet.write_number(row, col, creator_value['no_of_cars_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, creator_value['revenue_total'], main_heading)
                    col += 1
                    sheet.write_number(row, col, creator_value['no_of_cars_shipped'], main_heading)
                    no_of_cars_shipped_total += creator_value['no_of_cars_shipped']
                    col += 1
                    sheet.write_number(row, col, creator_value['revenue_shipped'], main_heading)
                    revenue_shipped_total += creator_value['revenue_shipped']
                    col += 1
                    sheet.write_number(row, col, creator_value['no_of_cars_unshipped'], main_heading)
                    no_of_cars_unshipped_total += creator_value['no_of_cars_unshipped']
                    col += 1
                    sheet.write_number(row, col, creator_value['revenue_unshipped'], main_heading)
                    revenue_unshipped_total += creator_value['revenue_unshipped']
                    col = 0
                    row += 1
            print('...........payment_method_grand_sum_dict..........', payment_method_grand_sum_dict)
            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
            col += 1
            car_nums_grand_sum = 0
            revenue_grand_sum = 0
            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                car_nums_grand_sum += pm_value['no_of_cars']
                col += 1
                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                revenue_grand_sum += pm_value['revenue_amount']
                col += 1
            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_grand_sum, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_shipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
            col += 1
            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
            col += 1
        if docs.grouping_by == 'by_partner_type':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Partner Type"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب نوع الشريك', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Partner Type', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'الفرع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branches', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_partner_type = bsg_cargo_lines.groupby(['partner_type_name'])
            for key_partner_type, df_partner_type in bsg_cargo_lines_grouped_partner_type:
                if key_partner_type:
                    grouped_by_branch = {}
                    branch_df_groupby = df_partner_type.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row,col, 'Partner Type', main_heading2)
                        sheet.write_string(row, col+1, str(key_partner_type), main_heading)
                        sheet.write(row, col+2, 'نوع الشريك', main_heading2)
                        row+=1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()), {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                        for branch_key, branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                                col = 1
                                for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                    sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                    col += 1
                                    payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                    payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value['revenue_amount']
                                sheet.write_number(row, col, branch_value['no_of_cars_total'], main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                revenue_shipped_total += branch_value['revenue_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                revenue_unshipped_total += branch_value['revenue_unshipped']
                                col = 0
                                row += 1
                        print('...........payment_method_grand_sum_dict..........', payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key, pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
        if docs.grouping_by == 'by_agreement_type':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Agreement Type"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب  نوع الاتفاقية', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Agreement Type', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'الفرع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branches', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_agreement_type = bsg_cargo_lines.groupby(['agreement_type'])


            for key_agr_type, df_agr_type in bsg_cargo_lines_grouped_agreement_type:
                if key_agr_type:
                    grouped_by_branch = {}
                    branch_df_groupby = df_agr_type.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Agreement Type', main_heading2)
                        sheet.write_string(row, col + 1, str(key_agr_type), main_heading)
                        sheet.write(row, col + 2, 'نوع الاتفاقية', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                        for branch_key, branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                                col = 1
                                for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                    sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                    col += 1
                                    payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                    payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                        'revenue_amount']
                                sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                revenue_shipped_total += branch_value['revenue_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                revenue_unshipped_total += branch_value['revenue_unshipped']
                                col = 0
                                row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key, pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
        if docs.grouping_by == 'by_car_size':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Car Size"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب حجم السيارة', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Car Size', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), ' الفرع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branches', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_car_size = bsg_cargo_lines.groupby(['car_size_name'])


            for key_car_size, df_car_size in bsg_cargo_lines_grouped_car_size:
                if key_car_size:
                    grouped_by_branch = {}
                    branch_df_groupby = df_car_size.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Car Size', main_heading2)
                        sheet.write_string(row, col + 1, str(key_car_size), main_heading)
                        sheet.write(row, col+2, 'حجم السيارة', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                        for branch_key, branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                            col = 1
                            for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                col += 1
                                payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                    'revenue_amount']
                            sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                               main_heading)
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                            col += 1
                            sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                            no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                            revenue_shipped_total += branch_value['revenue_shipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                            no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                            revenue_unshipped_total += branch_value['revenue_unshipped']
                            col = 0
                            row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key, pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
        if docs.grouping_by == 'by_car_maker':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Car Maker"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب ماركة السيارة', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Car Maker', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'الفرع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branches', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_car_maker = bsg_cargo_lines.groupby(['car_make_name'])


            for key_car_make,df_car_make in bsg_cargo_lines_grouped_car_maker:
                if key_car_make:
                    grouped_by_branch = {}
                    branch_df_groupby = df_car_make.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Car Make', main_heading2)
                        sheet.write_string(row, col + 1, str(key_car_make), main_heading)
                        sheet.write(row, col + 2, 'ماركة السيارة', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                        for branch_key, branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                                col = 1
                                for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                    sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                    col += 1
                                    payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                    payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value['revenue_amount']
                                sheet.write_number(row, col, branch_value['no_of_cars_total'],main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                revenue_shipped_total += branch_value['revenue_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                revenue_unshipped_total += branch_value['revenue_unshipped']
                                col = 0
                                row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key, pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
        if docs.grouping_by == 'by_shipment_type':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Shipment Type"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب نوع الشحن', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Shipment Type', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'الفرع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branches', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_shipment_type = bsg_cargo_lines.groupby(['shipment_type_name'])


            for key_shipment_type, df_shipment_type in bsg_cargo_lines_grouped_shipment_type:
                if key_shipment_type:
                    grouped_by_branch = {}
                    branch_df_groupby = df_shipment_type.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Shipment Type', main_heading2)
                        sheet.write_string(row, col + 1, str(key_shipment_type), main_heading)
                        sheet.write(row, col + 2, 'نوع الشحن', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                        for branch_key, branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                            col = 1
                            for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                col += 1
                                payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                    'revenue_amount']
                            sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                               main_heading)
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                            col += 1
                            sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                            no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                            revenue_shipped_total += branch_value['revenue_shipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                            no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                            revenue_unshipped_total += branch_value['revenue_unshipped']
                            col = 0
                            row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key, pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
        if docs.grouping_by == 'by_manufacture_year':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Manufacture Year"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب سنة الصنع', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Manufacture Year', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'الفرع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branches', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_manufacture_year = bsg_cargo_lines.groupby(['manufacture_year_name'])


            for key_manufacture_year, df_manufacture_year in bsg_cargo_lines_grouped_manufacture_year:
                if key_manufacture_year:
                    grouped_by_branch = {}
                    branch_df_groupby = df_manufacture_year.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Manufacture Year', main_heading2)
                        sheet.write_string(row, col + 1, str(key_manufacture_year), main_heading)
                        sheet.write(row, col + 2, 'سنة الصنع', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                        for branch_key, branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                            col = 1
                            for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                col += 1
                                payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                    'revenue_amount']
                            sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                               main_heading)
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                            col += 1
                            sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                            no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                            revenue_shipped_total += branch_value['revenue_shipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                            no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                            revenue_unshipped_total += branch_value['revenue_unshipped']
                            col = 0
                            row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key, pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
        if docs.grouping_by == 'by_pricelist':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Pricelist"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب قائمة الأسعار', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Pricelist', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'الفرع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branches', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0

            bsg_cargo_lines_grouped_pricelist = bsg_cargo_lines.groupby(['pricelist_name'])


            for key_pricelist, df_pricelist in bsg_cargo_lines_grouped_pricelist:
                if key_pricelist:
                    grouped_by_branch = {}
                    branch_df_groupby = df_pricelist.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col,'Pricelist', main_heading2)
                        sheet.write_string(row, col + 1, str(key_pricelist), main_heading)
                        sheet.write(row, col + 2, 'قائمه الاسعار', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                        for branch_key, branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                            col = 1
                            for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                sheet.write_number(row, col,pm_value['no_of_cars'], main_heading)
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                col += 1
                                payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                    'revenue_amount']
                            sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                               main_heading)
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                            col += 1
                            sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                            no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                            revenue_shipped_total += branch_value['revenue_shipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                            no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                            col += 1
                            sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                            revenue_unshipped_total += branch_value['revenue_unshipped']
                            col = 0
                            row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key, pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
        if docs.grouping_by == 'by_order_date':
            self.env.ref(
                'bsg_sales_revenue_sumary_report.sales_revenue_report_xlsx_id').report_file = "Sales Revenue Summary Report Group By Order Date"
            sheet.merge_range('A1:M1', 'تقرير ملخص مبيعات نقل السيارات بحسب التاريخ', main_heading3)
            sheet.merge_range('A2:M2', 'Sales Revenue Summary Report Group By Order Date', main_heading3)

            row = 3

            index = 0

            cols_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            sheet.write(cols_list[index] + str(row), 'الفرع', main_heading2)

            index += 1

            for pm_key, pm_value in payment_method_dict.items():
                sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), str(pm_key),
                                  main_heading2)
                index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'الاجمالي العام',
                              main_heading2)

            index += 2

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row), 'السيارات المرحلة',
                              main_heading2)
            index += 2
            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index + 1] + str(row),
                              'السيارات غير المرحلة', main_heading2)
            index += 2

            pm_index = index

            index = 0

            row += 1

            sheet.merge_range(cols_list[index] + str(row) + ':' + cols_list[index] + str(row + 1),
                              'Branches', main_heading2)

            index += 1

            nl_index = index

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'No of Cars', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'Revenue', main_heading2)
                index += 1

            index = nl_index

            row += 1

            while index < pm_index:
                sheet.write(cols_list[index] + str(row), 'عدد السيارات', main_heading2)
                index += 1
                sheet.write(cols_list[index] + str(row), 'الايراد', main_heading2)
                index += 1

            row += 1

            col = 0
            if not docs.period_grouping_by:
                bsg_cargo_lines_date = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] != 0)]
                bsg_cargo_lines_date['order_date_no_time'] = pd.DatetimeIndex(bsg_cargo_lines_date['order_date']).date
                bsg_cargo_lines_date_grouped = bsg_cargo_lines_date.groupby(['order_date_no_time'])
                grouped_by_order_date = {}
                for key_order_date, df_order_date in bsg_cargo_lines_date_grouped:
                    if key_order_date:
                        grouped_by_branch = {}
                        branch_df_groupby = df_order_date.groupby(['bsg_branch_name'])
                        if branch_df_groupby:
                            for key_branch, df_branch in branch_df_groupby:
                                if key_branch:
                                    payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                    no_of_cars_total = 0
                                    revenue_total = 0
                                    no_of_cars_shipped = 0
                                    revenue_shipped = 0
                                    no_of_cars_unshipped = 0
                                    revenue_unshipped = 0
                                    grouped_by_payment_method = OrderedDict.fromkeys(
                                        (index for index, value in payment_method_dict.items()),
                                        {'no_of_cars': 0, 'revenue_amount': 0})
                                    # print('...........key_all............',key_all)
                                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                    for key_pm, dataframe_pm in payment_method_df_groupby:
                                        no_of_cars = 0
                                        revenue_amount = 0
                                        if key_pm:
                                            # print('..........key_pm..........',key_pm)
                                            for key, value in dataframe_pm.iterrows():
                                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                    all(trip_type == 'local' for
                                                                                        trip_type in
                                                                                        [trip_id.trip_type for trip_id
                                                                                         in
                                                                                         t.trip_history_ids.mapped(
                                                                                             'fleet_trip_id')]))):
                                                    no_of_cars_unshipped += 1
                                                    revenue_unshipped += t.revenue_amount
                                                else:
                                                    no_of_cars_shipped += 1
                                                    revenue_shipped += t.revenue_amount
                                                no_of_cars += 1
                                                revenue_amount += value['revenue_amount']
                                            grouped_by_payment_method[key_pm] = {
                                                'no_of_cars': no_of_cars,
                                                'revenue_amount': revenue_amount
                                            }
                                            no_of_cars_total += no_of_cars
                                            revenue_total += revenue_amount
                                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                    grouped_by_branch[key_branch] = {
                                        'grouped_by_payment_method': grouped_by_payment_method,
                                        'no_of_cars_total': no_of_cars_total,
                                        'revenue_total': revenue_total,
                                        'no_of_cars_shipped': no_of_cars_shipped,
                                        'revenue_shipped': revenue_shipped,
                                        'no_of_cars_unshipped': no_of_cars_unshipped,
                                        'revenue_unshipped': revenue_unshipped
                                    }
                            # grouped_by_order_date[key_order_date] = {
                            #     'grouped_by_branch': grouped_by_branch
                            # }
                            no_of_cars_shipped_total = 0
                            revenue_shipped_total = 0
                            no_of_cars_unshipped_total = 0
                            revenue_unshipped_total = 0
                            sheet.write(row, col, 'Date', main_heading2)
                            sheet.write_string(row, col + 1, str(key_order_date), main_heading)
                            sheet.write(row, col + 2, 'التاريخ', main_heading2)
                            row += 1
                            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                                (index for index, value in payment_method_dict.items()),
                                {'no_of_cars': 0, 'revenue_amount': 0})
                            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                            for branch_key, branch_value in grouped_by_branch.items():
                                if branch_key:
                                    sheet.write_string(row, col, str(branch_key), main_heading)
                                    col = 1
                                    for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                        col += 1
                                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                        col += 1
                                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                            'revenue_amount']
                                    sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                       main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                    no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                    revenue_shipped_total += branch_value['revenue_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                    no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                    revenue_unshipped_total += branch_value['revenue_unshipped']
                                    col = 0
                                    row += 1
                            print('...........payment_method_grand_sum_dict..........',
                                  payment_method_grand_sum_dict)
                            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                            col += 1
                            car_nums_grand_sum = 0
                            revenue_grand_sum = 0
                            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                car_nums_grand_sum += pm_value['no_of_cars']
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                revenue_grand_sum += pm_value['revenue_amount']
                                col += 1
                            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_shipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                            col = 0
                            row += 1

            if docs.period_grouping_by == 'day':
                days_list = []
                day_name = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
                bsg_cargo_lines_day = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] != 0)]
                bsg_cargo_lines_day['order_date_weekday'] = pd.DatetimeIndex(bsg_cargo_lines_day['order_date']).weekday
                bsg_cargo_lines_day_grouped = bsg_cargo_lines_day.groupby(['order_date_weekday'])
                grouped_by_order_date = {}
                for key_day, df_day in bsg_cargo_lines_day_grouped:
                    if key_day:
                        grouped_by_branch = {}
                        branch_df_groupby = df_day.groupby(['bsg_branch_name'])
                        if branch_df_groupby:
                            for key_branch, df_branch in branch_df_groupby:
                                if key_branch:
                                    payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                    no_of_cars_total = 0
                                    revenue_total = 0
                                    no_of_cars_shipped = 0
                                    revenue_shipped = 0
                                    no_of_cars_unshipped = 0
                                    revenue_unshipped = 0
                                    grouped_by_payment_method = OrderedDict.fromkeys(
                                        (index for index, value in payment_method_dict.items()),
                                        {'no_of_cars': 0, 'revenue_amount': 0})
                                    # print('...........key_all............',key_all)
                                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                    for key_pm, dataframe_pm in payment_method_df_groupby:
                                        no_of_cars = 0
                                        revenue_amount = 0
                                        if key_pm:
                                            # print('..........key_pm..........',key_pm)
                                            for key, value in dataframe_pm.iterrows():
                                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                    all(trip_type == 'local' for
                                                                                        trip_type in
                                                                                        [trip_id.trip_type for trip_id
                                                                                         in t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                    no_of_cars_unshipped += 1
                                                    revenue_unshipped += t.revenue_amount
                                                else:
                                                    no_of_cars_shipped += 1
                                                    revenue_shipped += t.revenue_amount
                                                no_of_cars += 1
                                                revenue_amount += value['revenue_amount']
                                            grouped_by_payment_method[key_pm] = {
                                                'no_of_cars': no_of_cars,
                                                'revenue_amount': revenue_amount
                                            }
                                            no_of_cars_total += no_of_cars
                                            revenue_total += revenue_amount
                                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                    grouped_by_branch[key_branch] = {
                                        'grouped_by_payment_method': grouped_by_payment_method,
                                        'no_of_cars_total': no_of_cars_total,
                                        'revenue_total': revenue_total,
                                        'no_of_cars_shipped': no_of_cars_shipped,
                                        'revenue_shipped': revenue_shipped,
                                        'no_of_cars_unshipped': no_of_cars_unshipped,
                                        'revenue_unshipped': revenue_unshipped
                                    }
                            no_of_cars_shipped_total = 0
                            revenue_shipped_total = 0
                            no_of_cars_unshipped_total = 0
                            revenue_unshipped_total = 0
                            # grouped_by_order_date[key_order_date] = {
                            #     'grouped_by_branch': grouped_by_branch
                            # }
                            sheet.write(row, col, 'Day', main_heading2)
                            sheet.write_string(row, col + 1, str(day_name[key_day]), main_heading)
                            sheet.write(row, col + 2, 'يوم', main_heading2)
                            row += 1
                            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                                (index for index, value in payment_method_dict.items()),
                                {'no_of_cars': 0, 'revenue_amount': 0})
                            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                            for branch_key, branch_value in grouped_by_branch.items():
                                if branch_key:
                                    sheet.write_string(row, col, str(branch_key), main_heading)
                                    col = 1
                                    for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                        col += 1
                                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                        col += 1
                                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                            'revenue_amount']
                                    sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                       main_heading)
                                    col += 1
                                    sheet.write_number(row, col,branch_value['revenue_total'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                    no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                    revenue_shipped_total += branch_value['revenue_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                    no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                    revenue_unshipped_total += branch_value['revenue_unshipped']
                                    col = 0
                                    row += 1
                            print('...........payment_method_grand_sum_dict..........',
                                  payment_method_grand_sum_dict)
                            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                            col += 1
                            car_nums_grand_sum = 0
                            revenue_grand_sum = 0
                            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                car_nums_grand_sum += pm_value['no_of_cars']
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                revenue_grand_sum += pm_value['revenue_amount']
                                col += 1
                            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_shipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                            col = 0
                            row += 1
            if docs.period_grouping_by == 'weekly':
                bsg_cargo_lines_weekly = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] != 0)]
                bsg_cargo_lines_weekly['order_date_year'] = pd.DatetimeIndex(bsg_cargo_lines_weekly['order_date']).year
                bsg_cargo_lines_weekly['order_date_week'] = pd.DatetimeIndex(bsg_cargo_lines_weekly['order_date']).strftime("%V")
                bsg_cargo_lines_weekly_grouped = bsg_cargo_lines_weekly.groupby(['order_date_year','order_date_week'])
                for key_week, df_week in bsg_cargo_lines_weekly_grouped:
                    if key_week:
                        grouped_by_branch = {}
                        branch_df_groupby = df_week.groupby(['bsg_branch_name'])
                        if branch_df_groupby:
                            for key_branch, df_branch in branch_df_groupby:
                                if key_branch:
                                    payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                    no_of_cars_total = 0
                                    revenue_total = 0
                                    no_of_cars_shipped = 0
                                    revenue_shipped = 0
                                    no_of_cars_unshipped = 0
                                    revenue_unshipped = 0
                                    grouped_by_payment_method = OrderedDict.fromkeys(
                                        (index for index, value in payment_method_dict.items()),
                                        {'no_of_cars': 0, 'revenue_amount': 0})
                                    # print('...........key_all............',key_all)
                                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                    for key_pm, dataframe_pm in payment_method_df_groupby:
                                        no_of_cars = 0
                                        revenue_amount = 0
                                        if key_pm:
                                            # print('..........key_pm..........',key_pm)
                                            for key, value in dataframe_pm.iterrows():
                                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                    all(trip_type == 'local' for
                                                                                        trip_type in
                                                                                        [trip_id.trip_type for trip_id
                                                                                         in t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                    no_of_cars_unshipped += 1
                                                    revenue_unshipped += t.revenue_amount
                                                else:
                                                    no_of_cars_shipped += 1
                                                    revenue_shipped += t.revenue_amount
                                                no_of_cars += 1
                                                revenue_amount += value['revenue_amount']
                                            grouped_by_payment_method[key_pm] = {
                                                'no_of_cars': no_of_cars,
                                                'revenue_amount': revenue_amount
                                            }
                                            no_of_cars_total += no_of_cars
                                            revenue_total += revenue_amount
                                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                    grouped_by_branch[key_branch] = {
                                        'grouped_by_payment_method': grouped_by_payment_method,
                                        'no_of_cars_total': no_of_cars_total,
                                        'revenue_total': revenue_total,
                                        'no_of_cars_shipped': no_of_cars_shipped,
                                        'revenue_shipped': revenue_shipped,
                                        'no_of_cars_unshipped': no_of_cars_unshipped,
                                        'revenue_unshipped': revenue_unshipped
                                    }
                            no_of_cars_shipped_total = 0
                            revenue_shipped_total = 0
                            no_of_cars_unshipped_total = 0
                            revenue_unshipped_total = 0
                            # grouped_by_order_date[key_order_date] = {
                            #     'grouped_by_branch': grouped_by_branch
                            # }
                            year_week = "year %s Week %s" % (key_week[0], key_week[1])
                            sheet.write(row, col, 'Week', main_heading2)
                            sheet.write_string(row, col + 1, str(year_week), main_heading)
                            sheet.write(row, col + 2, 'الأسبوع', main_heading2)
                            row += 1
                            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                                (index for index, value in payment_method_dict.items()),
                                {'no_of_cars': 0, 'revenue_amount': 0})
                            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                            for branch_key, branch_value in grouped_by_branch.items():
                                if branch_key:
                                    sheet.write_string(row, col, str(branch_key), main_heading)
                                    col = 1
                                    for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                        col += 1
                                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                        col += 1
                                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                            'revenue_amount']
                                    sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                       main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                    no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                    revenue_shipped_total += branch_value['revenue_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                    no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                    revenue_unshipped_total += branch_value['revenue_unshipped']
                                    col = 0
                                    row += 1
                            print('...........payment_method_grand_sum_dict..........',
                                  payment_method_grand_sum_dict)
                            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                            col += 1
                            car_nums_grand_sum = 0
                            revenue_grand_sum = 0
                            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                car_nums_grand_sum += pm_value['no_of_cars']
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                revenue_grand_sum += pm_value['revenue_amount']
                                col += 1
                            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_shipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                            col = 0
                            row += 1
            if docs.period_grouping_by == 'month':
                bsg_cargo_lines_monthly = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] != 0)]
                bsg_cargo_lines_monthly['order_date_monthly'] = pd.DatetimeIndex(bsg_cargo_lines_monthly['order_date']).strftime('%B')
                bsg_cargo_lines_monthly_grouped = bsg_cargo_lines_monthly.groupby(['order_date_monthly'])
                grouped_by_order_date = {}
                for key_month, df_month in bsg_cargo_lines_monthly_grouped:
                    if key_month:
                        grouped_by_branch = {}
                        branch_df_groupby = df_month.groupby(['bsg_branch_name'])
                        if branch_df_groupby:
                            for key_branch, df_branch in branch_df_groupby:
                                if key_branch:
                                    payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                    no_of_cars_total = 0
                                    revenue_total = 0
                                    no_of_cars_shipped = 0
                                    revenue_shipped = 0
                                    no_of_cars_unshipped = 0
                                    revenue_unshipped = 0
                                    grouped_by_payment_method = OrderedDict.fromkeys(
                                        (index for index, value in payment_method_dict.items()),
                                        {'no_of_cars': 0, 'revenue_amount': 0})
                                    # print('...........key_all............',key_all)
                                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                    for key_pm, dataframe_pm in payment_method_df_groupby:
                                        no_of_cars = 0
                                        revenue_amount = 0
                                        if key_pm:
                                            # print('..........key_pm..........',key_pm)
                                            for key, value in dataframe_pm.iterrows():
                                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                    all(trip_type == 'local' for
                                                                                        trip_type in
                                                                                        [trip_id.trip_type for trip_id
                                                                                         in t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                    no_of_cars_unshipped += 1
                                                    revenue_unshipped += t.revenue_amount
                                                else:
                                                    no_of_cars_shipped += 1
                                                    revenue_shipped += t.revenue_amount
                                                no_of_cars += 1
                                                revenue_amount += value['revenue_amount']
                                            grouped_by_payment_method[key_pm] = {
                                                'no_of_cars': no_of_cars,
                                                'revenue_amount': revenue_amount
                                            }
                                            no_of_cars_total += no_of_cars
                                            revenue_total += revenue_amount
                                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                    grouped_by_branch[key_branch] = {
                                        'grouped_by_payment_method': grouped_by_payment_method,
                                        'no_of_cars_total': no_of_cars_total,
                                        'revenue_total': revenue_total,
                                        'no_of_cars_shipped': no_of_cars_shipped,
                                        'revenue_shipped': revenue_shipped,
                                        'no_of_cars_unshipped': no_of_cars_unshipped,
                                        'revenue_unshipped': revenue_unshipped
                                    }
                            no_of_cars_shipped_total = 0
                            revenue_shipped_total = 0
                            no_of_cars_unshipped_total = 0
                            revenue_unshipped_total = 0
                            # grouped_by_order_date[key_order_date] = {
                            #     'grouped_by_branch': grouped_by_branch
                            # }
                            sheet.write(row, col, 'Month', main_heading2)
                            sheet.write_string(row, col + 1, str(key_month), main_heading)
                            sheet.write(row, col + 2, 'شهر', main_heading2)
                            row += 1
                            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                                (index for index, value in payment_method_dict.items()),
                                {'no_of_cars': 0, 'revenue_amount': 0})
                            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                            for branch_key, branch_value in grouped_by_branch.items():
                                if branch_key:
                                    sheet.write_string(row, col, str(branch_key), main_heading)
                                    col = 1
                                    for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                        sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                        col += 1
                                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                        col += 1
                                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                            'revenue_amount']
                                    sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                       main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                    no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                    revenue_shipped_total += branch_value['revenue_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                    no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                    revenue_unshipped_total += branch_value['revenue_unshipped']
                                    col = 0
                                    row += 1
                            print('...........payment_method_grand_sum_dict..........',
                                  payment_method_grand_sum_dict)
                            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                            col += 1
                            car_nums_grand_sum = 0
                            revenue_grand_sum = 0
                            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                car_nums_grand_sum += pm_value['no_of_cars']
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                revenue_grand_sum += pm_value['revenue_amount']
                                col += 1
                            sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_grand_sum, main_heading)
                            col = 0
                            row += 1
            if docs.period_grouping_by == 'quarterly':
                first_quarter = [1, 2, 3]
                second_quarter = [4, 5, 6]
                third_quarter = [7, 8, 9]
                fourth_quarter = [10, 11, 12]
                bsg_cargo_lines_quarterly = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] != 0)]
                bsg_cargo_lines_quarterly['order_date_month'] = pd.DatetimeIndex(bsg_cargo_lines_quarterly['order_date']).month
                first_quarter_ids = bsg_cargo_lines_quarterly.loc[(bsg_cargo_lines_quarterly['order_date_month'].isin(first_quarter))]
                second_quarter_ids = bsg_cargo_lines_quarterly.loc[(bsg_cargo_lines_quarterly['order_date_month'].isin(second_quarter))]
                third_quarter_ids = bsg_cargo_lines_quarterly.loc[(bsg_cargo_lines_quarterly['order_date_month'].isin(third_quarter))]
                fourth_quarter_ids = bsg_cargo_lines_quarterly.loc[(bsg_cargo_lines_quarterly['order_date_month'].isin(fourth_quarter))]
                if not first_quarter_ids.empty:
                    grouped_by_branch = {}
                    branch_df_groupby = first_quarter_ids.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Quarter', main_heading2)
                        sheet.write_string(row, col + 1, str('First'), main_heading)
                        sheet.write(row, col + 2, 'ربع', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(
                            json.dumps(payment_method_grand_sum_dict))
                        for branch_key,branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                                col = 1
                                for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                    sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, pm_value['revenue_amount'],
                                                       main_heading)
                                    col += 1
                                    payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value[
                                        'no_of_cars']
                                    payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                        'revenue_amount']
                                sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                revenue_shipped_total += branch_value['revenue_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                revenue_unshipped_total += branch_value['revenue_unshipped']
                                col = 0
                                row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key,pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col,revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
                if not second_quarter_ids.empty:
                    grouped_by_branch = {}
                    branch_df_groupby = second_quarter_ids.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Quarter', main_heading2)
                        sheet.write_string(row, col + 1, str('Second'), main_heading)
                        sheet.write(row, col + 2, 'ربع', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(
                            json.dumps(payment_method_grand_sum_dict))
                        for branch_key,branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                                col = 1
                                for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                    sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, pm_value['revenue_amount'],
                                                       main_heading)
                                    col += 1
                                    payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value[
                                        'no_of_cars']
                                    payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                        'revenue_amount']
                                sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                revenue_shipped_total += branch_value['revenue_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                revenue_unshipped_total += branch_value['revenue_unshipped']
                                col = 0
                                row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key,pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col,revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
                if not third_quarter_ids.empty:
                    grouped_by_branch = {}
                    branch_df_groupby = third_quarter_ids.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Quarter', main_heading2)
                        sheet.write_string(row, col + 1, str('Third'), main_heading)
                        sheet.write(row, col + 2, 'ربع', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(
                            json.dumps(payment_method_grand_sum_dict))
                        for branch_key,branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                                col = 1
                                for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                    sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, pm_value['revenue_amount'],
                                                       main_heading)
                                    col += 1
                                    payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value[
                                        'no_of_cars']
                                    payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                        'revenue_amount']
                                sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                revenue_shipped_total += branch_value['revenue_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                revenue_unshipped_total += branch_value['revenue_unshipped']
                                col = 0
                                row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key,pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col,revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
                if not fourth_quarter_ids.empty:
                    grouped_by_branch = {}
                    branch_df_groupby = fourth_quarter_ids.groupby(['bsg_branch_name'])
                    if branch_df_groupby:
                        sheet.write(row, col, 'Quarter', main_heading2)
                        sheet.write_string(row, col + 1, str('Fourth'), main_heading)
                        sheet.write(row, col + 2, 'ربع', main_heading2)
                        row += 1
                        for key_branch, df_branch in branch_df_groupby:
                            if key_branch:
                                payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                no_of_cars_total = 0
                                revenue_total = 0
                                no_of_cars_shipped = 0
                                revenue_shipped = 0
                                no_of_cars_unshipped = 0
                                revenue_unshipped = 0
                                grouped_by_payment_method = OrderedDict.fromkeys(
                                    (index for index, value in payment_method_dict.items()),
                                    {'no_of_cars': 0, 'revenue_amount': 0})
                                # print('...........key_all............',key_all)
                                # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                for key_pm, dataframe_pm in payment_method_df_groupby:
                                    no_of_cars = 0
                                    revenue_amount = 0
                                    if key_pm:
                                        # print('..........key_pm..........',key_pm)
                                        for key, value in dataframe_pm.iterrows():
                                            t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                [('id', '=', int(value['so_line_id']))], limit=1)
                                            if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                    t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                    (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                all(trip_type == 'local' for trip_type
                                                                                    in [trip_id.trip_type for trip_id in
                                                                                        t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                no_of_cars_unshipped += 1
                                                revenue_unshipped += t.revenue_amount
                                            else:
                                                no_of_cars_shipped += 1
                                                revenue_shipped += t.revenue_amount
                                            no_of_cars += 1
                                            revenue_amount += value['revenue_amount']
                                        grouped_by_payment_method[key_pm] = {
                                            'no_of_cars': no_of_cars,
                                            'revenue_amount': revenue_amount
                                        }
                                        no_of_cars_total += no_of_cars
                                        revenue_total += revenue_amount
                                        # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                grouped_by_branch[key_branch] = {
                                    'grouped_by_payment_method': grouped_by_payment_method,
                                    'no_of_cars_total': no_of_cars_total,
                                    'revenue_total': revenue_total,
                                    'no_of_cars_shipped': no_of_cars_shipped,
                                    'revenue_shipped': revenue_shipped,
                                    'no_of_cars_unshipped': no_of_cars_unshipped,
                                    'revenue_unshipped': revenue_unshipped
                                }
                        no_of_cars_shipped_total = 0
                        revenue_shipped_total = 0
                        no_of_cars_unshipped_total = 0
                        revenue_unshipped_total = 0
                        payment_method_grand_sum_dict = OrderedDict.fromkeys(
                            (index for index, value in payment_method_dict.items()),
                            {'no_of_cars': 0, 'revenue_amount': 0})
                        payment_method_grand_sum_dict = json.loads(
                            json.dumps(payment_method_grand_sum_dict))
                        for branch_key,branch_value in grouped_by_branch.items():
                            if branch_key:
                                sheet.write_string(row, col, str(branch_key), main_heading)
                                col = 1
                                for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                    sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, pm_value['revenue_amount'],
                                                       main_heading)
                                    col += 1
                                    payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value[
                                        'no_of_cars']
                                    payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                        'revenue_amount']
                                sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_total'],
                                                   main_heading)
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                revenue_shipped_total += branch_value['revenue_shipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                col += 1
                                sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                revenue_unshipped_total += branch_value['revenue_unshipped']
                                col = 0
                                row += 1
                        print('...........payment_method_grand_sum_dict..........',
                              payment_method_grand_sum_dict)
                        sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                        col += 1
                        car_nums_grand_sum = 0
                        revenue_grand_sum = 0
                        for pm_key,pm_value in payment_method_grand_sum_dict.items():
                            sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                            car_nums_grand_sum += pm_value['no_of_cars']
                            col += 1
                            sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                            revenue_grand_sum += pm_value['revenue_amount']
                            col += 1
                        sheet.write_number(row, col, car_nums_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col,revenue_grand_sum, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_shipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                        col += 1
                        sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                        col = 0
                        row += 1
            if docs.period_grouping_by == 'year':
                bsg_cargo_lines_yearly = bsg_cargo_lines.loc[(bsg_cargo_lines['order_date'] != 0)]
                bsg_cargo_lines_yearly['order_date_yearly'] = pd.DatetimeIndex(bsg_cargo_lines_yearly['order_date']).year
                bsg_cargo_lines_yearly_grouped = bsg_cargo_lines_yearly.groupby(['order_date_yearly'])
                grouped_by_order_date = {}
                for key_year, df_year in bsg_cargo_lines_yearly_grouped:
                    if key_year:
                        grouped_by_branch = {}
                        branch_df_groupby = df_year.groupby(['bsg_branch_name'])
                        if branch_df_groupby:
                            for key_branch, df_branch in branch_df_groupby:
                                if key_branch:
                                    payment_method_df_groupby = df_branch.groupby(['payment_method_name'])
                                    no_of_cars_total = 0
                                    revenue_total = 0
                                    no_of_cars_shipped = 0
                                    revenue_shipped = 0
                                    no_of_cars_unshipped = 0
                                    revenue_unshipped = 0
                                    grouped_by_payment_method = OrderedDict.fromkeys(
                                        (index for index, value in payment_method_dict.items()),
                                        {'no_of_cars': 0, 'revenue_amount': 0})
                                    # print('...........key_all............',key_all)
                                    # print('...........payment_method_dict dict.........',grouped_by_payment_method)
                                    for key_pm, dataframe_pm in payment_method_df_groupby:
                                        no_of_cars = 0
                                        revenue_amount = 0
                                        if key_pm:
                                            # print('..........key_pm..........',key_pm)
                                            for key, value in dataframe_pm.iterrows():
                                                t = self.env['bsg_vehicle_cargo_sale_line'].search(
                                                    [('id', '=', int(value['so_line_id']))], limit=1)
                                                if t.state != 'cancel' and (not t.fleet_trip_id or (
                                                        t.fleet_trip_id and t.fleet_trip_id.trip_type == 'local')) and \
                                                        (not t.trip_history_ids or (t.trip_history_ids and \
                                                                                    all(trip_type == 'local' for
                                                                                        trip_type in
                                                                                        [trip_id.trip_type for trip_id
                                                                                         in t.trip_history_ids.mapped(
                                                                                            'fleet_trip_id')]))):
                                                    no_of_cars_unshipped += 1
                                                    revenue_unshipped += t.revenue_amount
                                                else:
                                                    no_of_cars_shipped += 1
                                                    revenue_shipped += t.revenue_amount
                                                no_of_cars += 1
                                                revenue_amount += value['revenue_amount']
                                            grouped_by_payment_method[key_pm] = {
                                                'no_of_cars': no_of_cars,
                                                'revenue_amount': revenue_amount
                                            }
                                            no_of_cars_total += no_of_cars
                                            revenue_total += revenue_amount
                                            # print('.........grouped_by_payment_method........',grouped_by_payment_method)
                                    grouped_by_branch[key_branch] = {
                                        'grouped_by_payment_method': grouped_by_payment_method,
                                        'no_of_cars_total': no_of_cars_total,
                                        'revenue_total': revenue_total,
                                        'no_of_cars_shipped': no_of_cars_shipped,
                                        'revenue_shipped': revenue_shipped,
                                        'no_of_cars_unshipped': no_of_cars_unshipped,
                                        'revenue_unshipped': revenue_unshipped
                                    }
                            no_of_cars_shipped_total = 0
                            revenue_shipped_total = 0
                            no_of_cars_unshipped_total = 0
                            revenue_unshipped_total = 0
                            # grouped_by_order_date[key_order_date] = {
                            #     'grouped_by_branch': grouped_by_branch
                            # }
                            sheet.write(row, col, 'Year', main_heading2)
                            sheet.write_string(row, col + 1, str(key_year), main_heading)
                            sheet.write(row, col + 2, 'عام', main_heading2)
                            row += 1
                            payment_method_grand_sum_dict = OrderedDict.fromkeys(
                                (index for index, value in payment_method_dict.items()),
                                {'no_of_cars': 0, 'revenue_amount': 0})
                            payment_method_grand_sum_dict = json.loads(json.dumps(payment_method_grand_sum_dict))
                            for branch_key, branch_value in grouped_by_branch.items():
                                if branch_key:
                                    sheet.write_string(row, col, str(branch_key), main_heading)
                                    col = 1
                                    for pm_key, pm_value in branch_value['grouped_by_payment_method'].items():
                                        sheet.write_number(row, col,pm_value['no_of_cars'], main_heading)
                                        col += 1
                                        sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                        col += 1
                                        payment_method_grand_sum_dict[pm_key]['no_of_cars'] += pm_value['no_of_cars']
                                        payment_method_grand_sum_dict[pm_key]['revenue_amount'] += pm_value[
                                            'revenue_amount']
                                    sheet.write_number(row, col, branch_value['no_of_cars_total'],
                                                       main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_total'], main_heading)
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_shipped'], main_heading)
                                    no_of_cars_shipped_total += branch_value['no_of_cars_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_shipped'], main_heading)
                                    revenue_shipped_total += branch_value['revenue_shipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['no_of_cars_unshipped'], main_heading)
                                    no_of_cars_unshipped_total += branch_value['no_of_cars_unshipped']
                                    col += 1
                                    sheet.write_number(row, col, branch_value['revenue_unshipped'], main_heading)
                                    revenue_unshipped_total += branch_value['revenue_unshipped']
                                    col = 0
                                    row += 1
                            print('...........payment_method_grand_sum_dict..........',
                                  payment_method_grand_sum_dict)
                            sheet.write(row, col, 'الإجمالي الكلي', main_heading2)
                            col += 1
                            car_nums_grand_sum = 0
                            revenue_grand_sum = 0
                            for pm_key, pm_value in payment_method_grand_sum_dict.items():
                                sheet.write_number(row, col, pm_value['no_of_cars'], main_heading)
                                car_nums_grand_sum += pm_value['no_of_cars']
                                col += 1
                                sheet.write_number(row, col, pm_value['revenue_amount'], main_heading)
                                revenue_grand_sum += pm_value['revenue_amount']
                                col += 1
                            sheet.write_number(row, col,car_nums_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col,revenue_grand_sum, main_heading)
                            col += 1
                            sheet.write_number(row, col, no_of_cars_shipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_shipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, no_of_cars_unshipped_total, main_heading)
                            col += 1
                            sheet.write_number(row, col, revenue_unshipped_total, main_heading)
                            col = 0
                            row += 1







