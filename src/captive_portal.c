#include "captive_portal.h"
#include "wifi_manager.h"

#include <string.h>
#include <stdlib.h>
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "lwip/sockets.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "PORTAL";
static httpd_handle_t s_server = NULL;
static TaskHandle_t s_dns_task = NULL;
static volatile bool s_dns_running = false;

/* ---- HTML page ---- */

static const char PORTAL_HTML[] =
"<!DOCTYPE html><html><head>"
"<meta charset='UTF-8'>"
"<meta name='viewport' content='width=device-width,initial-scale=1'>"
"<title>EPaper Config</title>"
"<style>"
"*{box-sizing:border-box;margin:0;padding:0}"
"body{font-family:system-ui,sans-serif;background:#1a1a2e;color:#eee;"
"display:flex;justify-content:center;align-items:center;min-height:100vh}"
".card{background:#16213e;border-radius:12px;padding:2rem;width:90%%;max-width:360px;"
"box-shadow:0 8px 32px rgba(0,0,0,.4)}"
"h1{text-align:center;margin-bottom:1.5rem;font-size:1.3rem;color:#e94560}"
"label{display:block;margin-bottom:.3rem;font-size:.85rem;color:#aaa}"
"input{width:100%%;padding:.7rem;border:1px solid #333;border-radius:8px;"
"background:#0f3460;color:#fff;font-size:1rem;margin-bottom:1rem;outline:none}"
"input:focus{border-color:#e94560}"
"button{width:100%%;padding:.8rem;border:none;border-radius:8px;"
"background:#e94560;color:#fff;font-size:1rem;cursor:pointer;font-weight:600}"
"button:active{background:#c33}"
".msg{text-align:center;margin-top:1rem;font-size:.9rem}"
".ok{color:#4f8}"
".err{color:#f66}"
"</style></head><body>"
"<div class='card'>"
"<h1>WiFi Setup</h1>"
"<form id='f'>"
"<label>SSID</label>"
"<input name='ssid' id='ssid' required maxlength='32' placeholder='Nazwa sieci'>"
"<label>Password</label>"
"<input name='pass' id='pass' type='password' maxlength='64' placeholder='Haslo (puste=open)'>"
"<button type='submit'>Connect</button>"
"</form>"
"<div class='msg' id='msg'></div>"
"</div>"
"<script>"
"document.getElementById('f').onsubmit=async function(e){"
"e.preventDefault();"
"var m=document.getElementById('msg');"
"m.className='msg';m.textContent='Connecting...';"
"try{"
"var r=await fetch('/connect',{method:'POST',"
"headers:{'Content-Type':'application/x-www-form-urlencoded'},"
"body:'ssid='+encodeURIComponent(document.getElementById('ssid').value)"
"+'&pass='+encodeURIComponent(document.getElementById('pass').value)});"
"var j=await r.json();"
"if(j.ok){m.className='msg ok';m.textContent='Connected! IP: '+j.ip;}"
"else{m.className='msg err';m.textContent='Failed: '+j.error;}"
"}catch(x){m.className='msg err';m.textContent='Connection lost - check if device connected to WiFi';}"
"};"
"</script>"
"</body></html>";

/* ---- URL decode helper ---- */

static void url_decode(char *dst, const char *src, size_t dst_size)
{
    size_t di = 0;
    while (*src && di < dst_size - 1) {
        if (*src == '%' && src[1] && src[2]) {
            char hex[3] = {src[1], src[2], 0};
            dst[di++] = (char)strtol(hex, NULL, 16);
            src += 3;
        } else if (*src == '+') {
            dst[di++] = ' ';
            src++;
        } else {
            dst[di++] = *src++;
        }
    }
    dst[di] = '\0';
}

static bool parse_form_value(const char *body, const char *key, char *out, size_t out_size)
{
    char search[40];
    snprintf(search, sizeof(search), "%s=", key);

    const char *p = strstr(body, search);
    if (!p) return false;
    p += strlen(search);

    const char *end = strchr(p, '&');
    size_t len = end ? (size_t)(end - p) : strlen(p);
    if (len >= out_size) len = out_size - 1;

    char encoded[128] = {0};
    memcpy(encoded, p, len);
    encoded[len] = '\0';

    url_decode(out, encoded, out_size);
    return true;
}

/* ---- HTTP handlers ---- */

