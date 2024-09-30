from django.db import models

class Character(models.Model):
    ocid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    level = models.IntegerField()
    class_name = models.CharField(max_length=255)
    world_name = models.CharField(max_length=255)

    # 추가 스탯 필드
    STR = models.FloatField(default=0)
    DEX = models.FloatField(default=0)
    INT = models.FloatField(default=0)
    LUK = models.FloatField(default=0)
    최소_공격력 = models.FloatField(default=0)
    최대_공격력 = models.FloatField(default=0)
    데미지 = models.FloatField(default=0)
    보스_몬스터_데미지 = models.FloatField(default=0)
    방어율_무시 = models.FloatField(default=0)
    크리티컬_확률 = models.FloatField(default=0)
    크리티컬_데미지 = models.FloatField(default=0)

    def __str__(self):
        return self.name
