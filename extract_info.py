from pdfminer.high_level import extract_text
from config import (pdf_extractor_prompt_template, 
                    model_name,
                    commodity_group_categories,
                    categorize_prompt, 
                    template_procurement_dictionary,
                    template_order_list)
from unstract.llmwhisperer import LLMWhispererClientV2

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from enum import Enum
from typing import Tuple, Dict, Any
import tiktoken
import copy
import os

MAX_CHARS = 40_000
MAX_TOKENS = 10_000
DEBUG = False
openai_key = os.getenv('OPENAI_API_KEY')
llm_whisperer_key = os.getenv('LLMWHISPERER_API_KEY')

if DEBUG:
    pdf_text = '\n\n                                                                                    styleGreen \n                                                                                    100% NATUR. 0% PFLEGE. \n\nstyleGREEN \n FlowerArt GmbH | Wächterhofstraße 50 | 85635 Höhenkirchen Angebot OF2312380 \n                                                           Datum:                                        26.11.23 \nLio Technologies GmbH \n                                                           Version:                                            1 \nVladimir Keil \n                                                           Kunden-Nr .:                                   57692 \nAgnes-Pockels-Bogen 1 \n80992 München                                              Gültig bis:                                   10.12.23 \n                                                           Ihre Anfrage vom:                             26.11.23 \n                                                           Bearbeiter:                                  Lisa Holz \n                                                           Telefon:                         +49 (0) 8102 / 9849621 \n                                                           E-Mail:                          lisa.holz@stylegreen.de \n\nherzlichen Dank für Ihre Anfrage bei styleGREEN. Gerne unterbreiten wir Ihnen folgendes Angebot. Wir freuen uns sehr auf die \n Bestätigung. \n\n       Pos.     Art .- Nr.     Bezeichnung                          Menge     Einheit    Preis/Einh €   Gesamt € \n       1        sG-IN-Be-WKm   styleGREEN INDIVIDUAL - m2             1,28       qm           559,00      715,52 \n                               Modul - Variante Wald- und \n                               Kugelmoos (bxh) 160 x 80 cm \n       2        sG-IN-Ka-Kb-Wm styleGREEN INDIVIDUAL -                4,80       Lfm           25,13       120,62 \n                               Kantenbegrünung Waldmoos pro \n                               Lfm (u) 160 x 80 cm \n       3        sG-IN-OB-Logo- Logo Acrylglas weiß 5mm "ask           1,00       Stk.         350,00       350,00 \n                Acrylglas      Lio " Lange 80 cm  mit \n                               Abstandshalter \n\n                                             Positionen netto                                           1.186,14 € \n                                             Versandkosten netto                                         113,85 € \n                                             Positionen USt. 19,00% auf 1.186,14 €                       225,37 € \n                                             Versandkosten Ust. 19,00% auf 113,85 €                       21,63 € \n                                             Endsumme                                                  1.546,99 € \n\nZahlungsbedingung: Zahlbar innerhalb 7 Tage ohne Abzug \nZahlungsart: Rechnung Individual \n\n Kennen Sie schon unser Moospärchen? Den absoluten Topseller können Sie jetzt einfach für nur UVP 79 € direkt mit bestellen. \n\n Sonderabsprachen: \n\n Dieselzuschlag: \n\n Aufgrund der dramatischen Entwicklung beim Dieselpreis müssen wir auf unsere Frachtraten ab 15.3.2022 einen Dieselzuschlag \n abrechnen. Wir werden nur das allernotwendigste weitergeben, um unsere gewohnt guten Konditionen zu gewährleisten. \n\n www.stylegreen.de | info@stylegreen.de \n FlowerArt GmbH | Wächterhofstraße 50 | 85635 Höhenkirchen | T. +49 8102 98496-0 \n Geschäftsführer: Simon Krämer | AG München | HRB: 185275 | USt-IdNr .: DE271073640 \n BITTE BEACHTEN SIE UNSERE NEUE BANKVERBINDUNG! \n Meine Volksbank Raiffeisenbank eG | IBAN: DE50 7116 0000 0202 6851 16 | BIC: GENODEF1VRR. \n<<<\x0c\n\n                                                                                          styleGreen \n                                                                                          100% NATUR. 0% PFLEGE. \n\nAngebots-Nr .: OF2312380                                 Datum:  27.11.23                               Seite:  2 /   2 \n\nBESTELLBEDINGUNGEN \nZahlungsbedingungen: \nIndividuelle Maßanfertigung: Rechnung, zahlbar innerhalb 7 Tage ohne Abzug \nStandardprodukte: Vorkasse, zahlbar innerhalb 7 Tage ohne Abzug \n\nstyleGREEN STANDARD Produkte \nLieferzeit: Unsere styleGREEN Standardprodukte sind i. d. R. Lagerprodukte und sofort versandbereit. Dies gilt nicht für individuelle \nAnfertigungen \n\nstyleGREEN INDIVIDUAL - Produkte nach Maß \nLieferzeit: ca. 5-6 Wochen nach Auftragserteilung, Abweichung unter Sonderabsprache \nExpressaufschlag: 25% bei Produktion innerhalb von 2 Wochen \nMindestabnahmemenge: 1 Quadratmeter; kleinere Flächen werden stets mit dem Preis eines Quadratmeters berechnet. \nMontage: Alle Preise verstehen sich exkl. Montage \nFertigung: Die Individualflächen werden in Einzelteilen gefertigt. Eine Aufbauanleitung liegt der Lieferung bei. \n\nPRODUKTHINWEISE \nBitte beherzigen Sie diese Hinweise und Sie werden viele Jahre Freude an Ihren styleGREEN Produkten haben! Informieren Sie gerne \nauch alle Personen, die mit diesen Produkten leben oder arbeiten, damit auch diese die Hinweise einhalten können. \nPflege: Es ist keine Pflege notwendig. Bitte gießen oder besprühen Sie unsere Produkte daher nicht. \nBitte vermeiden Sie: \n- dauerhafte, intensive Sonnen- oder Lichteinstrahlung (gilt auch für LED-Licht) \n- hohe Luftfeuchtigkeit (>70%) \n- sehr trockene Luft (<40%) \n- direkte Hitzeeinwirkung (z.B. Kamin, Heizung) \nGeruch: Durch die Konservierung bleibt der Geruch der Pflanzen kurzzeitig erhalten. Bei regelmäßigem Lüften verschwindet dieser \nGeruch jedoch nach wenigen Wochen. \nFarbe: Das Moos kann bei Berührung Farbe abgeben. Verwenden Sie zur Montage Handschuhe oder waschen Sie anschließend Ihre \nHände, um Verschmutzung anderer Gegenstände zu vermeiden. \nBei unseren Pflanzen und Moosen handelt es sich um rein natürliche Produkte, deshalb kann es in seltenen Fällen zu Veränderungen \nkommen (Farbveränderung, Flechtenbildung, Wachstum). \n\nEs gelten die AGB der FlowerArt GmbH. Diese finden Sie unter: www.stylegreen.de/allgemeine-geschaeftsbedingungen. \n\n www.stylegreen.de | info@stylegreen.de \n FlowerArt GmbH | Wächterhofstraße 50 | 85635 Höhenkirchen | T. +49 8102 98496-0 \n Geschäftsführer: Simon Krämer | AG München | HRB: 185275 | USt-IdNr .: DE271073640 \n BITTE BEACHTEN SIE UNSERE NEUE BANKVERBINDUNG! \n Meine Volksbank Raiffeisenbank eG | IBAN: DE50 7116 0000 0202 6851 16 | BIC: GENODEF1VRR. \n<<<\x0c'
