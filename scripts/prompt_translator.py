import os
import re
import csv
import modules.scripts as scripts
import gradio as gr

from transformers import MBart50TokenizerFast, MBartForConditionalGeneration

# The directory to store the models
cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')


class MBartTranslator:
    """MBartTranslator class provides a simple interface for translating text using the MBart language model.

    The class can translate between 50 languages and is based on the "facebook/mbart-large-50-many-to-many-mmt"
    pre-trained MBart model. However, it is possible to use a different MBart model by specifying its name.

    Attributes:
        model (MBartForConditionalGeneration): The MBart language model.
        tokenizer (MBart50TokenizerFast): The MBart tokenizer.
    """

    def __init__(self, model_name="facebook/mbart-large-50-many-to-many-mmt", src_lang=None, tgt_lang=None):

        self.supported_languages = [
            "ar_AR",
            "de_DE",
            "en_XX",
            "es_XX",
            "fr_XX",
            "hi_IN",
            "it_IT",
            "ja_XX",
            "ko_XX",
            "pt_XX",
            "ru_RU",
            "zh_XX",
            "af_ZA",
            "bn_BD",
            "bs_XX",
            "ca_XX",
            "cs_CZ",
            "da_XX",
            "el_GR",
            "et_EE",
            "fa_IR",
            "fi_FI",
            "gu_IN",
            "he_IL",
            "hi_XX",
            "hr_HR",
            "hu_HU",
            "id_ID",
            "is_IS",
            "ja_XX",
            "jv_XX",
            "ka_GE",
            "kk_XX",
            "km_KH",
            "kn_IN",
            "ko_KR",
            "lo_LA",
            "lt_LT",
            "lv_LV",
            "mk_MK",
            "ml_IN",
            "mr_IN",
            "ms_MY",
            "ne_NP",
            "nl_XX",
            "no_XX",
            "pl_XX",
            "ro_RO",
            "si_LK",
            "sk_SK",
            "sl_SI",
            "sq_AL",
            "sr_XX",
            "sv_XX",
            "sw_TZ",
            "ta_IN",
            "te_IN",
            "th_TH",
            "tl_PH",
            "tr_TR",
            "uk_UA",
            "ur_PK",
            "vi_VN",
            "war_PH",
            "yue_XX",
            "zh_CN",
            "zh_TW",
        ]
        print("Building translator")
        print("Loading generator (this may take few minutes the first time as I need to download the model)")
        self.model = MBartForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_dir)
        print("Loading tokenizer")
        self.tokenizer = MBart50TokenizerFast.from_pretrained(model_name, src_lang=src_lang, tgt_lang=tgt_lang,
                                                              cache_dir=cache_dir)
        print("Translator is ready")

    def translate(self, text: str, input_language: str, output_language: str) -> str:
        """Translate the given text from the input language to the output language.

        Args:
            text (str): The text to translate.
            input_language (str): The input language code (e.g. "hi_IN" for Hindi).
            output_language (str): The output language code (e.g. "en_US" for English).

        Returns:
            str: The translated text.
        """
        if input_language not in self.supported_languages:
            raise ValueError(f"Input language not supported. Supported languages: {self.supported_languages}")
        if output_language not in self.supported_languages:
            raise ValueError(f"Output language not supported. Supported languages: {self.supported_languages}")

        self.tokenizer.src_lang = input_language
        encoded_input = self.tokenizer(text, return_tensors="pt")
        generated_tokens = self.model.generate(
            **encoded_input, forced_bos_token_id=self.tokenizer.lang_code_to_id[output_language]
        )
        translated_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

        return translated_text[0]


class LanguageOption:
    """
    A class representing a language option in a language selector.

    Attributes:
        label (str): The display label for the language option.
        language_code (str): The ISO 639-1 language code for the language option.
    """

    def __init__(self, label, language_code):
        """
        Initializes a new LanguageOption instance.

        Args:
            label (str): The display label for the language option.
            language_code (str): The ISO 639-1 language code for the language option.
        """
        self.label = label
        self.language_code = language_code


