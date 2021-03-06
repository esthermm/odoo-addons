# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona- AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import fields
from dateutil.relativedelta import relativedelta


class TestAccountAnalyticPayment(common.TransactionCase):

    def setUp(self):
        super(TestAccountAnalyticPayment, self).setUp()
        self.analytic_model = self.env['account.analytic.account']
        self.invoice_model = self.env['account.invoice']
        self.pay_mode = self.env.ref(
            'account_banking_payment_export.payment_mode_2')
        self.partner = self.env.ref('base.res_partner_2')
        self.partner.customer_payment_mode = self.pay_mode
        self.partner.property_payment_term = (
            self.ref('account.account_payment_term_15days'))
        analytic_vals = {
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'recurring_next_date':
            (fields.Date.from_string(fields.Date.today()) -
             relativedelta(months=1)),
            'state': 'open',
            }
        self.contract = self.analytic_model.create(analytic_vals)
        self.contract2 = self.env.ref('account.analytic_support_internal')
        self.contract2.partner_id = self.partner

    def test_invoice_payment_mode(self):
        inv_vals = self.analytic_model._prepare_invoice(self.contract)
        self.assertEqual(
            inv_vals.get('payment_mode_id', False),
            self.pay_mode.id, 'Invoice Payment Mode is not correct.')

    def test_contract_to_invoice(self):
        res_id = self.contract2._recurring_create_invoice()
        invoice = self.invoice_model.browse(res_id)
        self.assertEqual(
            self.partner.customer_payment_mode, invoice.payment_mode_id)
        self.assertEqual(self.partner.customer_payment_mode.bank_id,
                         invoice.partner_bank_id)
        self.assertEqual(self.partner.property_payment_term,
                         invoice.payment_term)
