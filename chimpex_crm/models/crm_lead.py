# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
import uuid
from odoo.exceptions import Warning

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    customer_id = fields.Char(
        string='Id del Cliente',
        readonly=True)

    company_currency = fields.Many2one(
        string='Moneda',
        readonly=False,
        required=True,
        comodel_name='res.currency',
        default=lambda self: self.env['res.currency'].sudo().search([],limit=1).id)


    bill_ids = fields.One2many(
        comodel_name='crm.lead.bill',
        inverse_name='lead_id',
        string='Id de Factura')

    @api.model
    def create(self, values):
        crm = super(CRMLead, self).create(values)
        crm.customer_id = crm.create_customer_id()
        return crm

    @api.multi
    def create_customer_id(self):
        customer = self.search([('id','!=',self.id)], order='customer_id DESC', limit=1)
        if customer:
            previous_customer_id = customer.customer_id
            return 'A'+ str(int(previous_customer_id[1:])+1)
        return 'A1000001'

    @api.multi
    def generate_bills(self):
        if not self.bill_ids:
            return {
                'name': 'Generar Facturas',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'chimpex.crm.lead.wizard',
                'view_id': self.env.ref("chimpex_crm.crm_lead_wizard_view").id,
                'context': {'partner_id': self.partner_id.id, 
                            'default_planned_revenue': self.planned_revenue, 
                            'default_currency_id':self.company_currency.id},
                'target': 'new',
                'nodestroy': True,
            }
        raise Warning('Bills have already been generated!')


class CRMLeadBill(models.Model):
    _name = 'crm.lead.bill'
    _description = 'CRM Lead Bills'

    name = fields.Char(
        string='Facturas')

    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Potencial Cliente',
        required=True,
        ondelete='cascade')

    customer_id = fields.Char(
        related='lead_id.customer_id',
        store=True)

    partner_id = fields.Many2one(
        related='lead_id.partner_id',
        store=True)

    dni_rnc = fields.Char(
        string=u'Cédula o RNC',
        required=True)

    planned_revenue = fields.Monetary(
        string='Valor de la Propiedad', 
        currency_field='currency_id',
        required=True)

    initial_advance = fields.Monetary(
        string='Monto a Plazos',
        currency_field='currency_id',
        required=True)

    payment_due = fields.Monetary(
        string='Monto Adeudado',
        currency_field='currency_id',
        required=True)

    amount_paid = fields.Monetary(
        string='Monto Pagado',
        currency_field='currency_id')

    bill_balance = fields.Monetary(
        string='Balance Actual',
        currency_field='currency_id')

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        required=True)

    due_date = fields.Date(
        string=u'Fecha Límite de Pago',
        required=True)

    bill_payment_ids = fields.One2many(
        comodel_name='crm.lead.bill.payment',
        inverse_name='bill_id',
        string='Detalle de Pagos por Factura')

    state = fields.Selection(
        [('pending','Pendiente'),('partial', 'Parcial'), ('paid','Pagado')],
        string='Estado', 
        default='pending')


    @api.model
    def create(self, values):
        bill = super(CRMLeadBill, self).create(values)
        bill.name = bill.id
        return bill

    """
    @api.multi
    def calculate_amounts(self):
        for bill in self:
            amount_paid = 0
            for payment in bill.bill_payment_ids:
                amount_paid += payment.amount_to_pay
            bill.amount_paid = amount_paid
            bill.bill_balance = bill.payment_due - amount_paid
            bill.state = 'pending'
            if amount_paid > 0:
                if bill.payment_due == amount_paid:
                    bill.state = 'paid'
                else:
                    bill.state = 'partial'
    """


class CRMLeadBillPayment(models.Model):
    _name = 'crm.lead.bill.payment'
    _description = 'CRM Lead Bill Payment'

    bill_id = fields.Many2one(
        comodel_name='crm.lead.bill',
        ondelete='cascade',
        string='Id de Factura',
        required=True)

    currency_id = fields.Many2one(
        related='bill_id.currency_id',
        store=True)

    transaction_code = fields.Char(
        string=u'Código del Banco',
        required=True)

    name = fields.Char(
        related='transaction_code',
        store=True)

    amount_to_pay = fields.Monetary(
        string='Monto Pagado',
        currency_field='currency_id',
        required=True)

    payment_date = fields.Date(
        string='Fecha de Pago',
        required=True)

    # bill fields
    lead_id = fields.Many2one(
        related='bill_id.lead_id',
        store=True)

    customer_id = fields.Char(
        related='bill_id.customer_id',
        store=True)

    partner_id = fields.Many2one(
        related='bill_id.partner_id',
        store=True)

    dni_rnc = fields.Char(
        related='bill_id.dni_rnc',
        store=True)

    planned_revenue = fields.Monetary(
        related='bill_id.planned_revenue',
        currency_field='currency_id',
        store=True)

    initial_advance = fields.Monetary(
        related='bill_id.initial_advance',
        currency_field='currency_id',
        store=True)

    payment_due = fields.Monetary(
        related='bill_id.payment_due',
        currency_field='currency_id',
        store=True)

    amount_paid = fields.Monetary(
        related='bill_id.amount_paid',
        currency_field='currency_id',
        store=False)

    bill_balance = fields.Monetary(
        related='bill_id.bill_balance',
        currency_field='currency_id',
        store=False)

    due_date = fields.Date(
        related='bill_id.due_date',
        store=True)

    state = fields.Selection(
        [('pending','Pendiente'),('partial', 'Parcial'), ('paid','Pagado')],
        related='bill_id.state',
        store=True)

    @api.model
    def create(self, values):
        payment = super(CRMLeadBillPayment, self).create(values)
        if payment:
            amount_paid = payment.amount_to_pay
            bill = self.env['crm.lead.bill'].browse(payment.bill_id.id)
            bill.amount_paid = bill.amount_paid + amount_paid
            bill.bill_balance = bill.payment_due - bill.amount_paid
            bill.sate = 'pending'
            if amount_paid > 0:
                if bill.bill_balance == 0.0:
                    bill.state = 'paid'
                else:
                    bill.state = 'partial'
        return payment
        