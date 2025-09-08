

KEY_UNKNOWN: int = -1

KEY_SPACE: int = 32

KEY_APOSTROPHE: int = 39

KEY_COMMA: int = 44

KEY_MINUS: int = 45

KEY_PERIOD: int = 46

KEY_SLASH: int = 47

KEY_0: int = 48

KEY_1: int = 49

KEY_2: int = 50

KEY_3: int = 51

KEY_4: int = 52

KEY_5: int = 53

KEY_6: int = 54

KEY_7: int = 55

KEY_8: int = 56

KEY_9: int = 57

KEY_SEMICOLON: int = 59

KEY_EQUAL: int = 61

KEY_A: int = 65

KEY_B: int = 66

KEY_C: int = 67

KEY_D: int = 68

KEY_E: int = 69

KEY_F: int = 70

KEY_G: int = 71

KEY_H: int = 72

KEY_I: int = 73

KEY_J: int = 74

KEY_K: int = 75

KEY_L: int = 76

KEY_M: int = 77

KEY_N: int = 78

KEY_O: int = 79

KEY_P: int = 80

KEY_Q: int = 81

KEY_R: int = 82

KEY_S: int = 83

KEY_T: int = 84

KEY_U: int = 85

KEY_V: int = 86

KEY_W: int = 87

KEY_X: int = 88

KEY_Y: int = 89

KEY_Z: int = 90

KEY_LEFT_BRACKET: int = 91

KEY_BACKSLASH: int = 92

KEY_RIGHT_BRACKET: int = 93

KEY_GRAVE_ACCENT: int = 96

KEY_WORLD_1: int = 161

KEY_WORLD_2: int = 162

KEY_ESCAPE: int = 256

KEY_ENTER: int = 257

KEY_TAB: int = 258

KEY_BACKSPACE: int = 259

KEY_INSERT: int = 260

KEY_DELETE: int = 261

KEY_RIGHT: int = 262

KEY_LEFT: int = 263

KEY_DOWN: int = 264

KEY_UP: int = 265

KEY_PAGE_UP: int = 266

KEY_PAGE_DOWN: int = 267

KEY_HOME: int = 268

KEY_END: int = 269

KEY_CAPS_LOCK: int = 280

KEY_SCROLL_LOCK: int = 281

KEY_NUM_LOCK: int = 282

KEY_PRINT_SCREEN: int = 283

KEY_PAUSE: int = 284

KEY_F1: int = 290

KEY_F2: int = 291

KEY_F3: int = 292

KEY_F4: int = 293

KEY_F5: int = 294

KEY_F6: int = 295

KEY_F7: int = 296

KEY_F8: int = 297

KEY_F9: int = 298

KEY_F10: int = 299

KEY_F11: int = 300

KEY_F12: int = 301

KEY_F13: int = 302

KEY_F14: int = 303

KEY_F15: int = 304

KEY_F16: int = 305

KEY_F17: int = 306

KEY_F18: int = 307

KEY_F19: int = 308

KEY_F20: int = 309

KEY_F21: int = 310

KEY_F22: int = 311

KEY_F23: int = 312

KEY_F24: int = 313

KEY_F25: int = 314

KEY_KP_0: int = 320

KEY_KP_1: int = 321

KEY_KP_2: int = 322

KEY_KP_3: int = 323

KEY_KP_4: int = 324

KEY_KP_5: int = 325

KEY_KP_6: int = 326

KEY_KP_7: int = 327

KEY_KP_8: int = 328

KEY_KP_9: int = 329

KEY_KP_DECIMAL: int = 330

KEY_KP_DIVIDE: int = 331

KEY_KP_MULTIPLY: int = 332

KEY_KP_SUBTRACT: int = 333

KEY_KP_ADD: int = 334

KEY_KP_ENTER: int = 335

KEY_KP_EQUAL: int = 336

KEY_LEFT_SHIFT: int = 340

KEY_LEFT_CONTROL: int = 341

KEY_LEFT_ALT: int = 342

KEY_LEFT_SUPER: int = 343

KEY_RIGHT_SHIFT: int = 344

KEY_RIGHT_CONTROL: int = 345

KEY_RIGHT_ALT: int = 346

KEY_RIGHT_SUPER: int = 347

KEY_MENU: int = 348

KEY_LAST: int = 348

MOD_SHIFT: int = 1

MOD_CONTROL: int = 2

MOD_ALT: int = 4

MOD_SUPER: int = 8

MOUSE_BUTTON_1: int = 0

MOUSE_BUTTON_2: int = 1

MOUSE_BUTTON_3: int = 2

MOUSE_BUTTON_4: int = 3

MOUSE_BUTTON_5: int = 4

MOUSE_BUTTON_6: int = 5

MOUSE_BUTTON_7: int = 6

MOUSE_BUTTON_8: int = 7

MOUSE_BUTTON_LAST: int = 7

MOUSE_BUTTON_LEFT: int = 0

MOUSE_BUTTON_RIGHT: int = 1

MOUSE_BUTTON_MIDDLE: int = 2

RELEASE: int = 0

PRESS: int = 1

REPEAT: int = 2

DONT_CARE: int = -1

def GetTime() -> float: ...

def SetWindowSizeLimits(window: Window, min_width: int, min_height: int, max_width: int, max_height: int) -> None:
    """Set the size limits of the specified window"""

class Window:
    pass
