from transformers import pipeline
from spellchecker import SpellChecker

# Initialize the fill-mask pipeline with BERT
fill_mask = pipeline('fill-mask', model='bert-base-uncased')

# Initialize the spell checker
spell = SpellChecker()

def correct_text(text):
    words = text.split()
    corrected_words = []
    for word in words:
        # Check if the word is misspelled
        if word.lower() not in spell:
            # Replace the misspelled word with [MASK] in the text
            masked_text = text.replace(word, fill_mask.tokenizer.mask_token)
            # Get predictions for the masked word
            predictions = fill_mask(masked_text)
            if predictions:
                # Take the top prediction and replace it
                corrected_word = predictions[0]['token_str'].strip()
                corrected_words.append(corrected_word)
            else:
                # If no prediction is found, keep the original word
                corrected_words.append(word)
        else:
            # If the word is correctly spelled, keep it
            corrected_words.append(word)
    return ' '.join(corrected_words)

# Example usage
if __name__ == "__main__":
    text = "Iaw is important for society, and 1o0 people agree."
    corrected_text = correct_text(text)
    print("Original Text:")
    print(text)
    print("\nCorrected Text:")
    print(corrected_text)
