from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError, UserError
from datetime import date
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = 'Real Estate Property'
    _order = 'id desc'
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)',
        'The Expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
        'The Selling price must be positive.')
    ]
    
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
    best_price = fields.Float(compute='_compute_best_price')
    total_area = fields.Integer(compute='_compute_total_area')


    @api.depends('offer_ids', 'offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.mapped('offer_ids.price'))
            else:
                record.best_price = 0

    @api.depends('living_area', 'garden_area', 'garden')
    def _compute_total_area(self):
        for record in self:
            if record.garden:
                record.total_area = record.living_area + record.garden_area
            else:
                record.total_area = record.living_area

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.constrains('selling_price', 'expected_price', 'buyer_id')
    def _check_selling_price(self):
        for record in self:
            if record.buyer_id and (float_compare(record.selling_price, record.expected_price * 0.9, 2) < 0):
                raise ValidationError(message="Selling price must be at least 90% of expected price! You must reduce the expected price if you want to accept this offer.")
    
    @api.ondelete(at_uninstall=False)
    def _check_state_before_delete(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError(
                    "You can only delete properties in New or Cancelled state."
                )
            
    def action_sold(self):
        for record in self:
            if record.state != 'cancelled':
                record.state = 'sold'
                return True
            else:
                raise UserError(message="Cancelled properties cannot be sold.")
    
    def action_cancle(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'cancelled'
                return True
            else:
                raise UserError(message="Sold properties cannot be cancel.")
