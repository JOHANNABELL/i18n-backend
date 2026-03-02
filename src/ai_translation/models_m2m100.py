"""
Module de traduction utilisant M2M100-418M
Permet de traduire de l'anglais ou français vers le swahili
"""

from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
import os
import gradio as gr



class TranslationModel:
    """ Classe pour gérer les traductions avec M2M100"""

    def __init__(self):
        """initialise et charge le modèle M2M100-418M"""
        LOCAL_MODEL_PATH = "./models/m2m100_418M"

        # Créer le dossier si nécessaire
        os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)

        print("Chargement du modèle M2M100-418M ...")

        # # chargement du modèle  et du tokenizer
        # self.model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
        # self.tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

        self.model = M2M100ForConditionalGeneration.from_pretrained(LOCAL_MODEL_PATH)
        self.tokenizer = M2M100Tokenizer.from_pretrained(LOCAL_MODEL_PATH)

        #Détection du device (GPU ou CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Device utilisé : {self.device}")
        #Déplacer le modèle sur le device approprié
        self.model.to(self.device)

        print("M2M100-418M chargé !")

        # # Sauvegarde locale
        # self.model.save_pretrained(LOCAL_MODEL_PATH)
        # self.tokenizer.save_pretrained(LOCAL_MODEL_PATH)

        print("M2M100-418M sauvegardé !")
        
    def translate(self, text):
        """Traduit du texte anglais ou français vers le swahili

         Args:
            text (str): Texte à traduire
            source_lang (str): Code de la langue source ("en" ou "fr")

        Returns:
            str: Texte traduit en swahili

        Raises:
            ValueError: Si les paramètres sont invalides
        """

        #tokenisation du texte
        inputs = self.tokenizer(text, return_tensors="pt").input_ids.to(self.device)

        #traduction
        translation = self.model.generate(inputs)

        #détokenisation
        translated_text = self.tokenizer.batch_decode(translation, skip_special_tokens=True)[0]

        return translated_text

    def translate_text(self, text, source_lang, target_lang):
        self.tokenizer.src_lang = source_lang
        encoded_text = self.tokenizer(text, return_tensors="pt")
        generated_tokens = self.model.generate(**encoded_text, forced_bos_token_id=self.tokenizer.get_lang_id(target_lang))
        return self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
