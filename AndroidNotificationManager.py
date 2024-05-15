from jnius import autoclass
from android.runnable import run_on_ui_thread

PythonActivity = autoclass("org.kivy.android.PythonActivity")
mActivity = PythonActivity.mActivity

NotificationManager = autoclass("android.app.NotificationManager")
Context = autoclass("android.content.Context")
NotificationChannel = autoclass('android.app.NotificationChannel')
String = autoclass('java.lang.String')

THEFT_CHANNEL_ID = 'THEFT_CHANNEL'
FIRE_CHANNEL_ID = 'FIRE_CHANNEL'
RUNNING_SERVICES_CHANNEL_ID = 'RUNNING_SERVICES'
LPG_ALERT_CHANNEL_ID = 'LPG_CHANNEL'
BOARD_FAIL_CHANNEL = "BOARD_FAIL_CHANNEL"


@run_on_ui_thread
def show_notification(title: str, message: str, channel_id: str, notification_id: int = 0, sticky: bool = False):
    try:
        # Get the notification manager
        notification_manager = mActivity.getSystemService(Context.NOTIFICATION_SERVICE)

        # Create the notification
        builder = autoclass('android.app.Notification$Builder')(mActivity, channel_id)
        builder.setContentTitle(String(title))
        builder.setContentText(String(message))
        builder.setSmallIcon(mActivity.getApplicationInfo().icon)

        # builder.setLargeIcon(BitmapFactory.decodeResource(context.getResources(), R.drawable.my_large_icon))
        # builder.setAutoCancel(True)
        builder.setAutoCancel(False)
        if sticky:
            builder.setOnGoing(True)
        notification = builder.build()

        # Show the notification
        notification_manager.notify(notification_id, notification)
    except:
        import traceback
        import error_handler
        try:
            error_handler.write_log(traceback.format_exc())
        except PermissionError:
            pass


def create_channels():
    theft_channel = NotificationChannel(THEFT_CHANNEL_ID,
                                        String('Motion detection alert'),
                                        NotificationManager.IMPORTANCE_HIGH)
    theft_channel.setDescription(String('This channel alerts you when robot detects any motion'))

    fire_channel = NotificationChannel(FIRE_CHANNEL_ID,
                                       String('Fire detection alert'),
                                       NotificationManager.IMPORTANCE_HIGH)
    fire_channel.setDescription(String('This channel alerts you when robot detects smoke'))

    lpg_channel = NotificationChannel(LPG_ALERT_CHANNEL_ID,
                                      String('LPG gas detection alert'),
                                      NotificationManager.IMPORTANCE_HIGH)
    lpg_channel.setDescription(String('This channel alerts you when robot detects LPG gas'))

    service_channel = NotificationChannel(RUNNING_SERVICES_CHANNEL_ID,
                                          String('Running services'),
                                          NotificationManager.IMPORTANCE_HIGH)
    service_channel.setDescription(String('This is to ensure app is running in background as needed by android'))

    board_fail_channel = NotificationChannel(BOARD_FAIL_CHANNEL,
                                             String('Board fail info'),
                                             NotificationManager.IMPORTANCE_HIGH)
    board_fail_channel.setDescription(String('This channel notify you when board fails'))

    mActivity.getSystemService(Context.NOTIFICATION_SERVICE).createNotificationChannel(theft_channel)
    mActivity.getSystemService(Context.NOTIFICATION_SERVICE).createNotificationChannel(fire_channel)
    mActivity.getSystemService(Context.NOTIFICATION_SERVICE).createNotificationChannel(lpg_channel)
    mActivity.getSystemService(Context.NOTIFICATION_SERVICE).createNotificationChannel(service_channel)
    mActivity.getSystemService(Context.NOTIFICATION_SERVICE).createNotificationChannel(board_fail_channel)
