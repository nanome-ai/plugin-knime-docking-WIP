param($one, $two)

$l = $one, $two

foreach ($var in $l.GetEnumerator()) {
    Write-Host $var
}