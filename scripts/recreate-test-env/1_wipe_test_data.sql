-- Wipe transactional + product-catalog data from a freshly-duplicated EMG-O
-- test DB, while keeping config intact: companies, warehouses, chart of
-- accounts, users, security groups, product attributes/categories, and the
-- boq_estimation seed reference data (boq.cost.component, XML-loaded).
--
-- Built 2026-08-29 as part of the eg-tst recreate SOP — see
-- claude-knowledge/projects/emg-o/sop-recreate-eg-tst.md for the full
-- procedure this script is one step of. Run against the NEW duplicated DB
-- only, never against mbx-ee-dev or a live eg-tst still serving the client.
--
-- Usage:
--   docker exec -i pg18 psql -U postgres -d <new_db_name> -v ON_ERROR_STOP=1 \
--       -f 1_wipe_test_data.sql
--
-- Wrapped in one transaction: if any DELETE hits an unexpected FK
-- (e.g. a new model added since this script was written), the whole
-- thing rolls back cleanly — safe to fix the order and re-run.

BEGIN;

-- 1. Accounting: payments, reconciliation, journal entries/invoices
DELETE FROM account_partial_reconcile;
DELETE FROM account_full_reconcile;
DELETE FROM account_payment;
DELETE FROM account_bank_statement_line;
DELETE FROM account_bank_statement;
DELETE FROM account_move_line;
DELETE FROM account_move;

-- 2. Stock layer (move lines/moves before quants/pickings before lots)
DELETE FROM stock_move_line;
DELETE FROM stock_move;
DELETE FROM stock_quant;
DELETE FROM stock_picking;

-- 3. Manufacturing
DELETE FROM mrp_workorder;
DELETE FROM mrp_production;

-- 4. Repair
DELETE FROM repair_order;

-- 5. Custom stone transactional models (children before their stock_lot)
DELETE FROM stone_slab;
DELETE FROM stone_bundle_photo;
DELETE FROM stone_bundle;
DELETE FROM stone_container;
DELETE FROM stock_lot;

-- 6. BOQ documents/lines + ad-hoc rate cards entered during testing.
--    NOT touching boq_cost_component — confirmed 100% XML-seeded reference
--    data (module='boq_estimation' in ir_model_data), not test data.
DELETE FROM boq_line;
DELETE FROM boq_document;
DELETE FROM boq_rate_cost_line;
DELETE FROM boq_rate;

-- 7. Sales / Purchase
DELETE FROM sale_order_line;
DELETE FROM sale_order;
DELETE FROM purchase_order_line;
DELETE FROM purchase_order;

-- 8. Project (Mode 4 Sold-as-Project SO-generated tasks/projects)
DELETE FROM project_task;
DELETE FROM project_project;

-- 9. Product catalog itself — wiped so the bulk-import toolkit (step 2)
--    starts from a clean slate, not the old rehearsal data.
--    stone_material must go first: stone_material.product_id -> product_product
--    is a RESTRICT fkey, so the material record blocks product deletion
--    until it's gone (found live 2026-08-29, first run of this script).
--    mrp_bom_line/mrp_bom (auto-created per material for Cut-to-Order/FG
--    production, Modes 3/5) also RESTRICT-reference product_product/
--    product_template — same discovery, delete before the products.
DELETE FROM mrp_bom_line;
DELETE FROM mrp_bom;
DELETE FROM stone_material;
DELETE FROM product_product;
DELETE FROM product_template;

-- 10. Test contacts only — NOT touching company partners (My
--     Company/Empire Granite/Empire Stone), user partners (admin/
--     emgdemo/emgtest/egsale/system users). Re-verify this id list
--     against the target DB before running on a future recreate —
--     it is NOT auto-derived.
DELETE FROM res_partner WHERE id IN (13, 14, 16, 18);

-- 11. Orphaned chatter/attachments for everything wiped above (mail
--     messages/attachments use res_model+res_id, not real FKs, so they
--     don't cascade automatically).
DELETE FROM mail_followers WHERE res_model IN (
    'account.move','account.payment','stock.picking','stock.move',
    'mrp.production','repair.order','stone.slab','stone.bundle',
    'stone.container','boq.document','sale.order','purchase.order',
    'project.task','project.project','product.template','stone.material'
);
DELETE FROM mail_activity WHERE res_model IN (
    'account.move','account.payment','stock.picking','stock.move',
    'mrp.production','repair.order','stone.slab','stone.bundle',
    'stone.container','boq.document','sale.order','purchase.order',
    'project.task','project.project','product.template','stone.material'
);
DELETE FROM ir_attachment WHERE res_model IN (
    'account.move','account.payment','stock.picking','stock.move',
    'mrp.production','repair.order','stone.slab','stone.bundle',
    'stone.container','boq.document','sale.order','purchase.order',
    'project.task','project.project','product.template','stone.material'
);
DELETE FROM mail_message WHERE model IN (
    'account.move','account.payment','stock.picking','stock.move',
    'mrp.production','repair.order','stone.slab','stone.bundle',
    'stone.container','boq.document','sale.order','purchase.order',
    'project.task','project.project','product.template','stone.material'
);
DELETE FROM mail_followers WHERE res_model = 'res.partner' AND res_id IN (13,14,16,18);
DELETE FROM mail_message WHERE model = 'res.partner' AND res_id IN (13,14,16,18);
DELETE FROM ir_attachment WHERE res_model = 'res.partner' AND res_id IN (13,14,16,18);

COMMIT;
