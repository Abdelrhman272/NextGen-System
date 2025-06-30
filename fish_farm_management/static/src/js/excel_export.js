/** @odoo-module **/

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";

function customExcelExportAction(ev) {
    const action = ev.data.action;
    if (action.type === 'ir.actions.act_url' && action.url.includes('/fish_farm_management/report/excel/')) {
        ev.stopPropagation(); // Stop default action behavior
        download({
            url: action.url,
            data: action.data || {},
            success: function() {
                // Optional: show a notification to the user that download started
                request.bus.trigger('close_notification');
                request.bus.trigger('notification', {
                    type: 'success',
                    title: "Download Started",
                    message: "Your Excel report download has started.",
                });
            },
            error: function(error) {
                // Optional: show an error notification
                request.bus.trigger('close_notification');
                request.bus.trigger('notification', {
                    type: 'danger',
                    title: "Download Failed",
                    message: "Failed to download the Excel report.",
                });
            }
        });
    }
}

registry.category("action_handlers").add("custom_excel_export", customExcelExportAction);