package jp.kids.breaktimer;

import android.Manifest;
import android.app.Activity;
import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.text.InputType;
import android.view.Gravity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

/** 保護者用の設定画面。開くたびにパスワードを求める。 */
public class MainActivity extends Activity {
    private Store store;
    private boolean unlocked = false;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        store = new Store(this);
    }

    @Override protected void onResume() {
        super.onResume();
        if (!store.hasPin()) showCreatePin();
        else if (!unlocked) showPinGate();
        else showSettings();
    }

    @Override protected void onStop() {
        super.onStop();
        // アプリを離れたら次回はまたパスワードを求める
        unlocked = false;
    }

    // ---- 画面 ----

    private void showCreatePin() {
        LinearLayout l = column();
        l.addView(title("はじめに保護者パスワードを決めてください"));
        l.addView(text("4けた以上の数字。子どもに知られないものにしてください。"));
        EditText p1 = pinInput("パスワード");
        EditText p2 = pinInput("もう一度");
        l.addView(p1);
        l.addView(p2);
        l.addView(button("決定", () -> {
            String a = p1.getText().toString();
            if (a.length() < 4) { toast("4けた以上にしてください"); return; }
            if (!a.equals(p2.getText().toString())) { toast("一致しません"); return; }
            store.setPin(a);
            unlocked = true;
            showSettings();
        }));
        setScreen(l);
    }

    private void showPinGate() {
        LinearLayout l = column();
        l.addView(title("保護者パスワード"));
        EditText p = pinInput("パスワード");
        l.addView(p);
        l.addView(button("ひらく", () -> {
            if (store.checkPin(p.getText().toString())) {
                unlocked = true;
                showSettings();
            } else {
                toast("パスワードがちがいます");
                p.setText("");
            }
        }));
        setScreen(l);
    }

    private void showSettings() {
        LinearLayout l = column();
        l.addView(title("やすみタイマー"));

        UsageClock c = store.loadClock();
        long now = System.currentTimeMillis();
        String status;
        if (!store.enabled()) status = "状態：停止中";
        else if (c.isOnBreak(now)) status = "状態：休憩中（あと" + TimerService.fmt(c.breakRemainingMs(now)) + "）";
        else status = "状態：見守り中（使える時間 あと" + TimerService.fmt(c.useRemainingMs()) + "）";
        l.addView(text(status));

        l.addView(section("時間の設定（分）"));
        EditText use = numberInput("使える時間", store.useMinutes());
        EditText brk = numberInput("休憩時間", store.breakMinutes());
        l.addView(labeled("使える時間", use));
        l.addView(labeled("休憩時間", brk));
        l.addView(button("時間を保存", () -> {
            int u = parse(use), k = parse(brk);
            if (u < 1 || k < 1 || u > 600 || k > 600) { toast("1〜600分で入力してください"); return; }
            store.setMinutes(u, k);
            if (store.enabled()) {
                startForegroundService(new Intent(this, TimerService.class).setAction(TimerService.ACTION_RELOAD));
            }
            toast("保存しました");
        }));

        l.addView(section("必要な許可（すべて ✅ にしてください）"));
        l.addView(permButton("他のアプリの上に重ねて表示", Settings.canDrawOverlays(this), () ->
                startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getPackageName())))));
        if (Build.VERSION.SDK_INT >= 33) {
            boolean ok = checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED;
            l.addView(permButton("通知（残り時間の表示）", ok, () ->
                    requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1)));
        }
        boolean battery = getSystemService(PowerManager.class).isIgnoringBatteryOptimizations(getPackageName());
        l.addView(permButton("電池の最適化をしない（止まらないように）", battery, () ->
                startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                        Uri.parse("package:" + getPackageName())))));
        DevicePolicyManager dpm = getSystemService(DevicePolicyManager.class);
        ComponentName admin = new ComponentName(this, AdminReceiver.class);
        l.addView(permButton("端末管理アプリ（勝手に消されないように）", dpm.isAdminActive(admin), () -> {
            Intent i = new Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN);
            i.putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, admin);
            i.putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION, "やすみタイマーを子どもが削除できないようにします。");
            startActivity(i);
        }));

        l.addView(section("操作"));
        if (store.enabled()) {
            l.addView(button("見守りを止める", () -> {
                store.setEnabled(false);
                stopService(new Intent(this, TimerService.class));
                showSettings();
            }));
            l.addView(button("今すぐリセット（休憩終了・使用時間0）", () -> {
                startForegroundService(new Intent(this, TimerService.class).setAction(TimerService.ACTION_RESET));
                toast("リセットしました");
                l.postDelayed(this::showSettings, 300);
            }));
        } else {
            l.addView(button("見守りを開始する", () -> {
                if (!Settings.canDrawOverlays(this)) { toast("先に「他のアプリの上に重ねて表示」を許可してください"); return; }
                store.setEnabled(true);
                UsageClock fresh = store.loadClock();
                fresh.reset(System.currentTimeMillis());
                store.saveClock(fresh);
                TimerService.start(this);
                toast("開始しました");
                l.postDelayed(this::showSettings, 300);
            }));
        }
        l.addView(button("パスワードを変更", this::showCreatePin));
        setScreen(l);
    }

    @Override public void onRequestPermissionsResult(int code, String[] perms, int[] results) {
        super.onRequestPermissionsResult(code, perms, results);
        if (unlocked) showSettings();
    }

    // ---- 部品 ----

    private void setScreen(LinearLayout l) {
        ScrollView s = new ScrollView(this);
        s.addView(l);
        setContentView(s);
    }

    private LinearLayout column() {
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);
        int p = dp(20);
        l.setPadding(p, p * 2, p, p);
        return l;
    }

    private TextView title(String s) {
        TextView t = text(s);
        t.setTextSize(22);
        t.setPadding(0, 0, 0, dp(12));
        return t;
    }

    private TextView section(String s) {
        TextView t = text(s);
        t.setTextSize(17);
        t.setPadding(0, dp(20), 0, dp(6));
        return t;
    }

    private TextView text(String s) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(15);
        return t;
    }

    private Button button(String s, Runnable r) {
        Button b = new Button(this);
        b.setText(s);
        b.setAllCaps(false);
        b.setOnClickListener(v -> r.run());
        return b;
    }

    private Button permButton(String s, boolean ok, Runnable r) {
        Button b = button((ok ? "✅ " : "⚠️ ") + s, r);
        b.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        return b;
    }

    private EditText pinInput(String hint) {
        EditText e = new EditText(this);
        e.setHint(hint);
        e.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_VARIATION_PASSWORD);
        return e;
    }

    private EditText numberInput(String hint, int value) {
        EditText e = new EditText(this);
        e.setHint(hint);
        e.setInputType(InputType.TYPE_CLASS_NUMBER);
        e.setText(String.valueOf(value));
        e.setMinWidth(dp(100));
        return e;
    }

    private LinearLayout labeled(String label, EditText e) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        TextView t = text(label);
        t.setMinWidth(dp(120));
        row.addView(t);
        row.addView(e);
        return row;
    }

    private int parse(EditText e) {
        try { return Integer.parseInt(e.getText().toString().trim()); }
        catch (NumberFormatException ex) { return -1; }
    }

    private void toast(String s) { Toast.makeText(this, s, Toast.LENGTH_SHORT).show(); }

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }
}
