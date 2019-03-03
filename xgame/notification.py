


api_access_key = 'AAAA1IZC-14:APA91bH8Aj43MXPh-pHPB25NEOSWdWH_EQ4FSHh9Q5fUQYIsJHoS8l4Pm7SrWxmPL3z7nrHwD6DbVWjaJRojXJGyp8l9g8swPSYh239CS9ZYSIQfQQVsoKCEYwUIu-ftQUTHi7GFkm7m');
$registrationId = 'eenr49UuFR4:APA91bEFPQAt1G5NgY6H0nqAMPwsNk4qQmOW4c8dMnvutDaEqyFqfOzx4vonJT9sOTwfUiKGAuAxhKaY8TL-UVKs2nZueaEhiJaBomzk3mjbEmJo2JvBSuQRqT6L6tFuuIpjmI7Tsl0O';
$silent_notification = array
(
    'task'  => $notifiable->task,
    'op'	=> $notifiable->op,
    'type'  => $notifiable->type,
    'data' 	=> $notifiable->data,
);

$notification = array
(
    'title' => $notifiable->title,
    'body'	=> $notifiable->body,
    'icon'	=> 'myicon',/*Default Icon*/
    'sound' => 'mySound'/*Default sound*/
);

$fields = array
(
    'to' => $notifiable->to,
    ($notifiable->notif == false)? 'data' : 'notification' => ($notifiable->notif == false)? $silent_notification : $notification
);

$headers = array
(
    'Authorization: key=' . API_ACCESS_KEY,
    'Content-Type: application/json'
);
#Send Reponse To FireBase Server
$ch = curl_init();
curl_setopt( $ch,CURLOPT_URL, 'https://fcm.googleapis.com/fcm/send' );
curl_setopt( $ch,CURLOPT_POST, true );
curl_setopt( $ch,CURLOPT_HTTPHEADER, $headers );
curl_setopt( $ch,CURLOPT_RETURNTRANSFER, true );
curl_setopt( $ch,CURLOPT_SSL_VERIFYPEER, false );
curl_setopt( $ch,CURLOPT_POSTFIELDS, json_encode( $fields ) );
$result = curl_exec($ch );
curl_close( $ch );
echo $result;