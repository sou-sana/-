package jp.kids.breaktimer;

import android.app.KeyguardManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.widget.Toast;

/** 常駐して使用時間を数え、休憩中はロック画面（オーバーレイ）を出すサービス。 */
public class TimerService extends Service {
    public static final String ACTION_RESET = "jp.kids.breaktimer.RESET";
    public static final String ACTION_RELOAD = "jp.kids.breaktimer.RELOAD";
    private static final String CHANNEL = "timer";
    private static final int NOTIF_ID = 1;
    private static final long TICK_MS = 10_000L;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private Store store;
    private UsageClock clock;
    private BreakOverlay overlay;
    private long lastWarnedMinute = -1;

    private final Runnable tickTask = new Runnable() {
        @Override public void run() {
            tick();
            handler.postDelayed(this, TICK_MS);
        }
    };

    private final BroadcastReceiver screenReceiver = new BroadcastReceiver() {
        @Override public void onReceive(Context c, Intent i) {
            // 画面ON/ロック解除の瞬間に判定して、休憩中なら即座にロック画面を出す
            tick();
        }
    };

    public static void start(Context ctx) {
        ctx.startForegroundService(new Intent(ctx, TimerService.class));
    }

    @Override public void onCreate() {
        super.onCreate();
        store = new Store(this);
        clock = store.loadClock();
        overlay = new BreakOverlay(this, store, () -> {
            clock.reset(System.currentTimeMillis());
            store.saveClock(clock);
            tick();
        });
        createChannel();
        startInForeground(buildNotification("見守り中"));

        IntentFilter f = new IntentFilter();
        f.addAction(Intent.ACTION_SCREEN_ON);
        f.addAction(Intent.ACTION_SCREEN_OFF);
        f.addAction(Intent.ACTION_USER_PRESENT);
        registerReceiver(screenReceiver, f);
        handler.post(tickTask);
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_RESET.equals(intent.getAction())) {
            clock.reset(System.currentTimeMillis());
            store.saveClock(clock);
        } else if (intent != null && ACTION_RELOAD.equals(intent.getAction())) {
            clock.limitMs = store.useMinutes() * 60_000L;
            clock.breakMs = store.breakMinutes() * 60_000L;
        }
        if (!store.enabled()) {
            stopSelf();
            return START_NOT_STICKY;
        }
        tick();
        return START_STICKY;
    }

    @Override public void onDestroy() {
        handler.removeCallbacks(tickTask);
        try { unregisterReceiver(screenReceiver); } catch (Exception ignored) { }
        overlay.hide();
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) { return null; }

    private boolean isInUse() {
        PowerManager pm = getSystemService(PowerManager.class);
        KeyguardManager km = getSystemService(KeyguardManager.class);
        return pm.isInteractive() && !km.isKeyguardLocked();
    }

    private void tick() {
        long now = System.currentTimeMillis();
        boolean inUse = isInUse();
        clock.tick(now, inUse);
        store.saveClock(clock);

        NotificationManager nm = getSystemService(NotificationManager.class);
        if (clock.isOnBreak(now)) {
            long rem = clock.breakRemainingMs(now);
            // ロック画面（緊急通報）は覆わない。ロック解除された瞬間に覆う
            if (inUse) overlay.show(rem);
            else overlay.hide();
            nm.notify(NOTIF_ID, buildNotification("休憩中：あと" + fmt(rem)));
            lastWarnedMinute = -1;
        } else {
            overlay.hide();
            long rem = clock.useRemainingMs();
            nm.notify(NOTIF_ID, buildNotification("使える時間：あと" + fmt(rem)));
            long remMin = (rem + 59_999) / 60_000;
            if (inUse && (remMin == 5 || remMin == 1) && remMin != lastWarnedMinute) {
                lastWarnedMinute = remMin;
                Toast.makeText(this, "あと" + remMin + "分で休憩です", Toast.LENGTH_LONG).show();
            }
        }
    }

    static String fmt(long ms) {
        long s = (ms + 999) / 1000;
        return String.format("%d:%02d", s / 60, s % 60);
    }

    private void createChannel() {
        NotificationChannel ch = new NotificationChannel(CHANNEL, "タイマー", NotificationManager.IMPORTANCE_LOW);
        ch.setShowBadge(false);
        getSystemService(NotificationManager.class).createNotificationChannel(ch);
    }

    private Notification buildNotification(String text) {
        PendingIntent pi = PendingIntent.getActivity(this, 0,
                new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
        return new Notification.Builder(this, CHANNEL)
                .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
                .setContentTitle("やすみタイマー")
                .setContentText(text)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setContentIntent(pi)
                .build();
    }

    private void startInForeground(Notification n) {
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIF_ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        } else {
            startForeground(NOTIF_ID, n);
        }
    }
}
