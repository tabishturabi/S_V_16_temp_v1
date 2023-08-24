# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class IrModel(models.Model):
    _inherit = "ir.model"

    track = fields.Boolean('track', help='Track the changes on chatter?')


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _get_tracked_fields(self, updated_fields):
        if self.env['ir.model']._get(self._name).track:
            fields = self.fields_get()
            dels = [f for f in fields if f in models.LOG_ACCESS_COLUMNS or f.startswith('_') or f == 'id']
            for x in dels:
                del fields[x]
            return fields
        else:
            return super(MailThread, self)._get_tracked_fields(updated_fields)


class HrPayslipInput(models.Model):
    _inherit = "hr.payslip.input"

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'name': self.name if self.name else '', 'code': self.code if self.code else '',
                    'amount': self.amount if self.amount else '',
                    'description': self.description if self.description else ''}
        data_dict = {}
        reference = self.name if self.name else ''
        if values.get('name'):
            data_dict['name'] = {'name': 'Name', 'old': old_dict['name'], 'new': values.get('name')}
        if values.get('code'):
            data_dict['code'] = {'name': 'Code', 'old': old_dict['code'], 'new': values.get('code')}
        if values.get('amount'):
            data_dict['amount'] = {'name': 'Amount', 'old': old_dict['amount'], 'new': values.get('amount')}
        if values.get('description'):
            data_dict['description'] = {'name': 'Description', 'old': old_dict['description'],
                                        'new': values.get('description')}
        log_body = "<p>Reference/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.payslip', 'res_id': self.payslip_id.id, 'subtype_id': '2'})
        return super(HrPayslipInput, self).write(values)


class BsgHrInsurance(models.Model):
    _inherit = 'hr.insurance'

    @api.model
    def create(self, values):
        res = super(BsgHrInsurance, self).create(values)
        data_dict = {}
        reference = res.bsg_insurance_member.name if res.bsg_insurance_member.name else ''
        if res['bsg_insurance_company']:
            data_dict['bsg_insurance_company'] = {'name': 'Insurance Company name',
                                                  'new': res['bsg_insurance_company']}
        if res['bsg_insurance_member1']:
            data_dict['bsg_insurance_member1'] = {'name': 'Member Name',
                                                  'new': res['bsg_insurance_member1']}
        if res['bsg_insurance_member']:
            data_dict['bsg_insurance_member'] = {'name': 'Member Name',
                                                 'new': res['bsg_insurance_member'].name}
        if res['bsg_startdate']:
            data_dict['bsg_startdate'] = {'name': 'Start date',
                                          'new': res['bsg_startdate']}
        if res['bsg_enddate']:
            data_dict['bsg_enddate'] = {'name': 'End date',
                                        'new': res['bsg_enddate']}
        if res['bsg_premium']:
            data_dict['bsg_premium'] = {'name': 'Premium',
                                        'new': res['bsg_premium']}
        if res['bsg_insurancerelation']:
            data_dict['bsg_insurancerelation'] = {'name': 'Insurance Relation',
                                                  'new': res['bsg_insurancerelation']}
        if res['bsg_class']:
            data_dict['bsg_class'] = {'name': 'Class',
                                      'new': res['bsg_class']}
        if res['bsg_cardcode']:
            data_dict['bsg_cardcode'] = {'name': 'Card Code',
                                         'new': res['bsg_cardcode']}
        if res['bsg_gender']:
            data_dict['bsg_gender'] = {'name': 'Gender',
                                       'new': res['bsg_gender']}
        log_body = "<p>Insurance Created : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': res.employee_insurance.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'bsg_insurance_company': self.bsg_insurance_company if self.bsg_insurance_company else '',
                    'bsg_insurance_member1': self.bsg_insurance_member1 if self.bsg_insurance_member1 else '',
                    'bsg_insurance_member': self.bsg_insurance_member.name if self.bsg_insurance_member.name else '',
                    'bsg_startdate': self.bsg_startdate if self.bsg_startdate else '',
                    'bsg_enddate': self.bsg_enddate if self.bsg_enddate else '',
                    'bsg_premium': self.bsg_premium if self.bsg_premium else '',
                    'bsg_insurancerelation': self.bsg_insurancerelation if self.bsg_insurancerelation else '',
                    'bsg_class': self.bsg_class if self.bsg_class else '',
                    'bsg_cardcode': self.bsg_cardcode if self.bsg_cardcode else '',
                    'bsg_gender': self.bsg_gender if self.bsg_gender else ''}
        data_dict = {}
        reference = self.bsg_insurance_member.name if self.bsg_insurance_member.name else ''
        if values.get('bsg_insurance_company'):
            data_dict['bsg_insurance_company'] = {'name': 'Insurance Company name',
                                                  'old': old_dict['bsg_insurance_company'],
                                                  'new': values.get('bsg_insurance_company')}
        if values.get('bsg_insurance_member1'):
            data_dict['bsg_insurance_member1'] = {'name': 'Member Name', 'old': old_dict['bsg_insurance_member1'],
                                                  'new': values.get('bsg_insurance_member1')}
        if values.get('bsg_insurance_member'):
            data_dict['bsg_insurance_member'] = {'name': 'Member Name', 'old': old_dict['bsg_insurance_member'],
                                                 'new': values.get('bsg_insurance_member').name}
        if values.get('bsg_startdate'):
            data_dict['bsg_startdate'] = {'name': 'Start date', 'old': old_dict['bsg_startdate'],
                                          'new': values.get('bsg_startdate')}
        if values.get('bsg_enddate'):
            data_dict['bsg_enddate'] = {'name': 'End date', 'old': old_dict['bsg_enddate'],
                                        'new': values.get('bsg_enddate')}
        if values.get('bsg_premium'):
            data_dict['bsg_premium'] = {'name': 'Premium', 'old': old_dict['bsg_premium'],
                                        'new': values.get('bsg_premium')}
        if values.get('bsg_insurancerelation'):
            data_dict['bsg_insurancerelation'] = {'name': 'Insurance Relation',
                                                  'old': old_dict['bsg_insurancerelation'],
                                                  'new': values.get('bsg_insurancerelation')}
        if values.get('bsg_class'):
            data_dict['bsg_class'] = {'name': 'Class', 'old': old_dict['bsg_class'],
                                      'new': values.get('bsg_class')}
        if values.get('bsg_cardcode'):
            data_dict['bsg_cardcode'] = {'name': 'Card Code', 'old': old_dict['bsg_cardcode'],
                                         'new': values.get('bsg_cardcode')}
        if values.get('bsg_gender'):
            data_dict['bsg_gender'] = {'name': 'Gender', 'old': old_dict['bsg_gender'],
                                       'new': values.get('bsg_gender')}
        log_body = "<p>Insurance/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': self.employee_insurance.id, 'subtype_id': '2'})
        return super(BsgHrInsurance, self).write(values)


