# -*- coding: UTF-8 -*-


from .crackers.akamai import AkamaiV2Cracker, crack_akamai_v3, async_crack_akamai_v3
from .crackers.aws import AwsUniversalCracker
from .crackers.cloudflare import CloudFlareCracker
from .crackers.discord import DiscordCracker
from .crackers.hcaptcha import HcaptchaCracker
from .crackers.incapsula import (IncapsulaRbzidCracker,
                                 IncapsulaReese84Cracker,
                                 IncapsulaUtmvcCracker)
from .crackers.recaptcha import (ReCaptchaAppCracker,
                                 ReCaptchaEnterpriseCracker,
                                 ReCaptchaSteamCracker,
                                 ReCaptchaUniversalCracker)
from .crackers.datadome import crack_datadome, async_crack_datadome
from .crackers.kasada import KasadaCdCracker, crack_kasada, async_crack_kasada
from .crackers.perimeterx import PerimeterxCracker, crack_perimeterx, async_crack_perimeterx
from .crackers.shape import crack_shape_v1, async_crack_shape_v1, crack_shape_v2, async_crack_shape_v2
from .crackers.tls import TlsV1Cracker


__all__ = [
    'pynocaptcha', 'magneto',
    'CloudFlareCracker', 'IncapsulaReese84Cracker', 'IncapsulaUtmvcCracker', 'IncapsulaRbzidCracker', 'HcaptchaCracker', 
    'AkamaiV2Cracker', 'ReCaptchaUniversalCracker', 'ReCaptchaEnterpriseCracker', 'ReCaptchaSteamCracker',
    'TlsV1Cracker', 'DiscordCracker', 'ReCaptchaAppCracker', 'AwsUniversalCracker', 'PerimeterxCracker', 'KasadaCdCracker', 
    'crack_akamai_v3', 'async_crack_akamai_v3', 'crack_datadome', 'async_crack_datadome',
    'crack_kasada', 'async_crack_kasada', 'crack_perimeterx', 'async_crack_perimeterx',
    'crack_shape_v1', 'async_crack_shape_v1', 'crack_shape_v2', 'async_crack_shape_v2'
]
