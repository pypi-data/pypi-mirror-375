/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("stock_barcodes.FormView", function (require) {
    "use strict";

    var FormView = require("web.FormView");
    var FormController = require("web.FormController");

    FormView.include({
        /**
         * Adds support to define the 'control_panel_hidden' context key to
         * override 'withControlPanel' option.
         *
         * @override
         */
        _extractParamsFromAction: function (action) {
            const params = this._super.apply(this, arguments);
            if (action && action.context && action.context.control_panel_hidden) {
                params.withControlPanel = false;
            }
            return params;
        },
    });

    FormController.include({
        _barcodeActiveScanned: function () {
            this._super(...arguments);
            var record = this.model.get(this.handle);
            if (record.model.includes("wiz.stock.barcodes.read")) {
                $("#dummy_on_barcode_scanned").click();
            }
        },
    });
});
