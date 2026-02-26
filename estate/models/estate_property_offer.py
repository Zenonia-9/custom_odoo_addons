from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)',
         'The Offer price must be strictly positive.')
    ]

    price = fields.Float()
    status = fields.Selection(
        selection=[('accepted', 'Accepted'),
                   ('refused', 'Refused')
                   ],
        copy=False,
        readonly=True
    )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    property_type_id = fields.Many2one(
        "estate.property.type",
        related="property_id.property_type_id",
        store=True
    )
    validity = fields.Integer(
        string='Validity (days)',
        default=7
        )
    date_deadline = fields.Date(
        string='Deadline', 
        compute='_compute_date_deadline', 
        inverse='_inverse_date_deadline'
        )
    
    @api.model
    def create(self, vals):

        property_id = vals.get('property_id')
        price = vals.get('price')

        property_obj = self.env['estate.property'].browse(property_id)

        existing_offers = property_obj.offer_ids

        if existing_offers:
            max_price = max(existing_offers.mapped('price'))
            if price <= max_price:
                raise UserError(
                    "The offer must be higher than existing offers."
                )

        if property_obj.state == 'new':
            property_obj.state = 'offer_received'

        return super().create(vals)
    
    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            create_date = (record.create_date or fields.Date.today())
            record.date_deadline = create_date + timedelta(days=record.validity)
    
    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.today()
            if record.date_deadline:
                record.validity = (record.date_deadline - create_date.date()).days

    def action_accept(self):
        for offer in self:
            offer.property_id.write({
                'buyer_id': offer.partner_id.id,
                'selling_price': offer.price,
                'state' : 'accepted'
            })
            offer.status = 'accepted'

            other_offers = self.search([
                ('property_id', '=', offer.property_id.id),
                ('id', '!=', offer.id)
            ])

            other_offers.write({'status': 'refused'})
        return True

    def action_refuse(self):
        for offer in self:
            offer.status = 'refused'
            other_offers = self.search([
                ('property_id', '=', offer.property_id.id),
                ('id', '!=', offer.id)
            ])

            accepted = True if 'accepted' in other_offers.mapped('status') else False

            if not accepted:
                offer.property_id.write({
                    'buyer_id': None,
                    'selling_price': 0,
            })

        return True
    