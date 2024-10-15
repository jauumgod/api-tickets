# TICKET - API DJANGO

<span style="font-size: 16px">Essa api está sendo construida voltada para solucionar adições de tickets de produção de chegadas e saidas de produtos.</span>

<h3>Metodos Suportados</h3>
<div style="font-size: 18px">
  <ul>
    <li>GET</li>
    <li>POST</li>
    <li>PUT</li>
    <li>DELETE</li>
  </ul>
</div>

<div>
  <ul>
  <h3>Rotas</h3>
   <li><strong style="font-size: 20px">Empresas : POST</strong></li>

      /api/empresas/
      
      {
        "nome": "Empresa1",
        "cnpj": "01020304/0001-01",
        "endereco": "exemplo",
      }
   <li><strong style="font-size: 20px">Criar Usuários: POST</strong></li>

    /api/users/

    {
      "username": "username",
      "password": "passwd",
      "empresa": []
    }

   <li><strong style="font-size: 20px">Criar Tickets: POST</strong></li>

    /api/tickets/

    {
      "placa": "username",
      "produto": "passwd",
      "transportadora": "transportadora",
      "motorista": "motorista",
      "operador": "operador",
      "cliente": "cliente",
      "peso_entrada": "peso_entrada",
      "peso_saida": "peso_saida",
      "peso_liquido": "peso_liquido",
      "lote_leira": "lote_leira",
      "umidade": "umidade",
    }

  <li><strong style="font-size: 20px">Adicionar Imagens: POST</strong></li>

      /api/imagens/

      {
        "nome": "nome",
        "ticket": "001",
        "imagem": "nome_imagem_teste.png",
      }
  </ul>
   
</div>

<h3> Server Api Local : <a>http://127.0.0.1:8000/api/</a></h3>
