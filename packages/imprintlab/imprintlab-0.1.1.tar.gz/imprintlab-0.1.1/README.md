# Imprint

**Imprint** é uma biblioteca Python para criar e gerar modelos de documentos visuais, como certificados, crachás, convites e outros templates gráficos, de forma simples e programática. Ela permite preencher campos dinâmicos a partir de APIs, arquivos Excel, banco de dados ou qualquer fonte de dados.

---

## ⚡ Recursos

- Criação de **modelos** personalizados com múltiplas páginas.
- Adição de **campos dinâmicos**: textos, imagens e QR codes.
- Definição de **tamanho e posição** de campos em cada página.
- Exportação de modelos para **imagens PNG** ou outros formatos.
- Integração fácil com **APIs, Excel e bancos de dados**.
- Estrutura modular para extensões futuras (novos tipos de campos e efeitos gráficos).

---

## 🚀 Instalação

Você pode instalar diretamente do repositório (quando disponível no PyPI, basta substituir `git+...` por `pip install imprint`):

pip install git+https://github.com/seu-usuario/imprint.git

---

## 📝 Exemplo de uso básico

```python
from imprint import Model

def basic_model():
    model = Model.new(name="Modelo-Cracha-Basico")
    first_page = model.new_page(name="Frente")
    first_page.set_size(500, 500)
    first_page.set_background("/caminho/para/imagem.png")
    
    name = first_page.add_field(name="Nome Completo", component="text")
    name.set_position((140, 140))
    
    job = first_page.add_field(name="Cargo", component="text")
    job.set_position((150, 150))
    
    return model

# Uso do modelo
model = basic_model()
pages = model.to_png({
    "Nome Completo": "Daniel Fernandes Pereira", 
    "Cargo": "TI"
})
```
---

## 🔧 Estrutura do modelo

- **Model**: representa o documento completo, contendo múltiplas páginas.
- **Page**: representa cada página do modelo.
- **Field**: representa os campos dinâmicos que podem ser preenchidos (texto, imagem, QR code, etc.).
- **Components**: conjunto de tipos de campos disponíveis.

---

## 🌟 Próximos recursos planejados

- Suporte a **camadas e efeitos visuais**.
- Exportação em **PDF** diretamente.
- Integração com **planilhas Excel** e arquivos CSV.
- Suporte a **QR codes dinâmicos** e códigos de barras.
- Templates compartilháveis via **API**.

---

## 💡 Contribuindo

Contribuições são bem-vindas! Siga os passos abaixo:

1. **Faça um fork** do projeto
2. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/nova-funcionalidade
---

## 📄 Licença

MIT License © Daniel Fernandes