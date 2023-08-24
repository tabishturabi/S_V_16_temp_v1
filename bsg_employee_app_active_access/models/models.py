# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

#Employee Config

class EmployeeConfigTagsInherited(models.Model):
    _inherit = 'hr.employee.category'
    _description = 'add active in config category'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigContractTypesInherited(models.Model):
    _inherit = 'hr.contract.type'
    _description = 'add active in config contract types'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigGuarantorInherited(models.Model):
    _inherit = 'bsg.hr.guarantor'
    _description = 'add active in config guarantor definition'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigDocTypeInherited(models.Model):
    _inherit = 'hr.emp.doc.type'
    _description = 'add active in config doc type'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigAssetTypeInherited(models.Model):
    _inherit = 'hr.asset.type'
    _description = 'add active in config Asset type'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigAccessMgmtInherited(models.Model):
    _inherit = 'hr.emp.access.mgt'
    _description = 'add active in config Access Management'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigEducationTypeInherited(models.Model):
    _inherit = 'hr.education.type'
    _description = 'add active in config education type'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigaccessTypeInherited(models.Model):
    _inherit = 'hr.access.type'
    _description = 'add active in config access type'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigIdTypeInherited(models.Model):
    _inherit = 'hr.id.type'
    _description = 'add active in config id type'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigBanksDetailsInherited(models.Model):
    _inherit = 'hr.banks.details'
    _description = 'add active in config banks details'


    active = fields.Boolean(string='Active',default=True)

class EmployeeConfigEmployeeStateInherited(models.Model):
    _inherit = 'bsg.hr.state'
    _description = 'add active in config emp state'


    active = fields.Boolean(string='Active',default=True)





#Human Resouce Config


class EmployeeIqamaInherited(models.Model):
    _inherit = 'hr.iqama'
    _description = 'add active in iqama'


    active = fields.Boolean(string='Active',default=True)

class EmployeeBanksinherited(models.Model):
    _inherit = 'hr.banks'
    _description = 'add active in banks'


    active = fields.Boolean(string='Active',default=True)

class EmployeeNidinherited(models.Model):
    _inherit = 'hr.nationality'
    _description = 'add active in nid'


    active = fields.Boolean(string='Active',default=True)

class EmployeePassportinherited(models.Model):
    _inherit = 'hr.passport'
    _description = 'add active in passport'


    active = fields.Boolean(string='Active',default=True)

class EmployeeInsuranceinherited(models.Model):
    _inherit = 'hr.insurance'
    _description = 'add active in insurance'


    active = fields.Boolean(string='Active',default=True)

class EmployeeReligioninherited(models.Model):
    _inherit = 'hr.employee.religion'
    _description = 'add active in employee religion'


    active = fields.Boolean(string='Active',default=True)





