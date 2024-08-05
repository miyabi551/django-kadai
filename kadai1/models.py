from django.db import models


class Employee(models.Model):
    empid = models.CharField(max_length=8, primary_key=True)
    empfname = models.CharField(max_length=64)
    emplname = models.CharField(max_length=64)
    emppasswd = models.CharField(max_length=64)
    emprole = models.IntegerField()

    class Meta:
        db_table = 'kadai1_employee'


class Tabyouin(models.Model):
    tabyouinid = models.CharField(max_length=20, unique=True, primary_key=True)
    tabyouinmei = models.CharField(max_length=64)
    tabyouinaddress = models.CharField(max_length=64)
    tabyouintel = models.CharField(max_length=13)
    tabyouinshihonkin = models.CharField(max_length=13)
    kyukyu = models.BooleanField(default=False)

    class Meta:
        db_table = 'kadai1_tabyouin'


class Patient(models.Model):
    patid = models.CharField(max_length=8, primary_key=True)
    patfname = models.CharField(max_length=64)
    patlname = models.CharField(max_length=64)
    hokenmei = models.CharField(max_length=64)
    hokenexp = models.DateField()

    class Meta:
        db_table = 'kadai1_patient'


class Medication(models.Model):
    medicineid = models.AutoField(max_length=8, primary_key=True)
    medicinename = models.CharField(max_length=64, blank=True, null=True)
    unit = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        db_table = 'kadai1_medication'  # 明示的にテーブル名を指定


class Medication_K(models.Model):
    id = models.AutoField(primary_key=True)
    kanzyaid = models.IntegerField()
    kanzyasei = models.CharField(max_length=64, blank=False)
    kanzyamei = models.CharField(max_length=64, blank=False)
    kusuriname = models.CharField(max_length=100)
    suuryou = models.IntegerField()

    class Meta:
        db_table = 'kadai1_Medication_K'


