from datetime import timedelta
from odoo import _, api, fields, models

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'

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

    validity = fields.Integer(
        string='Validity (days)',
        default=7
        )
    date_deadline = fields.Date(
        string='Deadline', 
        compute='_compute_date_deadline', 
        inverse='_inverse_date_deadline'
        )

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
                'selling_price': offer.price
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

            accepted = False
            for other_offer in other_offers:
                if other_offer.status == 'accepted':
                    accepted = True
                else:
                    continue

            if not accepted:
                offer.property_id.write({
                    'buyer_id': None,
                    'selling_price': None
            })

        return True