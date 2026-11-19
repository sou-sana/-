package jp.kids.breaktimer;

import android.content.Context;
import android.content.SharedPreferences;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/** 設定と状態の保存（再起動しても休憩が続くように端末に保存する）。 */
public class Store {
    private final SharedPreferences p;

    public Store(Context ctx) {
        // 直接ブート対応のストレージに置き、ロック解除前の起動直後でも読めるようにする
        Context dp = ctx.createDeviceProtectedStorageContext();
        p = dp.getSharedPreferences("state", Context.MODE_PRIVATE);
    }

    public int useMinutes() { return p.getInt("useMin", 45); }
    public int breakMinutes() { return p.getInt("breakMin", 15); }
    public void setMinutes(int use, int brk) {
        p.edit().putInt("useMin", use).putInt("breakMin", brk).apply();
    }

    public boolean enabled() { return p.getBoolean("enabled", false); }
    public void setEnabled(boolean v) { p.edit().putBoolean("enabled", v).apply(); }

    public boolean hasPin() { return p.contains("pinHash"); }
    public void setPin(String pin) { p.edit().putString("pinHash", hash(pin)).apply(); }
    public boolean checkPin(String pin) {
        return hasPin() && hash(pin).equals(p.getString("pinHash", ""));
    }

    public UsageClock loadClock() {
        UsageClock c = new UsageClock(useMinutes() * 60_000L, breakMinutes() * 60_000L);
        c.usedMs = p.getLong("usedMs", 0);
        c.breakEndAt = p.getLong("breakEndAt", 0);
        c.idleSince = p.getLong("idleSince", -1);
        c.lastTick = p.getLong("lastTick", 0);
        return c;
    }

    public void saveClock(UsageClock c) {
        p.edit()
                .putLong("usedMs", c.usedMs)
                .putLong("breakEndAt", c.breakEndAt)
                .putLong("idleSince", c.idleSince)
                .putLong("lastTick", c.lastTick)
                .apply();
    }

    private static String hash(String s) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] d = md.digest(("breaktimer:" + s).getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : d) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
