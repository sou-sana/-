package jp.kids.breaktimer;

import android.app.admin.DeviceAdminReceiver;
import android.content.Context;
import android.content.Intent;

/** 端末管理アプリとして登録し、子どもが簡単にアンインストールできないようにする。 */
public class AdminReceiver extends DeviceAdminReceiver {
    @Override public CharSequence onDisableRequested(Context context, Intent intent) {
        return "解除すると、やすみタイマーが削除できるようになります。保護者に確認してください。";
    }
}
