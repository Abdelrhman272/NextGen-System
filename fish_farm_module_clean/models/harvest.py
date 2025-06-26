from odoo import models, fields, api

class FishHarvest(models.Model):
    _name = 'fish.harvest'
    _description = 'Fish Harvest'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'harvest_date desc'

    name = fields.Char('Harvest Reference', required=True, index=True, default='New')
    cycle_id = fields.Many2one('fish.breeding.cycle', 'Breeding Cycle', required=True)
    pond_id = fields.Many2one('fish.pond', related='cycle_id.pond_id', store=True)
    harvest_date = fields.Date('Harvest Date', default=fields.Date.today)
    quantity = fields.Float('Quantity (kg)', required=True)
    quality = fields.Selection([
        ('a', 'Grade A'),
        ('b', 'Grade B'),
        ('c', 'Grade C')
    ], 'Quality Grade', required=True)
    committee_member_ids = fields.Many2many('hr.employee', string='Committee Members')
    stock_move_id = fields.Many2one('stock.move', 'Inventory Transfer', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('harvested', 'Harvested'),
        ('transferred', 'Transferred to Warehouse'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], 'Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
            harvests = super(FishHarvest, self).create(vals_list)
    
    for harvest in harvests:
        if harvest.name == 'New':
            harvest.name = self.env['ir.sequence'].next_by_code('fish.harvest') or 'New'
    
    return harvests
  
    def action_transfer_to_warehouse(self):
        self.ensure_one()
        # Create stock move to transfer harvested fish to warehouse
        move = self.env['stock.move'].create({
            'name': f'Harvest Transfer: {self.name}',
            'product_id': self.cycle_id.fish_type_id.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.cycle_id.fish_type_id.product_id.uom_id.id,
            'location_id': self.pond_id.location_id.id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'picking_type_id': self.env.ref('fish_farm_management.picking_type_harvest').id,
            'harvest_id': self.id,
        })
        move._action_confirm()
        move._action_assign()
        move.quantity_done = self.quantity
        move._action_done()
        
        self.write({
            'stock_move_id': move.id,
            'state': 'transferred'
        })
        return True