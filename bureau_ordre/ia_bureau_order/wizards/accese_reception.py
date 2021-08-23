# -*- coding: utf-8 -*-

from odoo import models, fields, api


class accese_reception(models.TransientModel):


    _name = "create.accese"

    date_eccese = fields.Date(
        string='Date accuse de reception', default=fields.Date.today,
        required=False)
    parent_id = fields.Many2one(
        comodel_name='bureau.order',
        string='Parent_id',
        required=False,

    )

    @api.multi
    def create_date_accese(self):
        self.parent_id.date_eccese_form =self.date_eccese
        self.parent_id.state_emission = 'accese_reeption'




