# gerador-cupomfiscal-discord
Um pequeno bot do discord feito em python por mim para gerar cupons fiscais para seus produtos em png.

Passo 1: Iniciar o Bot

Certifique-se de que o bot está online. Execute o código do bot em um ambiente Python, e o bot estará pronto para responder a comandos.

Passo 2: Criar um Novo Ticket

Para criar um novo ticket, use o comando .ticket. O bot guiará você através do processo de criação do ticket. Você será solicitado a fornecer as seguintes informações:

Nome do Serviço: Digite o nome do serviço que deseja registrar no ticket.
Preço do Item: Insira o preço do item para o serviço.
Nome do Responsável: Forneça o nome da pessoa responsável pelo serviço.
Nome do Usuário: Insira o nome do usuário associado ao serviço.
Após fornecer todas as informações, o bot gerará um ticket fiscal com os detalhes do serviço e o enviará como uma imagem no canal.

Passo 3: Listar Tickets

Você pode listar todos os tickets criados usando o comando .tickets. O bot listará os tickets existentes, incluindo o ID do ticket, o nome do serviço, o preço, o nome do responsável e o nome do usuário.

Passo 4: Limpar Todos os Tickets

Se desejar limpar todos os tickets registrados, você pode usar o comando .cleartickets. Isso excluirá todos os registros de tickets no banco de dados.
Observações:

Certifique-se de que o bot tenha as permissões necessárias para enviar mensagens e anexar arquivos no canal em que você está interagindo com ele.
Se você desejar personalizar o bot ainda mais, é possível modificar a interface do ticket gerado, como as cores e o formato da fonte, alterando o código.
Lembre-se de substituir 'TOKEN DO SEU BOT' pelo token real do seu bot no código.