# This is a list of LanguageOption objects that represent the various language options available.
# Each LanguageOption object contains a label that represents the display name of the language and
# a language code that represents the code for the language that will be used by the translation model.
# The language codes follow a format of "xx_YY" where "xx" represents the language code and "YY" represents the
# country or region code. If the language code is not specific to a country or region, then "XX" is used instead.
# For example, "en_XX" represents English language and "fr_FR" represents French language specific to France.
# These LanguageOption objects will be used to display the language options to the user and to retrieve the
# corresponding language code when the user selects a language.
language_options = [
    LanguageOption("Arabic", "ar_AR"),
    LanguageOption("Deutsch", "de_DE"),
    LanguageOption("English", "en_XX"),
    LanguageOption("Spanish", "es_XX"),
    LanguageOption("French", "fr_XX"),
    LanguageOption("Hindi", "hi_IN"),
    LanguageOption("Italian", "it_IT"),
    LanguageOption("Japanese", "ja_XX"),
    LanguageOption("Korean", "ko_XX"),
    LanguageOption("Portuguese", "pt_XX"),
    LanguageOption("Russian", "ru_RU"),
    LanguageOption("Chinese", "zh_XX"),
    LanguageOption("Afrikaans", "af_ZA"),
    LanguageOption("Bengali", "bn_BD"),
    LanguageOption("Bosnian", "bs_XX"),
    LanguageOption("Catalan", "ca_XX"),
    LanguageOption("Czech", "cs_CZ"),
    LanguageOption("Danish", "da_XX"),
    LanguageOption("Greek", "el_GR"),
    LanguageOption("Estonian", "et_EE"),
    LanguageOption("Persian", "fa_IR"),
    LanguageOption("Finnish", "fi_FI"),
    LanguageOption("Gujarati", "gu_IN"),
    LanguageOption("Hebrew", "he_IL"),
    LanguageOption("Croatian", "hr_HR"),
    LanguageOption("Hungarian", "hu_HU"),
    LanguageOption("Indonesian", "id_ID"),
    LanguageOption("Icelandic", "is_IS"),
    LanguageOption("Javanese", "jv_XX"),
    LanguageOption("Georgian", "ka_GE"),
    LanguageOption("Kazakh", "kk_XX"),
    LanguageOption("Khmer", "km_KH"),
    LanguageOption("Kannada", "kn_IN"),
    LanguageOption("Korean", "ko_KR"),
    LanguageOption("Lao", "lo_LA"),
    LanguageOption("Lithuanian", "lt_LT"),
    LanguageOption("Latvian", "lv_LV"),
    LanguageOption("Macedonian", "mk_MK"),
    LanguageOption("Malayalam", "ml_IN"),
    LanguageOption("Marathi", "mr_IN"),
    LanguageOption("Malay", "ms_MY"),
    LanguageOption("Nepali", "ne_NP"),
    LanguageOption("Dutch", "nl_XX"),
    LanguageOption("Norwegian", "no_XX"),
    LanguageOption("Polish", "pl_XX"),
    LanguageOption("Romanian", "ro_RO"),
    LanguageOption("Sinhala", "si_LK"),
    LanguageOption("Slovak", "sk_SK"),
    LanguageOption("Slovenian", "sl_SI"),
    LanguageOption("Albanian", "sq_AL"),
    LanguageOption("Serbian", "sr_XX"),
    LanguageOption("Swedish", "sv_XX"),
    LanguageOption("Swahili", "sw_TZ"),
    LanguageOption("Tamil", "ta_IN"),
    LanguageOption("Telugu", "te_IN"),
    LanguageOption("Tamil ", "ta_IN"),
    LanguageOption("Telugu", "te_IN"),
    LanguageOption("Thai", "th_TH"),
    LanguageOption("Tagalog", "tl_PH"),
    LanguageOption("Turkish", "tr_TR"),
    LanguageOption("Ukrainian", "uk_UA"),
    LanguageOption("Urdu", "ur_PK"),
    LanguageOption("Vietnamese", "vi_VN"),
    LanguageOption("Waray", "war_PH"),
    LanguageOption("Cantonese", "yue_XX"),
    LanguageOption("Chinese", "zh_CN"),
    LanguageOption("Chinese", "zh_TW"),
]


def remove_unnecessary_spaces(text):
    """Removes unnecessary spaces between characters."""
    pattern = r"\)\s*\+\+|\)\+\+\s*"
    replacement = r")++"
    return re.sub(pattern, replacement, text)


def extract_plus_positions(text):
    """
    Given a string of text, extracts the positions of all sequences of one or more '+' characters.

    Args:
    - text (str): the input text

    Returns:
    - positions (list of lists): a list of [start, end, count] for each match, where start is the index of the
      first '+' character, end is the index of the last '+' character + 1, and count is the number of '+' characters
      in the match.
    """
    # Match any sequence of one or more '+' characters
    pattern = re.compile(r'\++')

    # Find all matches of the pattern in the text
    matches = pattern.finditer(text)

    # Loop through the matches and add their positions to the output list
    positions = []
    last_match_end = None
    for match in matches:
        if last_match_end is not None and match.start() != last_match_end:
            # If there is a gap between the current match and the previous one, add a new position
            j = last_match_end - 1
            while text[j] == "+":
                j -= 1
            j += 1
            positions.append([j, last_match_end, last_match_end - j])

        last_match_end = match.end()

    # If the final match extends to the end of the string, add its position to the output list
    if last_match_end is not None and last_match_end == len(text):
        j = last_match_end - 1
        while text[j] == "+":
            j -= 1
        j += 1
        positions.append([j, last_match_end, last_match_end - j])

    return positions


