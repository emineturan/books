import asyncio
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from app import getDefinitions

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP sunucusunu başlat
mcp = FastMCP("dictionary-mcp")

@mcp.tool()
async def get_definitions(word: str) -> str:
    """
    Get definitions for a word using Dictionary API.
    
    Args:
        word: The word to get definitions for
        
    Returns:
        String containing definitions or error message
    """
    try:
        # Input validation
        if not word or not word.strip():
            return "Lütfen geçerli bir kelime girin."
        
        # Kelimeyi temizle
        word = word.strip().lower()
        
        logger.info(f"Getting definitions for word: {word}")
        
        # Senkron fonksiyonu async içinde çalıştır
        loop = asyncio.get_event_loop()
        definitions = await loop.run_in_executor(None, getDefinitions, word)
        
        if not definitions or definitions == "No definitions found.":
            return f"'{word}' kelimesi için tanım bulunamadı."
        
        # Tanımları formatla
        formatted_definitions = f"**{word.upper()}** için tanımlar:\n\n{definitions}"
        
        logger.info(f"Successfully retrieved definitions for: {word}")
        return formatted_definitions
        
    except Exception as e:
        error_msg = f"Tanım alınırken hata oluştu: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def get_word_info(word: str) -> str:
    """
    Get detailed word information including definitions, pronunciation, and etymology.
    
    Args:
        word: The word to get information for
        
    Returns:
        Detailed word information
    """
    try:
        if not word or not word.strip():
            return "Lütfen geçerli bir kelime girin."
        
        word = word.strip().lower()
        logger.info(f"Getting detailed info for word: {word}")
        
        # Gelişmiş bilgi almak için Dictionary API'sini kullan
        import requests
        import json
        
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, url)
        
        if response.status_code == 200:
            data = response.json()
            word_data = data[0]
            
            # Detaylı bilgi formatla
            result = f"**{word_data.get('word', word).upper()}**\n\n"
            
            # Fonetik
            if 'phonetics' in word_data and word_data['phonetics']:
                phonetic = word_data['phonetics'][0]
                if 'text' in phonetic:
                    result += f"**Telaffuz:** {phonetic['text']}\n\n"
            
            # Anlamlar
            for i, meaning in enumerate(word_data.get('meanings', []), 1):
                part_of_speech = meaning.get('partOfSpeech', 'Bilinmiyor')
                result += f"**{i}. {part_of_speech.title()}**\n"
                
                for j, definition in enumerate(meaning.get('definitions', []), 1):
                    result += f"   {j}. {definition.get('definition', '')}\n"
                    
                    # Örnek cümle varsa ekle
                    if 'example' in definition:
                        result += f"      *Örnek: {definition['example']}*\n"
                
                # Eş anlamlılar
                if 'synonyms' in meaning and meaning['synonyms']:
                    result += f"   **Eş anlamlılar:** {', '.join(meaning['synonyms'][:5])}\n"
                
                # Zıt anlamlılar
                if 'antonyms' in meaning and meaning['antonyms']:
                    result += f"   **Zıt anlamlılar:** {', '.join(meaning['antonyms'][:5])}\n"
                
                result += "\n"
            
            return result
        else:
            return f"'{word}' kelimesi için detaylı bilgi bulunamadı."
            
    except Exception as e:
        error_msg = f"Kelime bilgisi alınırken hata oluştu: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def search_similar_words(word: str) -> str:
    """
    Search for words similar to the given word.
    
    Args:
        word: The word to find similar words for
        
    Returns:
        List of similar words or suggestions
    """
    try:
        if not word or not word.strip():
            return "Lütfen geçerli bir kelime girin."
        
        word = word.strip().lower()
        logger.info(f"Searching similar words for: {word}")
        
        # Önce normal tanımı dene
        loop = asyncio.get_event_loop()
        definitions = await loop.run_in_executor(None, getDefinitions, word)
        
        if definitions and definitions != "No definitions found.":
            return f"'{word}' kelimesi mevcut. Tanımları görmek için get_definitions aracını kullanın."
        
        # Benzer kelimeler için basit öneri sistemi
        import requests
        suggestions = []
        
        # Farklı varyasyonları dene
        variations = [
            word + 's',          # çoğul
            word + 'ed',         # geçmiş zaman
            word + 'ing',        # şimdiki zaman
            word[:-1] if len(word) > 3 else word,  # son harfi kaldır
            word[:-2] if len(word) > 4 else word,  # son 2 harfi kaldır
        ]
        
        for variation in variations:
            try:
                url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{variation}"
                response = await loop.run_in_executor(None, requests.get, url)
                if response.status_code == 200:
                    suggestions.append(variation)
            except:
                continue
        
        if suggestions:
            return f"'{word}' bulunamadı. Benzer kelimeler: {', '.join(suggestions[:5])}"
        else:
            return f"'{word}' kelimesi ve benzer varyasyonları bulunamadı. Yazımı kontrol edin."
            
    except Exception as e:
        error_msg = f"Benzer kelime arama sırasında hata oluştu: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    try:
        logger.info("Dictionary MCP sunucusu başlatılıyor...")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Sunucu kapatılıyor...")
    except Exception as e:
        logger.error(f"Sunucu hatası: {e}")
