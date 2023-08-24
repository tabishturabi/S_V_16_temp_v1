from odoo import models,fields,api,_
from datetime import datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
from pytz import timezone, UTC


class TripsReportPdf(models.AbstractModel):
    _name = 'report.bsg_trips_reports.trips_report_pdf'


    @api.model
    def _get_report_values(self, docids, data=None):
        model=self.env.context.get('active_model')
        wiz_id=self.env[model].browse(self.env.context.get('active_id'))
        print('..........wiz_id...............',wiz_id)

        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        form_tz = UTC.localize(wiz_id.form).astimezone(tz).replace(tzinfo=None)
        to_tz = UTC.localize(wiz_id.to).astimezone(tz).replace(tzinfo=None)

        domain=[('expected_start_date','>=',form_tz),('expected_start_date','<=',to_tz)]
        if wiz_id.vehicle_type:
            domain.append(('vehicle_id.vehicle_type','in',wiz_id.vehicle_type.ids))
        if wiz_id.trip_type:
            domain.append(('trip_type','=',wiz_id.trip_type))
        if wiz_id.branch_from:
            domain.append(('start_branch','in',wiz_id.branch_from.ids))
        if wiz_id.branch_to:
            domain.append(('end_branch','in',wiz_id.branch_to.ids))
        if wiz_id.trip_status:
            domain.append(('state','=',wiz_id.trip_status))
        if wiz_id.vehicle_group_id:
            domain.append(('vehicle_id.vehicle_group_name','=',wiz_id.vehicle_group_id.id))
        if wiz_id.truck_load == 'empty':
            domain.append(('total_cars','=',0))
        if wiz_id.truck_load == 'full':
            domain.append(('total_cars','!=',0))
        if wiz_id.user_id:
            domain.append(('create_uid','=',wiz_id.user_id.id))

        trip_ids = self.env['fleet.vehicle.trip'].search(domain)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs':wiz_id,
            'from_date':form_tz,
            'to_date':to_tz,
            'trips':trip_ids
        }




























