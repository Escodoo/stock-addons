# Copyright 2020 Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StockLocationRoute(models.Model):

    _inherit = 'stock.location.route'

    directsale = fields.Boolean(
        string='Direct Sale',
        default=False
    )