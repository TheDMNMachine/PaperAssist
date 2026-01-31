#include "epd_gfx.h"
#include "epd_font.h"
#include "ssd1681.h"
#include <string.h>

/*
 * Framebuffer layout: 200x200 pixels, 25 bytes per row, 5000 bytes total.
 * Byte [y * 25 + x/8], bit (0x80 >> (x%8)) = pixel (x, y).
 * MSB = leftmost pixel. 1 = white, 0 = black.
 */

void gfx_fill(uint8_t *buf, uint8_t color)
{
    memset(buf, color ? 0xFF : 0x00, EPD_BUF_SIZE);
}

void gfx_set_pixel(uint8_t *buf, int16_t x, int16_t y, uint8_t color)
{
    if (x < 0 || x >= EPD_WIDTH || y < 0 || y >= EPD_HEIGHT) return;

    uint16_t idx  = y * (EPD_WIDTH / 8) + (x / 8);
    uint8_t  mask = 0x80 >> (x % 8);

    if (color == EPD_WHITE)
        buf[idx] |= mask;
    else
        buf[idx] &= ~mask;
}

void gfx_draw_rect(uint8_t *buf, int16_t x, int16_t y, int16_t w, int16_t h, uint8_t color)
{
    for (int16_t i = x; i < x + w; i++) {
        gfx_set_pixel(buf, i, y, color);
        gfx_set_pixel(buf, i, y + h - 1, color);
    }
    for (int16_t j = y; j < y + h; j++) {
        gfx_set_pixel(buf, x, j, color);
        gfx_set_pixel(buf, x + w - 1, j, color);
    }
}

void gfx_fill_rect(uint8_t *buf, int16_t x, int16_t y, int16_t w, int16_t h, uint8_t color)
{
    for (int16_t j = y; j < y + h; j++)
        for (int16_t i = x; i < x + w; i++)
            gfx_set_pixel(buf, i, j, color);
}

void gfx_draw_char(uint8_t *buf, int16_t x, int16_t y, char c, uint8_t color, uint8_t scale)
{
    if (c < 32 || c > 126) c = '?';
    const uint8_t *glyph = font_5x7[c - 32];

    for (int col = 0; col < FONT_WIDTH; col++) {
        uint8_t col_data = glyph[col];
        for (int row = 0; row < FONT_HEIGHT; row++) {
            if (col_data & (1 << row)) {
                for (uint8_t sy = 0; sy < scale; sy++)
                    for (uint8_t sx = 0; sx < scale; sx++)
                        gfx_set_pixel(buf,
                            x + col * scale + sx,
                            y + row * scale + sy,
                            color);
            }
        }
    }
}

void gfx_draw_string(uint8_t *buf, int16_t x, int16_t y, const char *str, uint8_t color, uint8_t scale)
{
    int16_t cx = x;
    while (*str) {
        gfx_draw_char(buf, cx, y, *str, color, scale);
        cx += (FONT_WIDTH + 1) * scale;
        str++;
    }
}

int gfx_string_width(const char *str, uint8_t scale)
{
    int len = 0;
    while (str[len]) len++;
    if (len == 0) return 0;
    return len * (FONT_WIDTH + 1) * scale - scale;
}

int gfx_string_height(uint8_t scale)
{
    return FONT_HEIGHT * scale;
}
