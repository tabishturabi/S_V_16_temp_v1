#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

# -*- coding: utf-8 -*-
import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api, _
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
import string
from itertools import groupby

class HRPayslipXlsReport(models.TransientModel):
    _name = 'report.bsg_vehicle_prod_report.vehicle_prod_reports_temp'
    _inherit = 'report.report_xlsx.abstract'
    
    
    
    # @api.multi
    def generate_xlsx_report(self, workbook, input_records, lines):
        record_wizard = self.env['vehicle.prod.report'].browse(self.env.context.get('active_id'))

        domain = [('route_id', '!=', False), ('vehicle_id', '!=', False)]
        if record_wizard.date_condition not in [False, 'is_not_set', 'is_not_set', 'is_not_set', 'in']:
            domain.append(('start_date', record_wizard.date_condition, record_wizard.form))
        else:
            if record_wizard.date_condition == 'in':
                domain.append(('expected_start_date', '>=', record_wizard.form))
                domain.append(('expected_end_date', '<=', record_wizard.to))
        if record_wizard.from_location_ids:
            domain.append(('from', 'in', record_wizard.ids))
        if record_wizard.to_location_ids:
            domain.append(('to', 'in', record_wizard.to_location_ids.ids))
        if  record_wizard.vehicle_type_ids:
            domain.append(('vehicle_type_id', 'in', record_wizard.vehicle_type_ids.ids))
        if record_wizard.vehicle_ids:
            domain.append(('vehicle_id', 'in', record_wizard.vehicle_ids.ids))
        if record_wizard.driver_ids:
            domain.append(('driver_id', 'in', record_wizard.driver_ids.ids))
        trip_ids = self.env['fleet.vehicle.trip'].sudo().search(domain, order='vehicle_id,route_id')
        # sorted_trip_ids  = sorted(trip_ids ,key=lambda tr:(tr.vehicle_id.id, tr.route_id.id))
        # grouped_by_vehcile = groupby(trip_ids, lambda line: (line.vehicle_id))
        grouped_by_vehcile = groupby(trip_ids, lambda line: (line.vehicle_id))

        


        main_heading = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color":'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
            })

        main_heading1 = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color":'black',
            "bg_color": '#D3D3D3',
            'font_size': '14',
            })

        main_heading2 = workbook.add_format({
            "bold": 1, 
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color":'black',
            'font_size': '10',
            })

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '13',
            "font_color":'black',
            'bg_color': '#D3D3D3'})

        main_data = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            'font_size': '14',
            })
        merge_format.set_shrink()
        main_heading.set_text_justlast(1)
        main_data.set_border()
        worksheet = workbook.add_worksheet('Vehicle Productivity Report')
        
        worksheet.merge_range('A1:F1','Vehicle Productivity Report',merge_format)
        worksheet.write('A4', 'رقم الشاحنة', main_heading1)
        worksheet.write('B4', 'اسم الشاحنة', main_heading1)
        worksheet.write('C4',  'نشاط الشاحنة', main_heading1)
        # worksheet.write('D4',  'فرع الانصلاق', main_heading1)
        # worksheet.write('E4',  'فرع الوصول', main_heading1)
        # worksheet.write('F4',  'مسافة الرحلة', main_heading1)
        # worksheet.write('G4',  'المسافة الإضافية', main_heading1)
        worksheet.write('D4',  'اجمالي مسافة الرحلة', main_heading1) #
        # worksheet.write('I4',  'قيمة مصروف الطريق', main_heading1) #
        # worksheet.write('J4',  'مصروف الطريق للمسافة الإضافية', main_heading1)
        # worksheet.write('K4',  'مكافأة الحموله', main_heading1)
        # worksheet.write('L4',  'مكافأة الحموله الإضافية', main_heading1)
        worksheet.write('E4',  'إجمالي مصروف الرحلة', main_heading1)
        worksheet.write('F4',  'الايراد القياسي', main_heading1)
        worksheet.write('G4',  'الايراد الفعلي', main_heading1)
        worksheet.write('H4',  'عدد السيارات المحملة', main_heading1)
        # worksheet.write('I4',  'خط السير', main_heading1)
       
        row = 4
        col = 0
        # vehicle_ids = set(trip_ids.mapped('vehicle_id'))
        trip_distance = extra_distance = total_reward_amount = additional_fuel_exp = total_fuel_amount = total_extra_distance_amount= total_standard_revenue = total_actual_revenue =all_fuel_amount=0
                    
        for group, tr_ids in grouped_by_vehcile:
            # grouped_by_route = groupby(tr_ids, lambda t: (t.route_id))
            col = 0
            # for route_id, trs in grouped_by_route:
            trips = list(tr_ids)
            vehicle_id = group[0]
            # route_id = group[1]
            # trailer_id = vehicle_id.trailer_id
            worksheet.write_string (row, col, vehicle_id.taq_number or '',main_data)
            worksheet.write_string (row, col+1,vehicle_id.model_id.name or '',main_data)
            worksheet.write_string (row, col+2, vehicle_id.vehicle_type.vehicle_type_name or '',main_data)
            # worksheet.write_string (row, col+3,route_id.route_name.split('-')[0] or '',main_data)
            # worksheet.write_string (row, col+4, route_id.route_name.split('-')[-1] or '',main_data)
            
            #مسافة الرحلة
            # route_trip_distance = sum([t.trip_distance for t in trips])
            # worksheet.write_number (row, col+5,route_trip_distance or 0,main_data)#
            # trip_distance += route_trip_distance
            #المسافة الاضافية
            # route_extra_distance = sum([t.extra_distance for t in trips])
            # worksheet.write_number (row, col+6,route_extra_distance,main_data)
            # extra_distance+=route_extra_distance
            #مجكوع المسافات
            route_trip_distance = sum([t.trip_distance + t.extra_distance for t in trips])
            worksheet.write_number (row, col+3,route_trip_distance,main_data)
            trip_distance += route_trip_distance
            so_count = sum([len(t.stock_picking_id) for t in trips])
            #قيمة مصروف الطريق
            # route_total_fuel_amount = sum([t.total_fuel_amount for t in trips])
            # worksheet.write_number (row, col+8,route_total_fuel_amount,main_data)
            # total_fuel_amount += route_total_fuel_amount
            # #قيمة مصروف الطريق للمسافة الاضافية
            # route_extra_distance_amount =  sum([t.extra_distance_amount for t in trips])
            # worksheet.write_number (row, col+9,route_extra_distance_amount,main_data)
            # total_extra_distance_amount += route_extra_distance_amount
            
            # #مكافأة الحمولة
            # route_total_reward_amount =  sum([t.total_reward_amount for t in trips])
            # worksheet.write_number (row, col+10,route_total_reward_amount,main_data)
            # total_reward_amount+= route_total_reward_amount
            
            #  #مكافأة الحمولة الاضافية
            # route_additional_fuel_exp = sum([t.additional_fuel_exp for t in trips])
            # worksheet.write_number (row, col+11,route_additional_fuel_exp,main_data)
            # additional_fuel_exp += route_additional_fuel_exp
            
            
            #اجمالي مصروف الرحلة
            tot_fule = sum([t.total_fuel_amount + t.extra_distance_amount+ t.total_reward_amount+t.additional_fuel_exp for t in trips])
            #route_total_fuel_amount+route_extra_distance_amount+route_total_reward_amount+route_additional_fuel_exp
            worksheet.write_number (row, col+4,tot_fule,main_data)
            all_fuel_amount += tot_fule


            standard_revenue = round(sum([tr.standard_revenue for tr in trips]),2)
            total_standard_revenue+= standard_revenue
            # trip.total_capacity = route_id.total_distance
            actual_revenue = round(sum([t.actual_revenue for t in trips]),2) #TODO: read  from revenue amount before deploying to prod
            total_actual_revenue+=actual_revenue
            worksheet.write_number (row, col+5,standard_revenue,main_data)
            worksheet.write_number (row, col+6,actual_revenue,main_data)
            worksheet.write_number (row, col+7,so_count,main_data)
            # worksheet.write_string (row, col+7,route_id.route_name,main_data)
            row+=1
        col=3
        row+=2
        worksheet.write_number (row, col,trip_distance or 0,main_data)
        # worksheet.write_number (row, col+1,extra_distance,main_data)
        # worksheet.write_number (row, col+2,total_fuel_amount,main_data)
        # worksheet.write_number (row, col+3,total_reward_amount,main_data)
        # worksheet.write_number (row, col+4,total_extra_distance_amount,main_data)
        # worksheet.write_number (row, col+5,total_reward_amount,main_data)
        # worksheet.write_number (row, col+6,additional_fuel_exp,main_data)
        worksheet.write_number (row, col+1,all_fuel_amount,main_data)
        worksheet.write_number (row, col+2,round(total_standard_revenue,2),main_data)
        worksheet.write_number (row, col+3,round(total_actual_revenue,2),main_data)
        row+=1

        