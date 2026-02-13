from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase
from chatbot.utils import chunk_text, get_embedding
import os
import pandas as pd
from pathlib import Path

class Command(BaseCommand):
    help = 'Populate the knowledge base with chunks from documents'

    def handle(self, *args, **options):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        kb_dir = BASE_DIR / 'KB'
        kb_dir.mkdir(exist_ok=True)

        # Example: Load ICU antibiotic.xlsx
        excel_path = BASE_DIR / 'DB' / 'ICU antibiotic.xlsx'
        if excel_path.exists():
            df = pd.read_excel(excel_path)
            text = df.to_string()
            chunks = chunk_text(text)
            for chunk in chunks:
                embedding = get_embedding(chunk)
                KnowledgeBase.objects.create(
                    source='ICU antibiotic.xlsx',
                    content=chunk,
                    embedding=embedding
                )
            self.stdout.write(self.style.SUCCESS('Successfully populated KB with ICU antibiotic data'))

        # Add more sources as needed
