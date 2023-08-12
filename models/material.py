from odoo import models, fields, api, _
from datetime import date, datetime
from openerp.exceptions import except_orm, UserError, Warning, ValidationError
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from datetime import date, datetime, timedelta, time

_STATE = [
    ('draft','New'),
    ('vendor','Vendor'),
    ('to_approve','Waiting to Approve'),
    ('done','Done'),
    ('cancel','Canceled'),
]

class MaterialCreationRequest(models.Model):
    _name = 'material.creation.request'
    _description = "Material Creation Request Modul"
    _order = 'created_date DESC'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price > 100.0:
                raise ValidationError(_("Price limited in 100!"))
    
    @api.depends('code')
    def _get_code(self):
        for rec in self:
            if rec.code:
                rec.name = rec.code
            else:
                rec.name = None
    
    def _get_partner(self):
        for rec in self:
            rec.is_partner = False
            if rec.partner_id:
                rec.is_partner = True
    
    code = fields.Char(string="Code", default=lambda self: _('New'))
    name = fields.Char(string='Name', compute='_get_code')
    material_name = fields.Char(string='Name')
    created_date = fields.Datetime(string='Created Date',default=fields.Datetime.now,)
    material_type = fields.Selection(
        string='Material Type',
        selection=[('fabric', 'Fabric'), ('jeans', 'Jeans'), ('cotton', 'Cotton')]
    )
    state = fields.Selection(_STATE, string='Status', default='draft')
    price = fields.Float(string='Price')
    is_new_vendor = fields.Boolean(string='New Vendor')
    is_partner = fields.Boolean(compute='_get_partner')
    suplier_id = fields.Many2one(comodel_name='material.suplier', string='Suplier')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    suplier_ids = fields.One2many(comodel_name='material.suplier', inverse_name='mcr_id', string='REF TO LINE')
    
    @api.model
    def create(self, values):
        if not values.get('code', False) or values['code'] == _('New'):
            values['code'] = self.env['ir.sequence'].next_by_code('material.creation.seq') or _('New')
        seq_name = super(MaterialCreationRequest, self).create(values)
        return seq_name
    
    def action_submit(self):
        self.write({'state': 'vendor'})
        
    def add_suplier(self):
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id('material_creation_request.submit_vendor_wizards_view')
        result =  {
            'name': 'Submit Suplier',
            'type': 'ir.actions.act_window',
            'views': [[form_view_id, 'form']],
            'target': 'new',
            'res_model': 'create.suplier.wizard'
        }
        return result
    
    def to_approve(self):
        if not self.suplier_ids:
            raise ValidationError(_("Suplier must be Submited !"))
        else:
            self.write({'state': 'to_approve'}) 
    
    def select_suplier(self):
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id('material_creation_request.choose_sup_wizards_view')
        result =  {
            'name': 'Submit Suplier',
            'type': 'ir.actions.act_window',
            'views': [[form_view_id, 'form']],
            'target': 'new',
            'res_model': 'choose.suplier'
        }
        return result 
    
    def action_cancel(self):
        self.write({'state': 'cancel'}) 
    
    def set_to_draft(self):
        self.write({'state': 'draft'})
    
    def create_partner(self):
        for rec in self:
            partner_obj = self.env['res.partner']
            vals = {
                'name': rec.suplier_id.name,
                'street': rec.suplier_id.street,
                'street2': rec.suplier_id.street2,
                'zip': rec.suplier_id.zip,
                'city': rec.suplier_id.city,
                'phone': rec.suplier_id.phone,
                'mobile': rec.suplier_id.mobile,
                'email': rec.suplier_id.email,
                'website': rec.suplier_id.website,
                'state_id': rec.suplier_id.state_id.id,
                'country_id': rec.suplier_id.country_id.id,
            }
            partner_id = partner_obj.create(vals)
            if partner_id:
                self.write({'partner_id': partner_id.id})
    
class MaterialSuplier(models.Model):
    _name = 'material.suplier'
    _description = "Material Suplier Line"
    
    mcr_id = fields.Many2one(comodel_name='material.creation.request', string="REF TO HEADER")
    is_new_vendor = fields.Boolean(string='New Vendor')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Suplier')
    name = fields.Char(string='Nama Suplier')
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