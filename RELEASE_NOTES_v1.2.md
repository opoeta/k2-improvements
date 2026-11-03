# v1.2 — K2 Plus, firmware 1.1.7.0

Primeira versão deste fork validada no **firmware 1.1.7.0** (K2 Plus, 2 CFS, DXC2, PR Touch).

## Suporte ao 1.1.7.0
- `verifica-k2.sh` lê a versão por `fw_printenv version` e aceita `1.1.7.*`.
- `no-carto-k2.sh` é a rota única (1.1.6.x / 1.1.7.x), sem Cartographer.
- Descobertas e limites do firmware: [`docs/FIRMWARE-1.1.7.0.md`](docs/FIRMWARE-1.1.7.0.md).

## Novo
- `BED_MESH_SCALE` (`features/mesh_scale`): escala o mesh ativo; o PR Touch exagera a curvatura da mesa em 3–6×. Desligado por padrão (`mesh_scale` no `k2_vars.cfg`).
- `z_tilt` com `retry_tolerance: 0.03` (`probe-speed/tune.py`): rejeita amostra anômala do probe que passava com 0,1.
- `k2 update/status/verificar/install` corrigido: baixava um bootstrap com o nome antigo (404) depois do rename.

## Mudanças
- Clone na impressora agora é `/mnt/UDISK/k2-improvements`; o nome antigo do projeto saiu do código e da documentação.
- README reescrito para este fork (o do upstream erondiel foi para `docs/README-UPSTREAM-ERONDIEL.md`).
