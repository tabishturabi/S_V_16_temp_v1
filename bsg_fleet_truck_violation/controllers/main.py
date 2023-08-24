"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import logging
from odoo.exceptions import AccessError
import ast

from odoo import http
from odoo.addons.restful.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class ViolationController(http.Controller):
    # """."""

    @http.route("/tracking/violation", type="http", auth="public", methods=["POST"], csrf=False)
    def track_violation(self, **payload):
        if payload.get('access_token', False) == '770b27a4c5deac5f11c8cff387a49c533b3071d8':
            if payload.get('unit', False):
                vehicle_id = request.env['fleet.vehicle'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('taq_number', '=', payload['unit'])])
                if vehicle_id:
                    violation_datetime = datetime.strptime(payload.get('curr_time', False),DEFAULT_SERVER_DATETIME_FORMAT)
                    violation_date_24_ago = violation_datetime - timedelta(hours=27)#check for trips in the past 24 hrs
                    
                    trip = request.env['fleet.vehicle.trip'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('vehicle_id', '=', vehicle_id.id), ('state', '=', 'progress'), ('bsg_trip_arrival_ids.actual_start_time', '>=', violation_date_24_ago)],  limit=1)

                    violation_date = violation_datetime - timedelta(hours=3) # bc datetime is retreved as UTC 
                    if not trip:
                        last_trip = request.env['fleet.vehicle.trip'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).search([('vehicle_id', '=', vehicle_id.id)],  limit=1)
                        vals= {
                            'location_link': payload.get('l_link', False),
                            'zone': payload.get('br', False),
                            'google_link': payload.get('loc_google', False),
                            'fleet_vehicle_id': vehicle_id.id,
                            'violation_date': violation_date,
                            'driver_id': vehicle_id.bsg_driver.id or False,
                            'violation_name': payload.get('location', False),
                            'driver_phone': vehicle_id.mobile_phone,
                            'trip_id':last_trip.id or False
                        }
                        request.env['fleet.truck.violation'].sudo().with_context(force_company=request.env.user.company_id.id, company_id=request.env.user.company_id.id).create(vals)
            return valid_response([])

        