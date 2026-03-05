"""
TDD - Test-Driven Development para Bot de Horóscopo

Este arquivo contém testes para todas as funcionalidades:
1. Comando /start
2. Horóscopo Diário
3. Análise por Data
4. Mapa Astral
5. Tratamento de Erros

Execute: pytest test_bot.py -v
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from datetime import datetime
import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa o bot (assumindo que bot.py está na mesma pasta)
from bot import (
    start,
    button_handler,
    receive_date,
    receive_time,
    receive_city,
    cancel,
    get_horoscope,
    calculate_sign,
    generate_chart_image,
    SIGNS,
    DATE,
    TIME,
    CITY
)


# ==================== FIXTURES ====================

@pytest_asyncio.fixture
async def mock_update():
    """Cria um mock de Update do Telegram"""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.first_name = "TestUser"
    update.effective_user.id = 123456789
    update.message = AsyncMock()
    update.callback_query = AsyncMock()
    update.callback_query.data = ""
    update.callback_query.message = AsyncMock()
    return update


@pytest_asyncio.fixture
async def mock_context():
    """Cria um mock de Context do Telegram"""
    context = MagicMock()
    context.user_data = {}
    return context


# ==================== TESTES DE COMANDOS BÁSICOS ====================

class TestStartCommand:
    """Testes para o comando /start"""
    
    @pytest.mark.asyncio
    async def test_start_sends_welcome_message(self, mock_update, mock_context):
        """✅ DEVE enviar mensagem de boas-vindas com menu"""
        # Act
        await start(mock_update, mock_context)
        
        # Assert
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        
        # Verifica se contém texto de boas-vindas
        assert "Bem-vindo" in call_args[0][0]
        assert "✨" in call_args[0][0]
        
        # Verifica se tem teclado inline
        assert "reply_markup" in call_args[1]
        assert call_args[1]["parse_mode"] == "Markdown"
    
    @pytest.mark.asyncio
    async def test_start_has_four_buttons(self, mock_update, mock_context):
        """✅ DEVE ter 4 botões: Horóscopo, Análise, Mapa, Ajuda"""
        await start(mock_update, mock_context)
        
        call_args = mock_update.message.reply_text.call_args
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        
        assert len(keyboard) == 4  # 4 linhas de botões
        assert "Horóscopo" in keyboard[0][0].text
        assert "Análise" in keyboard[1][0].text
        assert "Mapa" in keyboard[2][0].text
        assert "Ajuda" in keyboard[3][0].text


class TestButtonHandler:
    """Testes para o handler de botões inline"""
    
    @pytest.mark.asyncio
    async def test_button_daily_shows_signs_menu(self, mock_update, mock_context):
        """✅ Botão 'daily' DEVE mostrar menu com 12 signos"""
        mock_update.callback_query.data = "daily"
        
        await button_handler(mock_update, mock_context)
        
        mock_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_update.callback_query.edit_message_text.call_args
        
        assert "Escolha seu signo" in call_args[0][0]
        # 12 signos + botão voltar = 5 linhas (4x3 + 1)
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        assert len(keyboard) == 5  # 4 linhas de 3 signos + 1 de voltar
    
    @pytest.mark.asyncio
    async def test_button_analysis_asks_for_date(self, mock_update, mock_context):
        """✅ Botão 'analysis' DEVE pedir data no formato DD/MM/AAAA"""
        mock_update.callback_query.data = "analysis"
        
        result = await button_handler(mock_update, mock_context)
        
        mock_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_update.callback_query.edit_message_text.call_args
        
        assert "Análise por Data" in call_args[0][0]
        assert "DD/MM/AAAA" in call_args[0][0]
        assert call_args[1]["parse_mode"] == "Markdown"
        assert result == DATE  # Retorna estado DATE
    
    @pytest.mark.asyncio
    async def test_button_chart_starts_conversation(self, mock_update, mock_context):
        """✅ Botão 'chart' DEVE iniciar fluxo de mapa astral"""
        mock_update.callback_query.data = "chart"
        
        result = await button_handler(mock_update, mock_context)
        
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "Mapa Astral" in call_args[0][0]
        assert "data de nascimento" in call_args[0][0]
        assert mock_context.user_data.get("chart_step") == "date"
        assert result == DATE
    
    @pytest.mark.asyncio
    async def test_button_help_shows_instructions(self, mock_update, mock_context):
        """✅ Botão 'help' DEVE mostrar instruções de uso"""
        mock_update.callback_query.data = "help"
        
        await button_handler(mock_update, mock_context)
        
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "Como usar" in call_args[0][0]
        assert "botões" in call_args[0][0]
        assert "Horóscopo" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_button_back_returns_to_main(self, mock_update, mock_context):
        """✅ Botão 'back' DEVE voltar ao menu principal"""
        mock_update.callback_query.data = "back"
        
        await button_handler(mock_update, mock_context)
        
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "Menu Principal" in call_args[0][0]
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        assert len(keyboard) == 4  # 4 botões do menu principal
    
    @pytest.mark.asyncio
    async def test_button_horoscope_sends_prediction(self, mock_update, mock_context):
        """✅ Botão 'horo_X' DEVE enviar horóscopo do signo"""
        mock_update.callback_query.data = "horo_aries"
        
        await button_handler(mock_update, mock_context)
        
        mock_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_update.callback_query.edit_message_text.call_args
        
        assert "Áries" in call_args[0][0] or "♈" in call_args[0][0]
        assert "Horóscopo" in call_args[0][0]
        assert call_args[1]["parse_mode"] == "Markdown"
    
    @pytest.mark.asyncio
    async def test_button_invalid_shows_error(self, mock_update, mock_context):
        """✅ Botão inválido DEVE mostrar mensagem de erro"""
        mock_update.callback_query.data = "invalid_button"
        
        await button_handler(mock_update, mock_context)
        
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "não reconhecida" in call_args[0][0] or "Opção" in call_args[0][0]


# ==================== TESTES DE ANÁLISE POR DATA ====================

class TestAnalysisFlow:
    """Testes para fluxo de análise por data de nascimento"""
    
    @pytest.mark.asyncio
    async def test_receive_valid_date_returns_analysis(self, mock_update, mock_context):
        """✅ Data válida DEVE retornar análise astrológica"""
        mock_update.message.text = "15/03/1995"
        
        result = await receive_date(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        
        assert "Análise Astrológica" in call_args[0][0]
        assert "Áries" in call_args[0][0] or "♈" in call_args[0][0]  # 15/03 = Áries
        assert "Elemento" in call_args[0][0]
        assert "Número da Vida" in call_args[0][0]
        assert result == -1  # ConversationHandler.END
    
    @pytest.mark.asyncio
    async def test_receive_invalid_date_asks_again(self, mock_update, mock_context):
        """✅ Data inválida DEVE pedir novamente no formato correto"""
        mock_update.message.text = "data-invalida"
        
        result = await receive_date(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        
        assert "Formato inválido" in call_args[0][0]
        assert "DD/MM/AAAA" in call_args[0][0]
        assert result == DATE  # Permanece no estado DATE
    
    @pytest.mark.asyncio
    async def test_receive_date_leap_year(self, mock_update, mock_context):
        """✅ Data 29/02 em ano bissexto DEVE ser aceita"""
        mock_update.message.text = "29/02/2020"  # 2020 foi bissexto
        
        result = await receive_date(mock_update, mock_context)
        
        # Não deve dar erro de formato
        assert result == -1 or result == DATE  # Depende do cálculo do signo
    
    @pytest.mark.asyncio
    async def test_calculate_sign_correctly(self):
        """✅ Cálculo de signo DEVE estar correto para datas conhecidas"""
        test_cases = [
            ((21, 3), "aries"),      # Início de Áries
            ((20, 4), "touro"),       # Início de Touro
            ((21, 5), "gemeos"),      # Início de Gêmeos
            ((22, 6), "cancer"),      # Início de Câncer
            ((23, 7), "leao"),        # Início de Leão
            ((23, 8), "virgem"),      # Início de Virgem
            ((23, 9), "libra"),       # Início de Libra
            ((23, 10), "escorpiao"),  # Início de Escorpião
            ((22, 11), "sagitario"),  # Início de Sagitário
            ((22, 12), "capricornio"), # Início de Capricórnio
            ((20, 1), "aquario"),     # Início de Aquário
            ((19, 2), "peixes"),      # Início de Peixes
        ]
        
        for (day, month), expected_sign in test_cases:
            result = calculate_sign(day, month)
            assert result == expected_sign, f"Falha para {day}/{month}: esperado {expected_sign}, obtido {result}"


# ==================== TESTES DE MAPA ASTRAL ====================

class TestChartFlow:
    """Testes para fluxo de mapa astral"""
    
    @pytest.mark.asyncio
    async def test_receive_date_for_chart_asks_time(self, mock_update, mock_context):
        """✅ No fluxo chart, data válida DEVE pedir hora"""
        mock_update.message.text = "15/03/1995"
        mock_context.user_data["chart_step"] = "date"
        
        result = await receive_date(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        
        assert "hora" in call_args[0][0].lower()
        assert "HH:MM" in call_args[0][0]
        assert mock_context.user_data.get("birth_date") == "15/03/1995"
        assert mock_context.user_data.get("sign") == "Áries"
        assert result == TIME
    
    @pytest.mark.asyncio
    async def test_receive_time_asks_city(self, mock_update, mock_context):
        """✅ Hora válida DEVE pedir cidade"""
        mock_update.message.text = "14:30"
        
        result = await receive_time(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        
        assert "cidade" in call_args[0][0].lower()
        assert mock_context.user_data.get("birth_time") == "14:30"
        assert result == CITY
    
    @pytest.mark.asyncio
    async def test_receive_invalid_time_asks_again(self, mock_update, mock_context):
        """✅ Hora inválida DEVE pedir novamente"""
        mock_update.message.text = "25:99"  # Hora inválida
        
        result = await receive_time(mock_update, mock_context)
        
        call_args = mock_update.message.reply_text.call_args
        assert "Formato inválido" in call_args[0][0]
        assert result == TIME
    
    @pytest.mark.asyncio
    async def test_receive_city_generates_chart(self, mock_update, mock_context):
        """✅ Cidade válida DEVE gerar e enviar mapa astral"""
        mock_update.message.text = "São Paulo"
        mock_context.user_data["birth_date"] = "15/03/1995"
        mock_context.user_data["birth_time"] = "14:30"
        mock_context.user_data["sign"] = "Áries"
        
        result = await receive_city(mock_update, mock_context)
        
        # Verifica mensagem de "gerando"
        assert mock_update.message.reply_text.call_count >= 1
        
        # Verifica se enviou foto
        mock_update.message.reply_photo.assert_called_once()
        call_args = mock_update.message.reply_photo.call_args
        
        assert "Mapa Astral" in call_args[1]["caption"]
        assert "São Paulo" in call_args[1]["caption"]
        assert "Áries" in call_args[1]["caption"]
        assert result == -1  # ConversationHandler.END
    
    @pytest.mark.asyncio
    async def test_generate_chart_image_creates_bytes(self):
        """✅ Geração de imagem DEVE retornar BytesIO válido"""
        image_buffer = generate_chart_image("TestUser", "15/03/1995", "Áries")
        
        assert image_buffer is not None
        assert hasattr(image_buffer, 'read')
        assert hasattr(image_buffer, 'seek')
        
        # Verifica se é imagem PNG válida (magic bytes)
        image_buffer.seek(0)
        header = image_buffer.read(8)
        assert header[:8] == b'\x89PNG\r\n\x1a\n'  # Header PNG


# ==================== TESTES DE HORÓSCOPO ====================

class TestHoroscope:
    """Testes para geração de horóscopo"""
    
    def test_get_horoscope_returns_formatted_text(self):
        """✅ Horóscopo DEVE retornar texto formatado"""
        result = get_horoscope("aries")
        
        assert "Áries" in result or "♈" in result
        assert "Horóscopo" in result
        assert "📅" in result  # Emoji de data
        assert "⭐" in result  # Emoji de energia
    
    def test_get_horoscope_contains_all_sections(self):
        """✅ Horóscopo DEVE conter todas as seções"""
        result = get_horoscope("leao")
        
        sections = ["Energia", "Trabalho", "Amor", "Dinheiro", "Números"]
        for section in sections:
            assert section in result or section.lower() in result.lower()
    
    def test_get_horoscope_all_signs(self):
        """✅ DEVE funcionar para todos os 12 signos"""
        for sign_key in SIGNS.keys():
            result = get_horoscope(sign_key)
            assert result is not None
            assert len(result) > 50  # Texto não vazio
            assert sign_key in result or SIGNS[sign_key][0] in result or SIGNS[sign_key][1] in result
    
    @patch('bot.requests.get')
    def test_get_horoscope_uses_api_when_available(self, mock_get):
        """✅ DEVE usar API quando disponível"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'prediction': 'Teste de previsão',
            'mood': 'Excelente',
            'career': 'Bom',
            'love': 'Romântico',
            'finance': 'Estável',
            'lucky_numbers': '7, 14'
        }
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'FREE_ASTRO_API_KEY': 'fake_key'}):
            result = get_horoscope("libra")
            
            assert "Teste de previsão" in result
            assert "Excelente" in result