class BsgHrEmpDoc(models.Model):
    _inherit = 'hr.emp.doc'

    @api.model
    def create(self, values):
        res = super(BsgHrEmpDoc, self).create(values)
        data_dict = {}
        reference = res.bsg_type.bsg_name if res.bsg_type.bsg_name else ''
        if res['bsg_type']:
            data_dict['bsg_type'] = {'name': 'Document Type',
                                     'new': res['bsg_type'].bsg_name}
        if res['bsg_startdate']:
            data_dict['bsg_startdate'] = {'name': 'Document Start Date',
                                          'new': res['bsg_startdate']}
        if res['bsg_enddate']:
            data_dict['bsg_enddate'] = {'name': 'Document End Date',
                                        'new': res['bsg_enddate']}
        log_body = "<p>Document Type Created : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': res.hrdoc.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'bsg_type': self.bsg_type if self.bsg_type else '',
                    'bsg_startdate': self.bsg_startdate if self.bsg_startdate else '',
                    'bsg_enddate': self.bsg_enddate if self.bsg_enddate else ''}
        data_dict = {}
        reference = self.bsg_type.bsg_name if self.bsg_type.bsg_name else ''
        if values.get('bsg_type'):
            data_dict['bsg_type'] = {'name': 'Document Type', 'old': old_dict['bsg_type'],
                                     'new': values.get('bsg_type')}
        if values.get('bsg_startdate'):
            data_dict['bsg_startdate'] = {'name': 'Document Start Date', 'old': old_dict['bsg_startdate'],
                                          'new': values.get('bsg_startdate')}
        if values.get('bsg_enddate'):
            data_dict['bsg_enddate'] = {'name': 'Document End Date', 'old': old_dict['bsg_enddate'],
                                        'new': values.get('bsg_enddate')}
        log_body = "<p>Document Type/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': self.hrdoc.id, 'subtype_id': '2'})
        return super(BsgHrEmpDoc, self).write(values)


