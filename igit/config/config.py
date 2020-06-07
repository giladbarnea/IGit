from traitlets import config

loader = config.PyFileConfigLoader('igitconfig.py', path='/home/gilad/.config/igit')
print(f'loader: ', loader)
