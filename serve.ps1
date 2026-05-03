$ErrorActionPreference = "Stop"

$root = (Resolve-Path ".").Path
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), 8000)
$listener.Start()

try {
  while ($true) {
    $client = $listener.AcceptTcpClient()
    try {
      $stream = $client.GetStream()
      $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::ASCII, $false, 1024, $true)
      $requestLine = $reader.ReadLine()

      while ($reader.Peek() -ge 0) {
        $header = $reader.ReadLine()
        if ([string]::IsNullOrEmpty($header)) { break }
      }

      $path = "index.html"
      if ($requestLine -match "^[A-Z]+\s+([^\s]+)") {
        $rawPath = [Uri]::UnescapeDataString($matches[1].Split("?")[0]).TrimStart("/")
        if ($rawPath) { $path = $rawPath }
      }

      $fullPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($root, $path))
      if (-not $fullPath.StartsWith($root)) { throw "Forbidden" }
      if (Test-Path -LiteralPath $fullPath -PathType Container) {
        $fullPath = Join-Path $fullPath "index.html"
      }

      if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
        $bytes = [System.IO.File]::ReadAllBytes($fullPath)
        $extension = [System.IO.Path]::GetExtension($fullPath).ToLowerInvariant()
        $contentType = switch ($extension) {
          ".html" { "text/html; charset=utf-8" }
          ".css" { "text/css; charset=utf-8" }
          ".js" { "text/javascript; charset=utf-8" }
          ".png" { "image/png" }
          ".jpg" { "image/jpeg" }
          ".jpeg" { "image/jpeg" }
          ".svg" { "image/svg+xml" }
          default { "application/octet-stream" }
        }
        $status = "200 OK"
      } else {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes("Not found")
        $contentType = "text/plain; charset=utf-8"
        $status = "404 Not Found"
      }

      $head = "HTTP/1.1 $status`r`nContent-Type: $contentType`r`nContent-Length: $($bytes.Length)`r`nConnection: close`r`n`r`n"
      $headBytes = [System.Text.Encoding]::ASCII.GetBytes($head)
      $stream.Write($headBytes, 0, $headBytes.Length)
      $stream.Write($bytes, 0, $bytes.Length)
    } finally {
      $client.Close()
    }
  }
} finally {
  $listener.Stop()
}
