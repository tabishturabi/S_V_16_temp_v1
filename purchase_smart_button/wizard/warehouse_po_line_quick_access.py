from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo import tools
from dateutil.relativedelta import relativedelta

class WarehouseOnHandReport(models.Model):
    _name = 'warehouse.on.hand.report'
    

    warehouse_id = fields.Many2one('stock.warehouse')
    quantity = fields.Float()


    @api.model
    def set_mode_values(self):
        if not self._context.get('product_id',False):
            raise UserError(_("You Must Choose Product First"))
        self.env.cr.execute("""DELETE FROM %s""" % (self._table))
        # self._table = sale_report
        warehouse_ids = self.env['stock.warehouse'].sudo().search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_quants_ids = self.env['stock.quant'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('location_id','child_of',warehouse.view_location_id.id)])
            self.env.cr.execute("""INSERT INTO %s  (warehouse_id,quantity) VALUES 
                            (%s,%s)""" % (self._table,str(warehouse.id),sum(stock_quants_ids.mapped('quantity'))))


#########################################POPOPOPOPO####################################################################
class WarehousePoYearOpenReport(models.Model):
    _name = 'warehouse.po.year.open.report'
    

    warehouse_id = fields.Many2one('stock.warehouse')
    count = fields.Integer()
    quantity = fields.Float()


    @api.model
    def set_mode_values(self):
        if not self._context.get('product_id',False):
            raise UserError(_("You Must Choose Product First"))
        self.env.cr.execute("""DELETE FROM %s""" % (self._table))
        date = fields.Datetime.now()
        res = self.env.user.company_id.compute_fiscalyear_dates(date)
        # self._table = sale_report
        warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
            ('purchase_line_id.date_planned','>=',str(res['date_from'])),('purchase_line_id.date_planned','<=',str(res['date_to'])),('purchase_line_id','!=',None),('picking_id.state','!=','done')])
            self.env.cr.execute("""INSERT INTO %s  (warehouse_id,count,quantity) VALUES 
                            (%s,%s,%s)""" % (self._table,str(warehouse.id),len(stock_move_ids.mapped('purchase_line_id.order_id')),sum(stock_move_ids.mapped('product_uom_qty'))))


    @api.model
    def get_total_count(self):
        if not self._context.get('product_id',False):
            return 0
        date = fields.Datetime.now()
        res = self.env.user.company_id.compute_fiscalyear_dates(date)
        total = 0
        warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
            ('purchase_line_id.date_planned','>=',str(res['date_from'])),('purchase_line_id.date_planned','<=',str(res['date_to'])),('purchase_line_id','!=',None),('picking_id.state','!=','done')])
            total += len(stock_move_ids.mapped('purchase_line_id.order_id'))
        return total   

class WarehousePoYearcloseReport(models.Model):
    _name = 'warehouse.po.year.close.report'
    

    warehouse_id = fields.Many2one('stock.warehouse')
    quantity = fields.Float()
    count = fields.Integer()


    @api.model
    def set_mode_values(self):
        if not self._context.get('product_id',False):
            raise UserError(_("You Must Choose Product First"))
        self.env.cr.execute("""DELETE FROM %s""" % (self._table))
        date = fields.Datetime.now()
        res = self.env.user.company_id.compute_fiscalyear_dates(date)
        # self._table = sale_report
        warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
            ('purchase_line_id.date_planned','>=',str(res['date_from'])),('purchase_line_id.date_planned','<=',str(res['date_to'])),('purchase_line_id','!=',None),('picking_id.state','=','done')])
            self.env.cr.execute("""INSERT INTO %s  (warehouse_id,count,quantity) VALUES 
                            (%s,%s,%s)""" % (self._table,str(warehouse.id),len(stock_move_ids.mapped('purchase_line_id.order_id')),sum(stock_move_ids.mapped('product_uom_qty'))))


    @api.model
    def get_total_count(self):
        if not self._context.get('product_id',False):
            return 0
        date = fields.Datetime.now()
        res = self.env.user.company_id.compute_fiscalyear_dates(date)
        total = 0
        warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
            ('purchase_line_id.date_planned','>=',str(res['date_from'])),('purchase_line_id.date_planned','<=',str(res['date_to'])),('purchase_line_id','!=',None),('picking_id.state','=','done')])
            total += len(stock_move_ids.mapped('purchase_line_id.order_id'))
        return total

