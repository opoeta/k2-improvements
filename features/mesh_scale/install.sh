#!/bin/ash
# Instala o BED_MESH_SCALE (extra do Klipper): escala o mesh ativo por um fator.
# Ver k2_mesh_scale.py. Idempotente: link + include so se faltar. Reinicia o
# Klipper porque e um extra novo.
set -e
SCRIPT_DIR=$(readlink -f $(dirname ${0}))
test -d ~/printer_data/config/custom || mkdir -p ~/printer_data/config/custom
rm -f ~/klipper/klippy/extras/k2_mesh_scale.pyc \
      ~/klipper/klippy/extras/__pycache__/k2_mesh_scale.*.pyc 2>/dev/null || true
ln -sf ${SCRIPT_DIR}/k2_mesh_scale.py  ~/klipper/klippy/extras/k2_mesh_scale.py
ln -sf ${SCRIPT_DIR}/k2_mesh_scale.cfg ~/printer_data/config/custom/k2_mesh_scale.cfg
python ${SCRIPT_DIR}/../../scripts/ensure_included.py \
    ~/printer_data/config/printer.cfg custom/main.cfg
python ${SCRIPT_DIR}/../../scripts/ensure_included.py \
    ~/printer_data/config/custom/main.cfg k2_mesh_scale.cfg
/etc/init.d/klipper restart
