import os
import re
from typing import Dict, Iterable, List, Optional
from dotenv import dotenv_values, load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class KeyVaultEnv:
    """
    Helper to upload secrets from a .env and fetch secrets from Azure Key Vault.

    IMPORTANT: A Key Vault must be specified explicitly via:
      - kv_uri (full vault URI), OR
      - vault_name (plain vault name) OR
      - environment variable KEYVAULT_URI
    """

    def __init__(self, vault_name: Optional[str] = None, kv_uri: Optional[str] = None):
        # Priority:
        # 1. explicit kv_uri
        # 2. explicit vault_name
        # 3. KEYVAULT_URI env var
        # 4. KEYVAULT_NAME env var
        env_kv_uri = os.environ.get("KEYVAULT_URI")
        env_kv_name = os.environ.get("KEYVAULT_NAME")

        if kv_uri:
            self.vault_url = kv_uri
        elif vault_name:
            self.vault_url = self._name_to_uri(vault_name)
        elif env_kv_uri:
            self.vault_url = env_kv_uri
        elif env_kv_name:
            self.vault_url = self._name_to_uri(env_kv_name)
        else:
            raise ValueError(
                "Key Vault not provided. Set KEYVAULT_URI environment variable or pass --vault / vault_name."
                " Example KEYVAULT_URI='https://myvault.vault.azure.net'"
            )

        # basic validation
        if not self.vault_url.startswith("https://") or ".vault.azure.net" not in self.vault_url:
            # allow plain name that will be converted earlier, but if we get here the user supplied invalid uri
            raise ValueError(f"Invalid Key Vault URI: {self.vault_url}. Expected form: https://<name>.vault.azure.net")

        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)
        logger.info("Initialized KeyVaultEnv for %s", self.vault_url)

    @staticmethod
    def _name_to_uri(name: str) -> str:
        name = name.strip()
        if name.startswith("https://"):
            return name
        return f"https://{name}.vault.azure.net"

    @staticmethod
    def _load_env_file(env_path: str = ".env") -> Dict[str, str]:
        load_dotenv(env_path, override=False)
        return dict(dotenv_values(env_path))

    @staticmethod
    def _normalize_secret_name(name: str) -> str:
        """
        Make a vault-safe secret name:
         - strip whitespace
         - lowercase
         - replace runs of non-alphanumeric characters with '-'
         - trim leading/trailing '-'
        """
        name = name.strip().lower()
        # replace spaces and other disallowed chars with '-'
        name = re.sub(r'[^a-z0-9]+', '-', name)
        name = name.strip('-')
        if not name:
            raise ValueError("Secret name is empty after normalization.")
        return name

    @staticmethod
    def _clean_value(val: Optional[str]) -> Optional[str]:
        """Trim whitespace and strip surrounding quotes if present."""
        if val is None:
            return None
        v = val.strip()
        # remove surrounding single/double quotes e.g. "value" or 'value'
        if len(v) >= 2 and ((v[0] == v[-1]) and v[0] in ("'", '"')):
            v = v[1:-1]
        return v

    def set_secrets_from_env(
        self,
        env_path: str = ".env",
        prefix: Optional[str] = "SECRET_",
        exclude_keys: Optional[Iterable[str]] = None,
        normalize_names: bool = True,
    ) -> Dict[str, str]:
        """
        Upload secrets from an .env file.

        - If prefix is a non-empty string: only keys that start with that prefix are uploaded,
          and the prefix is removed when forming the secret name.
        - If prefix is None (or empty string ""), upload all keys except the default excludes and any
          keys in exclude_keys.
        - exclude_keys can be passed to protect additional env keys from being uploaded.
        - normalize_names replaces non-alphanumeric chars with '-' and lowercases names so they are
          safe for Key Vault.
        """
        # default excludes (don't upload these control/auth keys)
        default_excludes = {
            "KEYVAULT_URI", "KEYVAULT_NAME",
            "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID",
            # optional: skip dotenv comment or runtime-only keys
        }
        if exclude_keys:
            default_excludes.update({k.upper() for k in exclude_keys})

        # load .env (won't override os.environ)
        load_dotenv(env_path, override=False)
        env_map = dict(dotenv_values(env_path))

        results: Dict[str, str] = {}

        # Decide behavior: prefix-based or all-keys mode
        use_all = prefix is None or prefix == ""

        for raw_k, raw_v in env_map.items():
            if raw_k is None:
                continue
            k = raw_k.strip()
            # skip control keys
            if k.upper() in default_excludes:
                continue

            # select keys matching prefix, or all if use_all
            if not use_all:
                if not k.startswith(prefix):
                    continue
                secret_name_raw = k[len(prefix):]
            else:
                secret_name_raw = k

            # final check and cleaning
            v = self._clean_value(raw_v)
            if v is None or v == "":
                # skip empty values
                continue

            # normalize secret name if requested
            if normalize_names:
                try:
                    secret_name = self._normalize_secret_name(secret_name_raw)
                except ValueError:
                    # skip keys that normalize to empty
                    continue
            else:
                secret_name = secret_name_raw.strip()

            # Upload
            try:
                self.client.set_secret(secret_name, v)
                results[secret_name] = v
            except Exception as e:
                # log and continue (preserve previous behavior)
                logger.exception("Failed to set secret %s from env var %s: %s", secret_name, k, e)

        logger.info("Finished setting %d secrets.", len(results))
        return results

    def set_secret(self, secret_name: str, value: str) -> None:
        logger.info("Setting secret '%s'...", secret_name)
        self.client.set_secret(secret_name, value)

    def get_secret(self, secret_name: str) -> Optional[str]:
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.exception("Failed to get secret %s: %s", secret_name, e)
            return None

    def get_secrets(self, secret_names: Iterable[str]) -> Dict[str, Optional[str]]:
        out = {}
        for name in secret_names:
            out[name] = self.get_secret(name)
        return out

    def list_secret_names(self, prefix_filter: Optional[str] = None) -> List[str]:
        names = []
        try:
            props_iter = self.client.list_properties_of_secrets()
            for prop in props_iter:
                if prop.name:
                    if prefix_filter is None or prop.name.startswith(prefix_filter):
                        names.append(prop.name)
        except Exception as e:
            logger.exception("Failed to list secrets: %s", e)
        return names

    def get_all_secrets(self, prefix_filter: Optional[str] = None) -> Dict[str, Optional[str]]:
        names = self.list_secret_names(prefix_filter=prefix_filter)
        logger.info("Fetching values for %d secrets...", len(names))
        return self.get_secrets(names)
