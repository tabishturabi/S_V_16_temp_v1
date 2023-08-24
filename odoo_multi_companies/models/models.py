# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class LocalCargoSale(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Local Cargo Sale")


class CargoSaleLine(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Cargo Sale Line")


class Trip(models.Model):
    _inherit = 'fleet.vehicle.trip'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Trip")


class BassamiInspection(models.Model):
    _inherit = 'bassami.inspection'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bassami Inspection")


class PriceLines(models.Model):
    _inherit = 'bsg_price_line'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Price Lines")


class PriceConfiguratioin(models.Model):
    _inherit = 'bsg_price_config'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Price Configuratioin")
    _sql_constraints = [
        ('value_bsg_price_config_uniq', 'unique (waypoint_from,waypoint_to,customer_type,company_id)',
         'This record already exists !')
    ]


class PartnerType(models.Model):
    _inherit = 'partner.type'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Partner Type")


class BsgRoute(models.Model):
    _inherit = 'bsg_route'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Route")


class BsgRouteWay(models.Model):
    _inherit = 'bsg_route_waypoints'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg Route Way")

    _sql_constraints = [('value_route_waypoint_name_uniq', 'unique (route_waypoint_name,company_id)',
                         'This Location Name Must Be Unique !')]


class BsgBranches(models.Model):
    _inherit = 'bsg_branches.bsg_branches'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this BsgBranches")


class DemurrageChargesConfig(models.Model):
    _inherit = 'demurrage_charges_config'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Demurrage Charges Config")
    _sql_constraints = [
        ('no_of_days_demurage_uniq', 'unique (starting_day_no, ending_day_no, chares,company_id)',
         'This record already exists !')]


class CustomerContractLine(models.Model):
    _inherit = 'bsg_customer_contract_line'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Customer Contract Line")


class CustomerContract(models.Model):
    _inherit = 'bsg_customer_contract'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Customer Contract")


class BsgCarShipmentType(models.Model):
    _inherit = 'bsg.car.shipment.type'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg Car Shipment Type")


class FleetVehicleState(models.Model):
    _inherit = 'fleet.vehicle.state'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Fleet Vehicle State")
    #_sql_constraints = [('fleet_state_name_unique', 'unique(name,company_id)', 'State name already exists')]



class BsgVehicleTypeTable(models.Model):
    _inherit = 'bsg.vehicle.type.table'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg Vehicle Type Table")


class BsgFleetTrailerConfig(models.Model):
    _inherit = 'bsg_fleet_trailer_config'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg Fleet Trailer Config")
    _sql_constraints = [
        ('trailer_taq_no_uniq', 'unique (trailer_taq_no, company_id)', _('The trailer_taq_no must be unique !')),
    ]


class BsgFuelExpenseMethod(models.Model):
    _inherit = 'bsg.fuel.expense.method'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg Fuel Expense Method")


class BsgTrailerCategories(models.Model):
    _inherit = 'bsg.trailer.categories'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg Trailer Categories")


class DriverUnassign(models.Model):
    _inherit = 'driver.unassign'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Driver Unassign")


class DriverAssign(models.Model):
    _inherit = 'driver.assign'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Driver assign")


class RenewalVehicleDocument(models.Model):
    _inherit = 'renewal.vehicle.document'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Renewal Vehicle Document")


class FleetTruckViolation(models.Model):
    _inherit = 'fleet.truck.violation'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Fleet Truck Violation")


class AccountCashRounding(models.Model):
    _inherit = 'account.cash.rounding'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Account Cash Rounding")


class FleetStatusModel(models.Model):
    _inherit = 'fleet.status.model'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Fleet Status Model")


class BsgEstimatedDeliveryDays(models.Model):
    _inherit = 'bsg.estimated.delivery.days'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg Estimated Delivery Days")


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Fleet Vehicle")


class BsgVehicleGroup(models.Model):
    _inherit = 'bsg.vehicle.group'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg vehicle group")


class DocumentInfoFleet(models.Model):
    _inherit = 'document.info.fleet'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Bsg vehicle group")


class HrIqama(models.Model):
    _inherit = 'hr.iqama'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Hr Iqama")


class HrBanks(models.Model):
    _inherit = 'hr.banks'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Hr Banks")


class HrPassport(models.Model):
    _inherit = 'hr.passport'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Hr Passport")


class HrInsurance(models.Model):
    _inherit = 'hr.insurance'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Hr Insurance")


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Hr Payslip Run")

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Hr Salary Rule")

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to Hr Payroll Structure")

class PettyCashExpensesAccounting(models.Model):
    _inherit = 'petty.cash.expense.accounting'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Petty Cash Expenses Accouting")


class ExpenseAccountingPetty(models.Model):
    _inherit = 'expense.accounting.petty'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Expense Accounting Petty")


class ExpenseAccountingTemplate(models.Model):
    _inherit = 'expense.accounting.template'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Expense Accounting Template")


class ResPettyCashConfig(models.Model):
    _inherit = 'res_petty_cash_config'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Res Petty Cash Config")


class HrNationality(models.Model):
    _inherit = 'hr.nationality'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Hr Nationality")


class AccountGroup(models.Model):
    _inherit = 'account.group'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Account Group")


class AccountFuelTripConfiguration(models.Model):
    _inherit = 'account.fuel.trip.configuration'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Account Fuel Trip Configuration")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        ('value_iqama_no_uniq', 'unique (iqama_no,company_id)', 'This iqama_no already exists !'),
        ('value_customer_id_card_no_uniq', 'unique (customer_id_card_no,company_id)',
         'This customer_id_card_no already exists !')
    ]

class ProductCategory(models.Model):
    _inherit = 'product.category'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this Product Category")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_get(self, fields_list):
        defaults = super(ProductTemplate, self).default_get(fields_list)
        category = self.env['product.category'].with_context(force_company=self.env.user.company_id.id,
                                                                    company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)],
                                                                                                                   limit=1)
        # location = self.env['stock.location'].with_context(force_company=self.env.user.company_id.id,
        #                                                           company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)],
        #                                                                                                          limit=1)


        defaults['categ_id'] = category.id
        defaults['property_stock_inventory'] = 5
        defaults['property_stock_production'] = 7
        return defaults

# Stop for Migration testing
# class CreditCustomerCollection(models.Model):
#     _inherit = 'credit.customer.collection'
#
#     company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
#                                  default=lambda self: self.env.user.company_id,
#                                  help="Company related to this Credit Customer Collection")
#
#
# class BxCreditCustomerCollection(models.Model):
#     _inherit = 'bx.credit.customer.collection'
#
#     company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
#                                  default=lambda self: self.env.user.company_id,
#                                  help="Company related to this Bx Credit Customer Collection")
