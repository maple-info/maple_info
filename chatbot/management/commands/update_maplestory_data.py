from django.core.management.base import BaseCommand
from chatbot.update_maplestory_data import update_maplestory_data

class Command(BaseCommand):
    help = '메이플스토리 데이터를 Pinecone DB에 업데이트합니다.'

    def handle(self, *args, **options):
        update_maplestory_data()
        self.stdout.write(self.style.SUCCESS('메이플스토리 데이터가 성공적으로 업데이트되었습니다.'))