class BsgHrAsset(models.Model):
    _inherit = 'hr.asset'

    @api.model
    def create(self, values):
        res = super(BsgHrAsset, self).create(values)
        data_dict = {}
        if res['bsg_typeasset']:
            data_dict['bsg_typeasset'] = {'name': 'Assets Type',
                                          'new': res['bsg_typeasset'].bsg_name}
        if res['bsg_issuedate']:
            data_dict['bsg_issuedate'] = {'name': 'Issue Date',
                                          'new': res['bsg_issuedate']}
        if res['bsg_appro']:
            data_dict['bsg_appro'] = {'name': 'Approved By',
                                      'new': res['bsg_appro'].name}

        log_body = "<p>Assets Info Created</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': res.assets_emp.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'bsg_assettype': self.bsg_assettype if self.bsg_assettype else '',
                    'bsg_issuedate': self.bsg_issuedate if self.bsg_issuedate else '',
                    'bsg_appro': self.bsg_appro if self.bsg_appro else ''}
        data_dict = {}
        if values.get('bsg_assettype'):
            data_dict['bsg_assettype'] = {'name': 'Assets Type', 'old': old_dict['bsg_assettype'],
                                          'new': values.get('bsg_assettype')}
        if values.get('bsg_issuedate'):
            data_dict['bsg_issuedate'] = {'name': 'Issue Date', 'old': old_dict['bsg_issuedate'],
                                          'new': values.get('bsg_issuedate')}
        if values.get('bsg_appro'):
            data_dict['bsg_appro'] = {'name': 'Approved By', 'old': old_dict['bsg_appro'],
                                      'new': values.get('bsg_appro')}

        log_body = "<p>Assets Info Updated</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': self.assets_emp.id, 'subtype_id': '2'})
        return super(BsgHrAsset, self).write(values)


class BsgHrEmployeesAccessManagemennt(models.Model):
    _inherit = 'hr.emp.access.mgt'

    @api.model
    def create(self, values):
        res = super(BsgHrEmployeesAccessManagemennt, self).create(values)
        data_dict = {}
        if res['bsg_accesstype']:
            data_dict['bsg_accesstype'] = {'name': 'Access Type',
                                           'new': res['bsg_accesstype'].bsg_name}
        if res['bsg_appro']:
            data_dict['bsg_appro'] = {'name': 'Approved By',
                                      'new': res['bsg_appro'].name}

        log_body = "<p>Employee Access Management Created</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': res.access_emp.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'bsg_accesstype': self.bsg_accesstype if self.bsg_accesstype else '',
                    'bsg_appro': self.bsg_appro if self.bsg_appro else ''}
        data_dict = {}
        if values.get('bsg_accesstype'):
            data_dict['bsg_accesstype'] = {'name': 'Access Type', 'old': old_dict['bsg_accesstype'],
                                           'new': values.get('bsg_accesstype')}
        if values.get('bsg_appro'):
            data_dict['bsg_appro'] = {'name': 'Approved By', 'old': old_dict['bsg_appro'],
                                      'new': values.get('bsg_appro')}

        log_body = "<p>Employee Access Management Updated</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': self.access_emp.id, 'subtype_id': '2'})
        return super(BsgHrEmployeesAccessManagemennt, self).write(values)


class BsgEducation(models.Model):
    _inherit = 'hr.education'

    @api.model
    def create(self, values):
        res = super(BsgEducation, self).create(values)
        data_dict = {}
        if res['bsg_edu_type']:
            data_dict['bsg_edu_type'] = {'name': 'Education Type',
                                         'new': res['bsg_edu_type'].bsg_type}
        if res['bsg_inst']:
            data_dict['bsg_inst'] = {'name': 'Institute Name',
                                     'new': res['bsg_inst']}

        log_body = "<p>Education Created</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': res.education_emp.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'bsg_edu_type': self.bsg_edu_type if self.bsg_edu_type else '',
                    'bsg_inst': self.bsg_inst if self.bsg_inst else ''}
        data_dict = {}
        if values.get('bsg_edu_type'):
            data_dict['bsg_edu_type'] = {'name': 'Education Type', 'old': old_dict['bsg_edu_type'],
                                         'new': values.get('bsg_edu_type')}
        if values.get('bsg_inst'):
            data_dict['bsg_inst'] = {'name': 'Institute Name', 'old': old_dict['bsg_inst'],
                                     'new': values.get('bsg_inst')}

        log_body = "<p>Education Updated</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': self.education_emp.id, 'subtype_id': '2'})
        return super(BsgEducation, self).write(values)


