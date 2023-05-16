from django.db.models.signals import post_save  
from django.dispatch import receiver   
from .models import BaseSetting, NissanMaster


@receiver(post_save, sender=NissanMaster)
def update_base_setting(sender, instance, **kwargs):
    try:
        agent_code = BaseSetting.objects.get(setting_value=instance.agent)
        agent_code.setting_value=int(agent_code.setting_value)+1

        address_1 = BaseSetting.objects.get(setting_value=instance.address_1)
        address_1.setting_value=int(address_1.setting_value)+1

        agent_code.save() 
        address_1.save()
    except Exception as e:
        print(e)


post_save.connect(update_base_setting, sender=NissanMaster)