def match_pluses(original_text, translated_text):
    """
    Given two strings of text, replaces sequences of '+' characters in the second string with the corresponding
    sequences of '+' characters in the first string.

    Args:
    - original_text (str): the original text
    - translated_text (str): the translated text with '+' characters

    Returns:
    - output (str): the translated text with '+' characters replaced by those in the original text
    """
    in_positions = extract_plus_positions(original_text)
    out_positions = extract_plus_positions(translated_text)

    out_vals = []
    out_current_pos = 0

    if len(in_positions) == len(out_positions):
        # Iterate through the positions and replace the sequences of '+' characters in the translated text
        # with those in the original text
        for in_, out_ in zip(in_positions, out_positions):
            out_vals.append(translated_text[out_current_pos:out_[0]])
            out_vals.append(original_text[in_[0]:in_[1]])
            out_current_pos = out_[1]

            # Check that the number of '+' characters in the original and translated sequences is the same
            if in_[2] != out_[2]:
                print("detected different + count")

    # Add any remaining text from the translated string to the output
    out_vals.append(translated_text[out_current_pos:])

    # Join the output values into a single string
    output = "".join(out_vals)
    return output


def post_process_prompt(original, translated):
    """Applies post-processing to the translated prompt such as removing unnecessary spaces and extra plus signs."""
    clean_prompt = remove_unnecessary_spaces(translated)
    clean_prompt = match_pluses(original, clean_prompt)
    # clean_prompt = remove_extra_plus(clean_prompt)
    return clean_prompt


