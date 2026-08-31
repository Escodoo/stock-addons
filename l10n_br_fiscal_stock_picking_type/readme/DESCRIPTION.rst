This module creates one stock picking type per standard Brazilian fiscal
operation, so the operations can be started from the Inventory overview with
their own numbering instead of relying on the company default.

The following picking types are created for every Brazilian warehouse:

* Simples Remessa (outgoing)
* Remessa para Industrialização (outgoing)
* Retorno de Industrialização (incoming)
* Retorno de Conserto ou Reparo (outgoing)
* Entrada para Conserto ou Reparo (incoming)

Each one is linked to the matching fiscal operation of ``l10n_br_fiscal``
through the ``Default Fiscal Operation`` field added by
``l10n_br_stock_account``, and gets its own sequence.

Without this module a picking with no fiscal operation on its picking type
still falls back to the company defaults (``stock_in_fiscal_operation_id`` and
``stock_out_fiscal_operation_id``); this module is about having each operation
separated in the Inventory menu.
