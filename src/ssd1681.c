#include "ssd1681.h"

#include <string.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_heap_caps.h"

static const char *TAG = "SSD1681";
static spi_device_handle_t spi_dev;

/* ---- Low-level helpers ---- */

/* Pre-transfer callback: sets DC pin based on transaction user data.
   user = 0 -> command (DC LOW), user = 1 -> data (DC HIGH) */
static void IRAM_ATTR spi_pre_cb(spi_transaction_t *t)
{
    int dc = (int)t->user;
    gpio_set_level(PIN_DC, dc);
}

static void epd_send_cmd(uint8_t cmd)
{
    spi_transaction_t t = {0};
    t.length    = 8;
    t.tx_buffer = &cmd;
    t.user      = (void *)0;
    spi_device_transmit(spi_dev, &t);
}

static void epd_send_data(const uint8_t *data, int len)
{
    if (len <= 0) return;
    spi_transaction_t t = {0};
    t.length    = len * 8;
    t.tx_buffer = data;
    t.user      = (void *)1;
    spi_device_transmit(spi_dev, &t);
}

static void epd_send_byte(uint8_t val)
{
    epd_send_data(&val, 1);
}

static void epd_wait_busy(void)
{
    vTaskDelay(pdMS_TO_TICKS(1));
    int timeout = 0;
    while (gpio_get_level(PIN_BUSY) == 1) {
        vTaskDelay(pdMS_TO_TICKS(10));
        timeout += 10;
        if (timeout > 10000) {
            ESP_LOGW(TAG, "BUSY timeout!");
            break;
        }
    }
}

/* ---- Init routines ---- */

static void gpio_init_epd(void)
{
    /* RST and DC as outputs */
    gpio_config_t out = {
        .pin_bit_mask = (1ULL << PIN_RST) | (1ULL << PIN_DC),
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    gpio_config(&out);

    /* BUSY as input */
    gpio_config_t in = {
        .pin_bit_mask = (1ULL << PIN_BUSY),
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    gpio_config(&in);

    gpio_set_level(PIN_RST, 1);
    gpio_set_level(PIN_DC, 1);
}

static void spi_init_epd(void)
{
    spi_bus_config_t bus = {
        .mosi_io_num   = PIN_MOSI,
        .miso_io_num   = -1,
        .sclk_io_num   = PIN_SCLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = EPD_BUF_SIZE + 8,
    };
    ESP_ERROR_CHECK(spi_bus_initialize(SPI3_HOST, &bus, SPI_DMA_CH_AUTO));

    spi_device_interface_config_t dev = {
        .clock_speed_hz = 4 * 1000 * 1000,
        .mode           = 0,
        .spics_io_num   = PIN_CS,
        .queue_size     = 1,
        .pre_cb         = spi_pre_cb,
    };
    ESP_ERROR_CHECK(spi_bus_add_device(SPI3_HOST, &dev, &spi_dev));
}

/* ---- SSD1681 command sequences ---- */

static void epd_hw_reset(void)
{
    gpio_set_level(PIN_RST, 1);
    vTaskDelay(pdMS_TO_TICKS(10));
    gpio_set_level(PIN_RST, 0);
    vTaskDelay(pdMS_TO_TICKS(10));
    gpio_set_level(PIN_RST, 1);
    vTaskDelay(pdMS_TO_TICKS(10));
}

static void epd_set_ram_area(uint16_t x, uint16_t y, uint16_t w, uint16_t h)
{
    epd_send_cmd(SSD1681_DATA_ENTRY_MODE);
    epd_send_byte(0x03);

    epd_send_cmd(SSD1681_SET_RAM_X);
    epd_send_byte(x / 8);
    epd_send_byte((x + w - 1) / 8);

    epd_send_cmd(SSD1681_SET_RAM_Y);
    epd_send_byte(y & 0xFF);
    epd_send_byte(y >> 8);
    epd_send_byte((y + h - 1) & 0xFF);
    epd_send_byte((y + h - 1) >> 8);

    epd_send_cmd(SSD1681_SET_RAM_X_CTR);
    epd_send_byte(x / 8);

    epd_send_cmd(SSD1681_SET_RAM_Y_CTR);
    epd_send_byte(y & 0xFF);
    epd_send_byte(y >> 8);
}

static void epd_init_display(void)
{
    epd_hw_reset();
    vTaskDelay(pdMS_TO_TICKS(10));

    epd_send_cmd(SSD1681_SW_RESET);
    vTaskDelay(pdMS_TO_TICKS(10));

    /* Driver output control: 200 lines (0xC7 = 199) */
    epd_send_cmd(SSD1681_DRIVER_OUTPUT);
    uint8_t drv[] = {0xC7, 0x00, 0x00};
    epd_send_data(drv, 3);

    /* Border waveform */
    epd_send_cmd(SSD1681_BORDER_WAVEFORM);
    epd_send_byte(0x05);

    /* Internal temperature sensor */
    epd_send_cmd(SSD1681_TEMP_SENSOR);
    epd_send_byte(0x80);

    /* Full screen RAM area */
    epd_set_ram_area(0, 0, EPD_WIDTH, EPD_HEIGHT);
}

static void epd_write_ram(uint8_t cmd, const uint8_t *data, size_t len)
{
    epd_set_ram_area(0, 0, EPD_WIDTH, EPD_HEIGHT);
    epd_send_cmd(cmd);
    epd_send_data(data, len);
}

/* ---- Public API ---- */

void ssd1681_init(void)
{
    gpio_init_epd();
    spi_init_epd();
    epd_init_display();
    ESP_LOGI(TAG, "Initialized");
}

void ssd1681_refresh_full(void)
{
    /* Fast full update (useFastFullUpdate = true for this panel) */
    epd_send_cmd(SSD1681_WRITE_TEMP);
    epd_send_byte(0x64);

    epd_send_cmd(SSD1681_UPDATE_CTRL2);
    epd_send_byte(0xD7);

    epd_send_cmd(SSD1681_MASTER_ACTIVATE);
    epd_wait_busy();
}

void ssd1681_display(const uint8_t *framebuffer)
{
    /* Write to both RAM planes for clean full refresh */
    epd_write_ram(SSD1681_WRITE_RED_RAM, framebuffer, EPD_BUF_SIZE);
    epd_write_ram(SSD1681_WRITE_BW_RAM,  framebuffer, EPD_BUF_SIZE);
    ssd1681_refresh_full();
}

void ssd1681_clear(uint8_t fill_value)
{
    uint8_t *buf = heap_caps_malloc(EPD_BUF_SIZE, MALLOC_CAP_DMA);
    if (!buf) {
        ESP_LOGE(TAG, "Alloc failed");
        return;
    }
    memset(buf, fill_value, EPD_BUF_SIZE);
    ssd1681_display(buf);
    free(buf);
}

void ssd1681_power_off(void)
{
    epd_send_cmd(SSD1681_UPDATE_CTRL2);
    epd_send_byte(0x83);
    epd_send_cmd(SSD1681_MASTER_ACTIVATE);
    epd_wait_busy();
}

void ssd1681_hibernate(void)
{
    ssd1681_power_off();
    epd_send_cmd(SSD1681_DEEP_SLEEP);
    epd_send_byte(0x01);
}
