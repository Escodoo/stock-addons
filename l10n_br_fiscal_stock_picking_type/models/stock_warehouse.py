# Copyright 2026 Escodoo - Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def _get_fiscal_picking_types(self):
        """Picking types created for each warehouse, one per fiscal operation.

        The direction comes from the fiscal operation itself: "Retorno de
        mercadoria ou bem remetido para conserto ou reparo" is an outgoing
        operation, since it is the repaired good going back to the customer.

        Meant to be overriden to add or remove operations.
        """
        return [
            {
                "fiscal_operation": "l10n_br_fiscal.fo_simples_remessa",
                "name": _("Simples Remessa"),
                "code": "internal",
                "sequence_code": "SR",
            },
            {
                "fiscal_operation": "l10n_br_fiscal.fo_remessa_industrializacao",
                "name": _("Remessa para Industrialização"),
                "code": "outgoing",
                "sequence_code": "RI",
                "return_to": "EI",
            },
            {
                "fiscal_operation": "l10n_br_fiscal.fo_entrada_industrializacao",
                "name": _("Retorno de Industrialização"),
                "code": "incoming",
                "sequence_code": "EI",
                "return_to": "RI",
            },
            {
                "fiscal_operation": "l10n_br_fiscal.fo_retorno_reparo",
                "name": _("Retorno de Conserto ou Reparo"),
                "code": "outgoing",
                "sequence_code": "RR",
                "return_to": "EMR",
            },
            {
                "fiscal_operation": "l10n_br_fiscal.fo_entrada_reparo",
                "name": _("Entrada para Conserto ou Reparo"),
                "code": "incoming",
                "sequence_code": "EMR",
                "return_to": "RR",
            },
        ]

    def _get_fiscal_picking_type_values(self, values, max_sequence):
        """Return the values to create one fiscal picking type, mirroring what
        stock.warehouse does for the picking types of the core."""
        self.ensure_one()
        customer_loc, supplier_loc = self._get_partner_locations()
        code = values["code"]
        if code == "incoming":
            src_loc, dest_loc = supplier_loc, self.lot_stock_id
        elif code == "outgoing":
            src_loc, dest_loc = self.lot_stock_id, customer_loc
        else:
            # Internal transfers stay inside the warehouse.
            src_loc = dest_loc = self.lot_stock_id
        return {
            "name": values["name"],
            "code": code,
            "sequence_code": values["sequence_code"],
            "default_location_src_id": src_loc.id,
            "default_location_dest_id": dest_loc.id,
            "warehouse_id": self.id,
            "company_id": self.company_id.id,
            "sequence": max_sequence + 1,
            "fiscal_operation_id": self.env.ref(values["fiscal_operation"]).id,
        }

    def _create_fiscal_picking_types(self):
        """Create the missing fiscal picking types for these warehouses.

        Existing ones are left untouched, so the method is safe to run again
        on a warehouse that was already set up.
        """
        picking_type_model = self.env["stock.picking.type"].sudo()
        sequence_model = self.env["ir.sequence"].sudo()

        for warehouse in self:
            if warehouse.company_id.country_id.code != "BR":
                continue

            # The names are translatable, so they must be evaluated in the
            # language of the company the picking types belong to.
            lang = warehouse.company_id.partner_id.lang or self.env.lang
            for values in warehouse.with_context(lang=lang)._get_fiscal_picking_types():
                fiscal_operation = self.env.ref(
                    values["fiscal_operation"], raise_if_not_found=False
                )
                if not fiscal_operation:
                    continue
                if picking_type_model.search_count(
                    [
                        ("warehouse_id", "=", warehouse.id),
                        ("fiscal_operation_id", "=", fiscal_operation.id),
                        ("sequence_code", "=", values["sequence_code"]),
                    ]
                ):
                    continue

                max_sequence = picking_type_model.search_read(
                    [("sequence", "!=", False)],
                    ["sequence"],
                    limit=1,
                    order="sequence desc",
                )
                max_sequence = max_sequence and max_sequence[0]["sequence"] or 0

                sequence = sequence_model.create(
                    {
                        "name": "{} {}".format(warehouse.name, values["name"]),
                        "prefix": "{}/{}/".format(
                            warehouse.code, values["sequence_code"]
                        ),
                        "padding": 5,
                        "company_id": warehouse.company_id.id,
                    }
                )
                picking_type_values = warehouse._get_fiscal_picking_type_values(
                    values, max_sequence
                )
                picking_type_values["sequence_id"] = sequence.id
                picking_type_model.with_context(lang=lang).create(picking_type_values)

            warehouse._link_fiscal_return_picking_types()

    def _link_fiscal_return_picking_types(self):
        """Point each shipping picking type at its return counterpart.

        The pairs are declared by ``return_to`` in
        ``_get_fiscal_picking_types``: an outbound operation and the inbound one
        that receives the same goods back. Runs after the creation loop, so both
        sides of a pair already exist.
        """
        self.ensure_one()
        picking_type_model = self.env["stock.picking.type"].sudo()
        by_code = {
            picking_type.sequence_code: picking_type
            for picking_type in picking_type_model.search(
                [("warehouse_id", "=", self.id)]
            )
        }
        for values in self._get_fiscal_picking_types():
            counterpart = values.get("return_to")
            if not counterpart:
                continue
            picking_type = by_code.get(values["sequence_code"])
            return_type = by_code.get(counterpart)
            if picking_type and return_type:
                picking_type.return_picking_type_id = return_type

    @api.model_create_multi
    def create(self, vals_list):
        warehouses = super().create(vals_list)
        warehouses._create_fiscal_picking_types()
        return warehouses