class BsgHrIqamaFamily(models.Model):
    _inherit = 'hr.iqama.family'

    @api.model
    def create(self, values):
        res = super(BsgHrIqamaFamily, self).create(values)
        data_dict = {}
        if res['bsg_name']:
            data_dict['bsg_name'] = {'name': 'Name',
                                     'new': res['bsg_name']}
        if res['bsg_iqamanumber']:
            data_dict['bsg_iqamanumber'] = {'name': 'Iqama Number',
                                            'new': res['bsg_iqamanumber']}
        if res['bsg_relation']:
            data_dict['bsg_relation'] = {'name': 'Relation',
                                         'new': res['bsg_relation']}
        if res['bsg_iqamaexpiry']:
            data_dict['bsg_iqamaexpiry'] = {'name': 'Iqama Expiry',
                                            'new': res['bsg_iqamaexpiry']}
        if res['bsg_iqamaissueplace']:
            data_dict['bsg_iqamaissueplace'] = {'name': 'Iqama Issues Place',
                                                'new': res['bsg_iqamaissueplace']}

        log_body = "<p>Family Info Created</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': res.hife.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'bsg_name': self.bsg_name if self.bsg_name else '',
                    'bsg_iqamanumber': self.bsg_iqamanumber if self.bsg_iqamanumber else '',
                    'bsg_relation': self.bsg_relation if self.bsg_relation else '',
                    'bsg_iqamaexpiry': self.bsg_iqamaexpiry if self.bsg_iqamaexpiry else '',
                    'bsg_iqamaissueplace': self.bsg_iqamaissueplace if self.bsg_iqamaissueplace else '',

                    }
        data_dict = {}
        reference = self.bsg_name if self.bsg_name else ''

        if values.get('bsg_name'):
            data_dict['bsg_name'] = {'name': 'Name', 'old': old_dict['bsg_name'],
                                     'new': values.get('bsg_name')}
        if values.get('bsg_iqamanumber'):
            data_dict['bsg_iqamanumber'] = {'name': 'Iqama Number', 'old': old_dict['bsg_iqamanumber'],
                                            'new': values.get('bsg_iqamanumber')}
        if values.get('bsg_relation'):
            data_dict['bsg_relation'] = {'name': 'Relation', 'old': old_dict['bsg_relation'],
                                         'new': values.get('bsg_relation')}
        if values.get('bsg_iqamaexpiry'):
            data_dict['bsg_iqamaexpiry'] = {'name': 'Iqama Expiry', 'old': old_dict['bsg_iqamaexpiry'],
                                            'new': values.get('bsg_iqamaexpiry')}
        if values.get('bsg_iqamaissueplace'):
            data_dict['bsg_iqamaissueplace'] = {'name': 'Iqama Issues Place', 'old': old_dict['bsg_iqamaissueplace'],
                                                'new': values.get('bsg_iqamaissueplace')}

        log_body = "<p>Family Info/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': self.hife.id, 'subtype_id': '2'})
        return super(BsgHrIqamaFamily, self).write(values)


class BsgEmergencyContact(models.Model):
    _inherit = 'hr.emergency.contact'

    @api.model
    def create(self, values):
        res = super(BsgEmergencyContact, self).create(values)
        data_dict = {}
        if res['bsg_name']:
            data_dict['bsg_name'] = {'name': 'Contact Person Name',
                                     'new': res['bsg_name']}
        if res['bsg_contact']:
            data_dict['bsg_contact'] = {'name': 'Contact Number',
                                        'new': res['bsg_contact']}
        if res['bsg_relation']:
            data_dict['bsg_relation'] = {'name': 'Relation',
                                         'new': res['bsg_relation']}

        log_body = "<p>Emergency Contact Created</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': res.emergency_employee.id, 'subtype_id': '2'})
        return res

    #@api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
        old_dict = {'bsg_name': self.bsg_name if self.bsg_name else '',
                    'bsg_contact': self.bsg_contact if self.bsg_contact else '',
                    'bsg_relation': self.bsg_relation if self.bsg_relation else ''}
        data_dict = {}
        reference = self.bsg_name if self.bsg_name else ''

        if values.get('bsg_name'):
            data_dict['bsg_name'] = {'name': 'Contact Person Name', 'old': old_dict['bsg_name'],
                                     'new': values.get('bsg_name')}
        if values.get('bsg_contact'):
            data_dict['bsg_contact'] = {'name': 'Contact Number ', 'old': old_dict['bsg_contact'],
                                        'new': values.get('bsg_contact')}
        if values.get('bsg_relation'):
            data_dict['bsg_relation'] = {'name': 'Relation', 'old': old_dict['bsg_relation'],
                                         'new': values.get('bsg_relation')}

        log_body = "<p>Emergency Contact/Description : " + reference + "</p>"
        for val in data_dict.keys():
            log_body += '<li>' + str(data_dict[val]['name']) + ' : ' + str(data_dict[val]['old']) + ' → ' + str(
                data_dict[val]['new']) + '</li>'
        self.env['mail.message'].create(
            {'body': log_body, 'model': 'hr.employee', 'res_id': self.emergency_employee.id, 'subtype_id': '2'})
        return super(BsgEmergencyContact, self).write(values)
