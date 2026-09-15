$ErrorActionPreference = 'Stop'
$rootPath = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $rootPath
$vc64 = Join-Path $rootPath 'build\toolchain\vc10_base\Program Files(64)\Microsoft Visual Studio 10.0\VC'
$vc32 = Join-Path $rootPath 'build\toolchain\vc10_base\Program Files\Microsoft Visual Studio 10.0\VC'
$sdkHeader = Get-ChildItem -LiteralPath (Join-Path $rootPath 'build\toolchain\sdk') -Recurse -Filter Windows.h | Select-Object -First 1
$sdkLibrary = Get-ChildItem -LiteralPath (Join-Path $rootPath 'build\toolchain\sdk') -Recurse -Filter kernel32.lib | Where-Object { $_.FullName -match 'x64|amd64' } | Select-Object -First 1
if (!$sdkHeader -or !$sdkLibrary) { throw 'Windows SDK headers and x64 libraries are required.' }
$deps = Join-Path $rootPath 'build\KenshiLib_Examples_deps'
$env:INCLUDE = "$vc32\include;$($sdkHeader.DirectoryName);$deps\KenshiLib\Include;$deps\boost_1_60_0"
$env:LIB = "$vc64\lib\amd64;$($sdkLibrary.DirectoryName);$deps\KenshiLib\Libraries"
$outPath = Join-Path $rootPath 'build\420_Smoking_RE'
$objPath = Join-Path $rootPath 'build\re_smoke_obj'
New-Item -ItemType Directory -Force $outPath,$objPath | Out-Null
& "$vc64\bin\amd64\cl.exe" /nologo /LD /MD /EHsc /O2 /GL /W3 /wd4819 /DNDEBUG /DUNICODE /D_UNICODE /DBOOST_ALL_NO_LIB /DBOOST_ERROR_CODE_HEADER_ONLY /D_WIN32_WINNT=0x0601 'src\re_smoke\SmokingSmoke.cpp' "/Fo$objPath\SmokingSmoke.obj" /link /LTCG "/OUT:$outPath\SmokingSmoke.dll" "/IMPLIB:$objPath\SmokingSmoke.lib" KenshiLib.lib OgreMain_x64.lib kernel32.lib user32.lib
if ($LASTEXITCODE -ne 0) { throw "Compiler exited with $LASTEXITCODE" }
& "$vc64\bin\amd64\dumpbin.exe" /exports "$outPath\SmokingSmoke.dll"
if ($LASTEXITCODE -ne 0) { throw 'DLL inspection failed' }
