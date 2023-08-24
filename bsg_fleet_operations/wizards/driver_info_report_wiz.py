# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import pandas as pd
from datetime import date,datetime, timedelta, timezone
from odoo.exceptions import UserError
import collections, functools, operator
from collections import OrderedDict


class DriverInfoReport(models.TransientModel):
    _name = 'driver.info.report.wizard'

    form = fields.Date(string='From',required=True)
    to = fields.Date(string='To',required=True)



    # @api.multi
    def click_print_excel(self):
        domain = [('card_expire_date', '>=', self.form), ('card_expire_date', '<=', self.to)]
        print('.............domain................', domain)
        driver_info_ids = self.env['driver.information'].search(domain)
        if driver_info_ids:
            data = {
                'ids': self.ids,
                'model': self._name,
            }
            return self.env.ref('bsg_fleet_operations.report_driver_info_id').report_action(self,data=data)
        else:
            raise UserError("No Data found against these parameters.")

    # @api.multi
    # def click_print_pdf(self):
    #     domain = [('create_date', '>=', self.form), ('create_date', '<=', self.to)]
    #     if self.trip_status:
    #         domain.append(('fleet_trip_id.state', '=', self.trip_status))
    #     if self.so_line_status:
    #         domain.append(('so_line_status', '=', self.so_line_status))
    #     if self.user_create_so_line:
    #         domain.append(('create_uid', '=', self.user_create_so_line.ids))
    #     if self.user_add_to_trip:
    #         domain.append(('partner_add_to_trip_id', '=', self.user_add_to_trip.id))
    #     print('.............domain................', domain)
    #     line_ids = self.env['bsg_vehicle_cargo_sale_line'].search(domain)
    #     if line_ids:
    #         data = {
    #             'ids': self.ids,
    #             'model': self._name,
    #         }
    #         return self.env.ref('bsg_operations_by_user_reports.obu_report_pdf_id').report_action(self,data=data)
    #     else:
    #         raise UserError("No Data found against these parameters.")














