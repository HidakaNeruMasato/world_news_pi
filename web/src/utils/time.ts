/** 時刻フォーマット・相対表記ユーティリティ (要件 20 遵守) */

export function formatRelativeTime(isoString: string | null): string {
  if (!isoString) return 'Unknown time';
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hr ago`;
    return date.toLocaleDateString();
  } catch (e) {
    return isoString;
  }
}

export function formatFullDateTime(isoString: string | null): string {
  if (!isoString) return 'N/A';
  try {
    const date = new Date(isoString);
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch (e) {
    return isoString;
  }
}

/** 時間経過に基づく Marker Opacity の透明度計算 (要件 8 遵守) */
export function calculateMarkerOpacity(lastSeenIso: string | null, expiresIso: string | null): number {
  if (!lastSeenIso) return 1.0;
  try {
    const lastSeen = new Date(lastSeenIso).getTime();
    const now = new Date().getTime();
    const ageHours = (now - lastSeen) / (1000 * 60 * 60);

    if (ageHours <= 2.0) return 1.0;    // 新しい (0~2h): opacity 1.0
    if (ageHours <= 4.0) return 0.75;   // 中間 (2~4h): opacity 0.75
    return 0.45;                        // 古い (4h~): opacity 0.45
  } catch (e) {
    return 1.0;
  }
}
