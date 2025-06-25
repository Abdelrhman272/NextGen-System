from odoo import models, fields
import base64
import io
import xlsxwriter

class FishFeedingExportWizard(models.TransientModel):
    _name = 'fish.farm.feed.export.wizard'
    _description = 'Export Fish Feed Report to Excel'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    export_file = fields.Binary("Excel File", readonly=True)
    file_name = fields.Char("Filename")

    def action_export_excel(self):
        feeds = self.env['fish.farm.feed'].search([
            ('feed_date', '>=', self.from_date),
            ('feed_date', '<=', self.to_date)
        ])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Feeding Report")

        headers = ['Date', 'Pond', 'Quantity (kg)', 'Feed Type']
        for col, h in enumerate(headers):
            sheet.write(0, col, h)

        row = 1
        for rec in feeds:
            sheet.write(row, 0, str(rec.feed_date))
            sheet.write(row, 1, rec.pond_id.name)
            sheet.write(row, 2, rec.quantity)
            sheet.write(row, 3, rec.feed_type)
            row += 1

        workbook.close()
        output.seek(0)
        self.export_file = base64.b64encode(output.read())
        self.file_name = "Feeding_Report.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fish.farm.feed.export.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
