package jp.kids.breaktimer;

import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.provider.Settings;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

/** 休憩中に画面全体を覆う表示。他のアプリやホーム画面には触れなくなる。 */
public class BreakOverlay {
    private final Context ctx;
    private final Store store;
    private final Runnable onParentUnlock;
    private final WindowManager wm;
    private LinearLayout root;
    private TextView countdown;
    private EditText pinField;
    private TextView message;

    public BreakOverlay(Context ctx, Store store, Runnable onParentUnlock) {
        this.ctx = ctx;
        this.store = store;
        this.onParentUnlock = onParentUnlock;
        this.wm = ctx.getSystemService(WindowManager.class);
    }

    public boolean isShowing() { return root != null; }

    public void show(long remainingMs) {
        if (root == null) {
            if (!Settings.canDrawOverlays(ctx)) return;
            build();
            WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                    WindowManager.LayoutParams.MATCH_PARENT,
                    WindowManager.LayoutParams.MATCH_PARENT,
                    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                    WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                            | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
                    PixelFormat.OPAQUE);
            lp.gravity = Gravity.CENTER;
            lp.softInputMode = WindowManager.LayoutParams.SOFT_INPUT_ADJUST_PAN;
            try {
                wm.addView(root, lp);
            } catch (Exception e) {
                root = null;
                return;
            }
        }
        update(remainingMs);
    }

    public void update(long remainingMs) {
        if (countdown != null) countdown.setText(TimerService.fmt(remainingMs));
    }

    public void hide() {
        if (root != null) {
            try { wm.removeView(root); } catch (Exception ignored) { }
            root = null;
            countdown = null;
            pinField = null;
            message = null;
        }
    }

    private void build() {
        root = new LinearLayout(ctx) {
            @Override public boolean dispatchKeyEvent(KeyEvent event) {
                // 戻るボタンで閉じられないようにする
                if (event.getKeyCode() == KeyEvent.KEYCODE_BACK) return true;
                return super.dispatchKeyEvent(event);
            }
        };
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setBackgroundColor(Color.rgb(32, 70, 110));
        int pad = dp(32);
        root.setPadding(pad, pad, pad, pad);

        TextView title = text("おやすみタイム", 32, Color.WHITE);
        TextView sub = text("目をやすめて、からだを動かそう", 18, Color.rgb(200, 220, 240));
        TextView label = text("あと", 20, Color.WHITE);
        countdown = text("--:--", 72, Color.WHITE);
        countdown.setPadding(0, 0, 0, dp(40));

        pinField = new EditText(ctx);
        pinField.setHint("保護者パスワード");
        pinField.setHintTextColor(Color.rgb(150, 170, 190));
        pinField.setTextColor(Color.WHITE);
        pinField.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_VARIATION_PASSWORD);
        pinField.setGravity(Gravity.CENTER);
        pinField.setVisibility(View.GONE);

        message = text("", 14, Color.rgb(255, 180, 180));

        Button parent = new Button(ctx);
        parent.setText("保護者");
        parent.setAlpha(0.6f);
        parent.setOnClickListener(v -> {
            if (pinField.getVisibility() != View.VISIBLE) {
                pinField.setVisibility(View.VISIBLE);
                pinField.requestFocus();
                parent.setText("休憩を終わらせる");
                return;
            }
            if (store.checkPin(pinField.getText().toString())) {
                onParentUnlock.run();
            } else {
                message.setText("パスワードがちがいます");
                pinField.setText("");
            }
        });

        root.addView(title);
        root.addView(sub);
        root.addView(space(dp(32)));
        root.addView(label);
        root.addView(countdown);
        root.addView(pinField, new LinearLayout.LayoutParams(dp(220), LinearLayout.LayoutParams.WRAP_CONTENT));
        root.addView(message);
        root.addView(parent);
    }

    private TextView text(String s, int sp, int color) {
        TextView t = new TextView(ctx);
        t.setText(s);
        t.setTextSize(sp);
        t.setTextColor(color);
        t.setGravity(Gravity.CENTER);
        return t;
    }

    private View space(int h) {
        View v = new View(ctx);
        v.setMinimumHeight(h);
        return v;
    }

    private int dp(int v) {
        return Math.round(v * ctx.getResources().getDisplayMetrics().density);
    }
}
