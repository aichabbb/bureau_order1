# -*- coding: utf-8 -*-

from odoo import models, fields, api


class motiverefuser(models.TransientModel):


    _name = "motive.refuser"

    motive_refuser = fields.Text(
       string="Motive de refuser",
       required=False)
    motive_id = fields.Many2one(
        comodel_name='bureau.order',
        string='motive_id',
        required=False,

    )

    @api.multi
    def create_date_accese(self):
        self.motive_id.motive_refuser_form = self.motive_refuser
        self.motive_id.state = 'refusé'







