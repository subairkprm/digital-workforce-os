import * as SecureStore from "expo-secure-store";

const ACCESS_KEY = "dwco.access-token";
const REFRESH_KEY = "dwco.refresh-token";

export interface TokenStore {
  load(): Promise<{accessToken: string; refreshToken: string} | null>;
  save(accessToken: string, refreshToken: string): Promise<void>;
  clear(): Promise<void>;
}

export const secureTokenStore: TokenStore = {
  async load() {
    const [accessToken, refreshToken] = await Promise.all([SecureStore.getItemAsync(ACCESS_KEY), SecureStore.getItemAsync(REFRESH_KEY)]);
    return accessToken && refreshToken ? {accessToken, refreshToken} : null;
  },
  async save(accessToken, refreshToken) {
    await Promise.all([SecureStore.setItemAsync(ACCESS_KEY, accessToken), SecureStore.setItemAsync(REFRESH_KEY, refreshToken)]);
  },
  async clear() { await Promise.all([SecureStore.deleteItemAsync(ACCESS_KEY), SecureStore.deleteItemAsync(REFRESH_KEY)]); }
};