class WarehousePoPeriodReport(models.Model):
    _name = 'warehouse.po.period.report'
    

    warehouse_id = fields.Many2one('stock.warehouse')
    quantity = fields.Float()
    count = fields.Integer()


    @api.model
    def set_mode_values(self):
        if not self._context.get('product_id',False):
            raise UserError(_("You Must Choose Product First"))
        self.env.cr.execute("""DELETE FROM %s""" % (self._table))
        res = {}
        res['date_from'] = fields.Date.today() + relativedelta(day=1)
        res['date_to'] = fields.Date.today() + relativedelta(months=1,day=1,days=-1)
        
        if res:
            warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
            for warehouse in warehouse_ids:
                stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
                ('purchase_line_id.date_planned','>=',str(res['date_from'])),('purchase_line_id.date_planned','<=',str(res['date_to'])),('purchase_line_id','!=',None)])
                self.env.cr.execute("""INSERT INTO %s  (warehouse_id,count,quantity) VALUES 
                                (%s,%s,%s)""" % (self._table,str(warehouse.id),len(stock_move_ids.mapped('purchase_line_id.order_id')),sum(stock_move_ids.mapped('product_uom_qty'))))


    @api.model
    def get_total_count(self):
        if not self._context.get('product_id',False):
            return 0
        total = 0
        res = {}
        res['date_from'] = fields.Date.today() + relativedelta(day=1)
        res['date_to'] = fields.Date.today() + relativedelta(months=1,day=1,days=-1)
        if res:
            warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
            for warehouse in warehouse_ids:
                stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
                ('purchase_line_id.date_planned','>=',str(res['date_from'])),('purchase_line_id.date_planned','<=',str(res['date_to'])),('purchase_line_id','!=',None)])
                total += len(stock_move_ids.mapped('purchase_line_id.order_id'))
        return total   

  

########################################################################################


class WarehousePrPeriodReport(models.Model):
    _name = 'warehouse.pr.period.report'
    

    warehouse_id = fields.Many2one('stock.warehouse')
    quantity = fields.Float()
    count = fields.Integer()


    @api.model
    def set_mode_values(self):
        if not self._context.get('product_id',False):
            raise UserError(_("You Must Choose Product First"))
        self.env.cr.execute("""DELETE FROM %s""" % (self._table))
        res = {}
        res['date_from'] = fields.Date.today() + relativedelta(day=1)
        res['date_to'] = fields.Date.today() + relativedelta(months=1,day=1,days=-1)
        
        if res:
            warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
            for warehouse in warehouse_ids:
                stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
                ('purchase_req_line_id.preq.date_pr','>=',str(res['date_from'])),('purchase_req_line_id.preq.date_pr','<=',str(res['date_to'])),('purchase_req_line_id','!=',None)])
                self.env.cr.execute("""INSERT INTO %s  (warehouse_id,count,quantity) VALUES 
                                (%s,%s,%s)""" % (self._table,str(warehouse.id),len(stock_move_ids.mapped('purchase_req_line_id.preq')),sum(stock_move_ids.mapped('product_uom_qty'))))


    @api.model
    def get_total_count(self):
        if not self._context.get('product_id',False):
            return 0
        total = 0
        res = {}
        res['date_from'] = fields.Date.today() + relativedelta(day=1)
        res['date_to'] = fields.Date.today() + relativedelta(months=1,day=1,days=-1)
        if res:
            warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
            for warehouse in warehouse_ids:
                stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
                ('purchase_req_line_id.preq.date_pr','>=',str(res['date_from'])),('purchase_req_line_id.preq.date_pr','<=',str(res['date_to'])),('purchase_req_line_id','!=',None)])
                total += len(stock_move_ids.mapped('purchase_req_line_id.preq'))
        return total

