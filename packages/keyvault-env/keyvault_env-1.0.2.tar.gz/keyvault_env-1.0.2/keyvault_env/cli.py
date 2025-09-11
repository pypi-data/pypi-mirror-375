import argparse
import os
import sys
from .core import KeyVaultEnv

def resolve_vault_arg(provided: str) -> str:
    """
    Accept either a full URI or a plain name. If provided is None, check KEYVAULT_URI env var.
    Returns final URI string or raises ValueError.
    """
    if provided:
        if provided.startswith("https://"):
            return provided
        else:
            return f"https://{provided}.vault.azure.net"
    env_uri = os.environ.get("KEYVAULT_URI")
    if env_uri:
        return env_uri
    env_name = os.environ.get("KEYVAULT_NAME")
    if env_name:
        return f"https://{env_name}.vault.azure.net"
    raise ValueError("No Key Vault specified. Provide --vault or set KEYVAULT_URI in environment.")

def main(argv=None):
    parser = argparse.ArgumentParser(prog="kv-env", description="Upload/fetch secrets to/from Azure Key Vault using a .env file")
    sub = parser.add_subparsers(dest="cmd", required=True)

    up = sub.add_parser("upload", help="Upload secrets from .env to Key Vault")
    up.add_argument("--env", "-e", default=".env", help="Path to .env file (default: .env)")
    up.add_argument("--prefix", "-p", default="SECRET_", help="Env var prefix used for secrets (default: SECRET_)")
    up.add_argument("--vault", "-v", help="Key Vault name or full URI. Example: https://myvault.vault.azure.net or myvault")

    get = sub.add_parser("get", help="Get secret(s) from Key Vault")
    get.add_argument("names", nargs="+", help="Secret name(s) to fetch")
    get.add_argument("--vault", "-v", help="Key Vault name or full URI")

    listp = sub.add_parser("list", help="List secrets in Key Vault (and optionally fetch values)")
    listp.add_argument("--fetch-values", action="store_true", help="Also fetch secret values (could be slow)")
    listp.add_argument("--prefix", "-p", default=None, help="Filter secret names by prefix")
    listp.add_argument("--vault", "-v", help="Key Vault name or full URI")

    args = parser.parse_args(argv)

    # Resolve vault URI (or exit with an error)
    try:
        vault_uri = resolve_vault_arg(args.vault)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Provide the vault using --vault <name-or-uri> or set KEYVAULT_URI environment variable.", file=sys.stderr)
        sys.exit(2)

    kv_env = KeyVaultEnv(kv_uri=vault_uri)

    if args.cmd == "upload":
        res = kv_env.set_secrets_from_env(env_path=args.env, prefix=args.prefix)
        print(f"Uploaded {len(res)} secrets.")
    elif args.cmd == "get":
        out = kv_env.get_secrets(args.names)
        for k, v in out.items():
            print(f"{k}={v}")
    elif args.cmd == "list":
        names = kv_env.list_secret_names(prefix_filter=args.prefix)
        print("\n".join(names))
        if args.fetch_values:
            values = kv_env.get_secrets(names)
            for k, v in values.items():
                print(f"{k}={v}")

if __name__ == "__main__":
    main()
