from odoo import _, api, fields, models

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'
    _rec_name = 'tag'

    tag = fields.Char(required=True)