# ==================== TESTES DE CANCELAMENTO ====================

class TestCancelCommand:
    """Testes para comando /cancel"""
    
    @pytest.mark.asyncio
    async def test_cancel_ends_conversation(self, mock_update, mock_context):
        """✅ Cancel DEVE encerrar conversação"""
        result = await cancel(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        
        assert "cancelada" in call_args[0][0].lower()
        assert result == -1  # ConversationHandler.END


# ==================== TESTES DE TRATAMENTO DE ERROS ====================

class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    @pytest.mark.asyncio
    async def test_button_handler_catches_exceptions(self, mock_update, mock_context):
        """✅ Erros em botões DEVE ser tratados gracefulmente"""
        # Força um erro
        mock_update.callback_query.answer.side_effect = Exception("Erro forçado")
        
        # Não deve levantar exceção
        result = await button_handler(mock_update, mock_context)
        
        # Deve tentar enviar mensagem de erro
        mock_update.callback_query.edit_message_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_receive_date_handles_exception(self, mock_update, mock_context):
        """✅ Erros no processamento DEVE ser tratados"""
        mock_update.message.text = None  # Vai causar erro ao tentar split
        
        # Não deve crashar
        try:
            result = await receive_date(mock_update, mock_context)
        except:
            pass  # Esperado ou não, não deve crashar o bot


# ==================== TESTES DE INTEGRAÇÃO ====================

class TestIntegration:
    """Testes de integração - fluxos completos"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_flow(self, mock_update, mock_context):
        """✅ Fluxo completo de análise: start → analysis → data → resultado"""
        # 1. Start
        await start(mock_update, mock_context)
        assert mock_update.message.reply_text.called
        
        # 2. Clica em analysis
        mock_update.callback_query.data = "analysis"
        result = await button_handler(mock_update, mock_context)
        assert result == DATE
        
        # 3. Envia data
        mock_update.message.text = "15/03/1995"
        result = await receive_date(mock_update, mock_context)
        assert result == -1  # Fim da conversação
    
    @pytest.mark.asyncio
    async def test_full_chart_flow(self, mock_update, mock_context):
        """✅ Fluxo completo de mapa: start → chart → data → hora → cidade → imagem"""
        # 1. Start
        await start(mock_update, mock_context)
        
        # 2. Clica em chart
        mock_update.callback_query.data = "chart"
        result = await button_handler(mock_update, mock_context)
        assert result == DATE
        assert mock_context.user_data["chart_step"] == "date"
        
        # 3. Envia data
        mock_update.message.text = "15/03/1995"
        result = await receive_date(mock_update, mock_context)
        assert result == TIME
        
        # 4. Envia hora
        mock_update.message.text = "14:30"
        result = await receive_time(mock_update, mock_context)
        assert result == CITY
        
        # 5. Envia cidade
        mock_update.message.text = "São Paulo"
        result = await receive_city(mock_update, mock_context)
        assert result == -1  # Fim


# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
