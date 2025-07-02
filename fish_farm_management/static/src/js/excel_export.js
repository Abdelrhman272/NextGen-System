// Excel export handler for Fish Farm Management reports

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";

function customExcelExportAction(ev) {
    const action = ev.data.action;
    const url = action.url || '';
    if (
        action.type === 'ir.actions.act_url' &&
        url.includes(
            '/fish_farm_management/report/excel/'
        )
    ) {
        ev.stopPropagation();
        download({
            url,
            data: action.data || {},
            success() {
                // Notify success
                request.bus.trigger('close_notification');
                request.bus.trigger('notification', {
                    type: 'success',
                    title: 'Download Started',
                    message: 'Your Excel report download has started.',
                });
            },
            error() {
                // Notify failure
                request.bus.trigger('close_notification');
                request.bus.trigger('notification', {
                    type: 'danger',
                    title: 'Download Failed',
                    message: 'Failed to download the Excel report.',
                });
            },
        });
    }
}

registry.category("action_handlers").add(
    "custom_excel_export",
    customExcelExportAction
);