class WarehousePrYearOpenReport(models.Model):
    _name = 'warehouse.pr.year.open.report'
    

    warehouse_id = fields.Many2one('stock.warehouse')
    quantity = fields.Float()
    count = fields.Integer()


    @api.model
    def set_mode_values(self):
        if not self._context.get('product_id',False):
            raise UserError(_("You Must Choose Product First"))
        self.env.cr.execute("""DELETE FROM %s""" % (self._table))
        date = fields.Datetime.now()
        res = self.env.user.company_id.compute_fiscalyear_dates(date)
        # self._table = sale_report
        warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
            ('purchase_req_line_id.preq.date_pr','>=',str(res['date_from'])),('purchase_req_line_id.preq.date_pr','<=',str(res['date_to'])),('purchase_req_line_id','!=',None),('purchase_req_line_id.preq.state','!=','done')])
            self.env.cr.execute("""INSERT INTO %s  (warehouse_id,count,quantity) VALUES 
                            (%s,%s,%s)""" % (self._table,str(warehouse.id),len(stock_move_ids.mapped('purchase_req_line_id.preq')),sum(stock_move_ids.mapped('product_uom_qty'))))


    @api.model
    def get_total_count(self):
        if not self._context.get('product_id',False):
            return 0
        date = fields.Datetime.now()
        res = self.env.user.company_id.compute_fiscalyear_dates(date)
        total = 0
        warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
            ('purchase_req_line_id.preq.date_pr','>=',str(res['date_from'])),('purchase_req_line_id.preq.date_pr','<=',str(res['date_to'])),('purchase_req_line_id','!=',None),('purchase_req_line_id.preq.state','!=','done')])
            total += len(stock_move_ids.mapped('purchase_req_line_id.preq'))
        return total 



class WarehousePrYearCloseReport(models.Model):
    _name = 'warehouse.pr.year.close.report'
    

    warehouse_id = fields.Many2one('stock.warehouse')
    quantity = fields.Float()
    count = fields.Integer()


    @api.model
    def set_mode_values(self):
        if not self._context.get('product_id',False):
            raise UserError(_("You Must Choose Product First"))
        self.env.cr.execute("""DELETE FROM %s""" % (self._table))
        date = fields.Datetime.now()
        res = self.env.user.company_id.compute_fiscalyear_dates(date)
        # self._table = sale_report
        warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
            ('purchase_req_line_id.preq.date_pr','>=',str(res['date_from'])),('purchase_req_line_id.preq.date_pr','<=',str(res['date_to'])),('purchase_req_line_id','!=',None),('purchase_req_line_id.preq.state','=','done')])
            self.env.cr.execute("""INSERT INTO %s  (warehouse_id,count,quantity) VALUES 
                            (%s,%s,%s)""" % (self._table,str(warehouse.id),len(stock_move_ids.mapped('purchase_req_line_id.preq')),sum(stock_move_ids.mapped('product_uom_qty'))))


    @api.model
    def get_total_count(self):
        if not self._context.get('product_id',False):
            return 0
        date = fields.Datetime.now()
        res = self.env.user.company_id.compute_fiscalyear_dates(date)
        total = 0
        warehouse_ids = self.env['stock.warehouse'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('company_id','=',self.env.user.company_id.id)])
        for warehouse in warehouse_ids:
            stock_move_ids = self.env['stock.move'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('product_id','=',self._context.get('product_id').id),('warehouse_id','=',warehouse.id),
            ('purchase_req_line_id.preq.date_pr','>=',str(res['date_from'])),('purchase_req_line_id.preq.date_pr','<=',str(res['date_to'])),('purchase_req_line_id','!=',None),('purchase_req_line_id.preq.state','=','done')])
            total += len(stock_move_ids.mapped('purchase_req_line_id.preq'))
        return total 

        
          

