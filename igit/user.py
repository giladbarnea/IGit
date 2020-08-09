# from traitlets.config import LazyConfigValue
#
# from igit.util import cachedprop
# from igit.config import loader
#
#
# class User:
#
#     def name(self):
#         config = loader.load_config()
#         print(f'loader.config: ', loader.config)
#         uzer: LazyConfigValue = loader.config["user"]
#         print(f'loader.config["user"]: ', uzer)
#         print(f'uzer._value: ', uzer._value)
#         print('config.keys():', config.keys())
#         print(f'config.values():', config.values())
#         uservalue: LazyConfigValue = config['user']
#         profilevalue: LazyConfigValue = config['user.profile']
#         print(f'profilevalue: ', profilevalue)
#         print(f'profilevalue.to_dict(): ', profilevalue.to_dict())
#         print(f'uservalue.has_trait("profile"): ', uservalue.has_trait("profile"))
#         print("config['user']: ", uservalue)
#         print(f'uservalue.to_dict(): ', uservalue.to_dict())
#         print(f'uservalue["profile"]: ', uservalue.get_value("profile"))
#
#         return 'giladbarnea'
