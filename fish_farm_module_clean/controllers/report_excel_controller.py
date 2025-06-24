from odoo import http
from odoo.http import request
import io
import xlsxwriter

class FishFarmExcelReportController(http.Controller):

    @http.route('/fish_farm/<string:report_name>/excel', type='http', auth="user")
    def export_report_excel(self, report_name=None, **kwargs):
        model_map = {
            "feeding": "fish.farm.feeding",
            "fishing": "fish.farm.fishing",
            "supplying": "fish.farm.supplying",
            "daily": "fish.farm.daily",
            "production": "fish.farm.production",
            "pond_statement": "fish.farm.pond.statement"
        }
        if report_name not in model_map:
            return request.not_found()

        records = request.env[model_map[report_name]].search([])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(f"{report_name.title()} Report")

        headers = ['Field 1', 'Field 2', 'Field 3']
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        for row, record in enumerate(records, start=1):
            sheet.write(row, 0, str(record.name or ''))
            sheet.write(row, 1, str(record.create_date or ''))
            sheet.write(row, 2, str(record.id))

        workbook.close()
        output.seek(0)
        return request.make_response(
            output.read(),
            [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={report_name}_report.xlsx')
            ]
        )
