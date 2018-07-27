# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from lxml import etree
import datetime
from  dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, Warning

class CRMLeadWizard(models.TransientModel):
    _name = 'chimpex.crm.lead.wizard'
    _description = 'Chimpex CRM Lead Wizard'

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

    down_payment = fields.Monetary(
        string='Cuota Inicial',
        currency_field='currency_id',
        required=True)

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        required=True)

    quote_amount = fields.Integer(
        string='Cantidad de Cuotas',
        required=True, 
        default=1)

    start_date = fields.Date(
        string='Fecha de Inicio',
        required=True,
        default=datetime.datetime.today())

    interval = fields.Selection(
        [('month','Mensual'),('day', u'15 días')],
        string=u'Intérvalos',
        default='month',
        required=True)

    lead_wizard_lines = fields.One2many(
        comodel_name='chimpex.crm.lead.wizard.line',
        inverse_name='lead_wizard_id',
        string='Lead Wizard Lines'
    )


    """@api.model
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
        return result"""

    def generate_bills(self):
        lead_id = self._context.get('active_id')
        self.env['crm.lead.bill'].create({
            'lead_id':lead_id,
            'dni_rnc':self.dni_rnc,
            'planned_revenue':self.planned_revenue,
            'initial_advance':self.initial_advance,
            'currency_id':self.currency_id.id,
            'payment_due':self.down_payment,
            'bill_balance': self.down_payment,
            'due_date': datetime.datetime.today(),
        })
        if self.lead_wizard_lines:
            total_amount = sum(self.lead_wizard_lines.mapped('amount'))
            if self.initial_advance != total_amount:
                raise ValidationError(u'El Total de las cuotas debe ser igual al total a financiar')
            for line in self.lead_wizard_lines:
                self.env['crm.lead.bill'].create({
                        'lead_id':lead_id,
                        'dni_rnc':self.dni_rnc,
                        'planned_revenue':self.planned_revenue,
                        'initial_advance':self.initial_advance,
                        'currency_id':self.currency_id.id,
                        'payment_due':line.amount,
                        'bill_balance': line.amount,
                        'due_date': line.date,
                        })
        else:
            raise ValidationError(u'Cantidad debe ser mayor a 0')

            """
            amount = self.initial_advance / self.quote_amount
            counter = 0
            due_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')

            while (self.quote_amount >= counter):
                if counter == 0:
                    self.env['crm.lead.bill'].create({
                        'lead_id':lead_id,
                        'dni_rnc':self.dni_rnc,
                        'planned_revenue':self.planned_revenue,
                        'initial_advance':self.initial_advance,
                        'currency_id':self.currency_id.id,
                        'payment_due':self.down_payment,
                        'bill_balance': self.down_payment,
                        'due_date': due_date,
                        })

                else:
                    self.env['crm.lead.bill'].create({
                        'lead_id':lead_id,
                        'dni_rnc':self.dni_rnc,
                        'planned_revenue':self.planned_revenue,
                        'initial_advance':self.initial_advance,
                        'currency_id':self.currency_id.id,
                        'payment_due':amount,
                        'bill_balance': amount,
                        'due_date': due_date,
                        })
                if self.interval == 'month':
                    due_date = due_date + relativedelta(months=1)
                else:
                    due_date =  due_date + relativedelta(days=15)
                counter += 1

        else:
            return ValidationError(u'Cantidad debe ser mayor a 0')
        """
        return

class CRMLeadWizard(models.TransientModel):
    _name = 'chimpex.crm.lead.wizard.line'
    _description = 'Chimpex CRM Lead Wizard Lines'

    amount = fields.Monetary(
        string='Monto Adeudado',
        currency_field='currency_id',
        required=True
    )
    date = fields.Date(
        string='Fecha Límite de Pago',
        required=True
    )
    currency_id = fields.Many2one(
        related='lead_wizard_id.currency_id'
    )

    lead_wizard_id = fields.Many2one(
        comodel_name='chimpex.crm.lead.wizard',

    )