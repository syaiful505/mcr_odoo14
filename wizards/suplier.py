from odoo import models, fields, api, _
from openerp.exceptions import except_orm, UserError, Warning, ValidationError

class CreateSuplier(models.TransientModel):
    _name = 'create.suplier.wizard'
    _description = 'This is models for Create vendor'
    
    @api.model
    def _get_active(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            mcr_obj = self.env['material.creation.request'].browse(active_id)
            return mcr_obj  
    
    mcr_active_id = fields.Many2one(comodel_name='material.creation.request', string='MCR ACTIVE', default=_get_active)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Vendor')
    is_new_vendor = fields.Boolean(string='New Vendor')
    new_partner_name = fields.Char(string='Name', )
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City',  store=True)
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country',)
    phone = fields.Char('Phone', tracking=50)
    mobile = fields.Char('Mobile')
    email = fields.Char('Email', help="Email address of the contact", tracking=40,)
    website = fields.Char('Website', index=True, help="Website of the contact")
    
    def action_submit(self):
        for rec in self:
            suplier_obj = self.env['material.suplier']
            if rec.is_new_vendor == False:
                vals = {
                    'mcr_id': rec.mcr_active_id.id,
                    'is_new_vendor': rec.is_new_vendor,
                    'partner_id': rec.partner_id.id,
                    'name': rec.partner_id.name,
                }
                suplier_obj.create(vals)
            else:
                
                if not rec.new_partner_name or not rec.phone or not rec.email:
                    raise ValidationError(_(" Name OR phone OR email must be inputed!"))
                
                value = {
                    'mcr_id': rec.mcr_active_id.id,
                    'is_new_vendor': rec.is_new_vendor,
                    'new_partner_name': rec.new_partner_name,
                    'name': rec.new_partner_name,
                    'street': rec.street,
                    'street2': rec.street2,
                    'city': rec.city,
                    'phone': rec.phone,
                    'mobile': rec.mobile,
                    'email': rec.email,
                    'website': rec.website,
                    'website': rec.website,
                    'state_id': rec.state_id.id,
                    'country_id': rec.country_id.id,
                }
                suplier_obj.create(value)

class ChooseSuplier(models.TransientModel):
    _name = 'choose.suplier'
    _description = "Choose Suplier"
    
    @api.model
    def _get_active(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            mcr_obj = self.env['material.creation.request'].browse(active_id)
            return mcr_obj  
    
    mcr_active_id = fields.Many2one(comodel_name='material.creation.request', string='MCR ACTIVE', default=_get_active)
    suplier_id = fields.Many2one(comodel_name='material.suplier', string='Suplier')
    is_new_vendor = fields.Boolean(string='New Vendor', related="suplier_id.is_new_vendor")

    
    def action_approve(self):
        vals = {
            'suplier_id': self.suplier_id.id,
            'is_new_vendor': self.is_new_vendor,
            'state': 'done'
        }
        self.mcr_active_id.write(vals)