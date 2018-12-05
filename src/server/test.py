# -*- coding: utf-8 -*-
# Common package
# Personal package
import util

aes_code = util.identifier_encrypt(util.aes_key, 'student', '3901160621')
print(aes_code)
print(util.identifier_decrypt(util.aes_key, aes_code))
# cd67e1c89588aa755c7974d0020be7ec
print(util.identifier_decrypt(util.aes_key, 'cd67e1c89588aa755c7974d0020be7ec'))