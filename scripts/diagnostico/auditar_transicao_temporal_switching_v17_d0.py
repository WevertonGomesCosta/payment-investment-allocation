from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

RAIZ = Path(__file__).resolve().parents[2]
XLSX = RAIZ / 'saidas' / 'oficial' / 'relatorio_operacional_v225.xlsx'
OUT = RAIZ / 'saidas' / 'diagnostico' / 'v17_d0'
OUT.mkdir(parents=True, exist_ok=True)


@dataclass
class Switching:
    lote_origem: str
    data_switching: str
    lote_destino: str
    valor_liquido_migrado: float


def _norm(s: str) -> str:
    s = (s or '').strip().lower()
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s


def _parse_float(v: str) -> float:
    t = (v or '').strip()
    if not t:
        return 0.0
    t = t.replace('.', '').replace(',', '.')
    try:
        return float(t)
    except Exception:
        return 0.0


def _xlsx_sheets(path: Path) -> dict[str, list[list[str]]]:
    if not path.exists():
        return {}
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root.findall('m:si', ns):
                txt = ''.join(t.text or '' for t in si.findall('.//m:t', ns))
                shared.append(txt)

        wb = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels}
        out: dict[str, list[list[str]]] = {}
        for sh in wb.findall('m:sheets/m:sheet', ns):
            nm = sh.attrib.get('name', '')
            rid = sh.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', '')
            target = rel_map.get(rid, '')
            part = 'xl/' + target.lstrip('/')
            if part not in z.namelist():
                continue
            ws = ET.fromstring(z.read(part))
            rows = []
            for row in ws.findall('m:sheetData/m:row', ns):
                vals = {}
                maxc = 0
                for c in row.findall('m:c', ns):
                    ref = c.attrib.get('r', 'A1')
                    col = ''.join(ch for ch in ref if ch.isalpha())
                    idx = 0
                    for ch in col:
                        idx = idx * 26 + (ord(ch) - 64)
                    idx -= 1
                    maxc = max(maxc, idx)
                    t = c.attrib.get('t', '')
                    v = c.find('m:v', ns)
                    value = v.text if v is not None and v.text is not None else ''
                    if t == 's' and value.isdigit():
                        value = shared[int(value)] if int(value) < len(shared) else ''
                    vals[idx] = value
                line = [''] * (maxc + 1)
                for i, v in vals.items():
                    line[i] = v
                rows.append(line)
            out[nm] = rows
    return out


def _extract_switchings(sheet: list[list[str]]) -> list[Switching]:
    if not sheet:
        return []
    header = [_norm(c) for c in sheet[0]]
    def idx(opts: list[str]) -> int:
        for o in opts:
            if o in header:
                return header.index(o)
        return -1
    i_origem = idx([
        'lote id antes',
        'lote antes',
        'lote origem',
        'lote origem switching',
        'lote_origem',
        'origem',
    ])
    i_data = idx([
        'data sugerida',
        'data switching',
        'data_switching',
        'data',
    ])
    i_dest = idx([
        'lote id depois',
        'lote depois',
        'lote destino',
        'lote_destino',
        'destino switching',
        'destino_switching',
        'produto destino switching',
        'destino',
    ])
    i_val = idx([
        'valor liquido migrado',
        'valor_liquido_migrado',
        'valor liquido origem',
        'valor_liquido_origem',
        'valor liquido',
        'valor_liquido',
    ])
    out = []
    for r in sheet[1:]:
        origem = r[i_origem] if i_origem >= 0 and i_origem < len(r) else ''
        if not origem:
            continue
        out.append(Switching(
            lote_origem=str(origem),
            data_switching=str(r[i_data] if i_data >= 0 and i_data < len(r) else ''),
            lote_destino=str(r[i_dest] if i_dest >= 0 and i_dest < len(r) else ''),
            valor_liquido_migrado=_parse_float(str(r[i_val] if i_val >= 0 and i_val < len(r) else '0')),
        ))
    return out


def _contains_lote(rows: list[list[str]], lote: str) -> bool:
    n = _norm(lote)
    for r in rows:
        for c in r:
            if n and n in _norm(c):
                return True
    return False


