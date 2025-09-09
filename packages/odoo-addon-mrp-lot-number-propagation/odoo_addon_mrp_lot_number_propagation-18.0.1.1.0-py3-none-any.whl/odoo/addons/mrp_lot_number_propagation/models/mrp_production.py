# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models, tools
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_lot_number_propagated = fields.Boolean(
        default=False,
        readonly=True,
        help=(
            "Lot/serial number is propagated "
            "from a component to the finished product."
        ),
    )
    propagated_lot_producing = fields.Char(
        compute="_compute_propagated_lot_producing",
        help=(
            "The BoM used on this manufacturing order is set to propagate "
            "lot number from one of its components. The value will be "
            "computed once the corresponding component is selected."
        ),
    )

    @api.depends(
        "move_raw_ids.propagate_lot_number",
        "move_raw_ids.move_line_ids.quantity",
        "move_raw_ids.move_line_ids.picked",
        "move_raw_ids.move_line_ids.lot_id",
    )
    def _compute_propagated_lot_producing(self):
        for order in self:
            order.propagated_lot_producing = False
            move_with_lot = order._get_propagating_component_move()
            line_with_sn = move_with_lot.move_line_ids.filtered(
                lambda ln: (
                    ln.lot_id
                    and ln.product_id.tracking == "serial"
                    and tools.float_compare(
                        ln.quantity, 1, precision_rounding=ln.product_uom_id.rounding
                    )
                    == 0
                )
            )
            if len(line_with_sn) == 1:
                order.propagated_lot_producing = line_with_sn.lot_id.name

    @api.onchange("bom_id")
    def _onchange_bom_id_lot_number_propagation(self):
        self.is_lot_number_propagated = self.bom_id.lot_number_propagation

    def action_confirm(self):
        res = super().action_confirm()
        self._set_lot_number_propagation_data_from_bom()
        return res

    def _get_propagating_component_move(self):
        self.ensure_one()
        return self.move_raw_ids.filtered(lambda o: o.propagate_lot_number)

    def _set_lot_number_propagation_data_from_bom(self):
        """Copy information from BoM to the manufacturing order."""
        for order in self:
            propagate_lot = order.bom_id.lot_number_propagation
            if not propagate_lot:
                continue
            order.is_lot_number_propagated = propagate_lot
            propagate_move = order.move_raw_ids.filtered(
                lambda m: m.bom_line_id.propagate_lot_number
            )
            if not propagate_move:
                raise UserError(
                    self.env._(
                        "Bill of material is marked for lot number propagation, but "
                        "there are no components propagating lot number. "
                        "Please check BOM configuration."
                    )
                )
            elif len(propagate_move) > 1:
                raise UserError(
                    self.env._(
                        "Bill of material is marked for lot number propagation, but "
                        "there are multiple components propagating lot number. "
                        "Please check BOM configuration."
                    )
                )
            else:
                propagate_move.propagate_lot_number = True

    def _get_quantity_produced_issues(self):
        if self.env.context.get("bypass_pre_button_mark_done_checks"):
            self = self.filtered(lambda prod: not prod.is_lot_number_propagated)
        return super()._get_quantity_produced_issues()

    def _set_quantities(self):
        if (
            self.env.context.get("bypass_pre_button_mark_done_checks")
            and self.is_lot_number_propagated
        ):
            return True
        return super()._set_quantities()

    def _auto_production_checks(self):
        if (
            self.env.context.get("bypass_pre_button_mark_done_checks")
            and self.is_lot_number_propagated
        ):
            return True
        return super()._auto_production_checks()

    def pre_button_mark_done(self):
        if all(prod._auto_production_checks() for prod in self):
            self._create_and_assign_propagated_lot_number()
        res = super().pre_button_mark_done()
        if isinstance(res, dict) and res["res_model"] == "mrp.batch.produce":
            # In case a wizard action for mrp.batch.produce is returned, we have to
            #  handle differently orders that need to go through this wizard and
            #  those which do not

            # But first let's check if actual production requiring batch producing
            #  is set to propagate lot number
            batch_order_id = res["context"]["default_production_id"]
            batch_order = self.browse(batch_order_id)
            # If it's not set to propagate lot number, return the action as it
            #  requires user input
            if not batch_order.is_lot_number_propagated:
                return res
            # Check if all batch productions are set to propagate lot number
            productions_auto_ids = set()
            productions_batch_ids = set()
            for order in self:
                if order._auto_production_checks():
                    productions_auto_ids.add(order.id)
                else:
                    productions_batch_ids.add(order.id)

            batch_productions = self.browse(productions_batch_ids)
            for order in batch_productions:
                # If any production is not set to propagate, it will require user input
                #  so return the wizard for that order instead of one with lot number
                #  propagation
                if not order.is_lot_number_propagated:
                    res["context"].update({"default_production_id": order.id})
                    return res
                # If any production is set to propagate, but has multiple tracked
                #  components, we cannot mass produce without user input for the
                #  components that don't propagate their lot number.
                #  so return the wizard for that order
                if (
                    len(
                        order.move_raw_ids.filtered(
                            lambda mv: mv.product_id.tracking != "none"
                        )
                    )
                    > 1
                ):
                    res["context"] = {"default_production_id": order.id}
                    return res
            # If we are here, it means we must be able to produce everything
            #  automatically
            # Now we need to finish whatever checks were meant to be done through
            #  pre_button_mark_done, but weren't finished as the batch product
            #  wizard had to be returned
            # FIXME: If an order to be propagated has consumption issue, and is meant
            #  to create backorder this will call button_mark_done, without having set
            #  up lot propagation beforehand
            res = super(
                MrpProduction,
                self.with_context(bypass_pre_button_mark_done_checks=True),
            ).pre_button_mark_done()
            # If any other wizard action had to be returned, (eg consumption issue,
            #  backorder) let's return it
            if isinstance(res, dict):
                return res
            # Now we can safely handle productions set to propagate lot number
            #  through specific wizard to allow user confirmation
            res = self.env["ir.actions.act_window"]._for_xml_id(
                "mrp_lot_number_propagation.action_mrp_batch_produce_propagate"
            )
            res["context"] = {"default_production_ids": batch_productions.ids}
        return res

    def _create_and_assign_propagated_lot_number(self):
        for order in self:
            if not order.is_lot_number_propagated or order.lot_producing_id:
                continue
            finish_moves = order.move_finished_ids.filtered(
                lambda mv, mo=order: mv.product_id == mo.product_id
                and mv.state not in ("done", "cancel")
            )
            if finish_moves and finish_moves.quantity and not finish_moves.picked:
                lot_model = self.env["stock.lot"]
                lot = lot_model.search(
                    [
                        ("product_id", "=", order.product_id.id),
                        ("company_id", "=", order.company_id.id),
                        ("name", "=", order.propagated_lot_producing),
                    ],
                    limit=1,
                )
                if lot.quant_ids:
                    raise UserError(
                        self.env._(
                            "Lot/Serial number %s already exists and has been used. "
                            "Unable to propagate it."
                        )
                    )
                if not lot:
                    lot = self.env["stock.lot"].create(
                        {
                            "product_id": order.product_id.id,
                            "company_id": order.company_id.id,
                            "name": order.propagated_lot_producing,
                        }
                    )
                order.with_context(lot_propagation=True).lot_producing_id = lot

    def write(self, vals):
        for order in self:
            if (
                order.is_lot_number_propagated
                and vals.get("lot_producing_id")
                and not self.env.context.get("lot_propagation")
            ):
                raise UserError(
                    self.env._(
                        "Lot/Serial number is propagated from a component, "
                        "you are not allowed to change it."
                    )
                )
        return super().write(vals)
