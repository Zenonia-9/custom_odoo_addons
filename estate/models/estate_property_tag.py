from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'
    _order = 'tag'
    _rec_name = 'tag'
    _sql_constraints = [
        ('unique_tag', 'UNIQUE(tag)',
         'The Tag must be UNIQUE.')
    ]

    tag = fields.Char(required=True)
    color = fields.Integer()
