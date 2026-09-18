$assembly = [Reflection.Assembly]::LoadFile('E:\AI_Playground\420\build\fcs_lab\forgotten construction set.exe')
try { $types = $assembly.GetTypes() } catch [Reflection.ReflectionTypeLoadException] { $types = $_.Exception.Types }
foreach ($type in $types) { if ($type -and $type.IsEnum -and $type.Name -match 'BuildingFunction|StatsEnumerated|ItemType') { Write-Output $type.FullName; foreach ($value in [Enum]::GetValues($type)) { Write-Output ('{0}={1}' -f $value,[int]$value) } } }
