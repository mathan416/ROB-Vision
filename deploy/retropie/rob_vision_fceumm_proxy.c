/* Pass an NES libretro core through while observing each video frame.
 * This file contains no Nintendo or emulator code. Build one proxy per core:
 * gcc -std=gnu11 -O2 -fPIC -shared -Wall -Wextra -o rob_vision_fceumm_libretro.so \
 *     rob_vision_fceumm_proxy.c -ldl
 * gcc -std=gnu11 -O2 -fPIC -shared -Wall -Wextra -DROB_USE_NESTOPIA \
 *     -o rob_vision_nestopia_libretro.so rob_vision_fceumm_proxy.c -ldl
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

struct retro_game_info;
struct retro_system_info;
struct retro_system_av_info;
typedef bool (*environment_cb)(unsigned, void *);
typedef void (*video_cb)(const void *, unsigned, unsigned, size_t);
typedef void (*audio_cb)(int16_t, int16_t);
typedef size_t (*audio_batch_cb)(const int16_t *, size_t);
typedef void (*input_poll_cb)(void);
typedef int16_t (*input_state_cb)(unsigned, unsigned, unsigned, unsigned);

static void *real_core;
static environment_cb frontend_environment;
static video_cb frontend_video;
static unsigned pixel_format;
static uint32_t frame_index;
static int frame_socket = -1;
#ifndef ROB_REAL_CORE_PATH
#ifdef ROB_USE_NESTOPIA
#define ROB_REAL_CORE_PATH "/opt/retropie/libretrocores/lr-nestopia/nestopia_libretro.so"
#else
#define ROB_REAL_CORE_PATH "/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so"
#endif
#endif
static const char *const real_path = ROB_REAL_CORE_PATH;
#ifndef ROB_FRAME_SOCKET_PATH
#ifdef ROB_TEST_SOCKET
#define ROB_FRAME_SOCKET_PATH "/tmp/rob-vision-nestopia-probe.sock"
#else
#define ROB_FRAME_SOCKET_PATH "/run/rob-vision/frames.sock"
#endif
#endif
static const char *const socket_path = ROB_FRAME_SOCKET_PATH;

static void load_core(void) {
    if (!real_core) {
        real_core = dlopen(real_path, RTLD_NOW | RTLD_LOCAL);
        if (!real_core) fprintf(stderr, "R.O.B. Vision: cannot load %s: %s\n", real_path, dlerror());
    }
}

#define REAL(name) \
    static __typeof__(&name) fn; \
    if (!fn) { load_core(); if (real_core) fn = (__typeof__(&name))dlsym(real_core, #name); }

static bool environment_tap(unsigned command, void *data) {
    bool result = frontend_environment && frontend_environment(command, data);
    if (result && command == 10 && data) pixel_format = *(const unsigned *)data;
    return result;
}

static char pixel_class(const uint8_t *p) {
    unsigned red, green, blue;
    if (pixel_format == 1) {
        uint32_t value;
        memcpy(&value, p, sizeof(value));
        red = (value >> 16) & 255;
        green = (value >> 8) & 255;
        blue = value & 255;
    } else {
        uint16_t value;
        memcpy(&value, p, sizeof(value));
        if (pixel_format == 2) {
            red = ((value >> 11) & 31) * 255 / 31;
            green = ((value >> 5) & 63) * 255 / 63;
            blue = (value & 31) * 255 / 31;
        } else {
            red = ((value >> 10) & 31) * 255 / 31;
            green = ((value >> 5) & 31) * 255 / 31;
            blue = (value & 31) * 255 / 31;
        }
    }
    if (red < 28 && green < 28 && blue < 28) return '0';
    if (green > 75 && green > red * 3 / 2 + 20 && green > blue * 3 / 2 + 20) return '1';
    return 'N';
}

/* A game command fills the entire NES output, while ordinary game art does not. */
static char frame_class(const void *data, unsigned width, unsigned height, size_t pitch) {
    if (!data || width < 32 || height < 32 || pixel_format > 2) return 'N';
    unsigned black = 0, green = 0, center_green = 0;
    unsigned bytes_per_pixel = pixel_format == 1 ? 4 : 2;
    for (unsigned row = 1; row <= 5; row++) {
        for (unsigned col = 1; col <= 5; col++) {
            unsigned x = col * width / 6, y = row * height / 6;
            const uint8_t *pixel = (const uint8_t *)data + y * pitch + x * bytes_per_pixel;
            char kind = pixel_class(pixel);
            black += kind == '0';
            green += kind == '1';
        }
    }
    /* NES Test screens retain a dark border. Sample the central picture area
     * separately, requiring nearly every point to be green for a light bit. */
    for (unsigned row = 3; row <= 5; row++) {
        for (unsigned col = 3; col <= 5; col++) {
            unsigned x = col * width / 8, y = row * height / 8;
            const uint8_t *pixel = (const uint8_t *)data + y * pitch + x * bytes_per_pixel;
            center_green += pixel_class(pixel) == '1';
        }
    }
    if (black >= 23) return '0';
    if (green >= 23 || center_green >= 8) return '1';
    return 'N';
}

