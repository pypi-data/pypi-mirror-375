# keyvault-env

### Prerequisites

* An **Azure account** and access to an  **Azure Key Vault** .
* **Azure CLI** installed and logged in (`az login`).

---

## 🔑 Authentication

Before using the library, ensure you are authenticated with Azure:

<pre><div class="relative m-0 rounded-md border border-default bg-[#1e1e1e] whitespace-break-spaces dark:bg-subtle"><div class="rounded-b-md select-text dark:bg-subtle!"><code class="language-bash"><span>az login</span></code></div></div></pre>

The library uses `DefaultAzureCredential`, which supports multiple authentication methods (CLI, Managed Identity, Service Principal, etc.).

---

## 🛠️ Usage

### 1. Initialize the Client

<pre><div class="relative m-0 rounded-md border border-default bg-[#1e1e1e] whitespace-break-spaces dark:bg-subtle"><div class="rounded-b-md select-text dark:bg-subtle!"><code class="language-python"><span class="token">from</span><span> keyvault_env </span><span class="token">import</span><span> KeyVaultEnv
</span>
<span></span><span class="token"># Initialize with Key Vault URI</span><span>
</span><span>kv </span><span class="token">=</span><span> KeyVaultEnv</span><span class="token">(</span><span>kv_uri</span><span class="token">=</span><span class="token">"https://your-vault-name.vault.azure.net"</span><span class="token">)</span><span>
</span>
<span></span><span class="token"># Or with just the vault name</span><span>
</span><span>kv </span><span class="token">=</span><span> KeyVaultEnv</span><span class="token">(</span><span>vault_name</span><span class="token">=</span><span class="token">"your-vault-name"</span><span class="token">)</span></code></div></div></pre>

### 2. Upload Secrets from `.env`

<pre><div class="relative m-0 rounded-md border border-default bg-[#1e1e1e] whitespace-break-spaces dark:bg-subtle"><div class="rounded-b-md select-text dark:bg-subtle!"><code class="language-python"><span class="token"># Upload all secrets from .env</span><span>
</span><span>kv</span><span class="token">.</span><span>set_secrets_from_env</span><span class="token">(</span><span class="token">)</span><span>
</span>
<span></span><span class="token"># Upload only secrets with a specific prefix</span><span>
</span><span>kv</span><span class="token">.</span><span>set_secrets_from_env</span><span class="token">(</span><span>prefix</span><span class="token">=</span><span class="token">"SECRET_"</span><span class="token">)</span><span>
</span>
<span></span><span class="token"># Exclude specific keys</span><span>
</span><span>kv</span><span class="token">.</span><span>set_secrets_from_env</span><span class="token">(</span><span>exclude_keys</span><span class="token">=</span><span class="token">[</span><span class="token">"DB_PASSWORD"</span><span class="token">,</span><span></span><span class="token">"API_KEY"</span><span class="token">]</span><span class="token">)</span></code></div></div></pre>

### 3. Fetch Secrets

<pre><div class="relative m-0 rounded-md border border-default bg-[#1e1e1e] whitespace-break-spaces dark:bg-subtle"><div class="rounded-b-md select-text dark:bg-subtle!"><code class="language-python"><span class="token"># Get a single secret</span><span>
</span><span>secret_value </span><span class="token">=</span><span> kv</span><span class="token">.</span><span>get_secret</span><span class="token">(</span><span class="token">"my-secret-name"</span><span class="token">)</span><span>
</span>
<span></span><span class="token"># Get multiple secrets</span><span>
</span><span>secrets </span><span class="token">=</span><span> kv</span><span class="token">.</span><span>get_secrets</span><span class="token">(</span><span class="token">[</span><span class="token">"secret1"</span><span class="token">,</span><span></span><span class="token">"secret2"</span><span class="token">]</span><span class="token">)</span><span>
</span>
<span></span><span class="token"># List all secret names</span><span>
</span><span>secret_names </span><span class="token">=</span><span> kv</span><span class="token">.</span><span>list_secret_names</span><span class="token">(</span><span class="token">)</span><span>
</span>
<span></span><span class="token"># Get all secrets (optionally filtered by prefix)</span><span>
</span><span>all_secrets </span><span class="token">=</span><span> kv</span><span class="token">.</span><span>get_all_secrets</span><span class="token">(</span><span>prefix_filter</span><span class="token">=</span><span class="token">"SECRET_"</span><span class="token">)</span></code></div></div></pre>

