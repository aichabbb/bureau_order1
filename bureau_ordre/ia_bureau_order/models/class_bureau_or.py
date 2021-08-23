# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)



from odoo import models, fields, api

from odoo.exceptions import UserError
from odoo import exceptions
from . import message_genre


class piece_joint(models.Model):
    _name = 'piece.joint2'
    _rec_name = 'nompiece'

    nompiece = fields.Char(string='Nom')


class pecej(models.Model):
    _name = 'piece.joint'
    _rec_name = 'emition_id'

    nom = fields.Many2one(
        comodel_name='piece.joint2',
        string='nom',
        required=True)

    emition_id = fields.Many2one(
        comodel_name='bureau.order',
        string='sequence',
        required=True,  invisible=True)

    npj = fields.Integer(string="nombre", default='1')
    Remarque = fields.Char()
    designation = fields.Char(string="Designation")

    @api.onchange('nom')
    def _onchange(self):
        self.designation = self.nom.nompiece



class bureauOrder(models.Model):
    _name = 'bureau.order'
    _rec_name = 'sequence'
    _description = 'bureau order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    Destinataire = fields.Many2one(
        comodel_name='hr.employee',
        string='destiné à',
        required=False)

    origin_emission = fields.Many2one(
        comodel_name='hr.employee',
        string='origine ',
        required=False)

    Objet = fields.Text()

    state = fields.Selection(
        [

            ('Brouillon', 'Brouillon'),
            ('valider', 'Validé'),
            ('approver', 'Approuvé'),
            ('refusé', 'Refusé'),

        ],
        default="Brouillon",

        track_visibility='onchange',

    )



    origine = fields.Many2one(
        comodel_name='res.partner',
        string='Origin',
        required=False)

    date_eccese_form = fields.Date(
        string='Date accuse de reception',
        required=False)
    destinataire_emmision = fields.Many2one(
        comodel_name='res.partner',
        string='Destinataire ',
        required=False)

    date = fields.Date(required=False, string='Date')

    Remarque = fields.Char()
    reception_id = fields.Many2one(
        comodel_name='reception',
        string='Reception ',
    )

    active = fields.Boolean('Active', default=True)


    motive_refuser_form = fields.Text(
        string="motive de refuser",
        required=False)





    piece_ligne = fields.One2many(
        comodel_name='piece.joint',
        inverse_name='emition_id',
        string='piece joint')


    state_emission = fields.Selection(
        [
            ('Brouillon', 'Brouillon'),
            ('valider', 'Validé'),
            ('accese_reeption', 'Accusé de réception'),


        ],
        default="Brouillon",

        track_visibility='onchange',

    )

    in_reception = fields.Boolean(
        string=' in_reception',
        required=False)

    sequence = fields.Char(string="sequence", default='New', readonly=True)

    def create_email(self):
        if self.Destinataire.work_email:
            self.send_email_to_golbal(self.Destinataire.work_email, self.origine.email,
                                      message_genre.message_email + self.origine.name, message_genre.message_email,button_valider=True,type_bureau='Reception')

        #     template_values = {
        #         'email_from': self.env.user.email,
        #         'email_to': self.Destinataire.work_email,
        #         'email_cc': False,
        #         'partner_to': False,
        #         'scheduled_date': False,
        #     }
        #     gamma_template = self.env.ref('ia_bureau_order.bureau_cart_email')
        #     gamma_template.write(template_values)
        #     with self.env.cr.savepoint():
        #         gamma_template.send_mail(self.id, force_send=True, raise_exception=True)
        else:

            raise UserError((message_genre.bureau_order_create_email) % self.Destinataire.name)

    @api.multi
    def action_send_valider_reception(self):
        message = []
        if not self.piece_ligne:
            message.append('piece joint')

        if not self.date:
            message.append('date')

        if message:
            msg = message_genre.bureau_order_action_send_valider_reception % ('\n- '.join(map(str, message)))
            raise exceptions.ValidationError(msg)
        self.avtiviter_reception()

        self.state = 'valider'

    def avtiviter_reception(self):

        if self.Destinataire.user_id.id:
            user_id = self.Destinataire.user_id.id
            ext = self.env.ref('ia_bureau_order.model_bureau_order').id
            self.activity_ids.create(
                {'activity_type_id': 4, 'res_id': self.id, 'user_id': user_id,
                 'res_model_id': ext,
                 'date_deadline': self.date,
                 'note': 'les courriers valider'
                 })
        elif self.Destinataire.parent_id.user_id.id:
            user_id = self.Destinataire.parent_id.user_id.id
            ext = self.env.ref('ia_bureau_order.model_bureau_order').id
            self.activity_ids.create(
                {'activity_type_id': 4, 'res_id': self.id, 'user_id': user_id,
                 'res_model_id': ext,
                 'date_deadline': self.date,
                 'note': 'les courriers valider'
                 })
        else:
            raise UserError(
                (
                    message_genre.bureau_order_avtiviter_reception) % self.Destinataire.name)

        self.create_email()

    @api.multi
    def action_send_aprouver(self):
        if self.create_uid.email:
            self.send_email_to_golbal(self.create_uid.email, self.Destinataire.work_email, message_genre.message_email_approuver + self.Destinataire.name, message_genre.subject_email_approuver,type_bureau='Reception')

            # template_values = {
            #     'email_from': self.Destinataire.work_email,
            #     'email_to': self.env.user.email,
            #     'email_cc': False,
            #     'partner_to': False,
            #     'scheduled_date': False,
            # }
            # gamma_template = self.env.ref('ia_bureau_order.bureau_reception_approuver')
            # gamma_template.write(template_values)
            # with self.env.cr.savepoint():
            #     gamma_template.send_mail(self.id, force_send=True, raise_exception=True)
        else:

            raise UserError(
                (
                    message_genre.bureau_order_avtiviter_reception) % self.create_uid.name)

        self.state = 'approver'

    @api.model
    def create(self, vals):
        result = super(bureauOrder, self).create(vals)
        if vals.get('in_reception'):
            result.sequence = self.env['ir.sequence'].next_by_code('bureau.reception')
        else:
            result.sequence = self.env['ir.sequence'].next_by_code('bureau.emission')

        return result

    @api.multi
    def action_send_mettre(self):
        self.state = ''

    @api.multi
    def action_send_refusé(self):
        if self.create_uid.email:
            self.send_email_to_golbal(self.create_uid.email, self.Destinataire.work_email, message_genre.message_email_refuser + self.Destinataire.name, message_genre.subject_email_refuser,type_bureau='Reception')

            # template_values = {
            #     'email_from': self.Destinataire.work_email,
            #     'email_to': self.env.user.email,
            #     'email_cc': False,
            #     'partner_to': False,
            #     'scheduled_date': False,
            # }
            # gamma_template = self.env.ref('ia_bureau_order.bureau_refesu_email')
            # gamma_template.write(template_values)
            # with self.env.cr.savepoint():
            #     gamma_template.send_mail(self.id, force_send=True, raise_exception=True)
            #
        else:
            raise UserError(
                (
                    message_genre.bureau_order_avtiviter_reception) % self.create_uid.name)



    @api.multi
    def action_send_valider_emision(self):

        message_list = []
        if not self.piece_ligne:
            message_list.append(message_genre.bureau_order_piece_joint)

        if not self.date:
            message_list.append(message_genre.bureau_order_date)

        if message_list:
            msg = message_genre.bureau_order_action_send_valider_reception % ('\n- '.join(map(str, message_list)))
            raise exceptions.ValidationError(msg)
        self.activity_email_emission()

        self.state_emission = 'valider'


    def email_accese_reception_E(self):

         if self.origin_emission.work_email:
            self.send_email_to_golbal(self.origin_emission.work_email,self.create_uid.email , message_genre.message_email_accuser_reception + self.destinataire_emmision.name, message_genre.message_subjet_email,button_accuser_reception_valider=True,type_bureau='Emission')

        #     template_values = {
        #         'email_from': self.destinataire_emmision.email,
        #         'email_to': self.create_uid.email,
        #         'email_cc': False,
        #         'partner_to': False,
        #         'scheduled_date': False,
        #     }
        #     gamma_template = self.env.ref('ia_bureau_order.bureau_accese_reeption_E')
        #     gamma_template.write(template_values)
        #     with self.env.cr.savepoint():
        #         gamma_template.send_mail(self.id, force_send=True, raise_exception=True)
        #
         else:

             raise UserError(

                 (
                     message_genre.bureau_order_create_email) % self.destinataire_emmision.name)



    def email_emisiion(self):

        if self.origin_emission.work_email:
            self.send_email_to_golbal(self.origin_emission.work_email,self.env.user.email , message_genre.message_email_valider_emission + self.destinataire_emmision.name, message_genre.message_subjet_valider_emission,type_bureau='Emission')

        #     template_values = {
        #         'email_from': self.destinataire_emmision.email,
        #         'email_to': self.env.user.email,
        #         'email_cc': False,
        #         'partner_to': False,
        #         'scheduled_date': False,
        #     }
        #     gamma_template = self.env.ref('ia_bureau_order.bureau_valider_email_emission')
        #     gamma_template.write(template_values)
        #     with self.env.cr.savepoint():
        #         gamma_template.send_mail(self.id, force_send=True, raise_exception=True)
        #
        else:

             raise UserError(

                 (
                     message_genre.bureau_order_create_email) % self.origin_emission.name)

    @api.multi
    def action_send_mettre_emission(self):

        self.state_emission = 'Brouillon'

    @api.model
    def activity_email_emission(self):
        # USER = self.env['res.users'].search([('partner_id', '=', self.destinataire_emmision.id)])
        # user_id = self.origin_emission.id
        # if user_id:
        # if self.origin_emission.user_id.id:
        #     user_id = self.origin_emission.user_id.id
        #
        #     ext = self.env.ref('ia_bureau_order.model_bureau_order').id
        #     self.activity_ids.create(
        #         {'activity_type_id': 4, 'res_id': self.id, 'user_id': user_id,
        #          'res_model_id': ext,
        #          'date_deadline': self.date,
        #          'note': 'les courriers valider'
        #          })
        #     self.email_emisiion()
        #
        #
        # else:
        #     self.email_emisiion()

        self.email_emisiion()

    @api.multi
    def creat_wizart(self):
        self.activiter_acuser_reception()
        self.email_accese_reception_E()

        return {
            'name': 'Confirmation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.accese',
            'context': {'default_parent_id': self.id},
            'view_id': False,
            'target': 'new',
            'nodestroy': True,
        }











    def activiter_acuser_reception(self):

        if self.origin_emission.user_id.id:
            user_id = self.origin_emission.user_id.id
            ext = self.env.ref('ia_bureau_order.model_bureau_order').id
            self.activity_ids.create(
                {'activity_type_id': 4, 'res_id': self.id, 'user_id': user_id,
                 'res_model_id': ext,
                 'date_deadline': self.date,
                 'note': 'les courriers valider'
                 })
        elif self.origin_emission.parent_id.user_id.id:
            user_id = self.Destinataire.parent_id.user_id.id
            ext = self.env.ref('ia_bureau_order.model_bureau_order').id
            self.activity_ids.create(
                {'activity_type_id': 4, 'res_id': self.id, 'user_id': user_id,
                 'res_model_id': ext,
                 'date_deadline': self.date,
                 'note': 'les courriers valider'
                 })
        else:
            raise UserError(
                (
                    message_genre.bureau_order_avtiviter_reception) % self.origin_emission.name)



    @api.multi
    def unlink(self):
        for list in self:
            if (list.state != 'Brouillon' and list.in_reception == True) or (list.state_emission != 'Brouillon' and list.in_reception == False):
                if (len(list.piece_ligne) > 0) or (len(list.piece_ligne) < 0):
                    list.active = False
            elif (list.state == 'Brouillon' and list.in_reception == True) or (list.state_emission == 'Brouillon' and list.in_reception == False):
                if len(list.piece_ligne) > 0:
                    self.env['piece.joint'].search([('emition_id', 'in', self.ids)]).unlink()
                    res = super(bureauOrder, self).unlink()
                    return res
                if len(list.piece_ligne) < 0:
                    resultat = super(bureauOrder, self).unlink()
                    return resultat

    @api.multi
    def send_email_to_golbal(self, mail_to, mail_form, body_msg, subject_mail,button_valider=False,button_accuser_reception_valider=False,type_bureau=''):

        template = self.env.ref('ia_bureau_order.bureau_cart_email')
        local_context = self.env.context.copy()
        local_context.update({
            'msg_body': body_msg,
            'subject': subject_mail,
            'b_valider': button_valider,
            'acuser_r_valider': button_accuser_reception_valider,
            'type': type_bureau,

        })
        template_values = {
            'email_from': mail_form,
            'email_to': mail_to,

        }


        with self.env.cr.savepoint():
            template.with_context(local_context).send_mail(self.id, force_send=True, raise_exception=True,
                                                           email_values=template_values)



    @api.multi
    def creat_wizart_motive_refuser(self):
        self.action_send_refusé()
        return {
            'name': 'Confirmation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'motive.refuser',
            'context': {'default_motive_id': self.id},
            'view_id': False,
            'target': 'new',
            'nodestroy': True,
        }



