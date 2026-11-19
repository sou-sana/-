package jp.kids.breaktimer;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** 再起動やアプリ更新のあと、自動で見守りを再開する。 */
public class BootReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent) {
        String a = intent.getAction();
        if (!Intent.ACTION_BOOT_COMPLETED.equals(a) && !Intent.ACTION_MY_PACKAGE_REPLACED.equals(a)) return;
        if (new Store(context).enabled()) TimerService.start(context);
    }
}
