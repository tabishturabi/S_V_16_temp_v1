# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BayanTripDetails(models.TransientModel):
    _name = "bayan.trip.details.wizard"

    @api.model
    def default_get(self, fields_list):
        defaults = super(BayanTripDetails, self).default_get(fields_list)
        data_dict = self.env.context.get('html_data')
        if data_dict:
            trip_id = str(data_dict['id'])
            createdAt = str(data_dict['createdAt'])
            carrier_name = str(data_dict['carrier']['nameArabic'])
            carrier_identityNumber = str(data_dict['carrier']['identityNumber'])
            carrier_carrierType = str(data_dict['carrier']['carrierType'])
            plateLetters = str(data_dict['vehicle']['plateLetters'])
            plateNumber = str(data_dict['vehicle']['plateNumber'])
            plateType = str(data_dict['vehicle']['plateType'])
            driver_name = str(data_dict['driver']['name'])
            driver_identityNumber = str(data_dict['driver']['identityNumber'])
            driver_mobile = str(data_dict['driver']['mobile'])
            receivedDate = str(data_dict['receivedDate'])
            expectedDeliveryDate = str(data_dict['expectedDeliveryDate'])
            actualDeliveryDate = str(data_dict['actualDeliveryDate'])

        defaults['trip_details'] = "<p>Trip ID : %s </p> <p>Created At : %s </p> <p>Carrier Name : %s </p> <p>Carrier Identity Number : %s </p> <p>Carrier Type : %s </p> <p>Plate Letters : %s </p> <p>Plate Number : %s </p> <p>PlateType : %s </p> <p>Driver Name :%s </p> <p>Driver Identity Number :%s </p><p>Driver Mobile : %s </p> <p>Received Date : %s </p> <p>Expected Delivery Date : %s </p><p>Actual Delivery Date : %s </p></p>"%(trip_id,createdAt,carrier_name,carrier_identityNumber,carrier_carrierType,plateLetters,plateNumber,plateType,driver_name,driver_identityNumber,driver_mobile,receivedDate,expectedDeliveryDate,actualDeliveryDate)
        return defaults

    trip_details = fields.Html("Details")
