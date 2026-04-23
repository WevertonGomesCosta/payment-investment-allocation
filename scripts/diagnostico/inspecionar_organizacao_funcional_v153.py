from __future__ import annotations

import ast
import json
from pathlib import Path


def gerar_inventario_funcoes(raiz: Path) -> dict:
    registros = []
    for arquivo in sorted(raiz.rglob('*.py')):
        if '__pycache__' in arquivo.parts:
            continue
        texto = arquivo.read_text(encoding='utf-8')
        try:
            arvore = ast.parse(texto)
            funcoes = []
            classes = []
            for no in arvore.body:
                if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcoes.append({
                        'name': no.name,
                        'lineno': no.lineno,
                        'visibility': 'private' if no.name.startswith('_') else 'public',
                    })
                elif isinstance(no, ast.ClassDef):
                    classes.append({'name': no.name, 'lineno': no.lineno})
            status = 'ok'
            parse_error = None
        except Exception as exc:
            funcoes = []
            classes = []
            status = 'parse_error'
            parse_error = str(exc)
        registros.append({
            'path': str(arquivo.relative_to(raiz)),
            'lines': len(texto.splitlines()),
            'functions': funcoes,
            'classes': classes,
            'function_count': len(funcoes),
            'class_count': len(classes),
            'status': status,
            'parse_error': parse_error,
        })
    return {'status': 'ok', 'versao': 'V153', 'arquivos': registros}


def main() -> int:
    raiz = Path(__file__).resolve().parents[2]
    payload = gerar_inventario_funcoes(raiz)
    saida = raiz / 'saidas' / 'diagnostico' / 'inventario_funcoes_v153.json'
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Inventário funcional salvo em {saida}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