#-----
class ExtractionMethod(Enum):
    TEXT_ONLY = 1
    OCR_TEXT = 2

def extract_pdf(file_path: str, extraction_method: ExtractionMethod = ExtractionMethod.OCR_TEXT) -> str:
    def ocr_text_method(file_path):
        pdf_extractor = LLMWhispererClientV2(base_url="https://llmwhisperer-api.us-central.unstract.com/api/v2", api_key=llm_whisperer_key)
        whisper_result = pdf_extractor.whisper(
                    file_path=file_path,
                    wait_for_completion=True,
                    mark_vertical_lines=True,
                    mark_horizontal_lines=True,
                    wait_timeout=200
                )
        extraction = whisper_result.get('extraction', {})
        return extraction.get('result_text', '')

    def text_only_method(file_path):
        pdf_text = extract_text(file_path)
        pdf_text = pdf_text.replace('\xa0', ' ')
        return pdf_text
    
    if extraction_method == ExtractionMethod.OCR_TEXT:
        try:
            return ocr_text_method(file_path)
        except Exception as e:
            print('---')
            print(f'LLMWhisperer Error: {str(e)}')
            print('Trying text only method pdfminer')
            print('---')
            try:
                return text_only_method(file_path)
            except Exception as e:
                print('---')
                print(f'PdfMiner Error: {str(e)}')
                print('---')
                return ''

    else:
        try:
            return text_only_method(file_path)
        except Exception as e:
            print('---')
            print(f'PdfMiner Error: {str(e)}')
            print('---')
            return ''

def check_token_limit(pdf_text: str):
    if len(pdf_text) > MAX_CHARS:
        raise ValueError("Document too large. Please upload a smaller file.")

    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(pdf_text + pdf_extractor_prompt_template))
    if num_tokens > MAX_TOKENS:
        raise ValueError("Document too large in token count. Please upload a smaller file.")

def extract_procurement_info(pdf_text: str) -> Tuple[Dict, str]:
    llm = ChatOpenAI(model=model_name, temperature=0, openai_api_key=openai_key)
    parser = JsonOutputParser()

    system_msg = SystemMessage(content="You are a precise information extraction assistant for procurement documents.")
    user_msg = HumanMessage(content=f"{pdf_extractor_prompt_template} \n PDF Text: {pdf_text} \n {parser.get_format_instructions()}")

    responses = llm.generate([[system_msg, user_msg]])
    responses = responses.generations[0][0].text
    parsed_output = parser.parse(responses)

    system_msg = SystemMessage(content="You are an expert procurement classifier. Categorize text accurately")
    user_msg = HumanMessage(content=f"{categorize_prompt} \n PDF Text: {pdf_text}")
    category = llm.generate([[system_msg, user_msg]])
    
    category = category.generations[0][0].text
    return parsed_output, category
    
