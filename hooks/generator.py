#!/usr/bin/env python3
"""
Hook Generator - Cria arquivos JSON de hooks a partir de configuração centralizada

Uso:
    python3 hooks/generator.py [--config FILE] [--agent NAME] [--list]
"""

import json
import sys
from pathlib import Path
import argparse


def load_config(config_path: str) -> dict:
    """Carrega configuração de hooks"""
    with open(config_path, 'r') as f:
        return json.load(f)


def generate_hook_json(hook_config: dict, base_path: str, agent: str):
    """Gera estrutura JSON de um hook individual"""
    script_path = f"{base_path}/{hook_config['script']}"
    triggers = hook_config.get('triggers', '').split("|")

    for trigger in triggers:
        # Split only on the FIRST colon to handle paths/values that contain ':'
        parts = trigger.split(":", 1)
        if len(parts) != 2:
            print(f"  ⚠ Trigger malformado ignorado: '{trigger}'", file=sys.stderr)
            continue

        _agent, event = parts
        if _agent == agent:
            yield {
                "hooks": {
                    event: [
                        {
                            "type": "command",
                            "command": script_path
                        }
                    ]
                }
            }


def create_hook_files(config: dict, output_dir: str, agent: str):
    """Cria arquivos JSON de hooks no diretório especificado"""
    output_path = Path(f"{output_dir}/hooks")
    output_path.mkdir(parents=True, exist_ok=True)

    base_path = output_path

    for hook in config.get('hooks', []):
        if not hook.get('enabled', True):
            print(f"⊘ Hook '{hook['name']}' está desabilitado, pulando...")
            continue

        hook_name = hook['name']
        generated = False

        for hook_json in generate_hook_json(hook, base_path, agent):
            output_file = output_path / f"{hook_name}.json"

            with open(output_file, 'w') as f:
                json.dump(hook_json, f, indent=2)

            print(f"✓ Criado: {output_file}")
            print(f"  → Script: {hook['script']}")
            print(f"  → Descrição: {hook.get('description', 'N/A')}")
            generated = True

        if not generated:
            print(f"⊘ Hook '{hook_name}' sem triggers para o agente '{agent}', pulando...")


def list_hooks(config: dict):
    """Lista todos os hooks disponíveis"""
    print("\n" + "="*60)
    print("HOOKS DISPONÍVEIS")
    print("="*60)

    for hook in config.get('hooks', []):
        status = "✓ ATIVO" if hook.get('enabled', True) else "⊘ DESABILITADO"
        print(f"\n{status} - {hook['name']}")
        print(f"   Descrição: {hook.get('description', 'N/A')}")
        print(f"   Script:    {hook['script']}")
        # Fixed: config uses 'triggers' (plural), not 'trigger'
        print(f"   Triggers:  {hook.get('triggers', config.get('defaultTrigger', 'N/A'))}")


def main():
    parser = argparse.ArgumentParser(
        description="Gera arquivos JSON de hooks a partir de configuração centralizada"
    )
    parser.add_argument(
        '--config',
        default='./hooks/config.json',
        help='Caminho para arquivo de configuração (padrão: ./hooks/config.json)'
    )
    parser.add_argument(
        '--agent',
        default='copilot',
        help='Nome do agente (padrão: copilot)'
    )
    parser.add_argument(
        '--output',
        default='./github',
        help='Diretório de saída para os arquivos gerados (padrão: ./hooks/output)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='Apenas lista os hooks disponíveis sem gerar arquivos'
    )

    args = parser.parse_args()
    config_path = Path(args.config)

    if not config_path.exists():
        print(f"Erro: arquivo de configuração não encontrado: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(str(config_path))
    except json.JSONDecodeError as e:
        print(f"Erro ao parsear JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if args.list:
        list_hooks(config)
    else:
        print(f"Gerando hooks a partir de: {config_path}")
        create_hook_files(config, args.output, args.agent)
        print("\n✓ Hooks gerados com sucesso!")


if __name__ == '__main__':
    main()