---

## 📖 Function Reference

### `KeyVaultEnv(vault_name=None, kv_uri=None)`

* **Parameters** :
* `vault_name`: Name of the Azure Key Vault (e.g., `my-vault`).
* `kv_uri`: Full URI of the Key Vault (e.g., `https://my-vault.vault.azure.net`).
* **Raises** : `ValueError` if neither `vault_name` nor `kv_uri` is provided.

### `set_secrets_from_env(env_path=".env", prefix="SECRET_", exclude_keys=None, normalize_names=True)`

* **Parameters** :
* `env_path`: Path to the `.env` file.
* `prefix`: Only upload keys starting with this prefix.
* `exclude_keys`: List of keys to exclude from upload.
* `normalize_names`: If `True`, normalizes secret names for Key Vault compatibility.
* **Returns** : Dictionary of uploaded secrets.

### `set_secret(secret_name, value)`

* **Parameters** :
* `secret_name`: Name of the secret.
* `value`: Value of the secret.
* **Returns** : `None`

### `get_secret(secret_name)`

* **Parameters** :
* `secret_name`: Name of the secret to fetch.
* **Returns** : Value of the secret, or `None` if not found.

### `get_secrets(secret_names)`

* **Parameters** :
* `secret_names`: List of secret names to fetch.
* **Returns** : Dictionary of secret names and values.

### `list_secret_names(prefix_filter=None)`

* **Parameters** :
* `prefix_filter`: Only list secrets starting with this prefix.
* **Returns** : List of secret names.

### `get_all_secrets(prefix_filter=None)`

* **Parameters** :
* `prefix_filter`: Only fetch secrets starting with this prefix.
* **Returns** : Dictionary of all secrets.

---

## 📝 Notes

* **Environment Variables** : The library respects `KEYVAULT_URI` and `KEYVAULT_NAME` environment variables for configuration.
* **Normalization** : Secret names are normalized to be Key Vault-compatible (lowercase, alphanumeric, hyphens).
* **Error Handling** : Errors are logged and skipped where possible.

---

## 💡 Example

<pre><div class="relative m-0 rounded-md border border-default bg-[#1e1e1e] whitespace-break-spaces dark:bg-subtle"><div class="rounded-b-md select-text dark:bg-subtle!"><code class="language-python"><span class="token">from</span><span> keyvault_env </span><span class="token">import</span><span> KeyVaultEnv
</span>
<span></span><span class="token"># Initialize</span><span>
</span><span>kv </span><span class="token">=</span><span> KeyVaultEnv</span><span class="token">(</span><span>vault_name</span><span class="token">=</span><span class="token">"my-vault"</span><span class="token">)</span><span>
</span>
<span></span><span class="token"># Upload secrets</span><span>
</span><span>kv</span><span class="token">.</span><span>set_secrets_from_env</span><span class="token">(</span><span>prefix</span><span class="token">=</span><span class="token">"SECRET_"</span><span class="token">)</span><span>
</span>
<span></span><span class="token"># Fetch secrets</span><span>
</span><span>secrets </span><span class="token">=</span><span> kv</span><span class="token">.</span><span>get_all_secrets</span><span class="token">(</span><span>prefix_filter</span><span class="token">=</span><span class="token">"SECRET_"</span><span class="token">)</span><span>
</span><span></span><span class="token">print</span><span class="token">(</span><span>secrets</span><span class="token">)</span></code></div></div></pre>

---

## 📄 License

MIT

<pre><div class="relative m-0 rounded-md border border-default bg-[#1e1e1e] whitespace-break-spaces dark:bg-subtle"><div class="rounded-b-md select-text dark:bg-subtle!"><code class="language-text"><span>---
</span>
You can **[download the README.md file here](sandbox/README.md)**.</code></div></div></pre>
