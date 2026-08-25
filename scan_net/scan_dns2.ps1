# 1. Carrega a biblioteca necessária do sistema
Add-Type -AssemblyName System.DirectoryServices

# 2. Define o domínio correto obtido do WMI
$NomeDominio = "policiacivil.local"

write-host "🔍 Localizando Controladores de Domínio ativos para $NomeDominio..." -ForegroundColor Cyan

# 3. Consulta o DNS para encontrar os servidores AD reais (Registros SRV LDAP)
try {
    $DCServidores = (Resolve-DnsName "_ldap._tcp.dc._msdcs.$NomeDominio" -ErrorAction Stop).NameHost
    $DC_Real = $DCServidores[0]
    write-host "✅ Servidor AD encontrado: $DC_Real" -ForegroundColor Green
} catch {
    write-host "❌ Erro ao localizar servidor via DNS. Tentando usar o nome direto do domínio..." -ForegroundColor Yellow
    $DC_Real = $NomeDominio
}

# 4. Monta a estrutura Distinguished Name (DC=policiacivil,DC=local)
$Componentes = $NomeDominio.Split('.') | ForEach-Object { "DC=$_" }
$CaminhoDN = [string]::Join(",", $Componentes)

# 5. Conecta diretamente usando o nome do servidor homologado pelo DNS
$dominio = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$DC_Real/$CaminhoDN")

# 6. Executa a busca pelos Domain Admins
try {
    $busca = New-Object System.DirectoryServices.DirectorySearcher($dominio)
    $busca.Filter = "(&(objectCategory=group)(cn=Domain Admins))"
    $grupo = $busca.FindOne()

    if ($grupo) {
        write-host "`n👥 Membros do grupo Domain Admins:" -ForegroundColor Green
        $grupo.Properties.member
    } else {
        write-host "⚠️ Grupo 'Domain Admins' não foi encontrado com este filtro." -ForegroundColor Yellow
    }
} catch {
    write-host "❌ Falha crítica ao acessar o AD: $_" -ForegroundColor Red
}
