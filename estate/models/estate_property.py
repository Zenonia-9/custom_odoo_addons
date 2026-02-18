from odoo import _, api, fields, models, exceptions
from datetime import date
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = 'Real Estate Property'

    name = fields.Char(
        string='Name', 
        required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(
        string='Available From', 
        default=lambda self: date.today() + relativedelta(months=3), 
        copy=False)
    expected_price = fields.Float(
        string='Expected Price (USD)', 
        required=True)
    selling_price = fields.Float(
        string='Selling Price (USD)', 
        readonly=True, 
        copy=False)
    bedrooms = fields.Integer(
        string='Bedrooms', 
        default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area (sqm)')
    garden_orientation = fields.Selection(
        string='Garden Orientation', 
        selection=[('north', 'North'), 
                   ('south', 'South'), 
                   ('east', 'East'), 
                   ('west', 'West')])
    
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    state = fields.Selection(
        string='Status',
        selection=[('new', 'New'),
                   ('received', 'Offer Received'),
                   ('accepted', 'Offer Accepted'),
                   ('sold', 'Sold'),
                   ('cancelled', 'Cancelled')],
        required=True,
        copy=False,
        default='new',
        readonly=True
        )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    property_type_id = fields.Many2one(
        comodel_name='estate.property.type',
        string='Property Type')
    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
        readonly=True
    )
    salesman_id = fields.Many2one(
        "res.users",
        string="Salesman",
        default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many(
        comodel_name='estate.property.tag'
    )
    offer_ids = fields.One2many(
        comodel_name='estate.property.offer',
        inverse_name='property_id',
        string='Offers'
    )
    total_area = fields.Integer(compute='_compute_total_area')

    @api.depends('living_area', 'garden_area', 'garden')
    def _compute_total_area(self):
        for record in self:
            if record.garden:
                record.total_area = record.living_area + record.garden_area
            else:
                record.total_area = record.living_area

    def action_sold(self):
        for record in self:
            if record.state != 'cancelled':
                record.state = 'sold'
                return True
            else:
                raise exceptions.UserError(message="Cancelled properties cannot be sold.")
    
    def action_cancle(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'cancelled'
                return True
            else:
                raise exceptions.UserError(message="Sold properties cannot be cancel.")