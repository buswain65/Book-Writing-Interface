import textstat

class DemographicAnalyzer:
    """Calculates readability metrics and projects target audience demographics."""

    def analyze(self, text: str) -> dict:
        if not text or len(text.strip()) == 0:
            return {
                "flesch_kincaid_grade": 0,
                "ari_score": 0,
                "reading_ease": 0,
                "projected_demographic": "N/A",
                "avg_sentence_length": 0,
                "avg_syllables_per_word": 0
            }

        fk_grade = textstat.flesch_kincaid_grade(text)
        ari = textstat.automated_readability_index(text)
        ease = textstat.flesch_reading_ease(text)
        words_per_sentence = textstat.avg_sentence_length(text)
        syllables_per_word = textstat.avg_syllables_per_word(text)

        # Algorithmically project age category based on grade level and syntactic density
        if fk_grade <= 6.5:
            demographic = "Middle Grade (Ages 8–12)"
        elif fk_grade <= 9.5:
            demographic = "Young Adult (Ages 12–18)"
        elif fk_grade <= 11.5:
            demographic = "New Adult (Ages 18–25)"
        else:
            demographic = "Adult (Ages 25+)"

        return {
            "flesch_kincaid_grade": round(fk_grade, 1),
            "ari_score": round(ari, 1),
            "reading_ease": round(ease, 1),
            "projected_demographic": demographic,
            "avg_sentence_length": round(words_per_sentence, 1),
            "avg_syllables_per_word": round(syllables_per_word, 2)
        }