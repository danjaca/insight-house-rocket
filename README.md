Aviso: O contexto para a realização deste projeto é fictício. A empresa, o contexto, o CEO, as perguntas de negócio foram criadas apenas para o desenvolvimento do projeto.

## House-rocket-insights
A House Rocket é uma empresa focada na compra e venda de imóveis, e sua estratégia é encontrar imóveis com boas condições e com boa localização para revendê-los posteriormente à preços mais altos.

Diante disso foi realizada uma análise onde diversos imóveis foram explorados e avaliados buscando o que poderia se tornar uma boa oportunidade para a empresa e alguns insights interessantes foram descobertos, algo que se tornará de extremo valor caso seja bem utilizado. Nenhum algoritimo de machine learning foi utilizado, os insights e recomendações forma feitas utilizando apenas a análise e exploração dos dados. Nesse processo buscou-se responder as perguntas abaixo: 

 1. Quais casas o CEO da House Rocket deveria comprar e por qual preço de compra?
 2. Uma vez a casa em posse da empresa, qual o melhor momento para vendê-las e qual seria o preço da venda?

 
## Dados
O conjunto de dados que representam o contexto está disponível na plataforma do Kaggle. Esse é o link: https://www.kaggle.com/harlfoxem/housesalesprediction.
Esse conjunto de dados contém casas vendidas entre Maio de 2014 e Maio de 2015. o dataset contém os seguintes atributos :

**id** - Numeração única de identificação de cada imóvel

**date** - Data da venda do imóvel

**price** - Preço da venda do imóvel

**bedrooms** - Numero de quartos 

**bathrooms** - Número de banheiros. 0.5 indica um banheiro sem chuveiro

**sqft_living** - Medida (em pés quadrado) do espaço interior dos imóveis

**sqft_lot** - Medida (em pés quadrado) do espaço total do terreno

**floors** - Numero de andares

**waterfront** - Variável que indica a presença ou não de vista para água (0 = não e 1 = sim)

**view** - Um índice de 0 a 4 que indica a qualidade da vista do imóvel. Onde: 0 = baixa 4 = alta

**condition** - Um índice de 1 a 5 que indica a condição do imóvel. Onde: 1 = baixo, 5 = alta

**grade** - Um índice de 1 a 13 que indica a construção e o design do imóvel. Varia de 1 a 13, onde: 1-3 = baixo, 7 = médio e 11-13 = alta

**sqft_above** - Medida (em pés quadrado) do espaço interior dos comodos que estão acima do nível do solo

**sqft_basement** - Medida (em pés quadrado) do espaço interior dos comodos que estão abaixo do nível do solo

**yr_built** - Ano de construção do imóvel

**yr_renovated** - Ano de reforma do imóvel

**zipcode** - Região onde cada imóvel se encontra

**lat** - Latitude

**long** - Longitude

**sqft_living15** - Medida (em pés quadrado) do espaço interno de habitação para os 15 vizinhos mais próximo

**sqft_lot15** - Medida (em pés quadrado) dos lotes de terra dos 15 vizinhos mais próximo

## Premissas

-A coluna 'price' foi considerada como o valor atual do imóvel, como se ele estivesse disponivel a venda.
-Foi removido um imóvel que possuia supostamente 33 quartos ( possuia as mesmas caracteristicas que quaisquer outro imóvel como o tamanho do terreno, numero de andares) pois foi considerado como um Outlier
-A avaliação de qualquer parâmetro foi feita a partir da região de cada imóvel ( zipcode ) para eliminarmos possiveis variáveis quanto a diferentes localizações (segurança, padrões sociais e etc)

## Planejamento da solução

1-Coleta dos dados -> o dataset pode ser encontrado no site [kaggle](https://www.kaggle.com/harlfoxem/housesalesprediction) 
2-Entedimento do negócio
3-Limpeza e tratamento dos dados
4-Exploração dos dados para resolver os problemas de negócio ->

 -Para a compra dos imóveis, obteve-se a mediana dos preços por região e se as condições do imóvel forem parecidas (no caso maior ou igual a 3) então estes seriam a indicação ideal para a compra.
 -Para a venda, é interessante colocar os imóveis a venda no período do ano onde os preços se encontram mais altos incluindo algumas condições:
 
   -**Se o preço do imóvel (cujo as condições dele são boas) for menor que a média dos preços no melhor período do ano = é interessante, pelo                                 menos, equiparar o valor atual dele para o valor da média. 
   
   -**Se o preço do imóvel for maior ou igual a média dos preços no melhor período do ano = há um incremento de 10% no valor (para obter um lucro                             mínimo)
                         
5- Avaliação de algumas hipóteses afim de encontrar possiveis insights de negócio
6-Resultados obtidos
7-Criação de uma aplicação na Web afim de visualizar melhor os resultados obtidos
8-Conclusão

## Melhores Insights 


**1. Há um crescimento anual de 10% -> TRUE**
 Esta afirmação pode ser usada estratégicamente se o CEO da House Rocket decidir comprar os imóveis avaliados e aguardar o próximo ano para a venda.
 
 **2. Imóveis com mais de 3 quartos são 20% mais caros na média -> TRUE**
 Já que são mais de 40% mais caros, pode entrar em pauta uma reforma no imóvel visando adicionar mais quartos.
 
 **3. O zipcode mais lucrativo é o 98004 -> TRUE **
 Dar ênfase nesta região seria a melhor opção para começar a execução do projeto.
 
 **4. Casas com mais de 1 andar são 20% mais caras na média -> TRUE**
 Mais outro insight onde poderia ser avaliado uma reforma mas agora visando a construção de outro andar.
 
 **5. Casas com reforma são 10% mais caras -> TRUE**
Seria interessante realizar alguma reforma antes de colocar a casa para venda, provavelmente quanto mais expressiva melhor na hora de vender.
 
 
 


