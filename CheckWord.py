# dependency : pyspellchecker
# pip install pyspellchecker

from spellchecker import SpellChecker

class checkSpelling():
    spell = SpellChecker()
    
    def check_spelling(self,word):
        misspelled = self.spell.unknown([word])
        if len(misspelled)>0:
            return self.spell.correction(word)
        else:
            return word


     
