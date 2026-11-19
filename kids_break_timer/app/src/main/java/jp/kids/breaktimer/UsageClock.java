package jp.kids.breaktimer;

/**
 * 「N分使ったらM分休み」の判定ロジック（Android非依存なので単体テスト可能）。
 *
 * - 画面ON＆ロック解除中だけ使用時間を数える
 * - 使用時間が上限に達したら休憩に入る（休憩は実時間で数える）
 * - 休憩が終わったら使用時間を0に戻す
 * - 画面OFFが休憩時間以上続いた場合も、休んだとみなして0に戻す
 */
public class UsageClock {
    /** 1回のtickで加算する最大時間。端末スリープ等で間が空いても一気に加算しない。 */
    static final long MAX_TICK_MS = 60_000L;

    public long limitMs;
    public long breakMs;

    public long usedMs = 0;
    /** 休憩の終了時刻（0なら休憩中でない） */
    public long breakEndAt = 0;
    /** 使っていない状態が始まった時刻（-1なら使用中） */
    public long idleSince = -1;
    /** 前回tickの時刻（0なら未初期化） */
    public long lastTick = 0;

    public UsageClock(long limitMs, long breakMs) {
        this.limitMs = limitMs;
        this.breakMs = breakMs;
    }

    public boolean isOnBreak(long now) {
        return breakEndAt > 0 && now < breakEndAt;
    }

    public long breakRemainingMs(long now) {
        return isOnBreak(now) ? breakEndAt - now : 0;
    }

    public long useRemainingMs() {
        return Math.max(0, limitMs - usedMs);
    }

    /** 現在の状態で時間を進める。inUse = 画面ON＆ロック解除中。 */
    public void tick(long now, boolean inUse) {
        if (lastTick == 0 || now < lastTick) {
            // 初回 or 時計が巻き戻された：基準だけ取り直す
            lastTick = now;
            if (breakEndAt > now + breakMs) breakEndAt = now + breakMs;
            return;
        }
        long dt = Math.min(now - lastTick, MAX_TICK_MS);

        if (breakEndAt > 0) {
            // 時計を進めて休憩をごまかした場合などに備え、残りは最大でも休憩時間まで
            if (breakEndAt > now + breakMs) breakEndAt = now + breakMs;
            if (now >= breakEndAt) {
                breakEndAt = 0;
                usedMs = 0;
                idleSince = inUse ? -1 : now;
            }
            lastTick = now;
            return;
        }

        if (inUse) {
            idleSince = -1;
            usedMs += dt;
            if (usedMs >= limitMs) {
                breakEndAt = now + breakMs;
            }
        } else {
            if (idleSince < 0) idleSince = lastTick;
            if (now - idleSince >= breakMs) usedMs = 0;
        }
        lastTick = now;
    }

    /** 保護者による即時リセット（休憩終了＋使用時間0）。 */
    public void reset(long now) {
        usedMs = 0;
        breakEndAt = 0;
        idleSince = -1;
        lastTick = now;
    }
}
