#ifndef EPD_GFX_H
#define EPD_GFX_H

#include <stdint.h>
#include <stddef.h>

/* Colors: in framebuffer bit=1 is white, bit=0 is black (SSD1681 convention) */
#define EPD_WHITE  1
#define EPD_BLACK  0

void gfx_fill(uint8_t *buf, uint8_t color);
void gfx_set_pixel(uint8_t *buf, int16_t x, int16_t y, uint8_t color);
void gfx_draw_rect(uint8_t *buf, int16_t x, int16_t y, int16_t w, int16_t h, uint8_t color);
void gfx_fill_rect(uint8_t *buf, int16_t x, int16_t y, int16_t w, int16_t h, uint8_t color);
void gfx_draw_char(uint8_t *buf, int16_t x, int16_t y, char c, uint8_t color, uint8_t scale);
void gfx_draw_string(uint8_t *buf, int16_t x, int16_t y, const char *str, uint8_t color, uint8_t scale);
int  gfx_string_width(const char *str, uint8_t scale);
int  gfx_string_height(uint8_t scale);

#endif
