function doPost(e) {
  // WebHookで受信した応答用Token
  var replyToken = JSON.parse(e.postData.contents).events[0].replyToken;
  // ユーザーのメッセージを取得
  var userMessage = JSON.parse(e.postData.contents).events[0].message.text;
            pubData = '{"TOKEN":"'+replyToken+'","MESG":"' + userMessage+'"}';
            mqttPub(pubData);

  return ContentService.createTextOutput(JSON.stringify({'content': 'post ok'})).setMimeType(ContentService.MimeType.JSON);
}

function mqttPub(ledMessage) {
  var headers = {
    "Content-Type": "application/json",
    "X-Auth-Token": "token_"
  };

  var json = '{"data":['+ ledMessage +']}';

  var options = {
    "headers": headers,
    "method": "post",
    "payload": json
  };
  UrlFetchApp.fetch("https://api.beebotte.com/v1/data/publish/IoT/line_bot", options);
}
