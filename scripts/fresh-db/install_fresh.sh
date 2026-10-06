S=/tmp/claude-0/-root/9b6def15-9dde-4050-b179-2a7cb1c187c4/scratchpad
for db in eg-tst-fresh mbx-ee-dev-fresh; do
  docker run --rm --entrypoint /entrypoint.sh --env-file $S/dev.env -v /opt/docker/slab-lot-dev/addons:/mnt/extra-addons odoo19-ent-mbx odoo -d $db -i base,account_accountant,l10n_th,l10n_th_reports,l10n_account_withholding_tax,stone_slab_inventory,boq_estimation,mx_chatter_toggle --without-demo=all --stop-after-init --no-http --log-level=warn > $S/$db.log 2>&1
  echo "DONE $db" >> $S/install_fresh.status
done
