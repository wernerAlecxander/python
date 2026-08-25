Add-Type -AssemblyName System.DirectoryServices
$NomeDominio = "policiacivil.local"

Write-Host "⏳ Aguardando conexão física com a rede da Polícia Civil..." -ForegroundColor Yellow
Write-Host "👉 Pode deixar esta janela aberta. O script rodará sozinho assim que detectar o servidor." -ForegroundColor Cyan

# Loop que testa a conexão a cada 5 segundos
while ($true) {
    $teste = Test-NetConnection $NomeDominio -Port 389 -WarningAction SilentlyContinue
    if ($teste.TcpTestSucceeded -eq $true) {
        Write-Host "✅ Rede detectada com sucesso! Extraindo dados..." -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 5
}

# Bloco de execução principal (roda apenas quando conectado)
try {
    $Componentes = $NomeDominio.Split('.') | ForEach-Object { "DC=$_" }
    $CaminhoDN = [string]::Join(",", $Componentes)
    $dominio = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$NomeDominio/$CaminhoDN")
    $busca = New-Object System.DirectoryServices.DirectorySearcher($dominio)
    $busca.Filter = "(&(objectCategory=group)(cn=Domain Admins))"
    $grupo = $busca.FindOne()
    
    # Salva o resultado em um arquivo de texto na Área de Trabalho para você não perder
    $CaminhoArquivo = "$HOME\Desktop\Membros_Domain_Admins.txt"
    $grupo.Properties.member | Out-File -FilePath $CaminhoArquivo
    
    Write-Host "`n🎉 Sucesso! A lista de administradores foi salva na sua Área de Trabalho no arquivo: Membros_Domain_Admins.txt" -ForegroundColor Green
} catch {
    Write-Host "❌ Falha ao ler os dados do AD: $_" -ForegroundColor Red
}
