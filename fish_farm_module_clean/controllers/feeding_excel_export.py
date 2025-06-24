from odoo import http
from odoo.http import request
import io
import xlsxwriter

class FeedingExcelReportController(http.Controller):

    @http.route('/fish_farm/feeding/excel', type='http', auth="user")
    def export_feeding_excel(self, **kwargs):
        feeding_records = request.env['fish.farm.feeding'].search([])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Feeding Report")

        headers = ['Date', 'Pond', 'Zone', 'Sector', 'Feed Type', 'Quantity (kg)']
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        for row, record in enumerate(feeding_records, start=1):
            sheet.write(row, 0, str(record.date))
            sheet.write(row, 1, record.pond_id.name or '')
            sheet.write(row, 2, record.zone_id.name or '')
            sheet.write(row, 3, record.sector_id.name or '')
            sheet.write(row, 4, record.feed_type or '')
            sheet.write(row, 5, record.quantity_kg or 0)

        workbook.close()
        output.seek(0)

        return request.make_response(
            output.read(),
            [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=feeding_report.xlsx')
            ]
        )
