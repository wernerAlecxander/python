# Configura o arquivo de saída
$ArquivoSaida = "$PSScriptRoot\relatorio_rede_fabricantes.txt"
# Altere para a sua faixa de IP (mantenha o asterisco no final)
$SubredeAlvo = "192.168.1.*"

Write-Host "1. Enviando pings automáticos em paralelo..." -ForegroundColor Cyan
# Envia pings rápidos para toda a rede de forma assíncrona
Get-CimInstance Win32_PingStatus -Filter "Address like '$SubredeAlvo' and Timeout=100 and ResolveAddress=false" | Out-Null

Write-Host "2. Coletando dados da tabela ARP do Windows..." -ForegroundColor Cyan
$TabelaARP = Get-NetNeighbor -AddressFamily IPv4 | Where-Object { $_.State -ne "Permanent" -and $_.IPAddress -notlike "224.*" -and $_.IPAddress -notlike "255.*" }

$Dispositivos = [System.Collections.Generic.List[PSObject]]::new()
$MacsVistos = @{}

Write-Host "3. Consultando fabricantes dos dispositivos..." -ForegroundColor Cyan
foreach ($Item in $TabelaARP) {
    $IP = $Item.IPAddress
    $MAC = $Item.LinkLayerAddress.ToUpper()

    # Filtra para trazer apenas a subrede configurada e evitar duplicatas de MAC
    if ($IP -like $SubredeAlvo -and -not $MacsVistos.ContainsKey($MAC)) {
        $MacsVistos[$MAC] = $true
        
        # Consulta o fabricante usando uma API web gratuita
        $Fabricante = "Desconhecido"
        try {
            $MacLimpo = $MAC -replace '[:-]', ''
            $Fabricante = Invoke-RestMethod -Uri "https://macvendors.com" -TimeoutSec 2 -ErrorAction Stop
        } catch {
            $Fabricante = "Não Encontrado / Timeout"
        }

        $Dispositivos.Add([PSCustomObject]@{
            "Endereço IP" = $IP
            "Endereço MAC" = $MAC
            "Fabricante Hardware" = $Fabricante
        })
    }
}

# Ordena pelo último número do IP
$ResultadosOrdenados = $Dispositivos | Sort-Object { [version]$_."Endereço IP" }

# Formata o relatório em texto plano alinhado
$Relatorio = $ResultadosOrdenados | Format-Table -AutoSize | Out-String
$TotalText = "`r`nTotal de dispositivos mapeados ativos: $($ResultadosOrdenados.Count)"
$ConteudoFinal = $Relatorio + $TotalText

# Exibe na tela e salva no arquivo TXT
Write-Host $ConteudoFinal
$ConteudoFinal | Out-File -FilePath $ArquivoSaida -Encoding utf8

Write-Host "`r`n[SUCESSO] Relatório salvo em: $ArquivoSaida" -ForegroundColor Green
