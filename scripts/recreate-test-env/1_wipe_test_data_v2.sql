BEGIN;
-- accounting
DELETE FROM account_partial_reconcile; DELETE FROM account_full_reconcile;
DELETE FROM account_payment; DELETE FROM account_bank_statement_line; DELETE FROM account_bank_statement;
DELETE FROM account_analytic_line;
DELETE FROM account_move_line; DELETE FROM account_move;
-- stock / valuation
DELETE FROM stock_landed_cost_lines; DELETE FROM stock_valuation_adjustment_lines; DELETE FROM stock_landed_cost;
DELETE FROM stock_scrap; DELETE FROM mrp_unbuild;
DELETE FROM stock_move_line; DELETE FROM stock_move; DELETE FROM stock_quant; DELETE FROM stock_picking;
-- mrp
DELETE FROM mrp_workcenter_productivity; DELETE FROM mrp_workorder; DELETE FROM mrp_production;
-- stone transactional
DELETE FROM stone_fg_source; DELETE FROM stone_lot_selection; DELETE FROM stone_refinish_slab_line;
DELETE FROM stone_sale_line_piece_op; DELETE FROM stone_sale_line_piece; DELETE FROM stone_fg_offcut;
DELETE FROM stone_price_approval; DELETE FROM stone_cut_order_slab_line;
DELETE FROM stone_bundle_resize_log; DELETE FROM stone_lot_resize_log;
DELETE FROM stone_bundle_photo; DELETE FROM stone_bundle; DELETE FROM stone_container;
DELETE FROM stock_lot;
-- boq
DELETE FROM boq_line_piece; DELETE FROM boq_line; DELETE FROM boq_document;
DELETE FROM boq_consumable_set_line; 
-- sales/purchase/project
DELETE FROM sale_order_line; DELETE FROM sale_order;
DELETE FROM purchase_requisition_line; DELETE FROM purchase_requisition;
DELETE FROM purchase_order_line; DELETE FROM purchase_order;
DELETE FROM project_task; DELETE FROM project_update; DELETE FROM project_project;
-- catalog
DELETE FROM product_combo_item; DELETE FROM mrp_bom_byproduct; DELETE FROM mrp_bom_line; DELETE FROM mrp_bom;
DELETE FROM stone_material; DELETE FROM product_product; DELETE FROM product_template;
-- chatter/attachments of wiped models
DELETE FROM mail_followers WHERE res_model IN ('account.move','account.payment','stock.picking','stock.move','stock.lot','mrp.production','stone.bundle','stone.container','boq.document','sale.order','purchase.order','project.task','project.project','product.template','stone.material');
DELETE FROM mail_activity WHERE res_model IN ('account.move','account.payment','stock.picking','stock.move','stock.lot','mrp.production','stone.bundle','stone.container','boq.document','sale.order','purchase.order','project.task','project.project','product.template','stone.material');
DELETE FROM ir_attachment WHERE res_model IN ('account.move','account.payment','stock.picking','stock.move','stock.lot','mrp.production','stone.bundle','stone.container','boq.document','sale.order','purchase.order','project.task','project.project','product.template','stone.material');
DELETE FROM mail_message WHERE model IN ('account.move','account.payment','stock.picking','stock.move','stock.lot','mrp.production','stone.bundle','stone.container','boq.document','sale.order','purchase.order','project.task','project.project','product.template','stone.material');
CREATE TEMP TABLE _pdel AS SELECT id FROM res_partner WHERE id NOT IN (SELECT partner_id FROM res_company) AND id NOT IN (SELECT partner_id FROM res_users);
DELETE FROM account_payment_register WHERE partner_id IN (SELECT id FROM _pdel);
DELETE FROM payment_transaction WHERE partner_id IN (SELECT id FROM _pdel);
DELETE FROM payment_token WHERE partner_id IN (SELECT id FROM _pdel);
DELETE FROM mail_scheduled_message WHERE author_id IN (SELECT id FROM _pdel);
DELETE FROM snailmail_letter WHERE partner_id IN (SELECT id FROM _pdel);
DELETE FROM mail_push_device WHERE partner_id IN (SELECT id FROM _pdel);
DELETE FROM mail_followers WHERE res_model='res.partner' AND res_id IN (SELECT id FROM _pdel);
DELETE FROM mail_message WHERE model='res.partner' AND res_id IN (SELECT id FROM _pdel);
DELETE FROM ir_attachment WHERE res_model='res.partner' AND res_id IN (SELECT id FROM _pdel);
DELETE FROM res_partner WHERE id IN (SELECT id FROM _pdel);
COMMIT;
