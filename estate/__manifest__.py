{
    'name' : 'Real Estate',
    'version' : '1.0',
    'category' : 'Sales',
    'summary' : 'Manage real estate properties',
    'author' : 'Elliot',
    'depends' : ['base'], # required
    'data' : [
        'security\ir.model.access.csv',
        'views\estate_property_views.xml',     
        'views\estate_property_type_view.xml',
        'views\estate_property_tag_view.xml',
        'views\estate_menus.xml'
    ],
    'installable' : True,
    'application' : True,
    'license' : 'LGPL-3'
} # type: ignore