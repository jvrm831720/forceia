"""
Cria um workspace (cliente ForceIA) no Supabase.

  python create_workspace.py --name "Clinica Exemplo" --slug clinica-exemplo
  python create_workspace.py --name "Agencia X" --slug agencia-x --instance agencia-x-wa
"""

from __future__ import annotations

import argparse
import secrets

from db import create_workspace, get_workspace_by_slug


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--instance", default=None, help="Nome da instancia Evolution")
    parser.add_argument("--plan", default="completo")
    args = parser.parse_args()

    if get_workspace_by_slug(args.slug):
        print(f"Slug '{args.slug}' ja existe")
        return

    api_key = secrets.token_hex(24)
    row = create_workspace(
        name=args.name,
        slug=args.slug,
        api_key=api_key,
        evolution_instance=args.instance or args.slug,
        plan=args.plan,
    )
    print("Workspace criado:")
    print(f"  id:       {row.get('id')}")
    print(f"  name:     {row.get('name')}")
    print(f"  slug:     {row.get('slug')}")
    print(f"  api_key:  {row.get('api_key') or api_key}")
    print(f"  instance: {row.get('evolution_instance')}")
    print("\nUse no webhook: header X-Workspace-Key ou instance Evolution = slug/instance")


if __name__ == "__main__":
    main()
