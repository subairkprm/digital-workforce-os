import * as SecureStore from "expo-secure-store";

const ACCESS_KEY = "dwco.access-token";
const REFRESH_KEY = "dwco.refresh-token";
const TENANT_KEY = "dwco.tenant-id";

export type StoredSession = {accessToken: string; refreshToken: string; tenantId: string};

export interface TokenStore {
  load(): Promise<StoredSession | null>;
  save(session: StoredSession): Promise<void>;
  clear(): Promise<void>;
}

export const secureTokenStore: TokenStore = {
  async load() {
    const [accessToken, refreshToken, tenantId] = await Promise.all([SecureStore.getItemAsync(ACCESS_KEY), SecureStore.getItemAsync(REFRESH_KEY), SecureStore.getItemAsync(TENANT_KEY)]);
    return accessToken && refreshToken && tenantId ? {accessToken, refreshToken, tenantId} : null;
  },
  async save({accessToken, refreshToken, tenantId}) {
    await Promise.all([SecureStore.setItemAsync(ACCESS_KEY, accessToken), SecureStore.setItemAsync(REFRESH_KEY, refreshToken), SecureStore.setItemAsync(TENANT_KEY, tenantId)]);
  },
  async clear() { await Promise.all([SecureStore.deleteItemAsync(ACCESS_KEY), SecureStore.deleteItemAsync(REFRESH_KEY), SecureStore.deleteItemAsync(TENANT_KEY)]); }
};
