from odoo import fields, models
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
    state = fields.Selection(
        string='Status',
        selection=[('new', 'New'),
                   ('received', 'Offer Received'),
                   ('accepted', 'Offer Accepted'),
                   ('sold', 'Sold'),
                   ('cancelled', 'Cancelled')],
        required=True,
        copy=False,
        default='new')
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
        copy=False
    )
    salesman_id = fields.Many2one(
        "res.users",
        string="Salesman",
        default=lambda self: self.env.user
    )