static void send_frame(char level) {
    if (frame_socket < 0) frame_socket = socket(AF_UNIX, SOCK_DGRAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (frame_socket < 0) return;
    struct sockaddr_un address = {0};
    address.sun_family = AF_UNIX;
    snprintf(address.sun_path, sizeof(address.sun_path), "%s", socket_path);
    uint8_t packet[5];
    memcpy(packet, &frame_index, sizeof(frame_index));
    packet[4] = (uint8_t)level;
    sendto(frame_socket, packet, sizeof(packet), MSG_DONTWAIT,
           (const struct sockaddr *)&address, sizeof(address));
}

static void video_tap(const void *data, unsigned width, unsigned height, size_t pitch) {
    frame_index++;
    send_frame(frame_class(data, width, height, pitch));
    if (frontend_video) frontend_video(data, width, height, pitch);
}

unsigned retro_api_version(void) { REAL(retro_api_version); return fn ? fn() : 0; }
void retro_set_environment(environment_cb cb) {
    frontend_environment = cb;
    REAL(retro_set_environment); if (fn) fn(environment_tap);
}
void retro_set_video_refresh(video_cb cb) {
    frontend_video = cb;
    REAL(retro_set_video_refresh); if (fn) fn(video_tap);
}
void retro_set_audio_sample(audio_cb cb) { REAL(retro_set_audio_sample); if (fn) fn(cb); }
void retro_set_audio_sample_batch(audio_batch_cb cb) { REAL(retro_set_audio_sample_batch); if (fn) fn(cb); }
void retro_set_input_poll(input_poll_cb cb) { REAL(retro_set_input_poll); if (fn) fn(cb); }
void retro_set_input_state(input_state_cb cb) { REAL(retro_set_input_state); if (fn) fn(cb); }
void retro_init(void) { REAL(retro_init); if (fn) fn(); }
void retro_deinit(void) {
    REAL(retro_deinit); if (fn) fn();
    if (frame_socket >= 0) { close(frame_socket); frame_socket = -1; }
}
void retro_get_system_info(struct retro_system_info *info) { REAL(retro_get_system_info); if (fn) fn(info); }
void retro_get_system_av_info(struct retro_system_av_info *info) { REAL(retro_get_system_av_info); if (fn) fn(info); }
void retro_set_controller_port_device(unsigned port, unsigned device) {
#ifdef ROB_USE_NESTOPIA
    /* Nestopia defines 1 as Auto. Gyromite's ROM selects the optical R.O.B.
     * peripheral for port 2 in that mode, so a virtual joypad cannot press
     * the gates. Its explicit Gamepad device is subclass 0 of Joypad (257). */
    if (port == 1 && device == 1) device = 257;
#endif
    REAL(retro_set_controller_port_device); if (fn) fn(port, device);
}
void retro_reset(void) { REAL(retro_reset); if (fn) fn(); }
void retro_run(void) { REAL(retro_run); if (fn) fn(); }
size_t retro_serialize_size(void) { REAL(retro_serialize_size); return fn ? fn() : 0; }
bool retro_serialize(void *data, size_t size) { REAL(retro_serialize); return fn && fn(data, size); }
bool retro_unserialize(const void *data, size_t size) { REAL(retro_unserialize); return fn && fn(data, size); }
void retro_cheat_reset(void) { REAL(retro_cheat_reset); if (fn) fn(); }
void retro_cheat_set(unsigned index, bool enabled, const char *code) {
    REAL(retro_cheat_set); if (fn) fn(index, enabled, code);
}
bool retro_load_game(const struct retro_game_info *game) {
    frame_index = 0; pixel_format = 0;
    REAL(retro_load_game);
    bool loaded = fn && fn(game);
#ifdef ROB_USE_NESTOPIA
    /* Nestopia auto-selects the ROM's peripheral while loading. Restore the
     * explicit second gamepad after that selection, including when RetroArch
     * sent its device choice before retro_load_game. */
    if (loaded) retro_set_controller_port_device(1, 257);
#endif
    return loaded;
}
bool retro_load_game_special(unsigned type, const struct retro_game_info *games, size_t count) {
    frame_index = 0; pixel_format = 0;
    REAL(retro_load_game_special); return fn && fn(type, games, count);
}
void retro_unload_game(void) { REAL(retro_unload_game); if (fn) fn(); }
unsigned retro_get_region(void) { REAL(retro_get_region); return fn ? fn() : 0; }
void *retro_get_memory_data(unsigned id) { REAL(retro_get_memory_data); return fn ? fn(id) : NULL; }
size_t retro_get_memory_size(unsigned id) { REAL(retro_get_memory_size); return fn ? fn(id) : 0; }