def _write_csv(path: Path, cols: list[str], data: list[dict]) -> None:
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for d in data:
            w.writerow(d)


def main() -> int:
    sheets = _xlsx_sheets(XLSX)
    switching_sheet = sheets.get('Switching', [])
    situacao = sheets.get('Situação Atual', []) or sheets.get('Situacao Atual', [])
    inventario = sheets.get('Inventário de Lotes', []) or sheets.get('Inventario de Lotes', [])
    extrato_futuro = sheets.get('Extrato Futuro', [])

    switchings = _extract_switchings(switching_sheet)
    origens = []
    usos = []
    destinos = []
    matriz = []

    for s in switchings:
        ativo = _contains_lote(situacao, s.lote_origem)
        exaurido = _contains_lote(inventario, s.lote_origem) and ('exaur' in _norm(' '.join(' '.join(r) for r in inventario[:30])))
        viol_ativo = bool(ativo)
        origens.append({
            'lote_origem': s.lote_origem, 'data_switching': s.data_switching, 'destino_switching': s.lote_destino,
            'valor_liquido_migrado': s.valor_liquido_migrado, 'aparece_em_situacao_atual_ativo': ativo,
            'aparece_em_lotes_exauridos': exaurido, 'status_observado': 'ativo_pos_switching' if ativo else 'nao_ativo_pos_switching',
            'status_esperado_contrato': 'origem_migrada_nao_ativa', 'violacao_lote_origem_ativo': viol_ativo,
            'justificativa': 'lote de origem ainda visível após switching' if viol_ativo else 'sem indício de atividade indevida',
        })

        uso_pos = _contains_lote(extrato_futuro, s.lote_origem)
        usos.append({
            'lote_origem': s.lote_origem, 'data_switching': s.data_switching, 'data_pagamento': '', 'descricao_pagamento': '',
            'valor_pagamento': 0.0, 'origem_ocorrencia': 'Extrato Futuro', 'dias_apos_switching': '',
            'violacao_uso_pos_switching': uso_pos,
            'justificativa': 'origem aparece em estrutura de pagamentos futuros' if uso_pos else 'sem uso pós-switching detectado',
        })

        ap_inv = _contains_lote(inventario, s.lote_destino)
        ap_sit = _contains_lote(situacao, s.lote_destino)
        ap_sint = _contains_lote(switching_sheet, s.lote_destino)
        mat = ap_inv or ap_sit
        viol_dest = not mat
        destinos.append({
            'lote_origem': s.lote_origem, 'lote_destino': s.lote_destino, 'produto_destino': '', 'data_recebimento': '', 'data_aplicacao': '',
            'valor_liquido_migrado': s.valor_liquido_migrado, 'aparece_no_inventario': ap_inv, 'aparece_na_situacao_atual': ap_sit,
            'aparece_como_lote_sintetico': ap_sint, 'materializacao_observada': 'sim' if mat else 'nao', 'materializacao_esperada': 'sim',
            'violacao_destino_nao_materializado': viol_dest,
            'justificativa': 'destino sem materialização auditável' if viol_dest else 'destino identificado em estado temporal',
        })

    origens_ativas = sum(1 for x in origens if x['violacao_lote_origem_ativo'])
    usos_pos = sum(1 for x in usos if x['violacao_uso_pos_switching'])
    dest_nao = sum(1 for x in destinos if x['violacao_destino_nao_materializado'])
    dupla = any(o['violacao_lote_origem_ativo'] and (not d['violacao_destino_nao_materializado']) for o, d in zip(origens, destinos))

    if usos_pos:
        matriz.append({'regra_contrato_modelo': 'origem_migrada_nao_pode_pagar', 'evidencia_observada': f'{usos_pos} origens usadas pós-switching', 'status_aderencia': 'violado', 'severidade': 'alta', 'impacto_potencial': 'pagamento indevido', 'tipo_correcao_futura': 'v17_d1_transicao_temporal', 'observacao': 'uso pós-switching detectado'})
    if origens_ativas:
        matriz.append({'regra_contrato_modelo': 'origem_migrada_nao_pode_estar_ativa', 'evidencia_observada': f'{origens_ativas} origens ativas', 'status_aderencia': 'violado', 'severidade': 'alta', 'impacto_potencial': 'dupla contagem patrimonial', 'tipo_correcao_futura': 'v17_d1_transicao_temporal', 'observacao': 'origem ainda ativa'})
    if dest_nao:
        matriz.append({'regra_contrato_modelo': 'destino_pos_switching_deve_materializar', 'evidencia_observada': f'{dest_nao} destinos não materializados', 'status_aderencia': 'violado', 'severidade': 'alta', 'impacto_potencial': 'quebra de rastreabilidade', 'tipo_correcao_futura': 'v17_d1_transicao_temporal', 'observacao': 'destino ausente'})
    if not matriz:
        matriz.append({'regra_contrato_modelo': 'aderencia_geral', 'evidencia_observada': 'sem violacoes detectadas', 'status_aderencia': 'aderente', 'severidade': 'baixa', 'impacto_potencial': 'nenhum', 'tipo_correcao_futura': 'sem_correcao', 'observacao': ''})

    resumo = [
        {'metrica': 'status_global_v17_d0', 'valor': 'ok_diagnostico'},
        {'metrica': 'switchings_auditados', 'valor': len(switchings)},
        {'metrica': 'lotes_origem_auditados', 'valor': len({s.lote_origem for s in switchings})},
        {'metrica': 'lotes_destino_auditados', 'valor': len({s.lote_destino for s in switchings})},
        {'metrica': 'origens_ativas_pos_switching', 'valor': origens_ativas},
        {'metrica': 'origens_usadas_pagamento_pos_switching', 'valor': usos_pos},
        {'metrica': 'destinos_nao_materializados', 'valor': dest_nao},
        {'metrica': 'possivel_dupla_contagem', 'valor': dupla},
        {'metrica': 'violacoes_contrato_modelo_total', 'valor': sum(1 for m in matriz if m['status_aderencia'] == 'violado')},
        {'metrica': 'decisao_correcao_funcional', 'valor': 'abrir_v17_d1_se_confirmadas_violacoes_temporais' if any(m['status_aderencia']=='violado' for m in matriz) else 'sem_correcao_funcional_necessaria'},
        {'metrica': 'confirmacao_sem_alterar_motor', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_contrato_modelo', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_ranking', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_pagamentos', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_switching', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_saida_operacional', 'valor': True},
    ]

    _write_csv(OUT / 'v17_d0_origens_switching_estado_atual.csv', list(origens[0].keys()) if origens else ['lote_origem','data_switching','destino_switching','valor_liquido_migrado','aparece_em_situacao_atual_ativo','aparece_em_lotes_exauridos','status_observado','status_esperado_contrato','violacao_lote_origem_ativo','justificativa'], origens)
    _write_csv(OUT / 'v17_d0_uso_pos_switching_pagamentos.csv', list(usos[0].keys()) if usos else ['lote_origem','data_switching','data_pagamento','descricao_pagamento','valor_pagamento','origem_ocorrencia','dias_apos_switching','violacao_uso_pos_switching','justificativa'], usos)
    _write_csv(OUT / 'v17_d0_destinos_switching_materializacao.csv', list(destinos[0].keys()) if destinos else ['lote_origem','lote_destino','produto_destino','data_recebimento','data_aplicacao','valor_liquido_migrado','aparece_no_inventario','aparece_na_situacao_atual','aparece_como_lote_sintetico','materializacao_observada','materializacao_esperada','violacao_destino_nao_materializado','justificativa'], destinos)
    _write_csv(OUT / 'v17_d0_matriz_aderencia_contrato_modelo.csv', list(matriz[0].keys()), matriz)
    _write_csv(OUT / 'v17_d0_resumo.csv', ['metrica', 'valor'], resumo)

    print('=== V17-D0 — AUDITORIA TRANSICAO TEMPORAL POS-SWITCHING ===')
    for r in resumo:
        print(f"{r['metrica']}={r['valor']}")
    print(f'output_dir={OUT}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
