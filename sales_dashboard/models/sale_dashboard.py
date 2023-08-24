from odoo import _, api, fields, models
import pandas as pd


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    # @api.multi
    def open_rec(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fleet.vehicle.trip',
            'res_id': self.trip_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class SaleDashboard(models.Model):
    _name = "sale.dashboard"
    _description = 'Sale Dashboard'

    @api.model
    def get_sales_info(self, **kw):
        if kw['0'] == 'all_branches' and kw['1']:
            branch_details = self.env['bsg_branches.bsg_branches'].sudo().search_read([])
        else:
            branch_details = self.env['bsg_branches.bsg_branches'].sudo().search_read(
                [('member_ids', 'in', self.env.user.employee_ids.id)])

        d1 = []
        shipment_types = self.env['bsg.car.shipment.type'].sudo().search([])
        shipment_type_name_list = [rec['display_name'] for rec in shipment_types]
        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,shipment_type,create_date,loc_to FROM " + table_name + " ")
        result = self._cr.fetchall()
        cargo_lines = pd.DataFrame(list(result))
        cargo_lines = cargo_lines.rename(
            columns={0: 'self_id', 1: 'shipment_type', 2: 'create_date', 3: 'loc_to'})
        cargo_lines['counter'] = 1

        years = pd.DatetimeIndex(cargo_lines['create_date']).year.unique()

        for rec in years:
            v1 = []
            for s in shipment_types:
                cargo_lines_ext = cargo_lines.loc[(pd.DatetimeIndex(cargo_lines['create_date']).year == rec)]
                cargo_lines_ext = cargo_lines_ext.loc[(cargo_lines_ext['shipment_type'] == s.id)]
                if kw['0'] == 'all_branches':
                    all_branches = [branch['id'] for branch in branch_details]
                    cargo_lines_ext = cargo_lines_ext.loc[(cargo_lines_ext['loc_to'].isin(all_branches))]
                elif kw['0'] == 'your_branches':
                    user_branches = [branch['id'] for branch in branch_details]
                    cargo_lines_ext = cargo_lines_ext.loc[(cargo_lines_ext['loc_to'].isin(user_branches))]
                else:
                    cargo_lines_ext = cargo_lines_ext.loc[(cargo_lines_ext['loc_to'].isin([int(kw['0'])]))]
                cargo_lines_ext = cargo_lines_ext.groupby(['shipment_type'], as_index=False).sum()
                for index, line in cargo_lines_ext.iterrows():
                    counter = line['counter']
                    v1.append(counter)

            traces = {
                'x': shipment_type_name_list,
                'y': v1,
                'name': str(rec),
                'type': 'bar',
            }
            d1.append(traces)

        fleet_status = self.env['bsg_branches.bsg_branches'].search([])
        fleet_dict = {}
        for fleet in fleet_status:
            fleet_dict[str(fleet.branch_no)] = {'trucks_avail': fleet.trucks_available,
                                                'trucks_final': fleet.trucks_final_stop,
                                                'trucks_coming': fleet.trucks_comming,
                                                'shipping_cars': fleet.shiping_cars,
                                                'arrived_cars': fleet.arrived_cars}
        data = {'branches': branch_details, 'd1': d1, 'fleet_data': fleet_dict}
        return data
