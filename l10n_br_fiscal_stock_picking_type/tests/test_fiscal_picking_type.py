# Copyright 2026 Escodoo - Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFiscalPickingType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type_model = cls.env["stock.picking.type"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.fiscal_types = cls.warehouse._get_fiscal_picking_types()

    def _fiscal_picking_types(self, warehouse):
        return self.picking_type_model.search(
            [
                ("warehouse_id", "=", warehouse.id),
                ("fiscal_operation_id", "!=", False),
            ]
        )

    def test_post_init_created_picking_types(self):
        """The hook created one picking type per fiscal operation."""
        picking_types = self._fiscal_picking_types(self.warehouse)
        self.assertEqual(len(picking_types), len(self.fiscal_types))

        by_code = {p.sequence_code: p for p in picking_types}
        for values in self.fiscal_types:
            picking_type = by_code.get(values["sequence_code"])
            self.assertTrue(
                picking_type,
                "missing picking type for %s" % values["sequence_code"],
            )
            self.assertEqual(picking_type.code, values["code"])
            self.assertEqual(
                picking_type.fiscal_operation_id,
                self.env.ref(values["fiscal_operation"]),
            )
            self.assertTrue(picking_type.sequence_id)

    def test_locations_follow_direction(self):
        """Incoming types come from the supplier, outgoing go to the customer."""
        customer_loc, supplier_loc = self.warehouse._get_partner_locations()
        for picking_type in self._fiscal_picking_types(self.warehouse):
            if picking_type.code == "incoming":
                self.assertEqual(picking_type.default_location_src_id, supplier_loc)
                self.assertEqual(
                    picking_type.default_location_dest_id, self.warehouse.lot_stock_id
                )
            else:
                self.assertEqual(
                    picking_type.default_location_src_id, self.warehouse.lot_stock_id
                )
                self.assertEqual(picking_type.default_location_dest_id, customer_loc)

    def test_new_warehouse_gets_picking_types(self):
        """A warehouse created later also gets the fiscal picking types."""
        warehouse = self.env["stock.warehouse"].create(
            {"name": "WH Fiscal Test", "code": "WHFT"}
        )
        self.assertEqual(
            len(self._fiscal_picking_types(warehouse)), len(self.fiscal_types)
        )

    def test_creation_is_idempotent(self):
        """Running the creation again does not duplicate the picking types."""
        before = self._fiscal_picking_types(self.warehouse)
        self.warehouse._create_fiscal_picking_types()
        self.assertEqual(self._fiscal_picking_types(self.warehouse), before)