static esp_err_t handler_root(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html");
    httpd_resp_send(req, PORTAL_HTML, HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

static esp_err_t handler_connect(httpd_req_t *req)
{
    char body[256] = {0};
    int len = httpd_req_recv(req, body, sizeof(body) - 1);
    if (len <= 0) {
        httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "No body");
        return ESP_FAIL;
    }
    body[len] = '\0';

    char ssid[33] = {0};
    char pass[65] = {0};

    if (!parse_form_value(body, "ssid", ssid, sizeof(ssid)) || strlen(ssid) == 0) {
        httpd_resp_set_type(req, "application/json");
        httpd_resp_sendstr(req, "{\"ok\":false,\"error\":\"SSID is required\"}");
        return ESP_OK;
    }
    parse_form_value(body, "pass", pass, sizeof(pass));

    ESP_LOGI(TAG, "Attempting connection to \"%s\"", ssid);

    /* Stop DNS so we don't interfere with STA connection */
    s_dns_running = false;
    vTaskDelay(pdMS_TO_TICKS(100));

    if (wifi_manager_connect(ssid, pass)) {
        /* Get assigned IP */
        esp_netif_ip_info_t ip_info;
        esp_netif_t *netif = esp_netif_get_handle_from_ifkey("WIFI_STA_DEF");
        char ip_str[16] = "unknown";
        if (netif && esp_netif_get_ip_info(netif, &ip_info) == ESP_OK) {
            snprintf(ip_str, sizeof(ip_str), IPSTR, IP2STR(&ip_info.ip));
        }

        char resp[128];
        snprintf(resp, sizeof(resp), "{\"ok\":true,\"ip\":\"%s\"}", ip_str);
        httpd_resp_set_type(req, "application/json");
        httpd_resp_sendstr(req, resp);
        return ESP_OK;
    }

    /* Failed - restart DNS */
    s_dns_running = true;

    httpd_resp_set_type(req, "application/json");
    httpd_resp_sendstr(req, "{\"ok\":false,\"error\":\"Could not connect. Check credentials.\"}");
    return ESP_OK;
}

/* Catch-all: redirect everything to root (captive portal detection) */
static esp_err_t handler_redirect(httpd_req_t *req)
{
    httpd_resp_set_status(req, "302 Found");
    httpd_resp_set_hdr(req, "Location", "http://192.168.4.1/");
    httpd_resp_send(req, NULL, 0);
    return ESP_OK;
}

/* ---- DNS server (redirects all queries to 192.168.4.1) ---- */

static void dns_server_task(void *arg)
{
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        ESP_LOGE(TAG, "DNS socket failed");
        vTaskDelete(NULL);
        return;
    }

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(53),
        .sin_addr.s_addr = htonl(INADDR_ANY),
    };
    bind(sock, (struct sockaddr *)&addr, sizeof(addr));

    /* Set receive timeout so we can check s_dns_running */
    struct timeval tv = {.tv_sec = 1, .tv_usec = 0};
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    ESP_LOGI(TAG, "DNS server started on :53");

    uint8_t buf[512];
    while (s_dns_running) {
        struct sockaddr_in client;
        socklen_t client_len = sizeof(client);

        int len = recvfrom(sock, buf, sizeof(buf), 0,
                           (struct sockaddr *)&client, &client_len);
        if (len < 12) continue; /* too short or timeout */

        /* Build minimal DNS response: same header + answer pointing to 192.168.4.1 */
        uint8_t resp[512];
        memcpy(resp, buf, len);

        /* Set QR=1 (response), AA=1, no error */
        resp[2] = 0x84;
        resp[3] = 0x00;
        /* Answer count = 1 */
        resp[6] = 0x00;
        resp[7] = 0x01;

        int rlen = len;
        /* Pointer to question name */
        resp[rlen++] = 0xC0;
        resp[rlen++] = 0x0C;
        /* Type A */
        resp[rlen++] = 0x00; resp[rlen++] = 0x01;
        /* Class IN */
        resp[rlen++] = 0x00; resp[rlen++] = 0x01;
        /* TTL = 60 */
        resp[rlen++] = 0x00; resp[rlen++] = 0x00;
        resp[rlen++] = 0x00; resp[rlen++] = 0x3C;
        /* Data length = 4 */
        resp[rlen++] = 0x00; resp[rlen++] = 0x04;
        /* 192.168.4.1 */
        resp[rlen++] = 192; resp[rlen++] = 168;
        resp[rlen++] = 4;   resp[rlen++] = 1;

        sendto(sock, resp, rlen, 0,
               (struct sockaddr *)&client, client_len);
    }

    close(sock);
    ESP_LOGI(TAG, "DNS server stopped");
    vTaskDelete(NULL);
}

/* ---- Public API ---- */

void captive_portal_start(void)
{
    /* HTTP server */
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.max_uri_handlers = 8;
    config.uri_match_fn = httpd_uri_match_wildcard;
    config.lru_purge_enable = true;

    if (httpd_start(&s_server, &config) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to start HTTP server");
        return;
    }

    httpd_uri_t uri_root = {
        .uri = "/",
        .method = HTTP_GET,
        .handler = handler_root,
    };
    httpd_uri_t uri_connect = {
        .uri = "/connect",
        .method = HTTP_POST,
        .handler = handler_connect,
    };
    httpd_uri_t uri_catchall = {
        .uri = "/*",
        .method = HTTP_GET,
        .handler = handler_redirect,
    };

    httpd_register_uri_handler(s_server, &uri_root);
    httpd_register_uri_handler(s_server, &uri_connect);
    httpd_register_uri_handler(s_server, &uri_catchall);

    ESP_LOGI(TAG, "HTTP server started on :80");

    /* DNS server */
    s_dns_running = true;
    xTaskCreate(dns_server_task, "dns_srv", 4096, NULL, 5, &s_dns_task);
}

void captive_portal_stop(void)
{
    s_dns_running = false;
    if (s_server) {
        httpd_stop(s_server);
        s_server = NULL;
    }
    ESP_LOGI(TAG, "Portal stopped");
}
