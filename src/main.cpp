#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "wifi_config.h"
#include "esp_sleep.h"

// WIFI
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// SERVER LAPTOP
const char* serverUrl = "http://192.168.1.3:5000/upload"; // GANTI IP

// PIR
#define PIR_PIN 13

// CAMERA PIN (AI THINKER)
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

bool isCapturing = false;
bool lastMotionState = LOW;
unsigned long lastTriggerTime = 0;
const unsigned long COOLDOWN_TIME = 10000; // 10 detik

// moving average config
const int SAMPLE_COUNT = 5;
const int THRESHOLD = 3; // minimal HIGH dianggap valid

void sendImage(camera_fb_t * fb){

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");

    int response = http.POST(fb->buf, fb->len);

    Serial.print("HTTP Response: ");
    Serial.println(response);

    http.end();
}

void setupCamera(){

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

    //SETTING
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 15;
    config.fb_count = 1; // lebih aman untuk RAM

    esp_err_t err = esp_camera_init(&config);

    if (err != ESP_OK) {
        Serial.println("Camera init failed");
        return;
    }
}

void connectWiFi(){

    WiFi.begin(ssid, password);
    Serial.print("Connecting WiFi");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi connected");
    Serial.println(WiFi.localIP());
}

void setup(){

    Serial.begin(115200);

    pinMode(PIR_PIN, INPUT_PULLDOWN);
    //PIR WARM-UP
    Serial.println("PIR warming up (30 detik)...");
    delay(30000);
    Serial.println("PIR READY!");

    setupCamera();
    connectWiFi();
}

void enterLightSleep(){

    Serial.println("Masuk light sleep...");

    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIR_PIN, 1);

    delay(100); // biar serial kebaca

    esp_light_sleep_start();

    Serial.println("Bangun dari sleep!");
}

void loop(){

    //MOVING AVERAGE FILTER
    int highCount = 0;

    for(int i = 0; i < SAMPLE_COUNT; i++){
        if(digitalRead(PIR_PIN) == HIGH){
            highCount++;
        }
        delay(10);
    }

    bool motionFiltered = (highCount >= THRESHOLD);

    // debug pir state (RAW + FILTERED)
    Serial.print("PIR RAW: ");
    Serial.print(digitalRead(PIR_PIN));
    Serial.print(" | FILTERED: ");
    Serial.println(motionFiltered);

    unsigned long now = millis();

    //EDGE DETECTION + COOLDOWN (pakai FILTERED)
    if(motionFiltered == HIGH && lastMotionState == LOW && !isCapturing){

        if(now - lastTriggerTime < COOLDOWN_TIME){
            Serial.println("Cooldown aktif, skip trigger");
        } else {

            Serial.println("Motion VALID detected!");

            isCapturing = true;
            lastTriggerTime = now;

            // ambil 15 frame
            for(int i = 0; i < 15; i++){

                camera_fb_t * fb = esp_camera_fb_get();

                // VALIDASI FRAME
                if(!fb){
                    Serial.println("Frame NULL");
                    continue;
                }

                if(fb->len < 2000){
                    Serial.print("Frame terlalu kecil: ");
                    Serial.println(fb->len);
                    esp_camera_fb_return(fb);
                    continue;
                }

                Serial.print("Size: ");
                Serial.println(fb->len);

                sendImage(fb);

                esp_camera_fb_return(fb);

                delay(400);
            }

            Serial.println("Capture selesai");

            isCapturing = false;
        }
    }

    //update state pakai FILTERED
    lastMotionState = motionFiltered;
    
    //masuk ke mode sleep
    if(!isCapturing && motionFiltered == LOW){

        enterLightSleep();
    }

    delay(100);
}
