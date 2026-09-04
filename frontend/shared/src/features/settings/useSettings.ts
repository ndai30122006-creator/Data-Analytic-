import { useState } from "react";
import { auth } from "../../api/auth.js";
import { PROVIDERS, type Provider } from "./providers.js";

export function useSettings() {
  const [apiKey, setApiKey] = useState("");
  const [provider, setProvider] = useState<Provider>(PROVIDERS[0]);
  const [saving, setSaving] = useState(false);

  const saveApiKey = async (key: string, prov: Provider = provider) => {
    setSaving(true);
    try {
      const res = await auth.saveApiKey(key);
      setApiKey(key);
      setProvider(prov);
      return res;
    } finally {
      setSaving(false);
    }
  };

  return { apiKey, provider, saving, setApiKey, setProvider, saveApiKey, PROVIDERS };
}
