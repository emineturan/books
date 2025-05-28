import asyncio
import json
import logging
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.server.stdio
from app import getDefinitions

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dictionary-mcp")

# MCP sunucusunu oluştur
server = Server("dictionary-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    Mevcut araçların listesini döndür.
    """
    return [
        Tool(
            name="get_definitions",
            description="Get definitions for a word using Dictionary API",
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "The word to get definitions for",
                    }
                },
                "required": ["word"],
            },
        ),
        Tool(
            name="get_word_info",
            description="Get detailed word information including definitions, pronunciation, and etymology",
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "The word to get detailed information for",
                    }
                },
                "required": ["word"],
            },
        ),
        Tool(
            name="search_similar_words",
            description="Search for words similar to the given word",
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "The word to find similar words for",
                    }
                },
                "required": ["word"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Araç çağrılarını işle.
    """
    try:
        if name == "get_definitions":
            word = arguments.get("word", "").strip()
            if not word:
                return [TextContent(type="text", text="Lütfen geçerli bir kelime girin.")]
            
            logger.info(f"Getting definitions for word: {word}")
            
            # Senkron fonksiyonu async içinde çalıştır
            loop = asyncio.get_event_loop()
            definitions = await loop.run_in_executor(None, getDefinitions, word)
            
            if not definitions or definitions == "No definitions found.":
                result = f"'{word}' kelimesi için tanım bulunamadı."
            else:
                result = f"**{word.upper()}** için tanımlar:\n\n{definitions}"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_word_info":
            word = arguments.get("word", "").strip().lower()
            if not word:
                return [TextContent(type="text", text="Lütfen geçerli bir kelime girin.")]
            
            logger.info(f"Getting detailed info for word: {word}")
            
            import requests
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, requests.get, url)
            
            if response.status_code == 200:
                data = response.json()
                word_data = data[0]
                
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
                        
                        if 'example' in definition:
                            result += f"      *Örnek: {definition['example']}*\n"
                    
                    if 'synonyms' in meaning and meaning['synonyms']:
                        result += f"   **Eş anlamlılar:** {', '.join(meaning['synonyms'][:5])}\n"
                    
                    if 'antonyms' in meaning and meaning['antonyms']:
                        result += f"   **Zıt anlamlılar:** {', '.join(meaning['antonyms'][:5])}\n"
                    
                    result += "\n"
                
                return [TextContent(type="text", text=result)]
            else:
                return [TextContent(type="text", text=f"'{word}' kelimesi için detaylı bilgi bulunamadı.")]
        
        elif name == "search_similar_words":
            word = arguments.get("word", "").strip().lower()
            if not word:
                return [TextContent(type="text", text="Lütfen geçerli bir kelime girin.")]
            
            logger.info(f"Searching similar words for: {word}")
            
            loop = asyncio.get_event_loop()
            definitions = await loop.run_in_executor(None, getDefinitions, word)
            
            if definitions and definitions != "No definitions found.":
                return [TextContent(type="text", text=f"'{word}' kelimesi mevcut. Tanımları görmek için get_definitions aracını kullanın.")]
            
            # Benzer kelimeler için varyasyonları dene
            import requests
            suggestions = []
            
            variations = [
                word + 's',
                word + 'ed', 
                word + 'ing',
                word[:-1] if len(word) > 3 else word,
                word[:-2] if len(word) > 4 else word,
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
                result = f"'{word}' bulunamadı. Benzer kelimeler: {', '.join(suggestions[:5])}"
            else:
                result = f"'{word}' kelimesi ve benzer varyasyonları bulunamadı. Yazımı kontrol edin."
            
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Bilinmeyen araç: {name}")]
    
    except Exception as e:
        error_msg = f"Hata oluştu: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Ana fonksiyon."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    logger.info("Dictionary MCP sunucusu başlatılıyor...")
    asyncio.run(main())
