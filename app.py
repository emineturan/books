import requests
import json
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getDefinitions(word: str) -> str:
    """
    Get definitions for a word.
    """
    try:
        if not word or not word.strip():
            return "No definitions found."
        
        word = word.strip().lower()
        logger.info(f"Fetching definitions for: {word}")
        
        # Use 'https://api.dictionaryapi.dev/api/v2/entries/en/<word>' to get definitions
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            definitions = []
            
            # Her anlam için tanımları topla
            for meaning in data[0]['meanings']:
                part_of_speech = meaning.get('partOfSpeech', '')
                for i, definition in enumerate(meaning['definitions']):
                    if part_of_speech:
                        definitions.append(f"({part_of_speech}) {definition['definition']}")
                    else:
                        definitions.append(definition['definition'])
            
            if definitions:
                result = "\n\n".join(definitions)
                logger.info(f"Successfully found {len(definitions)} definitions for: {word}")
                return result
            else:
                return "No definitions found."
        else:
            logger.warning(f"API returned status code {response.status_code} for word: {word}")
            return "No definitions found."
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching definitions for {word}: {e}")
        return "No definitions found."
    except Exception as e:
        logger.error(f"Error while fetching definitions for {word}: {e}")
        return "No definitions found."

def getWordDetails(word: str) -> str:
    """
    Get detailed word information including phonetics, synonyms, etc.
    """
    try:
        if not word or not word.strip():
            return "No word details found."
        
        word = word.strip().lower()
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            word_data = data[0]
            
            result = f"Word: {word_data.get('word', word).upper()}\n\n"
            
            # Phonetics
            if 'phonetics' in word_data and word_data['phonetics']:
                for phonetic in word_data['phonetics']:
                    if 'text' in phonetic:
                        result += f"Pronunciation: {phonetic['text']}\n"
                        break
                result += "\n"
            
            # Meanings with details
            for meaning in word_data.get('meanings', []):
                part_of_speech = meaning.get('partOfSpeech', 'Unknown')
                result += f"Part of Speech: {part_of_speech.title()}\n"
                
                for i, definition in enumerate(meaning.get('definitions', []), 1):
                    result += f"  {i}. {definition.get('definition', '')}\n"
                    
                    if 'example' in definition:
                        result += f"     Example: {definition['example']}\n"
                
                # Synonyms
                if 'synonyms' in meaning and meaning['synonyms']:
                    result += f"  Synonyms: {', '.join(meaning['synonyms'][:5])}\n"
                
                # Antonyms
                if 'antonyms' in meaning and meaning['antonyms']:
                    result += f"  Antonyms: {', '.join(meaning['antonyms'][:5])}\n"
                
                result += "\n"
            
            return result.strip()
        else:
            return "No word details found."
            
    except Exception as e:
        logger.error(f"Error while fetching word details for {word}: {e}")
        return "No word details found."
