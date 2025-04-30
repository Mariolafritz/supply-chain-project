from PyPDF2 import PdfReader
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# Paths to my three Pdf files for the wordcloud
file_paths = [
    "koalitionsvertrag-2025.pdf",
    "stellungnahme-mensch-und-maschine.pdf",
    "m_mhb_po2021_ba_scm_2425.pdf"
]

# Read and combine text from all PDFs
all_text = ""
for path in file_paths:
    reader = PdfReader(path)
    for page in reader.pages:
        all_text += page.extract_text() or ""

# Set stopwords to exclude common words
stopwords = set(STOPWORDS)

# Create the Word Cloud
wordcloud = WordCloud(
    width=1200,
    height=600,
    background_color="white",
    stopwords=stopwords,
    collocations=False
).generate(all_text)

# Save image as PNG
wordcloud.to_file("wordcloud_combined_documents.png")

# Display in VS Code 
plt.figure(figsize=(15, 7.5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.tight_layout()
plt.show()