# 读取 csv 文件到内存中缓存起来
def load_csv(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        cache = dict(reader)
    return cache


def custom_translate(text, cache):
    if text in cache:
        return cache[text]
    else:
        return None


class Script(scripts.Script):
    def __init__(self) -> None:
        """Initializes the Script class and sets the default value for enable_translation attribute."""
        super().__init__()
        self.enable_translation = False
        self.is_negative_translate_active = False

    def title(self):
        """Returns the title of the script."""
        return "Translate prompt to english"

    def show(self, is_img2img):
        """Returns the visibility status of the script in the interface."""
        return scripts.AlwaysVisible

    def set_active(self, active):
        """Sets the is_active attribute and initializes the translator object if not already created.
        Also, sets the visibility of the language dropdown to True."""
        self.is_active = active
        if not hasattr(self, "translator"):
            self.translator = MBartTranslator()
        if self.is_active:
            return "# I am ready", self.options.update(visible=True)
        else:
            return "After enabling translation, please Wait until I am ready", self.options.update(visible=False)

    def set_negative_translate_active(self, negative_translate_active):
        """Sets the is_active attribute and initializes the translator object if not already created.
        Also, sets the visibility of the language dropdown to True."""
        self.is_negative_translate_active = negative_translate_active

    def ui(self, is_img2img):
        """Sets up the user interface of the script."""
        self.is_active = False
        self.current_axis_options = [x for x in language_options]

        with gr.Row():
            with gr.Column(scale=19):
                with gr.Accordion("Prompt Translator", open=False):
                    with gr.Accordion("Help", open=False):
                        md = gr.Markdown("""
                        # Description
                        This script translates your prompt from another language to english before generating the image allowing you to write prompts in your native language.
                        # How to use
                        Select Enable translation and wait until you the label shows ready.
                        Once the label has Ready on it, select the prompt language, write the prompt in the prompt field then press generate. The script will translate the prompt and generate the text.
                        # Note
                        First time you enable the script, it may take a long time (around a minute), but once loaded, it will be faster.
                        """)
                    with gr.Column():
                        self.enable_translation = gr.Checkbox(label="Enable translation")
                        with gr.Column() as options:
                            self.options = options
                            self.translate_negative_prompt = gr.Checkbox(label="Translate negative prompt")
                            self.enable_translation.value = False
                            self.language = gr.Dropdown(
                                label="Source language",
                                choices=[x.label for x in self.current_axis_options],
                                value="Chinese",
                                type="index",
                                elem_id=self.elem_id("x_type")
                            )
                        self.output = gr.Markdown(value="After enabling translation, please Wait until I am ready",
                                                  visible=True)
                        self.enable_translation.change(
                            self.set_active,
                            [self.enable_translation],
                            [self.output, self.options],
                            show_progress=True
                        )
                        self.translate_negative_prompt.change(
                            self.set_negative_translate_active,
                            [self.translate_negative_prompt],
                        )

        self.options.visible = False
        return [self.language]

    def get_prompts(self, p):
        """Returns the original prompts and negative prompts associated with a Prompt object."""
        original_prompts = p.all_prompts if len(p.all_prompts) > 0 else [p.prompt]
        original_negative_prompts = (
            p.all_negative_prompts
            if len(p.all_negative_prompts) > 0
            else [p.negative_prompt]
        )

        return original_prompts, original_negative_prompts

    def is_english(self, text):
        # 判断字符串是否只包含英文字符和空格
        return all(c.isascii() or c.isspace() for c in text)

    def transfer(self, text, ln_code):
        # 加载 csv 文件并缓存到内存中
        csv_path = os.path.join(os.path.dirname(__file__), 'translations.csv')
        cache = load_csv(csv_path)
        # 自定义翻译
        result = custom_translate(text, cache)
        if result is not None:
            return result
        else:
            # 调用 API 进行翻译
            en_prompt = self.translator.translate(text, ln_code, "en_XX")
            return en_prompt

    def process_text(self, text, ln_code):
        # 将中文全角标点符号替换为半角标点符号
        text = text.translate(str.maketrans('，。！？；：‘’“”（）【】', ',.!?;:\'\'\"\"()[]'))
        # 使用正则表达式来分割尖括号内外的内容
        parts = re.split(r'(<[^>]*>)', text)

        # 遍历分割后的字符串列表，对尖括号外的内容进行翻译
        translated_parts = []
        for part in parts:
            if part.startswith('<') and part.endswith('>'):
                translated_parts.append(part)
            else:
                # 使用逗号分割字符串，并对每个字符串进行翻译（如果不是英文）
                translated_segments = [self.transfer(segment, ln_code) if not self.is_english(segment) else segment for
                                       segment in part.split(',')]
                translated_parts.append(','.join(translated_segments))

        # 将翻译后的字符串拼接成一个字符串
        return ''.join(translated_parts)

    def process(self, p, language, **kwargs):
        """Translates the prompts from a non-English language to English using the MBartTranslator object."""

        if hasattr(self, "translator") and self.is_active:
            original_prompts, original_negative_prompts = self.get_prompts(p)
            translated_prompts = []
            previous_prompt = ""
            previous_translated_prompt = ""

            for original_prompt in original_prompts:
                if previous_prompt != original_prompt:
                    print(f"Translating prompt to English from {language_options[language].label}")
                    print(f"Initial prompt:{original_prompt}")

                    ln_code = language_options[language].language_code
                    translated_prompt = self.process_text(original_prompt, ln_code)
                    #translated_prompt = self.translator.translate(original_prompt, ln_code, "en_XX")

                    translated_prompt = post_process_prompt(original_prompt, translated_prompt)
                    print(f"Translated prompt:{translated_prompt}")
                    translated_prompts.append(translated_prompt)

                    previous_prompt = original_prompt
                    previous_translated_prompt = translated_prompt
                else:
                    translated_prompts.append(previous_translated_prompt)

            if p.negative_prompt != '' and self.is_negative_translate_active:
                previous_negative_prompt = ""
                previous_translated_negative_prompt = ""
                translated_negative_prompts = []
                for negative_prompt in original_negative_prompts:
                    if previous_negative_prompt != negative_prompt:
                        print(f"Translating negative prompt to English from {language_options[language].label}")
                        print(f"Initial negative prompt:{negative_prompt}")
                        ln_code = language_options[language].language_code
                        #translated_negative_prompt = self.translator.translate(negative_prompt, ln_code, "en_XX")
                        translated_negative_prompt = self.process_text(negative_prompt, ln_code)
                        translated_negative_prompt = post_process_prompt(negative_prompt, translated_negative_prompt)
                        print(f"Translated negative prompt:{translated_negative_prompt}")
                        translated_negative_prompts.append(translated_negative_prompt)

                        previous_negative_prompt = negative_prompt
                        previous_translated_negative_prompt = translated_negative_prompt
                    else:
                        translated_negative_prompts.append(previous_translated_negative_prompt)

                p.negative_prompt = translated_negative_prompts[0]
                p.all_negative_prompts = translated_negative_prompts
            p.prompt = translated_prompts[0]
            p.prompt_for_display = translated_prompts[0]
            p.all_prompts = translated_prompts
