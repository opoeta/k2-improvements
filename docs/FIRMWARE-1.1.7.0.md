# Firmware Creality 1.1.7.0 — suporte e descobertas (K2 Plus)

> Validado na K2 Plus do dono (`CR0CN240110C10`, 2 CFS, DXC2, PR Touch), set–nov/2026.
> Uma única máquina: o que está aqui é **observado**, não garantia para outras unidades.
> Itens marcados **(não explicado)** são fatos medidos sem causa raiz confirmada.

## 1. Suporte no repo

| Peça | Estado no 1.1.7.0 |
|---|---|
| `verifica-k2.sh` | Lê a versão por `fw_printenv version` (fallback: log do upgrade-server / nome do `.img`). `1.1.7.*` = rota suportada. |
| `no-carto-k2.sh` | Rota única de instalação (sem Cartographer). Banner e comentários agora dizem 1.1.6.x / 1.1.7.x. |
| `k2` (CLI na impressora) | `k2 update/status/verificar/install`. Versão instalada em `/mnt/UDISK/.k2-version`. |
| Central (`calibra.html`) | Tudo testado nesta firmware. |
| KAMP vendorado, `box_guard`, `prtouch_safe_xy`, `mesh_scale`, DXC2 | Instalam e rodam; detalhes abaixo. |
| Cartographer / Beacon | **Não** testados aqui (sem o hardware). O Beacon da referência externa é pinado no 1.1.6.1. |

Firmwares anteriores seguem aceitas pelo verificador (1.1.5.2, 1.1.6.x); qualquer outra gera aviso e pede para não instalar às cegas.

## 2. Sistema da impressora

- Versão: `fw_printenv version` → `version=1.1.7.0`. É a mesma fonte do componente `k2_info.py` (`/server/k2/info`).
- OpenWrt 21.02-SNAPSHOT, kernel `5.4.61` armv7l, rootfs squashfs. Partições **A/B** (`boot_partition=bootB`, `root_partition=rootfsB` quando medido).
- Klipper embarcado em `/usr/share/klipper` com Python 3.9. Blobs compilados, **sem fonte público**:
  `box_wrapper`, `filament_rack_wrapper`, `motor_control_wrapper`, `prtouch_v1/v2/v3_wrapper`, `serial_485_wrapper` (`*.cpython-39.so`).
- Moonraker `:7125` e Fluidd `:4408` de fábrica; API stock `:80`; WebSocket do CFS/Creality Print em **`:9999`** (não é HTTP).
- BusyBox: **sem** `nohup`, `setsid`, `curl`, `git`; `pkill -f` pode matar o próprio shell; `ls --time-style` não existe.
  Tem `python3` (`urllib`) e `ssh`. Para daemon use `os.fork()` + `os.setsid()` em Python. RAM baixa: nunca ler log grande em Python (`Killed`) — use `grep -a … | tail`.
- `/root` vem vazio: o instalador cria `~/printer_data` → `/mnt/UDISK/printer_data` e `~/klipper` → `/usr/share/klipper`.
- O clone do repo na impressora é um **tarball extraído** em `/mnt/UDISK/k2-improvements` (não é repositório git). Qualquer arquivo seu ali que não esteja no `main` é apagado no próximo `k2 update`. Os links de `klippy/extras` e `config/custom` apontam para esse diretório: **se a pasta sumir, o Klipper para** com `Unable to open config file …/custom/<x>.cfg`.

## 3. Diferenças e fatos de compatibilidade

- **Código stock comparado com forks:** `probe.py` do stock = 513 linhas (a versão do Rcpilot33 tem 514, 1 linha a mais); `configfile.py` base = 558 linhas. Por isso `axis_twist_compensation` e `save-config-restart` foram portados (opt-in) a partir dessas bases.
- **KAMP-K2 (grant0013) não se aplica** (verificado em 13/out/2026, print real): o `BED_MESH_CALIBRATE ADAPTIVE=1` sonda só a área da peça e antes de `File opened` o master-server só faz `G28_RE_CHECK` (6 toques no centro) + `BED_MESH_PROFILE LOAD="default"`. Nosso KAMP vendorado mantém o "PATCH K2" (contagem do mesh travada na grade do `[bed_mesh]`, 5×5) — o probe é blob e assume essa grade; contagem menor derruba o Klipper (`IndexError`, `key60`).
- **DXC2:** `cut_pos_offset` (doc do Tinman, firmware 1.1.6.1) **não existe**; use as chaves reais do `box.cfg` do seu aparelho. O `M1501` que o fix de purga da referência edita **não existe**. `FILAMENT_RACK_FLUSH` (~100 mm fixos) só roda na carga do suporte externo; a troca do CFS passa por `M8200`.
- **Limites de movimento:** `toolhead.axis_maximum.y = 352`, mas o `stepper_y` aceita 400; os movimentos de troca até Y≈378 só valem dentro da janela `M8200 P … M8200 O`. Fora dela, `Move out of range` (`key586`).
- **CFS (`box`):** a escrita ao vivo é o comando `set` da porta 9999 (cor em ARGB `#FFRRGGBB`); a leitura de presença usa `materials[].state` (0 vazio · 1 manual · 2 RFID · 3 alimentando · 4 retraindo) e `selected`; `printer.box.map` guarda o mapa do fatiador (usado pelo `CODEX_CFS_SELECT`).
- **Códigos de erro vistos:** `key60`/`key171` (`BOX_SET_PRE_LOADING` com parâmetros vazios — bloqueado pelo `box_guard`), `key586` (movimento fora da faixa), `key836`/`key839` (entupimento CFS→sensor), `key798` (*Motor connection failed, exceeding maximum retry count*), `key301` (*Failed automated reset of MCU* — ver §5).
- **Z-offset da tela:** não validado no 1.1.7.0 (o `prtouch-touchscreen` do Rcpilot33 foi feito para 1.1.5.5). Ajuste Z **só pela Central**, nunca pela tela da impressora.

