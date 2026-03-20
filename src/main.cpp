#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "wifi_config.h"

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

    // 🔥 SETTING KAMU
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 20;
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
    
    setupCamera();
    connectWiFi();
}

void loop(){

    int motion = digitalRead(PIR_PIN);

    if(motion == HIGH && !isCapturing){

        Serial.println("🚨 Motion detected!");

        isCapturing = true;

        // 🔥 ambil 15 frame
        for(int i = 0; i < 15; i++){

            camera_fb_t * fb = esp_camera_fb_get();

            if(fb){

                Serial.print("Frame ");
                Serial.println(i+1);

                sendImage(fb);

                esp_camera_fb_return(fb);
            }

            delay(300); // stabilisasi jaringan
        }

        Serial.println("✅ Capture selesai");

        isCapturing = false;

        delay(3000); // cooldown biar tidak trigger terus
    }

    delay(100);
}