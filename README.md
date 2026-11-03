# k2-improvements — Creality K2 Plus

Fork de [erondiel/k2-improvements](https://github.com/erondiel/k2-improvements) (que parte de [Jacob10383/k2-improvements](https://github.com/Jacob10383/k2-improvements)) para a **Creality K2 Plus no firmware stock, sem Cartographer**. Licença GPLv3 (ver `LICENSE`).

**Firmware validado: 1.1.7.0** (também aceitos: 1.1.6.x e 1.1.5.2). Detalhes e descobertas: [`docs/FIRMWARE-1.1.7.0.md`](docs/FIRMWARE-1.1.7.0.md).

## Instalar

Pré-requisito: SSH root habilitado na impressora (tela: *Configurações → Geral → Open Root*). Do PC (Linux/Mac/WSL/Git Bash):

```sh
# só verifica (firmware, respond, espaço, backup) — não instala nada
curl -sSL https://raw.githubusercontent.com/opoeta/k2-improvements/main/instalar-remoto.sh | sh -s -- <ip-da-impressora>

# verifica e instala
curl -sSL https://raw.githubusercontent.com/opoeta/k2-improvements/main/instalar-remoto.sh | sh -s -- <ip-da-impressora> install
```

Direto no shell da impressora (não tem `curl`/`wget`; usa `python3`):

```sh
python3 -c "import urllib.request,ssl;ctx=ssl._create_unverified_context();open('/tmp/bj.sh','wb').write(urllib.request.urlopen('https://raw.githubusercontent.com/opoeta/k2-improvements/main/bootstrap-k2.sh',context=ctx).read())" && sh /tmp/bj.sh install
```

O clone fica em `/mnt/UDISK/k2-improvements` e a instalação roda `no-carto-k2.sh` (cada feature reinicia o Klipper; ~2–3 min).

## Atualizar

```sh
ssh root@<ip> "k2 update"     # só reinstala se houver commit novo no main
ssh root@<ip> "k2 status"     # versão instalada x GitHub
ssh root@<ip> "k2 verificar"  # pré-verificação, não muda nada
ssh root@<ip> "k2 install"    # força reinstalação completa
```

Faça com a impressora **parada**. Se o Klipper ficar em erro (`key301`/`key798`), rode `POST /printer/firmware_restart` (às vezes duas vezes). O clone é um tarball extraído, não um repositório git: arquivos seus dentro de `/mnt/UDISK/k2-improvements` que não estão no `main` são apagados a cada update.

## O que vem instalado

- **Central de Calibração** (`features/nivela_web`, abra `http://<ip>:4408/calibra.html`): nivelamento dos parafusos (medição robusta, wizard), probe & Z-offset **persistente por placa + material**, Pressure Advance, mesh, PID, input shaper/ressonância, extrusora, **Filament Box (CFS)** com leitura ao vivo pela porta 9999, Spoolman, console e câmera. Tudo em pt-BR, falando com o Moonraker por HTTP.
- **Macros:** `START_PRINT` paramétrico (offset por material e por placa auto-registrada, PA por material, KAMP, `BED_MESH_SCALE` opcional), `MESH_IF_NEEDED`, `M191`, `overrides`, `SCREWS_TILT_CALCULATE`, `K2_FLUSH` (purga da troca de cor).
- **Segurança do probe/CFS:** `box_guard` (bloqueia o `BOX_SET_PRE_LOADING` com parâmetros vazios → `key171/key60`), `prtouch_safe_xy` (anti-arrasto do bico), `start_print_fast_stop`, `virtual-sdcard-guard`, `abort_homing`.
- **Mesh:** `probe-speed` (mesh/`z_tilt` mais rápidos, `retry_tolerance` 0,03), `kamp-adaptive-purge` (mesh adaptativo + `LINE_PURGE`, com o PATCH K2), `mesh_scale` (`BED_MESH_SCALE`, **desligado** por padrão), `prime_tower`.
- **Moonraker:** componentes próprios (`k2_info`, `k2_cfs_edit`, `k2_resonances`, `k2_dxc2`, `k2_features`, `k2_abort`, `spoolman_admin`) e Fluidd upstream com câmera WebRTC (`camera-fix`).
- **Opt-in (ligam pelo painel):** DXC2 (extrusor dual-drive + cortador), `axis_twist_compensation`, `save-config-restart`.

Não instalados de propósito: `cartographer` e dependentes, `motor-state-guard` (não testado), `obico` (WIP), `secure-auth` (risco de lockout) e o antigo `[mmu]`/`orca-filament-sync` (removido; o sync do Orca usa o CFS nativo pela porta 9999).

## Depois de instalar — fatiador

G-code inicial da máquina (Creality Print / OrcaSlicer):

```
START_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer_single] CHAMBER_TEMP=[overall_chamber_temperature] MATERIAL={filament_type[initial_tool]} CURR_BED_TYPE="{curr_bed_type}" ADAPTIVE=1
```

- `MATERIAL=` ativa o Z-offset por material; `CURR_BED_TYPE=` o offset **por placa** (cada placa do slicer vira um offset próprio na 1ª impressão); `ADAPTIVE=1` faz o mesh só da área da peça.
- Ligue **"Etiquetar objetos"** (Label objects) — sem isso o KAMP cai pra mesa inteira.
- Templates prontos em `features/kamp-adaptive-purge/slicer-templates/`.

## Avisos

- Incompatível com a auto-calibração da Creality (`forced_leveling: false` no `overrides`).
- Ajuste o Z **só pela Central**, nunca pela tela da impressora (não validado no 1.1.7.0).
- `CALIBRATE_CUT_POS`, edições de `box.cfg` e qualquer movimento perto do cortador mexem em hardware: a Central sempre pede confirmação e bloqueia durante a impressão.
- O probe (`prtouch_v3`) é um blob compilado: o mesh precisa manter a grade do `[bed_mesh]` (5×5), senão o Klipper cai.

## Documentação

| Arquivo | Conteúdo |
|---|---|
| [`docs/FIRMWARE-1.1.7.0.md`](docs/FIRMWARE-1.1.7.0.md) | Suporte e descobertas do firmware 1.1.7.0 (sistema, blobs, PR Touch, erros, operação) |
| [`docs/K2-HANDOFF.md`](docs/K2-HANDOFF.md) | Histórico, objeto `box`, schema do Spoolman, receitas de `curl` |
| [`docs/HANDOFF-SESSAO-2026-10.md`](docs/HANDOFF-SESSAO-2026-10.md) | Problemas abertos e regras para operar a impressora |
| [`docs/REFERENCIAS-EXTERNAS.md`](docs/REFERENCIAS-EXTERNAS.md) | Repos de terceiros avaliados e o que foi aproveitado |
| [`docs/README-UPSTREAM-ERONDIEL.md`](docs/README-UPSTREAM-ERONDIEL.md) | README original do fork erondiel (instalador TUI, firmware 1.1.5.2 + Cartographer) |
| [`CLAUDE.md`](CLAUDE.md) | Contexto operacional do projeto |

## Créditos

[Jacob10383](https://github.com/Jacob10383) (upstream), [erondiel](https://github.com/erondiel) (fork-base), [Rcpilot33](https://github.com/Rcpilot33/k2-improvements) (axis_twist, save-config-restart, prtouch), [Tinman-FP](https://github.com/Tinman-FP/Creality-K2-Plus-DXC2-Beacon) (perfil DXC2), [kyleisah](https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging) (KAMP), [DnG-Crafts](https://github.com/DnG-Crafts) (calibração pelo papel), [military-cat](https://github.com/military-cat/Mainsail-CFS-Panel) (protocolo do CFS na porta 9999).
