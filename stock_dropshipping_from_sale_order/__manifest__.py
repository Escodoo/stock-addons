# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Dropshipping From Sale Order',
    'summary': """
        Route for dropshipping from sale order.""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'website': 'www.escodoo.com.br',
    'depends': [
        'sale',
        'stock',
        'stock_picking_sale_order_link',
    ],
    'data': [
        'views/stock_location_route.xml',
        'views/sale_order.xml',
        'data/stock_data.xml',
    ],''
    'demo': [
    ],
}
