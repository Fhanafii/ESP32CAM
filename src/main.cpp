#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include "wifi_config.h"
#include "esp_sleep.h"

const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
#define PIR_PIN 13

volatile bool allowStreaming = false;
bool streaming = false;
unsigned long streamStart = 0;
const unsigned long STREAM_DURATION = 20000; // 20 detik

static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=frame";
static const char* _STREAM_BOUNDARY = "\r\n--frame\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

httpd_handle_t stream_httpd = NULL;

static esp_err_t stream_handler(httpd_req_t *req){

    camera_fb_t * fb = NULL;
    esp_err_t res = ESP_OK;
    size_t _jpg_buf_len;
    uint8_t * _jpg_buf;
    char part_buf[64];

    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);

    while(allowStreaming){

        fb = esp_camera_fb_get();
        if(!fb){
            return ESP_FAIL;
        }

        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;

        size_t hlen = snprintf(part_buf, 64, _STREAM_PART, _jpg_buf_len);

        res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
        res = httpd_resp_send_chunk(req, part_buf, hlen);
        res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);

        esp_camera_fb_return(fb);

        if(res != ESP_OK){
            break;
        }
    }

    return res;
}

void startCameraServer(){

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 81;

    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    if(httpd_start(&stream_httpd, &config) == ESP_OK){
        httpd_register_uri_handler(stream_httpd, &stream_uri);
    }
}

void stopCameraServer(){
    if(stream_httpd){
        httpd_stop(stream_httpd);
        stream_httpd = NULL;
    }
}

void enterLightSleep(){

    Serial.println("Entering light sleep...");

    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIR_PIN, 1);

    esp_light_sleep_start();

    Serial.println("Woke up!");
}

void setup(){

    Serial.begin(115200);
    pinMode(PIR_PIN, INPUT);
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;

    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;

    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;

    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;

    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;

    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Bisa diubah resolusi sesuai ukuran
    config.frame_size = FRAMESIZE_SVGA;    
    config.jpeg_quality = 20;
    config.fb_count = 2;

    esp_camera_init(&config);

    WiFi.begin(ssid,password);

    while(WiFi.status()!=WL_CONNECTED){
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");

    Serial.print("Stream: http://");
    Serial.print(WiFi.localIP());
    Serial.println(":81/stream");

    // startCameraServer();
}

void loop(){

    if(!streaming){

        enterLightSleep();

        if(digitalRead(PIR_PIN) == HIGH){

            Serial.println("Motion detected!");

            startCameraServer();

            streaming = true;
            streamStart = millis();
        }
    }

    if(streaming){

        if(millis() - streamStart > STREAM_DURATION){

            Serial.println("Stopping stream");

            stopCameraServer();

            streaming = false;
        }
    }
    delay(50);
}