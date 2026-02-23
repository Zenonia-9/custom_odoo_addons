from odoo import api, fields, models

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'
    _rec_name = 'property_type'

    _sql_constraints = [
        ('unique_property_type', 'UNIQUE(property_type)',
         'The Property type must be UNIQUE.')
    ]
    _order = 'property_type'

    property_type = fields.Char(required=True)
    property_ids = fields.One2many(
        comodel_name='estate.property', 
        inverse_name='property_type_id')
    
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")

    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_type_id",
        string="Offers"
    )
    offer_count = fields.Integer(
        compute="_compute_offer_count"
    )

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)