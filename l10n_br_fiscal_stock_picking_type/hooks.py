# Copyright 2026 Escodoo - Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Create the fiscal picking types for the warehouses that already exist.

    Warehouses created afterwards get them from stock.warehouse.create().
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    warehouses = env["stock.warehouse"].search([])
    warehouses._create_fiscal_picking_types()
    _logger.info("Fiscal picking types created for %s warehouse(s).", len(warehouses))
