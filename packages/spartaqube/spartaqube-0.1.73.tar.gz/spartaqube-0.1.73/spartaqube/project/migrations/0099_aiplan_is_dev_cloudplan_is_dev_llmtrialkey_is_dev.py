_B=False
_A='is_dev'
from django.db import migrations,models
class Migration(migrations.Migration):dependencies=[('project','0098_cloudplan_ipv4')];operations=[migrations.AddField(model_name='aiplan',name=_A,field=models.BooleanField(default=_B)),migrations.AddField(model_name='cloudplan',name=_A,field=models.BooleanField(default=_B)),migrations.AddField(model_name='llmtrialkey',name=_A,field=models.BooleanField(default=_B))]