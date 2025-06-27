/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class FishFarmDashboard extends Component {
    static template = "fish_farm_management.fish_farm_dashboard_template";
    
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            loading: true,
            data: null
        });
        
        onWillStart(() => this.loadData());
        onMounted(() => this.renderCharts());
    }

    async loadData() {
        this.state.data = await this.rpc("/fish_farm/dashboard/data");
        this.state.loading = false;
    }

    renderCharts() {
        if (!window.Chart || !this.state.data) return;
        
        // Render production chart
        new Chart(
            document.getElementById("productionChart").getContext("2d"),
            this.state.data.production
        );
        
        // Render pond status chart
        new Chart(
            document.getElementById("pondChart").getContext("2d"),
            this.state.data.pondStatus
        );
    }
}

registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);