# -*- coding: utf-8 -*-
# © 2018 Tosin Komolafe <http://tosinkomolafe.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from lxml import etree
import datetime
from  dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class CRMLeadWizard(models.TransientModel):
    _name = 'chimpex.crm.lead.wizard'
    _description = 'Chimpex CRM Lead Wizard'

    dni_rnc = fields.Char(
        string='DNI/RNC',
        required=True)

    planned_revenue = fields.Monetary(
        string='Property Value', 
        currency_field='currency_id',
        required=True)

    initial_advance = fields.Monetary(
        string='Initial Advance',
        currency_field='currency_id',
        required=True)

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True)

    quote_amount = fields.Integer(
        string='Amount of Quotes',
        required=True, 
        default=1)

    start_date = fields.Date(
        string='Starting Date',
        required=True,
        default=datetime.datetime.today())

    interval = fields.Selection(
        [('month','Monthly'),('day', '15 Days')],
        string='Periodicity',
        default='month',
        required=True)


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(CRMLeadWizard, self).fields_view_get(view_id=view_id,
                                                           view_type=view_type,
                                                           toolbar=toolbar,
                                                           submenu=submenu)


        partner_id = self._context.get('active_id')
        if view_type == 'form':
            view_obj = etree.XML(result['arch'])
            elements = []
            update_fields = {}
            result['fields'].update(update_fields)
            result['arch'] = etree.tostring(view_obj)
        return result

    def generate_bills(self):
        lead_id = self._context.get('active_id')
        if self.quote_amount > 0:
            amount = self.initial_advance / self.quote_amount
            counter = 0
            due_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
            while (self.quote_amount > counter):
                self.env['crm.lead.bill'].create({
                    'lead_id':lead_id,
                    'dni_rnc':self.dni_rnc,
                    'planned_revenue':self.planned_revenue,
                    'initial_advance':self.initial_advance,
                    'currency_id':self.currency_id.id,
                    'payment_due':amount,
                    'due_date': due_date,
                    })
                if self.interval == 'month':
                    due_date = due_date + relativedelta(months=1)
                else:
                    due_date =  due_date + relativedelta(days=15)
                counter += 1

        else:
            return ValidationError('Amount must be greater an zero!')

        return