def validate_dict_structure(llm_dictionary: Dict, template_dictionary:Dict):
    keys_match = set(llm_dictionary.keys()) == set(template_dictionary.keys())
    if not keys_match:
        print('Some/All LLM keys in response not in template')
    for key, val in llm_dictionary.items():
        if not isinstance(val, template_dictionary[key]):
            print(f'Expected {template_dictionary[key]} but got\
                {val} in LLM response')
        if key == "Order Lines":
            for subdict in val:
                if not isinstance(subdict, dict):
                    print(f'Expected the elements in Order List to be Dict')
                keys_match = set(subdict.keys()) == set(template_order_list.keys())
                for subkey, subval in subdict.items():
                    if not isinstance(subval, template_order_list[subkey]):
                        try:
                            subval = template_order_list[subkey](subval)
                        except:
                            print(f'Expected {template_order_list[subkey]} \
                                but got {subval} i.e. type {type(subval)} in LLM response')

def format_llm_response(llm_dictionary: Dict[str, Any], template_dictionary: Dict[str, Any], template_order_list: Dict[str, Any], verbose: bool = True) -> Dict[str, Any]:
    formatted_dictionary = copy.deepcopy(template_dictionary)

    for key, template_val in template_dictionary.items():
        if key not in llm_dictionary:
            if verbose:
                print(f"Missing key: '{key}' – using template default: {template_val}")
            continue

        val = llm_dictionary[key]

        if isinstance(template_val, list) and template_val and isinstance(template_order_list, dict):
            if isinstance(val, list):
                formatted_list = []
                for i, subdict in enumerate(val):
                    if not isinstance(subdict, dict):
                        if verbose:
                            print(f"Element {i} in '{key}' is not a dict, skipping")
                        continue
                    formatted_subdict = {}
                    for subkey, subtemplate_val in template_order_list.items():
                        subval = subdict.get(subkey, subtemplate_val)
                        try:
                            subval = subtemplate_val(subval)
                        except (ValueError, TypeError):
                            if verbose:
                                print(f"'{key}[{i}][{subkey}]' expected {subtemplate_val.__name__}, "
                                      f"but got {type(subval).__name__} ({subval}). Using default {subtemplate_val}")
                            subval = subtemplate_val
                        formatted_subdict[subkey] = subval
                    formatted_list.append(formatted_subdict)
                formatted_dictionary[key] = formatted_list
            else:
                if verbose:
                    print(f"'{key}' expected a list, but got {type(val).__name__}. Using template default.")
                formatted_dictionary[key] = template_val

        elif isinstance(template_val, dict) and isinstance(val, dict):
            formatted_dictionary[key] = format_llm_response(val, template_val, verbose=verbose)

        else:
            try:
                formatted_dictionary[key] = template_val(val)
                if verbose and not isinstance(val, template_val):
                    print(f"'{key}' casted from {type(val).__name__} to {template_val.__name__}")
            except (ValueError, TypeError):
                if verbose:
                    print(f"'{key}' expected {template_val.__name__}, "
                          f"but got {type(val).__name__} ({val}). Using template default.")
                formatted_dictionary[key] = template_val

    return formatted_dictionary

def extract_info(file_path):
    if DEBUG:
        extracted_text = pdf_text
    else:
        extracted_text = extract_pdf(file_path)
    
    check_token_limit(extracted_text)
    
    if DEBUG:
        llm_dictionary = {'Vendor Name': 'styleGREEN', 'USt-IdNr': 'DE271073640', 'Requestor Department': '-', 'Order Lines': [{'Product': 'styleGREEN INDIVIDUAL - m2 Modul - Variante Wald- und Kugelmoos (bxh) 160 x 80 cm', 'Unit Price': '€559.00', 'Quantity': '1.28', 'Total': '€715.52'}, {'Product': 'styleGREEN INDIVIDUAL - Kantenbegrünung Waldmoos pro Lfm (u) 160 x 80 cm', 'Unit Price': '€25.13', 'Quantity': '4.80', 'Total': '€120.62'}, {'Product': "Logo Acrylglas weiß 5mm 'ask Lio' Lange 80 cm mit Abstandshalter", 'Unit Price': '€350.00', 'Quantity': '1', 'Total': '€350.00'}], 'Total Cost': '€1546.99'}
        category = 'Facility Management Services'
    else:
        llm_dictionary, category = extract_procurement_info(extracted_text)
    
    formatted_dictionary = format_llm_response(llm_dictionary, template_procurement_dictionary, template_order_list)
    if category not in commodity_group_categories:
        print("Category returned is not in acceptable category list")
        category = ""
    
    formatted_dictionary["Commodity Group"] = category
    return formatted_dictionary