## 4. PR Touch (`prtouch_v3`) — calibração medida no 1.1.7.0

O bico é a sonda (célula de carga); tudo mede **quente** (o firmware só proba a ~140 °C).

- **Log por amostra:** `step_bst_indx`, `step_bst_time`, `tri_pose`, `bst_pose`, `bst_zoft`. Normal: índice ≈ 47–57 e `bst_zoft` 0,010–0,035. **Anomalias** (índice 8–43, `bst_zoft` 0,04–0,107) em ≈ 2 % das amostras.
- **`Z_TILT`** usa `bst_pose` (não `tri_pose`) no "Probed points range". Config: pontos X=5/345 Y=175. A rotina marca "feito" quando o erro ≤ `retry_tolerance`. Com 0,1 uma amostra anômala passou (faixa L/R de 0,0775); o valor foi baixado para **0,03** (`probe-speed/tune.py`, idempotente). Faixa L/R normal: 0,007–0,0225.
- **Queda de borda do `Z_TILT`** (`tri_pose` em X=5/345): ≈ −0,35/−0,38 mm em corridas "quentes"; −0,77 a −1,92 em partidas a frio **(não explicado)**.
- **Mesh exagera a curvatura da mesa.** O mesh 5×5 (25–325 mm) é um parabolóide quase perfeito centrado em (175,175) (≈ 1,4·10⁻⁵·r² mm). Medido: meio da borda −0,26 a −0,33 mm, canto −0,60 a −0,66 mm. A mesa real é bem mais plana (cantos ≈ 0,10 frente a 0,15–0,25 fundo; meio da borda ≈ 0–0,05). Resultado: bordas e cantos ficam esmagados 3–6× além do real, e parece que "o Z-offset varia" e "a mesa está inclinada". **Por que o probe exagera: (não explicado).**
- **Parafusos não são a causa:** medição repetível, mesa praticamente nivelada (FE como base: FD −0,03 a −0,04, TD ≈ 0, TE +0,06). Resta uma diferença real frente/fundo de ≈ 0,05–0,1 mm que um fator único não corrige.
- **Mitigação (desligada por padrão):** `BED_MESH_SCALE FACTOR=0.x` (`features/mesh_scale`) multiplica o mesh ativo em torno de 0 (referência do `G28 Z` no centro). O `START_PRINT` só chama se `mesh_scale < 1` existir no `k2_vars.cfg`. **Validado com 0,30 (nov/2026, 9 quadrados 40×40 mm, fotos, PLA, placa high_temp):** mesh escalado de −0,196 a −0,001 mm; os 9 fecham a 1ª camada sem esmagamento severo e sem vazios. Resíduo qualitativo: brilho granulado (leve esmagamento) nos quadrados da frente, centro e fundo-esquerdo; leve falta de contato no canto fundo-direito. Ordem de grandeza do resíduo: ≈ 0,03–0,05 mm, compatível com a diferença frente/fundo. `mesh_scale = 0.3` está gravado no `k2_vars.cfg`.
- **Ordem do `START_PRINT`:** `G28 Z` → `Z_TILT` → `G28 Z` → mesh → (escala do mesh) → Z-offset por placa/material → PA. O caminho `ADAPTIVE=0` carrega o perfil em cache.
- **Z-offset tem dois níveis:** `SET_GCODE_OFFSET` (transitório, o `START_PRINT` o re-seta a cada print) e `Z_OFFSET_APPLY_PROBE` + `SAVE_CONFIG` (probe). Nunca aplique a mesma correção nos dois.

## 5. Operação: lições que custaram tempo

- **Dois `restart` do Klipper em sequência rápida** (dois `install.sh` seguidos) levaram a `key798` e depois a `key301` (*Failed automated reset of MCU*). Recuperação: `POST /printer/firmware_restart`; às vezes é preciso **repetir** a chamada. Não está provado que os dois restarts foram a causa.
- **`k2 update` = reinstalação completa** (~2–3 min, vários restarts). Faça com a impressora **parada**.
- **Bootstrap do updater:** o CLI antigo (anterior ao rename para `k2`) baixava um bootstrap com o nome antigo (404, arquivo de 0 bytes); corrigido. Se o download falhar, o `k2` cai no `bootstrap-k2.sh` local.
- Reiniciar o Klipper só com `print_stats.state != printing`. `SET_EXTRUDER_ROTATION_DISTANCE` é só em runtime.

## 6. Em aberto no 1.1.7.0

1. Por que o PR Touch exagera a curvatura (e se `BED_MESH_SCALE` com ≈ 0,30 resolve).
2. Queda de borda do `Z_TILT` em partida a frio.
3. Causa do `key798` / `key301` após restarts seguidos.
4. `step_bst_indx` anômalo (blob).
5. `key586` na purga da troca de cor (hipóteses vivas no `docs/HANDOFF-SESSAO-2026-10.md`).
6. Entupimentos recorrentes no slot T2B (`key836/839`).
