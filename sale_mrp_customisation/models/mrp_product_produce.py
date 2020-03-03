# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"
    _description = "Record Production"

    expiration_date = fields.Datetime(help="Helps to know the expiration Date of product.")
    lot_id = fields.Many2one('stock.production.lot', string='Lot',
                             compute='calculate_lot',
                             readonly=False, store=True)

    @api.depends('raw_workorder_line_ids.lot_id')
    def calculate_lot(self):
        final_lots = []
        self.lot_id = False
        for line in self.raw_workorder_line_ids:
            if line.lot_id:
                final_lots.append(line.lot_id.name)
        if final_lots:
            final_lot_id = self.env['stock.production.lot'].search(
                [('name', '=', " / ".join(final_lots))])
            if not final_lot_id:
                final_lot_id = self.env['stock.production.lot'].create(
                    {'name': " / ".join(final_lots),
                     'product_id': self.product_id.id,
                     'product_uom_id': self.product_uom_id.id,
                     })
            self.lot_id = final_lot_id.id

    def do_produce(self):
        """Inherit this method to add expiration date on lot which is created
        by default get."""
        res = super(MrpProductProduce, self).do_produce()
        if self.expiration_date and self.lot_id:
            self.lot_id.removal_date = self.expiration_date
        return res
