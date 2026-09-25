// R.O.B. Vision: 13x8 UNO Q matrix face and controller status.
#include "Arduino_RouterBridge.h"
#include <Arduino_LED_Matrix.h>
#include <zephyr/kernel.h>

enum RobDisplay { LOADING = 0, IDLE = 1, GYROMITE = 2, STACK_UP = 3,
                  TEST = 4, TEST_FLASH = 5, PAIRING = 6, FAULT = 7, OFF = 8 };

Arduino_LED_Matrix matrix;
volatile int requestedMode = LOADING;
volatile int requestedHint = 0;
volatile unsigned long hintAt = 0;
volatile unsigned long heartbeatAt = 0;
int drawnMode = -1;
unsigned long modeAt = 0;
unsigned long nextFrameAt = 0;
unsigned int frameNumber = 0;
struct k_thread displayThread;
k_thread_stack_t* displayStack = nullptr;
k_tid_t displayThreadId = nullptr;

const char* const loading[][8] = {
  {"...7777777...","....73337....",".....737.....","......7......","......3......",".....7.7.....","....7...7....","...7777777..."},
  {"...7777777...","....7...7....",".....737.....","......3......","......7......",".....737.....","....7.3.7....","...7777777..."},
  {"...7777777...","....7...7....",".....7.7.....","......3......","......7......",".....737.....","....73337....","...7777777..."}
};
const uint8_t G[7]={14,16,16,23,17,17,14};
const uint8_t Y[7]={17,17,10,4,4,4,4};
const uint8_t S[7]={15,16,16,14,1,1,30};
const uint8_t U[7]={17,17,17,17,17,17,14};
const uint8_t T[7]={31,4,4,4,4,4,4};
const uint8_t P[7]={30,17,17,30,16,16,16};
const uint8_t X[7]={17,17,10,4,10,17,17};

void pixel(uint8_t* pixels, int x, int y, uint8_t value) {
  if (x >= 0 && x < 13 && y >= 0 && y < 8 && value > pixels[y*13+x])
    pixels[y*13+x] = value;
}

void glyph(uint8_t* pixels, const uint8_t rows[7], int left, uint8_t value) {
  for (int y=0;y<7;++y) for (int x=0;x<5;++x)
    if (rows[y] & (1 << (4-x))) pixel(pixels,left+x,y,value);
}

void hourglass(unsigned int frame) {
  uint8_t pixels[104]={0};
  for (int y=0;y<8;++y) for (int x=0;x<13;++x) {
    const char value=loading[frame%3][y][x];
    if (value >= '1' && value <= '7') pixel(pixels,x,y,value-'0');
  }
  matrix.draw(pixels);
}

void eyes(uint8_t* pixels, unsigned int frame, int mode, int hint) {
  const int glances[4]={0,1,0,-1};
  int look=glances[(frame/10)%4];
  if (hint==1) look=-1;
  if (hint==2) look=1;
  const bool blink=frame%23==21;
  for (int center=3;center<=9;center+=6) {
    for (int x=center-2;x<=center+2;++x) { pixel(pixels,x,1,5);pixel(pixels,x,5,4); }
    for (int y=2;y<=4;++y) { pixel(pixels,center-3,y,4);pixel(pixels,center+3,y,4); }
    if (blink || hint==5 || hint==6) {
      for (int x=center-1;x<=center+1;++x) pixel(pixels,x,3,7);
    } else {
      int offsetY = hint==3 ? -1 : hint==4 ? 1 : 0;
      pixel(pixels,center+look,3+offsetY,7);
      pixel(pixels,center+look,4+offsetY,6);
    }
  }
  if (mode==GYROMITE) {
    const int dot[4]={5,6,7,6};pixel(pixels,dot[frame%4],7,5);
  } else if (mode==STACK_UP) {
    for(int x=5;x<=7;++x) pixel(pixels,x,7-(frame/3)%3,5);
  }
}

void refreshMatrix() {
  const unsigned long now=millis();
  const int mode=(heartbeatAt != 0 && now-heartbeatAt > 3500) ? LOADING : requestedMode;
  if (mode != drawnMode) {
    drawnMode=mode;modeAt=now;frameNumber=0;nextFrameAt=0;
    if (mode==OFF) matrix.clear();
  }
  if (mode==OFF || now<nextFrameAt) return;
  uint8_t pixels[104]={0};
  if (mode==LOADING) {
    hourglass(frameNumber++);nextFrameAt=now+240;return;
  }
  if (mode==IDLE || mode==GYROMITE || mode==STACK_UP) {
    if (mode!=IDLE && now-modeAt<1300) {
      glyph(pixels,mode==GYROMITE?G:S,1,7);
      glyph(pixels,mode==GYROMITE?Y:U,7,7);
    } else {
      const int hint=now-hintAt<700 ? requestedHint : 0;
      eyes(pixels,frameNumber,mode,hint);
    }
    nextFrameAt=now+180;
  } else if (mode==TEST || mode==TEST_FLASH) {
    glyph(pixels,T,4,mode==TEST_FLASH && frameNumber%4<2 ? 7 : 4);
    nextFrameAt=now+380;
  } else if (mode==PAIRING) {
    glyph(pixels,P,4,frameNumber%4<2?7:4);
    nextFrameAt=now+380;
  } else if (mode==FAULT) {
    if (frameNumber%2==0) glyph(pixels,X,4,7);
    nextFrameAt=now+550;
  }
  matrix.draw(pixels);
  ++frameNumber;
}

void set_rob_display(int mode,int hint) {
  requestedMode=(mode>=LOADING && mode<=OFF)?mode:FAULT;
  heartbeatAt=millis();
  if (hint>=1 && hint<=6) {requestedHint=hint;hintAt=heartbeatAt;}
}

void displayTask(void*,void*,void*) {
  while(true) {refreshMatrix();k_msleep(5);}
}

void setup() {
  matrix.begin();
  matrix.setGrayscaleBits(3);
  hourglass(0);
  displayStack=k_thread_stack_alloc(2048,0);
  if(displayStack!=nullptr) {
    displayThreadId=k_thread_create(&displayThread,displayStack,2048,displayTask,
                                   nullptr,nullptr,nullptr,5,0,K_NO_WAIT);
    k_thread_name_set(displayThreadId,"rob-matrix");
  }
  Bridge.begin();
  Bridge.provide("set_rob_display",set_rob_display);
}

void loop() {
  if(displayThreadId==nullptr) refreshMatrix();
  delay(5);
}
