#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_heap_caps.h"

#include "ssd1681.h"
#include "epd_gfx.h"
#include "wifi_manager.h"
#include "captive_portal.h"

static const char *TAG = "MAIN";

/* BOOT button = GPIO0 on most ESP32 boards */
#define PIN_BOOT 0
#define BOOT_HOLD_MS 3000 /* hold 3s to reset WiFi */

static void show_epd_demo(void)
{
    ssd1681_init();

    uint8_t *fb = (uint8_t *)heap_caps_malloc(EPD_BUF_SIZE, MALLOC_CAP_DMA);
    if (!fb) {
        ESP_LOGE(TAG, "Framebuffer alloc failed!");
        return;
    }

    gfx_fill(fb, EPD_WHITE);
    gfx_draw_rect(fb, 5, 5, EPD_WIDTH - 10, EPD_HEIGHT - 10, EPD_BLACK);

    const char *text = "Hello E-Paper";
    uint8_t scale = 2;
    int tw = gfx_string_width(text, scale);
    int th = gfx_string_height(scale);
    int x  = (EPD_WIDTH  - tw) / 2;
    int y  = (EPD_HEIGHT - th) / 2;
    gfx_draw_string(fb, x, y, text, EPD_BLACK, scale);

    gfx_fill_rect(fb, 10, EPD_HEIGHT - 28, EPD_WIDTH - 20, 18, EPD_BLACK);
    gfx_draw_string(fb, 14, EPD_HEIGHT - 26, "SSD1681 OK", EPD_WHITE, 1);

    ESP_LOGI(TAG, "Sending to display...");
    ssd1681_display(fb);

    ESP_LOGI(TAG, "Hibernating display");
    ssd1681_hibernate();
    free(fb);
}

static void show_epd_status(const char *line1, const char *line2)
{
    ssd1681_init();

    uint8_t *fb = (uint8_t *)heap_caps_malloc(EPD_BUF_SIZE, MALLOC_CAP_DMA);
    if (!fb) return;

    gfx_fill(fb, EPD_WHITE);
    gfx_draw_rect(fb, 2, 2, EPD_WIDTH - 4, EPD_HEIGHT - 4, EPD_BLACK);

    int y1 = (EPD_HEIGHT / 2) - 20;
    int x1 = (EPD_WIDTH - gfx_string_width(line1, 2)) / 2;
    gfx_draw_string(fb, x1, y1, line1, EPD_BLACK, 2);

    if (line2) {
        int y2 = (EPD_HEIGHT / 2) + 10;
        int x2 = (EPD_WIDTH - gfx_string_width(line2, 1)) / 2;
        gfx_draw_string(fb, x2, y2, line2, EPD_BLACK, 1);
    }

    ssd1681_display(fb);
    ssd1681_hibernate();
    free(fb);
}

static void boot_button_init(void)
{
    gpio_config_t cfg = {
        .pin_bit_mask = (1ULL << PIN_BOOT),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&cfg);
}

/* Check if BOOT button is held for BOOT_HOLD_MS at startup */
static bool boot_button_held(void)
{
    if (gpio_get_level(PIN_BOOT) != 0) return false;

    ESP_LOGI(TAG, "BOOT button pressed, hold %d ms to reset WiFi...", BOOT_HOLD_MS);
    int elapsed = 0;
    while (gpio_get_level(PIN_BOOT) == 0 && elapsed < BOOT_HOLD_MS) {
        vTaskDelay(pdMS_TO_TICKS(100));
        elapsed += 100;
    }
    return (elapsed >= BOOT_HOLD_MS);
}

void app_main(void)
{
    ESP_LOGI(TAG, "E-Paper + WiFi Manager");

    boot_button_init();

    /* Check for WiFi reset (hold BOOT 3s) */
    if (boot_button_held()) {
        ESP_LOGW(TAG, "WiFi reset requested!");
        show_epd_status("WiFi Reset", "Restarting...");
        wifi_manager_init();  /* init NVS first */
        wifi_manager_reset(); /* erase + restart */
        return; /* won't reach here, esp_restart() called */
    }

    /* Init WiFi */
    bool connected = wifi_manager_init();

    if (connected) {
        ESP_LOGI(TAG, "WiFi connected, showing demo");
        show_epd_demo();
        /* TODO: here you will fetch data from API and display it */
    } else {
        ESP_LOGI(TAG, "AP mode - starting captive portal");
        show_epd_status("WiFi Setup", "Connect to EPaper-Config");
        captive_portal_start();
        /* Portal runs in background, main task can idle or do other work */
    }

    ESP_LOGI(TAG, "Done.");
}
