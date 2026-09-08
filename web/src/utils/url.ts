/**
 * URL 安全性検証ユーティリティ (T023-1)
 * http: および https: プロトコルの安全な外部リンクのみを許可します。
 */
export function isSafeHttpUrl(value?: string | null): boolean {
  if (!value || typeof value !== 'string') {
    return false;
  }

  const trimmed = value.trim();
  if (!trimmed) {
    return false;
  }

  try {
    const url = new URL(trimmed);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}
