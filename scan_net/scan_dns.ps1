# 1. PREENCHA AQUI: Coloque o nome do domínio da sua empresa (ex: empresa.local)
>> $NomeDominio = "policiacivil.local"
>>
>> # 2. Configurações de rede fixas baseadas nos testes anteriores
>> $IP_do_DC = "192.168.0.2"
>>
>> # Força o carregamento da biblioteca do Active Directory no PowerShell
>> Add-Type -AssemblyName System.DirectoryServices
>>
>> # Transforma o nome (ex: empresa.local) no formato Distinguished Name (DC=empresa,DC=local)
>> $Componentes = $NomeDominio.Split('.') | ForEach-Object { "DC=$_" }
>> $CaminhoDN = [string]::Join(",", $Componentes)
>>
>> # Conecta diretamente no IP do servidor usando o caminho estruturado
>> $dominio = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$IP_do_DC/$CaminhoDN")
>>
>> # Executa a busca pelo grupo Domain Admins
>> $busca = New-Object System.DirectoryServices.DirectorySearcher($dominio)
>> $busca.Filter = "(&(objectCategory=group)(cn=Domain Admins))"
>> $grupo = $busca.FindOne()
>>
>> # Exibe os membros na tela
>> $grupo.Properties.member