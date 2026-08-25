# Configura o arquivo de saída
$ArquivoSaida = "$PSScriptRoot\relatorio_rede_completo.txt"
# Altere para a sua faixa de IP (mantenha o asterisco no final)
$SubredeAlvo = "192.168.1.*"

Write-Host "1. Enviando pings automáticos em paralelo..." -ForegroundColor Cyan
Get-CimInstance Win32_PingStatus -Filter "Address like '$SubredeAlvo' and Timeout=100 and ResolveAddress=false" | Out-Null

Write-Host "2. Coletando dados da tabela ARP..." -ForegroundColor Cyan
$TabelaARP = Get-NetNeighbor -AddressFamily IPv4 | Where-Object { $_.State -ne "Permanent" -and $_.IPAddress -notlike "224.*" -and $_.IPAddress -notlike "255.*" }

$Dispositivos = [System.Collections.Generic.List[PSObject]]::new()
$MacsVistos = @{}

Write-Host "3. Resolvendo Nomes de Rede (Hostnames) e Fabricantes..." -ForegroundColor Cyan
foreach ($Item in $TabelaARP) {
    $IP = $Item.IPAddress
    $MAC = $Item.LinkLayerAddress.ToUpper()

    if ($IP -like $SubredeAlvo -and -not $MacsVistos.ContainsKey($MAC)) {
        $MacsVistos[$MAC] = $true
        
        # --- Descoberta de Hostname ---
        $Hostname = "Desconhecido"
        # Estratégia 1: Resolução de DNS nativa do .NET
        try {
            $Hostname = [System.Net.Dns]::GetHostEntry($IP).HostName
        } catch {
            # Estratégia 2: Comando nbtstat para nomes NetBIOS/Windows
            $NbtData = nbtstat -A $IP 2>$null
            if ($NbtData) {
                $LinhaNome = $NbtData | Where-Object { $_ -match '<00>\s+(UNIQUE|ÚNICO)' }
                if ($LinhaNome) {
                    $Hostname = $LinhaNome.Split([char[]]@(' ', "`t"), [StringSplitOptions]::RemoveEmptyEntries)[0].Trim()
                }
            }
        }

        # --- Descoberta de Fabricante ---
        $Fabricante = "Desconhecido"
        try {
            $MacLimpo = $MAC -replace '[:-]', ''
            $Fabricante = Invoke-RestMethod -Uri "https://macvendors.com" -TimeoutSec 2 -ErrorAction Stop
        } catch {
            $Fabricante = "Não Encontrado"
        }

        $Dispositivos.Add([PSCustomObject]@{
            "Endereço IP"     = $IP
            "Endereço MAC"    = $MAC
            "Nome de Rede (Hostname)" = $Hostname
            "Fabricante Hardware"      = $Fabricante
        })
    }
}

# Ordena e gera o layout final
$ResultadosOrdenados = $Dispositivos | Sort-Object { [version]$_."Endereço IP" }
$Relatorio = $ResultadosOrdenados | Format-Table -AutoSize | Out-String
$TotalText = "`r`nTotal de dispositivos mapeados ativos: $($ResultadosOrdenados.Count)"
$ConteudoFinal = $Relatorio + $TotalText

# Exibe na tela e grava no TXT
Write-Host $ConteudoFinal
$ConteudoFinal | Out-File -FilePath $ArquivoSaida -Encoding utf8

Write-Host "`r`n[SUCESSO] Relatório completo salvo em: $ArquivoSaida" -ForegroundColor Green
