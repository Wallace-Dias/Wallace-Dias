#!/usr/bin/env python3
"""
Atualiza a seção '## 🚀 Projetos' do README.md com os top N repositórios do usuário GitHub.
Uso:
  - Opcionalmente exporte GITHUB_TOKEN para aumentar limites: export GITHUB_TOKEN=ghp_...
  - python3 scripts/update_top_repos.py
"""
import os
import sys
import json
import urllib.request
import urllib.error
import ssl
import re
import textwrap
import urllib.parse

# Config
USERNAME = 'Wallace-Dias'
TOP_N = 3
README_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
GITHUB_API = f'https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner'
TOKEN = os.environ.get('GITHUB_TOKEN')

HEADERS = {'User-Agent': 'update-top-repos-script'}
if TOKEN:
    HEADERS['Authorization'] = f'token {TOKEN}'


def fetch_repos():
    req = urllib.request.Request(GITHUB_API, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
            return data
    except urllib.error.HTTPError as e:
        print('HTTPError:', e.code, e.reason, file=sys.stderr)
        try:
            msg = e.read().decode()
            print('Response:', msg, file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    except Exception as e:
        print('Erro ao consultar API do GitHub:', e, file=sys.stderr)
        sys.exit(1)


def make_markdown(repos):
    # Gera markdown com uma tabela simples contendo os top repos
    md = []
    md.append('## 🚀 Projetos')
    md.append('')
    md.append('A seguir, os repositórios mais populares do meu perfil (atualizado automaticamente).')
    md.append('')
    md.append('| Projeto | Descrição | Linguagem | Estrelas |')
    md.append('|---|---|---:|---:|')

    for r in repos:
        name = r.get('name')
        url = r.get('html_url')
        desc = r.get('description') or ''
        desc = ' '.join(desc.split())  # single line
        if len(desc) > 140:
            desc = desc[:137].rstrip() + '...'
        lang = r.get('language') or ''
        stars = r.get('stargazers_count', 0)
        # badges
        lang_badge = f'![lang](https://img.shields.io/badge/language-{urllib.parse.quote_plus(lang)}-blue)' if lang else ''
        stars_badge = f'![stars](https://img.shields.io/github/stars/{USERNAME}/{name}?style=social)'
        md.append(f'| [{name}]({url}) | {desc} | {lang_badge} | {stars_badge} |')

    md.append('')
    md.append('> Dica: este bloco é gerado automaticamente por `scripts/update_top_repos.py`.')
    md.append('')
    return '\n'.join(md)


def replace_readme(markdown):
    if not os.path.isfile(README_PATH):
        print('README não encontrado em', README_PATH, file=sys.stderr)
        sys.exit(1)

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Procurar a seção que contenha 'Projetos' no título e substituir até a próxima linha com apenas '---' (delimitador)
    pattern = re.compile(r"(##\s*.*Projetos.*\n)(.*?)(\n---\n)", re.DOTALL | re.IGNORECASE)
    match = pattern.search(content)
    if not match:
        print("Não foi possível encontrar a seção de 'Projetos' seguida pelo delimitador '---'.", file=sys.stderr)
        print('Verifique o formato do README e que exista "---" após a seção de projetos.', file=sys.stderr)
        sys.exit(1)

    new_content = content[:match.start(1)] + markdown + content[match.end(3):]

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print('README atualizado com os top repos.')


def main():
    print('Buscando repositórios de', USERNAME)
    repos = fetch_repos()
    if not isinstance(repos, list):
        print('Resposta inesperada da API', file=sys.stderr)
        sys.exit(1)
    # ordenar por estrelas
    repos_sorted = sorted(repos, key=lambda r: r.get('stargazers_count', 0), reverse=True)
    top = repos_sorted[:TOP_N]
    md = make_markdown(top)
    replace_readme(md)


if __name__ == '__main__':
    main()
