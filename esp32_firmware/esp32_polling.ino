#include <WiFi.h>
#include <HTTPClient.h>
#include "driver/i2s.h"
#include <ArduinoJson.h>

const char* ssid     = "Uang_10rb";
const char* password = "1223334444";
String aws_server    = "http://3.27.18.184"; 

#define SAMPLE_RATE 16000 
#define BUFFER_SIZE 1024
#define I2S_DOUT  2
#define I2S_BCLK  4
#define I2S_LRC   15
#define RELAY_PIN 5  

i2s_config_t i2s_config = {
  .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
  .sample_rate = SAMPLE_RATE,
  .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
  .channel_format = I2S_CHANNEL_FMT_ONLY_RIGHT, 
  .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
  .intr_alloc_flags = 0,
  .dma_buf_count = 8,
  .dma_buf_len = BUFFER_SIZE,
  .use_apll = false
};

i2s_pin_config_t pin_config = {
  .bck_io_num = I2S_BCLK,
  .ws_io_num = I2S_LRC,
  .data_out_num = I2S_DOUT,
  .data_in_num = I2S_PIN_NO_CHANGE
};

unsigned long lastCheck = 0;

void setup() {
  Serial.begin(115200);
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
}

void playAudio(String url, int id) {
  HTTPClient http;
  http.setTimeout(10000);
  http.begin(url);
  
  if (http.GET() == 200) {
    int len = http.getSize();
    WiFiClient* stream = http.getStreamPtr();
    uint8_t buff[BUFFER_SIZE];
    if(len > 44) { stream->readBytes(buff, 44); len -= 44; }

    while (http.connected() && (len > 0 || len == -1)) {
      int available = stream->available();
      if (available > 0) {
        int bytesRead = stream->readBytes(buff, (available > BUFFER_SIZE) ? BUFFER_SIZE : available);
        size_t written;
        i2s_write(I2S_NUM_0, buff, bytesRead, &written, portMAX_DELAY);
        if (len > 0) len -= bytesRead;
      }
    }
    
    uint8_t silence[BUFFER_SIZE] = {0}; 
    size_t bytesWritten;
    for(int i=0; i<6; i++) i2s_write(I2S_NUM_0, silence, BUFFER_SIZE, &bytesWritten, portMAX_DELAY);

    HTTPClient doneReq;
    doneReq.begin(aws_server + "/api.php?action=done&id=" + String(id));
    doneReq.GET();
    doneReq.end();
  }
  http.end();
}

void checkServer() {
  HTTPClient http;
  http.begin(aws_server + "/api.php?action=check_status");
  
  if (http.GET() == 200) {
    String payload = http.getString();
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);
    
    if (String(doc["status"]) == "ready") {
      playAudio(String(doc["url"]), doc["id"]);
    }
  }
  http.end();
}

void checkRelay() {
  HTTPClient http;
  http.begin(aws_server + "/api.php?action=relay_status");
  if (http.GET() == 200) {
    String payload = http.getString();
    if (payload.indexOf("on") > 0) digitalWrite(RELAY_PIN, HIGH);
    else digitalWrite(RELAY_PIN, LOW);
  }
  http.end();
}

void loop() {
  if (millis() - lastCheck > 2000) {
    lastCheck = millis();
    if (WiFi.status() == WL_CONNECTED) {
      checkServer();
      checkRelay();
    }
  }
}