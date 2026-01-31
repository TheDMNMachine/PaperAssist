#ifndef SSD1681_H
#define SSD1681_H

#include <stdint.h>

/* Display dimensions */
#define EPD_WIDTH       200
#define EPD_HEIGHT      200
#define EPD_BUF_SIZE    (EPD_WIDTH / 8 * EPD_HEIGHT)  /* 5000 bytes */

/* Pin assignments (matching original Arduino project) */
#define PIN_CS          5
#define PIN_DC          17
#define PIN_RST         16
#define PIN_BUSY        27
#define PIN_SCLK        18
#define PIN_MOSI        23

/* SSD1681 command definitions */
#define SSD1681_SW_RESET        0x12
#define SSD1681_DRIVER_OUTPUT   0x01
#define SSD1681_BORDER_WAVEFORM 0x3C
#define SSD1681_TEMP_SENSOR     0x18
#define SSD1681_WRITE_TEMP      0x1A
#define SSD1681_DATA_ENTRY_MODE 0x11
#define SSD1681_SET_RAM_X       0x44
#define SSD1681_SET_RAM_Y       0x45
#define SSD1681_SET_RAM_X_CTR   0x4E
#define SSD1681_SET_RAM_Y_CTR   0x4F
#define SSD1681_WRITE_BW_RAM    0x24
#define SSD1681_WRITE_RED_RAM   0x26
#define SSD1681_UPDATE_CTRL2    0x22
#define SSD1681_MASTER_ACTIVATE 0x20
#define SSD1681_DEEP_SLEEP      0x10

/* Public API */
void ssd1681_init(void);
void ssd1681_display(const uint8_t *framebuffer);
void ssd1681_clear(uint8_t fill_value);
void ssd1681_refresh_full(void);
void ssd1681_power_off(void);
void ssd1681_hibernate(void);

#endif
